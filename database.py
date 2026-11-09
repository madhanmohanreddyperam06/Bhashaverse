"""
BhashaVerse 2.0 - Database Module
SQLite database interface with connection pooling context,
WAL journal mode, foreign key enforcement, and parameterized operations.
"""

from __future__ import annotations
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

from config import (
    DEFAULT_DB_PATH,
    LANGUAGE_MAP_BY_NAME,
    STATUS_APPROVED,
    STATUS_PENDING,
    STATUS_REJECTED,
)

# ==========================================
# Connection & Pragma Management
# ==========================================

def get_db_path(db_path: Optional[Union[str, Path]] = None) -> Path:
    """Resolve and ensure the database file path."""
    if db_path is None:
        target = DEFAULT_DB_PATH
    else:
        target = Path(db_path)
    if str(target) != ":memory:":
        target.parent.mkdir(parents=True, exist_ok=True)
    return target


@contextmanager
def get_connection(
    db_path: Optional[Union[str, Path]] = None,
    timeout: float = 20.0,
) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager providing a managed SQLite connection.
    Enforces foreign keys, row dict factories, and transactional commits.
    """
    resolved_path = get_db_path(db_path)
    conn = sqlite3.connect(
        str(resolved_path),
        timeout=timeout,
        detect_types=sqlite3.PARSE_DECLTYPES,
    )
    conn.row_factory = sqlite3.Row
    try:
        # Enforce foreign keys and performance settings
        conn.execute("PRAGMA foreign_keys = ON;")
        if str(resolved_path) != ":memory:":
            try:
                conn.execute("PRAGMA journal_mode = WAL;")
                conn.execute("PRAGMA synchronous = NORMAL;")
            except sqlite3.DatabaseError:
                pass
        yield conn
    finally:
        conn.close()


def row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    """Convert a sqlite3.Row into a standard Python dict."""
    if row is None:
        return None
    return dict(row)


def rows_to_dicts(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    """Convert a list of sqlite3.Row objects into a list of dicts."""
    return [dict(r) for r in rows]


# ==========================================
# Schema Initialization
# ==========================================

PROVERBS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS proverbs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_uuid TEXT UNIQUE NOT NULL,
    proverb TEXT NOT NULL,
    language TEXT NOT NULL,
    language_code TEXT NOT NULL,
    english_translation TEXT,
    meaning TEXT NOT NULL,
    cultural_context TEXT,
    category TEXT,
    contributor_name TEXT,
    contributor_email TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    rejection_reason TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    moderated_at TEXT,
    moderated_by TEXT
);
"""

MODERATION_LOGS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS moderation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proverb_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    moderator TEXT,
    reason TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (proverb_id) REFERENCES proverbs(id) ON DELETE CASCADE
);
"""

INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_proverbs_language ON proverbs(language);",
    "CREATE INDEX IF NOT EXISTS idx_proverbs_status ON proverbs(status);",
    "CREATE INDEX IF NOT EXISTS idx_proverbs_category ON proverbs(category);",
    "CREATE INDEX IF NOT EXISTS idx_proverbs_created_at ON proverbs(created_at);",
    "CREATE INDEX IF NOT EXISTS idx_proverbs_submission_uuid ON proverbs(submission_uuid);",
    "CREATE INDEX IF NOT EXISTS idx_moderation_logs_proverb_id ON moderation_logs(proverb_id);",
]


def init_db(
    db_path: Optional[Union[str, Path]] = None,
    seed_if_empty: bool = True,
    seed_defaults: Optional[bool] = None,
) -> None:
    """
    Initialize SQLite database schema and indexes.
    Optionally seeds curated high-quality proverbs if table is empty.
    """
    if seed_defaults is not None:
        seed_if_empty = seed_defaults

    with get_connection(db_path) as conn:
        with conn:
            conn.execute(PROVERBS_TABLE_SQL)
            conn.execute(MODERATION_LOGS_TABLE_SQL)
            for idx_stmt in INDEXES_SQL:
                conn.execute(idx_stmt)

    if seed_if_empty:
        seed_default_proverbs(db_path)


# ==========================================
# Proverb Submission & CRUD
# ==========================================

def add_proverb(
    proverb: Union[str, Dict[str, Any], None] = None,
    language: Optional[str] = None,
    language_code: Optional[str] = None,
    meaning: Optional[str] = None,
    english_translation: Optional[str] = None,
    cultural_context: Optional[str] = None,
    category: Optional[str] = None,
    contributor_name: Optional[str] = None,
    contributor_email: Optional[str] = None,
    status: str = STATUS_PENDING,
    db_path: Optional[Union[str, Path]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Insert a new proverb submission into the database.
    Accepts either individual parameters, keyword arguments, or a validated dictionary.
    Returns the created record as a dictionary.
    """
    if isinstance(proverb, dict):
        data = proverb
        clean_proverb = (data.get("proverb") or "").strip()
        clean_language = (data.get("language") or "").strip()
        clean_code = (data.get("language_code") or "").strip()
        if not clean_code and clean_language in LANGUAGE_MAP_BY_NAME:
            clean_code = LANGUAGE_MAP_BY_NAME[clean_language].get("code", "hi")
        clean_meaning = (data.get("meaning") or "").strip()
        clean_translation = data.get("english_translation")
        clean_translation = clean_translation.strip() if clean_translation else None
        clean_context = data.get("cultural_context")
        clean_context = clean_context.strip() if clean_context else None
        clean_category = (data.get("category") or "Wisdom").strip()
        clean_name = (data.get("contributor_name") or "Anonymous Contributor").strip()
        clean_email = data.get("contributor_email")
        clean_email = clean_email.strip() if clean_email else None
        target_status = data.get("status", status)
        target_db_path = kwargs.get("db_path", db_path)
    else:
        clean_proverb = (proverb or kwargs.get("proverb") or "").strip()
        clean_language = (language or kwargs.get("language") or "").strip()
        clean_code = (language_code or kwargs.get("language_code") or "").strip()
        if not clean_code and clean_language in LANGUAGE_MAP_BY_NAME:
            clean_code = LANGUAGE_MAP_BY_NAME[clean_language].get("code", "hi")
        clean_meaning = (meaning or kwargs.get("meaning") or "").strip()
        raw_trans = english_translation or kwargs.get("english_translation")
        clean_translation = raw_trans.strip() if raw_trans else None
        raw_ctx = cultural_context or kwargs.get("cultural_context")
        clean_context = raw_ctx.strip() if raw_ctx else None
        raw_cat = category or kwargs.get("category")
        clean_category = raw_cat.strip() if raw_cat else "Wisdom"
        raw_name = contributor_name or kwargs.get("contributor_name")
        clean_name = raw_name.strip() if raw_name else "Anonymous Contributor"
        raw_email = contributor_email or kwargs.get("contributor_email")
        clean_email = raw_email.strip() if raw_email else None
        target_status = kwargs.get("status", status)
        target_db_path = kwargs.get("db_path", db_path)

    submission_uuid = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    query = """
    INSERT INTO proverbs (
        submission_uuid, proverb, language, language_code, english_translation,
        meaning, cultural_context, category, contributor_name, contributor_email,
        status, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    with get_connection(target_db_path) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    submission_uuid,
                    clean_proverb,
                    clean_language,
                    clean_code,
                    clean_translation,
                    clean_meaning,
                    clean_context,
                    clean_category,
                    clean_name,
                    clean_email,
                    target_status,
                    now_iso,
                    now_iso,
                ),
            )
            new_id = cursor.lastrowid

            # Log creation event
            conn.execute(
                """
                INSERT INTO moderation_logs (proverb_id, action, moderator, reason, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (new_id, "submitted", clean_name, "New user submission", now_iso),
            )

    return get_proverb_by_id(new_id, db_path=target_db_path)  # type: ignore[return-value]


def check_duplicate_proverb(
    proverb: str,
    language: str,
    exclude_id: Optional[int] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    """
    Check if an identical or normalized proverb already exists for the given language.
    """
    normalized = " ".join(proverb.strip().lower().split())
    query = "SELECT id, proverb FROM proverbs WHERE language = ?"
    params: List[Any] = [language]
    if exclude_id is not None:
        query += " AND id != ?"
        params.append(exclude_id)

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        for row in rows:
            existing_norm = " ".join(row["proverb"].strip().lower().split())
            if existing_norm == normalized:
                return True
    return False


def get_proverb_by_id(
    proverb_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieve a single proverb by its primary key ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM proverbs WHERE id = ?", (proverb_id,))
        return row_to_dict(cursor.fetchone())


def get_proverb_by_uuid(
    submission_uuid: str,
    db_path: Optional[Union[str, Path]] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieve a single proverb by its public submission UUID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM proverbs WHERE submission_uuid = ?", (submission_uuid,))
        return row_to_dict(cursor.fetchone())


def get_approved_proverbs(
    limit: Optional[int] = None,
    offset: int = 0,
    query: Optional[str] = None,
    language: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = "newest",
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], int]]:
    """
    Fetch public approved proverbs.
    If page, per_page, query, or filters are passed, returns (results, total_count).
    Otherwise returns results list.
    """
    if (
        page is not None
        or per_page is not None
        or (query and query.strip())
        or (language and language != "All")
        or (category and category != "All")
    ):
        effective_limit = per_page if per_page is not None else (limit or 50)
        effective_offset = (page - 1) * effective_limit if page is not None else offset
        return search_proverbs(
            query=query,
            language=language,
            category=category,
            sort_by=sort_by,
            limit=effective_limit,
            offset=effective_offset,
            status=STATUS_APPROVED,
            db_path=db_path,
        )

    query_sql = "SELECT * FROM proverbs WHERE status = ? ORDER BY id DESC"
    params: List[Any] = [STATUS_APPROVED]
    if limit is not None:
        query_sql += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query_sql, params)
        return rows_to_dicts(cursor.fetchall())


def get_pending_proverbs(
    limit: Optional[int] = None,
    offset: int = 0,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Fetch pending proverbs for maintainer review."""
    query = "SELECT * FROM proverbs WHERE status = ? ORDER BY id ASC"
    params: List[Any] = [STATUS_PENDING]
    if limit is not None:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return rows_to_dicts(cursor.fetchall())


def get_rejected_proverbs(
    limit: Optional[int] = None,
    offset: int = 0,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Fetch rejected proverbs for maintainer review."""
    query = "SELECT * FROM proverbs WHERE status = ? ORDER BY id DESC"
    params: List[Any] = [STATUS_REJECTED]
    if limit is not None:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return rows_to_dicts(cursor.fetchall())


def update_proverb(
    proverb_id: int,
    proverb: Optional[str] = None,
    language: Optional[str] = None,
    language_code: Optional[str] = None,
    english_translation: Optional[str] = None,
    meaning: Optional[str] = None,
    cultural_context: Optional[str] = None,
    category: Optional[str] = None,
    contributor_name: Optional[str] = None,
    moderator: str = "maintainer",
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    """
    Update editable fields of a proverb record and log the edit event.
    """
    fields: List[str] = []
    params: List[Any] = []
    now_iso = datetime.now(timezone.utc).isoformat()

    if proverb is not None:
        fields.append("proverb = ?")
        params.append(proverb.strip())
    if language is not None:
        fields.append("language = ?")
        params.append(language)
    if language_code is not None:
        fields.append("language_code = ?")
        params.append(language_code)
    if english_translation is not None:
        fields.append("english_translation = ?")
        params.append(english_translation.strip())
    if meaning is not None:
        fields.append("meaning = ?")
        params.append(meaning.strip())
    if cultural_context is not None:
        fields.append("cultural_context = ?")
        params.append(cultural_context.strip())
    if category is not None:
        fields.append("category = ?")
        params.append(category)
    if contributor_name is not None:
        fields.append("contributor_name = ?")
        params.append(contributor_name.strip())

    if not fields:
        return False

    fields.append("updated_at = ?")
    params.append(now_iso)
    params.append(proverb_id)

    query = f"UPDATE proverbs SET {', '.join(fields)} WHERE id = ?"

    with get_connection(db_path) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if cursor.rowcount > 0:
                conn.execute(
                    """
                    INSERT INTO moderation_logs (proverb_id, action, moderator, reason, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (proverb_id, "edited", moderator, "Record details updated", now_iso),
                )
                return True
    return False


# ==========================================
# Moderation Actions
# ==========================================

def approve_proverb(
    proverb_id: int,
    moderator: str = "maintainer",
    notes: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    """
    Approve a pending or rejected proverb.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE proverbs
                SET status = ?, rejection_reason = NULL, moderated_at = ?, moderated_by = ?, updated_at = ?
                WHERE id = ? AND status != ?
                """,
                (STATUS_APPROVED, now_iso, moderator, now_iso, proverb_id, STATUS_APPROVED),
            )
            if cursor.rowcount > 0:
                conn.execute(
                    """
                    INSERT INTO moderation_logs (proverb_id, action, moderator, reason, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (proverb_id, "approved", moderator, notes or "Submission approved", now_iso),
                )
                return True
    return False


def reject_proverb(
    proverb_id: int,
    reason: str,
    moderator: str = "maintainer",
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    """
    Reject a pending or approved proverb with a recorded reason.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    clean_reason = reason.strip() if reason else "Does not meet community guidelines"

    with get_connection(db_path) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE proverbs
                SET status = ?, rejection_reason = ?, moderated_at = ?, moderated_by = ?, updated_at = ?
                WHERE id = ?
                """,
                (STATUS_REJECTED, clean_reason, now_iso, moderator, now_iso, proverb_id),
            )
            if cursor.rowcount > 0:
                conn.execute(
                    """
                    INSERT INTO moderation_logs (proverb_id, action, moderator, reason, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (proverb_id, "rejected", moderator, clean_reason, now_iso),
                )
                return True
    return False


def restore_proverb_to_pending(
    proverb_id: int,
    moderator: str = "maintainer",
    reason: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    """
    Restore a rejected or approved proverb back to 'pending' state.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE proverbs
                SET status = ?, rejection_reason = NULL, moderated_at = ?, moderated_by = ?, updated_at = ?
                WHERE id = ?
                """,
                (STATUS_PENDING, now_iso, moderator, now_iso, proverb_id),
            )
            if cursor.rowcount > 0:
                conn.execute(
                    """
                    INSERT INTO moderation_logs (proverb_id, action, moderator, reason, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (proverb_id, "restored_to_pending", moderator, reason or "Restored for re-evaluation", now_iso),
                )
                return True
    return False


def delete_proverb(
    proverb_id: int,
    moderator: str = "maintainer",
    reason: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    """
    Permanently delete a proverb (cascades to moderation_logs).
    """
    with get_connection(db_path) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM proverbs WHERE id = ?", (proverb_id,))
            return cursor.rowcount > 0


def get_moderation_logs(
    proverb_id: Optional[int] = None,
    limit: int = 100,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Retrieve moderation logs, optionally filtered by proverb ID."""
    query = """
    SELECT l.id, l.proverb_id, l.action, l.moderator, l.reason, l.timestamp,
           p.proverb, p.language
    FROM moderation_logs l
    LEFT JOIN proverbs p ON l.proverb_id = p.id
    """
    params: List[Any] = []
    if proverb_id is not None:
        query += " WHERE l.proverb_id = ?"
        params.append(proverb_id)
    query += " ORDER BY l.id DESC LIMIT ?"
    params.append(limit)

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return rows_to_dicts(cursor.fetchall())


# ==========================================
# Search & Filtering
# ==========================================

def search_proverbs(
    query: Optional[str] = None,
    language: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = "newest",
    limit: int = 50,
    offset: int = 0,
    status: str = STATUS_APPROVED,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Search and filter proverbs with pagination and total count.
    Searches across proverb, english_translation, meaning, and cultural_context.
    """
    where_clauses: List[str] = ["status = ?"]
    params: List[Any] = [status]

    if language and language != "All":
        where_clauses.append("language = ?")
        params.append(language)

    if category and category != "All":
        where_clauses.append("category = ?")
        params.append(category)

    if query and query.strip():
        search_pattern = f"%{query.strip()}%"
        where_clauses.append(
            "(proverb LIKE ? OR english_translation LIKE ? OR meaning LIKE ? OR cultural_context LIKE ?)"
        )
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

    where_sql = " WHERE " + " AND ".join(where_clauses)

    count_query = f"SELECT COUNT(*) as total FROM proverbs {where_sql}"

    # Determine sorting
    if sort_by == "oldest":
        order_sql = " ORDER BY id ASC"
    elif sort_by == "alphabetical":
        order_sql = " ORDER BY proverb COLLATE NOCASE ASC"
    else:  # newest
        order_sql = " ORDER BY id DESC"

    data_query = f"SELECT * FROM proverbs {where_sql} {order_sql} LIMIT ? OFFSET ?"
    data_params = list(params) + [limit, offset]

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(count_query, params)
        count_row = cursor.fetchone()
        total_count = count_row["total"] if count_row else 0

        cursor.execute(data_query, data_params)
        results = rows_to_dicts(cursor.fetchall())

    return results, total_count


# ==========================================
# Statistics & Analytics
# ==========================================

def get_statistics(db_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Compute real-time platform statistics from the SQLite database.
    """
    stats: Dict[str, Any] = {
        "total_submissions": 0,
        "approved_proverbs": 0,
        "pending_submissions": 0,
        "rejected_submissions": 0,
        "unique_contributors": 0,
        "active_languages": 0,
        "language_distribution": {},
        "category_distribution": {},
        "recent_submissions": [],
    }

    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # Overall counts by status
        cursor.execute("SELECT status, COUNT(*) as cnt FROM proverbs GROUP BY status")
        for row in cursor.fetchall():
            st = row["status"]
            cnt = row["cnt"]
            if st == STATUS_APPROVED:
                stats["approved_proverbs"] = cnt
            elif st == STATUS_PENDING:
                stats["pending_submissions"] = cnt
            elif st == STATUS_REJECTED:
                stats["rejected_submissions"] = cnt
        stats["total_submissions"] = (
            stats["approved_proverbs"] + stats["pending_submissions"] + stats["rejected_submissions"]
        )

        # Unique contributors (excluding anonymous and empty)
        cursor.execute(
            """
            SELECT COUNT(DISTINCT contributor_identifier) as total_contributors
            FROM (
                SELECT LOWER(TRIM(contributor_email)) as contributor_identifier
                FROM proverbs
                WHERE contributor_email IS NOT NULL AND TRIM(contributor_email) != ''
                UNION
                SELECT LOWER(TRIM(contributor_name)) as contributor_identifier
                FROM proverbs
                WHERE contributor_name IS NOT NULL
                  AND LOWER(TRIM(contributor_name)) NOT IN ('', 'anonymous', 'anonymous contributor')
                  AND (contributor_email IS NULL OR TRIM(contributor_email) = '')
            )
            """
        )
        contrib_row = cursor.fetchone()
        stats["unique_contributors"] = contrib_row["total_contributors"] if contrib_row else 0

        # Language distribution (for approved items)
        cursor.execute(
            """
            SELECT language, COUNT(*) as cnt
            FROM proverbs
            WHERE status = ?
            GROUP BY language
            ORDER BY cnt DESC
            """,
            (STATUS_APPROVED,),
        )
        lang_dist = {row["language"]: row["cnt"] for row in cursor.fetchall()}
        stats["language_distribution"] = lang_dist
        stats["active_languages"] = len(lang_dist)
        stats["active_languages_count"] = len(lang_dist)

        # Category distribution (for approved items)
        cursor.execute(
            """
            SELECT category, COUNT(*) as cnt
            FROM proverbs
            WHERE status = ?
            GROUP BY category
            ORDER BY cnt DESC
            """,
            (STATUS_APPROVED,),
        )
        stats["category_distribution"] = {
            (row["category"] or "Uncategorized"): row["cnt"] for row in cursor.fetchall()
        }

        # Convenience aliases for UI components
        stats["approved_count"] = stats["approved_proverbs"]
        stats["pending_count"] = stats["pending_submissions"]
        stats["rejected_count"] = stats["rejected_submissions"]
        stats["total_contributors"] = stats["unique_contributors"]

        # Recent 5 approved submissions
        cursor.execute(
            """
            SELECT id, submission_uuid, proverb, language, language_code, english_translation,
                   meaning, category, contributor_name, created_at
            FROM proverbs
            WHERE status = ?
            ORDER BY id DESC
            LIMIT 5
            """,
            (STATUS_APPROVED,),
        )
        recent_rows = rows_to_dicts(cursor.fetchall())
        stats["recent_submissions"] = recent_rows
        stats["recent_proverbs"] = recent_rows

    return stats


# ==========================================
# Export Utilities
# ==========================================

EXPORT_PUBLIC_COLUMNS = [
    "id",
    "submission_uuid",
    "proverb",
    "language",
    "language_code",
    "english_translation",
    "meaning",
    "cultural_context",
    "category",
    "contributor_name",
    "created_at",
]

EXPORT_MAINTAINER_COLUMNS = EXPORT_PUBLIC_COLUMNS + [
    "status",
    "rejection_reason",
    "updated_at",
    "moderated_at",
    "moderated_by",
]


def export_proverbs(
    approved_only: bool = True,
    include_maintainer_meta: bool = False,
    status: Optional[str] = None,
    include_private: bool = False,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve proverb records formatted for CSV/JSON export.
    CRITICAL: Never includes contributor_email in any export!
    """
    if status is not None:
        approved_only = (status == STATUS_APPROVED)
    if include_private:
        include_maintainer_meta = True

    cols = EXPORT_MAINTAINER_COLUMNS if include_maintainer_meta else EXPORT_PUBLIC_COLUMNS
    col_str = ", ".join(cols)

    query = f"SELECT {col_str} FROM proverbs"
    params: List[Any] = []
    if approved_only:
        query += " WHERE status = ?"
        params.append(STATUS_APPROVED)
    query += " ORDER BY id ASC"

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return rows_to_dicts(cursor.fetchall())


# ==========================================
# Default Seed Data (10 Indian Languages)
# ==========================================

SEED_PROVERBS = [
    # 1. Hindi (hi)
    {
        "proverb": "जल में रहकर मगर से बैर ठीक नहीं।",
        "language": "Hindi",
        "language_code": "hi",
        "english_translation": "It is unwise to live in the water and make enemies with the crocodile.",
        "meaning": "Do not antagonize powerful individuals or forces within their own sphere of influence.",
        "cultural_context": "Rooted in ancient riverine wisdom, emphasizing adaptability and prudence in social life.",
        "category": "Wisdom",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    {
        "proverb": "अधजल गगरी छलकत जाए।",
        "language": "Hindi",
        "language_code": "hi",
        "english_translation": "A half-filled water pitcher spills more.",
        "meaning": "People with shallow knowledge often boast and speak the loudest, while truly wise people remain humble.",
        "cultural_context": "Derived from the village experience of carrying water pots from the community well.",
        "category": "Education",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    # 2. Telugu (te)
    {
        "proverb": "అడుసు తొక్కనేల కాలు కడగనేల.",
        "language": "Telugu",
        "language_code": "te",
        "english_translation": "Why step into the mud only to wash your feet?",
        "meaning": "Prevention is better than cure; avoid avoidable troubles instead of trying to fix them afterward.",
        "cultural_context": "Reflects pastoral Andhra-Telangana agrarian culture where clean paths were prized.",
        "category": "Life Lessons",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    {
        "proverb": "దీపం ఉండగానే ఇల్లు చక్కబెట్టుకోవాలి.",
        "language": "Telugu",
        "language_code": "te",
        "english_translation": "Set the house in order while the lamp is still burning.",
        "meaning": "Make hay while the sun shines; seize opportunities while resources and health are favorable.",
        "cultural_context": "Before electricity, oil lamps illuminated homes; all important tasks had to be finished before the oil ran dry.",
        "category": "Wisdom",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    # 3. Tamil (ta)
    {
        "proverb": "சிறு துளி பெரு வெள்ளம்.",
        "language": "Tamil",
        "language_code": "ta",
        "english_translation": "Little drops of water make a mighty deluge.",
        "meaning": "Consistent small savings, habits, and efforts compound over time into massive accomplishments.",
        "cultural_context": "Classical Sangam and everyday Tamil wisdom emphasizing thrift, discipline, and nature observation.",
        "category": "Wisdom",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    {
        "proverb": "தொட்டில் பழக்கம் சுடுகாடு மட்டும்.",
        "language": "Tamil",
        "language_code": "ta",
        "english_translation": "Habits cultivated in the cradle last until the cremation ground.",
        "meaning": "Early childhood habits, morals, and character stay with an individual throughout their entire life.",
        "cultural_context": "Emphasizes the vital role of parental guidance and virtuous early upbringing in Tamil culture.",
        "category": "Morality",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    # 4. Bengali (bn)
    {
        "proverb": "অতি চালাকের গলায় দড়ি।",
        "language": "Bengali",
        "language_code": "bn",
        "english_translation": "Too much cleverness ties a noose around one's own neck.",
        "meaning": "Excessive cunning and over-scheming often leads to one's own downfall.",
        "cultural_context": "A prominent warning in Bengal folklore against deceitful and overambitious behavior.",
        "category": "Morality",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    {
        "proverb": "দশের লাঠি একের বোঝা।",
        "language": "Bengali",
        "language_code": "bn",
        "english_translation": "A stick contributed by ten is a light burden, but for one it is an impossible load.",
        "meaning": "Unity and cooperative solidarity make monumental tasks effortless.",
        "cultural_context": "Celebrates the communal spirit of rural Bengal village life and collective labor.",
        "category": "Society",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    # 5. Marathi (mr)
    {
        "proverb": "अति शहाणा त्याचा बैल रिकामा.",
        "language": "Marathi",
        "language_code": "mr",
        "english_translation": "An over-clever farmer's ox remains idle in the shed.",
        "meaning": "Someone who overthinks or believes they are wiser than everyone else ends up achieving nothing practical.",
        "cultural_context": "Centuries-old Maharashtrian farming wisdom balancing practical action against useless theorizing.",
        "category": "Life Lessons",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    {
        "proverb": "शितावरून भाताची परीक्षा.",
        "language": "Marathi",
        "language_code": "mr",
        "english_translation": "Testing a single grain reveals the state of the entire pot of rice.",
        "meaning": "A small representative sample can reveal the true quality or nature of the whole entity.",
        "cultural_context": "Daily domestic cooking observation in Maharashtra kitchen culture, frequently used in philosophy and literature.",
        "category": "Wisdom",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    # 6. Urdu (ur)
    {
        "proverb": "ڈوبتے کو تنکے کا سہارا۔",
        "language": "Urdu",
        "language_code": "ur",
        "english_translation": "A drowning person grasps even at a straw.",
        "meaning": "In times of utter desperation, even the smallest glimmer of hope or assistance is cherished.",
        "cultural_context": "Classical Persian-influenced Hindustani idiom used in classical Urdu poetry and everyday discourse.",
        "category": "Life Lessons",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    {
        "proverb": "ہاتھ کنگن کو آرسی کیا؟",
        "language": "Urdu",
        "language_code": "ur",
        "english_translation": "Why does one wearing a wrist bangle need a small thumb-mirror to inspect it?",
        "meaning": "Truth and obvious realities do not need external proof; evidence is directly visible.",
        "cultural_context": "Refers to traditional Indian jewelry ('Aarsi', a thumb ring mirror) worn by women in royal Mughal courts.",
        "category": "Wisdom",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    # 7. Gujarati (gu)
    {
        "proverb": "ઝાઝા હાથ રળિયામણા.",
        "language": "Gujarati",
        "language_code": "gu",
        "english_translation": "Many hands make tasks joyful and beautiful.",
        "meaning": "Cooperation and team labor turn difficult undertakings into enjoyable community successes.",
        "cultural_context": "Reflects Gujarat's vibrant cooperative business traditions and festive community celebrations.",
        "category": "Society",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    {
        "proverb": "બોલે તેના બોર વેચાય.",
        "language": "Gujarati",
        "language_code": "gu",
        "english_translation": "Only the vendor who calls out sells their berries.",
        "meaning": "Expression, communication, and proactive advocacy are essential for success in commerce and life.",
        "cultural_context": "Originating from traditional open-air bazaars in Saurashtra and Gujarat.",
        "category": "Life Lessons",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    # 8. Kannada (kn)
    {
        "proverb": "ಹಾಸಿಗೆ ಇದ್ದಷ್ಟು ಕಾಲು ಚಾಚು.",
        "language": "Kannada",
        "language_code": "kn",
        "english_translation": "Stretch your legs only as far as your bed extends.",
        "meaning": "Live within your means and manage your finances and desires according to your current capacity.",
        "cultural_context": "A timeless household maxim across Karnataka emphasizing financial prudence and contentment.",
        "category": "Wisdom",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    {
        "proverb": "ಉಪ್ಪಿಗಿಂತ ರುಚಿ ಇಲ್ಲ, ತಾಯಿಗಿಂತ ಬಂಧುವಿಲ್ಲ.",
        "language": "Kannada",
        "language_code": "kn",
        "english_translation": "There is no flavor surpassing salt, and no relative surpassing a mother.",
        "meaning": "The fundamental essentials of life—simple nutrition and maternal love—are incomparable and irreplaceable.",
        "cultural_context": "Deeply revered sentiment across South Indian folk poetry celebrating motherhood and humility.",
        "category": "Family",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    # 9. Malayalam (ml)
    {
        "proverb": "മിന്നുന്നതെല്ലാം പൊன்னಲ್ಲ.",
        "language": "Malayalam",
        "language_code": "ml",
        "english_translation": "All that glitters is not gold.",
        "meaning": "Superficial exterior shine often conceals ordinary or fraudulent substance; do not judge by appearances.",
        "cultural_context": "Commonly cited in Kerala literature and moral education to instill discernment.",
        "category": "Wisdom",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    {
        "proverb": "കൂട്ടിലിട്ട കിളി പാടുമോ?",
        "language": "Malayalam",
        "language_code": "ml",
        "english_translation": "Will a bird kept in a cage sing freely?",
        "meaning": "True creativity, happiness, and genius flourish only in an environment of freedom and dignity.",
        "cultural_context": "Inspired by Kerala's lush verdant nature, bird sanctuaries, and egalitarian literary traditions.",
        "category": "Nature",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    # 10. Odia (or)
    {
        "proverb": "ବିନ୍ଦୁ ବିନ୍ଦୁ ଜଳରେ ସିନ୍ଧୁ ଗଠନ।",
        "language": "Odia",
        "language_code": "or",
        "english_translation": "Drop by drop of water builds the ocean.",
        "meaning": "Patience and small continuous contributions lead to monumental results.",
        "cultural_context": "Rooted in coastal Odisha's reverence for the Bay of Bengal (Mahodadhi) and Jagannath culture.",
        "category": "Wisdom",
        "contributor_name": "BhashaVerse Heritage Team",
    },
    {
        "proverb": "ନ ଦେଖିଲା କଥା ନ କହିବା ଭଲ।",
        "language": "Odia",
        "language_code": "or",
        "english_translation": "It is best not to speak of that which you haven't seen with your own eyes.",
        "meaning": "Avoid rumors, hearsay, and speaking falsehoods without direct verification.",
        "cultural_context": "Traditional village moral code in rural Odisha emphasizing honesty and integrity.",
        "category": "Morality",
        "contributor_name": "BhashaVerse Heritage Team",
    },
]


def seed_default_proverbs(db_path: Optional[Union[str, Path]] = None) -> int:
    """
    Seed initial authentic proverbs into the database if proverbs table is empty.
    Returns the count of seeded proverbs.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM proverbs")
        row = cursor.fetchone()
        if row and row["cnt"] > 0:
            return 0  # Already has data

    inserted = 0
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        with conn:
            for item in SEED_PROVERBS:
                sub_uuid = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO proverbs (
                        submission_uuid, proverb, language, language_code, english_translation,
                        meaning, cultural_context, category, contributor_name,
                        status, created_at, updated_at, moderated_at, moderated_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sub_uuid,
                        item["proverb"],
                        item["language"],
                        item["language_code"],
                        item["english_translation"],
                        item["meaning"],
                        item["cultural_context"],
                        item["category"],
                        item["contributor_name"],
                        STATUS_APPROVED,
                        now_iso,
                        now_iso,
                        now_iso,
                        "system_seed",
                    ),
                )
                inserted += 1
    return inserted


# ==========================================
# Backward Compatibility Aliases
# ==========================================
seed_initial_proverbs = seed_default_proverbs
restore_proverb = restore_proverb_to_pending
get_db_connection = get_connection

