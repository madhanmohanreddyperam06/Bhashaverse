"""
BhashaVerse - Frontend API Client
Centralized client communicating with the FastAPI REST backend.
Includes automatic fallback to local backend services if the API server
is starting up or temporarily offline.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import requests

from Frontend.config import API_BASE_URL

# Default request timeout in seconds
TIMEOUT = 10.0


class BhashaverseAPIClient:
    """Client for Bhashaverse REST API."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")
        # Proactively ensure local SQLite database is ready if running standalone
        try:
            from Backend.database import ensure_db_initialized
            ensure_db_initialized()
        except Exception:
            pass

    # -------------------------------------------------------------
    # System & Health
    # -------------------------------------------------------------
    def check_health(self) -> Dict[str, Any]:
        """Check status of FastAPI backend."""
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=2.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

        # Local fallback
        try:
            from Backend.database import get_statistics
            from Backend.config import APP_NAME, APP_VERSION
            stats = get_statistics()
            return {
                "status": "healthy (local)",
                "app": APP_NAME,
                "version": APP_VERSION,
                "database_connected": True,
                "total_proverbs": stats.get("total_submissions", 0),
            }
        except Exception:
            return {
                "status": "degraded",
                "app": "Bhashaverse",
                "version": "2.0.0",
                "database_connected": False,
                "total_proverbs": 0,
            }

    # -------------------------------------------------------------
    # Proverbs Exploration & Retrieval
    # -------------------------------------------------------------
    def get_proverbs(
        self,
        query: Optional[str] = None,
        language: Optional[str] = None,
        category: Optional[str] = None,
        sort_by: str = "newest",
        page: int = 1,
        page_size: int = 12,
        status: str = "approved",
    ) -> Tuple[List[Dict[str, Any]], int, int]:
        """
        Fetch filtered and paginated proverbs.
        Returns: (items, total_count, total_pages)
        """
        params: Dict[str, Any] = {
            "page": page,
            "page_size": page_size,
            "sort_by": sort_by,
            "status": status,
        }
        if query and query.strip():
            params["query"] = query.strip()
        if language and language.strip() and language != "All":
            params["language"] = language.strip()
        if category and category.strip() and category != "All":
            params["category"] = category.strip()

        try:
            resp = requests.get(f"{self.base_url}/proverbs", params=params, timeout=TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("items", []), data.get("total_count", 0), data.get("total_pages", 1)
        except Exception:
            pass

        # Local fallback
        try:
            import math
            from Backend.database import search_proverbs
            offset = (page - 1) * page_size
            clean_query = query.strip() if query and query.strip() else None
            clean_lang = language.strip() if language and language != "All" else None
            clean_cat = category.strip() if category and category != "All" else None
            items, total = search_proverbs(
                query=clean_query,
                language=clean_lang,
                category=clean_cat,
                sort_by=sort_by,
                limit=page_size,
                offset=offset,
                status=status,
            )
            total_pages = max(1, math.ceil(total / page_size)) if total > 0 else 1
            return items, total, total_pages
        except Exception as e:
            return [], 0, 1

    def get_proverb_by_id(self, proverb_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a single proverb by its ID."""
        try:
            resp = requests.get(f"{self.base_url}/proverbs/{proverb_id}", timeout=TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

        # Local fallback
        try:
            from Backend.database import get_proverb_by_id
            return get_proverb_by_id(proverb_id)
        except Exception:
            return None

    # -------------------------------------------------------------
    # Proverbs Contribution
    # -------------------------------------------------------------
    def submit_proverb(self, form_data: Dict[str, Any]) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        Submit a new proverb.
        Returns: (success: bool, record_or_error_message: Dict or str)
        """
        payload = {
            "proverb": form_data.get("proverb"),
            "language": form_data.get("language"),
            "meaning": form_data.get("meaning"),
            "english_translation": form_data.get("english_translation") or None,
            "cultural_context": form_data.get("cultural_context") or None,
            "category": form_data.get("category") or "Other",
            "contributor_name": form_data.get("contributor_name") or "Anonymous",
            "contributor_email": form_data.get("contributor_email") or None,
            "terms_confirmed": bool(form_data.get("terms_confirmed", True)),
        }

        try:
            resp = requests.post(f"{self.base_url}/proverbs", json=payload, timeout=TIMEOUT)
            if resp.status_code == 201:
                return True, resp.json()
            elif resp.status_code in (400, 422):
                err = resp.json().get("detail", "Validation failed.")
                if isinstance(err, list):
                    err = "; ".join(f"{item.get('loc', [''])[-1]}: {item.get('msg')}" for item in err)
                return False, str(err)
            else:
                return False, resp.json().get("detail", f"Server error: {resp.status_code}")
        except Exception:
            pass

        # Local fallback
        try:
            from Backend.utils.validation import validate_proverb_submission
            from Backend.database import add_proverb

            is_valid, validation_result = validate_proverb_submission(payload, check_duplicates=True)
            if not is_valid:
                return False, str(validation_result)

            record = add_proverb(**validation_result)
            return True, record
        except Exception as e:
            return False, f"Failed to submit: {e}"

    # -------------------------------------------------------------
    # Conversational Cultural AI
    # -------------------------------------------------------------
    def chat(
        self,
        query: str,
        language_filter: Optional[str] = None,
        engine_choice: str = "Auto-Detect",
        custom_api_key: Optional[str] = None,
    ) -> str:
        """Query the cultural AI chatbot."""
        payload = {
            "query": query,
            "language_filter": language_filter,
            "engine_choice": engine_choice,
            "custom_api_key": custom_api_key,
        }

        try:
            resp = requests.post(f"{self.base_url}/chat", json=payload, timeout=30.0)
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception:
            pass

        # Local fallback
        try:
            from Backend.utils.chatbot_utils import generate_chat_response
            return generate_chat_response(
                query=query,
                language_filter=language_filter,
                engine_choice=engine_choice,
                custom_api_key=custom_api_key,
            )
        except Exception as e:
            return f"Chat error: {e}"

    # -------------------------------------------------------------
    # Analytics
    # -------------------------------------------------------------
    def get_analytics_stats(self) -> Dict[str, Any]:
        """Fetch corpus analytics and metrics."""
        try:
            resp = requests.get(f"{self.base_url}/analytics/stats", timeout=TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

        # Local fallback
        try:
            from Backend.database import get_statistics
            stats = get_statistics()
            return {
                "total_approved": stats.get("approved_proverbs", 0),
                "total_pending": stats.get("pending_submissions", 0),
                "total_rejected": stats.get("rejected_submissions", 0),
                "total_all": stats.get("total_submissions", 0),
                "languages_represented": stats.get("active_languages", 0),
                "language_counts": stats.get("language_distribution", {}),
                "category_counts": stats.get("category_distribution", {}),
                "recent_approved": stats.get("recent_proverbs", []),
            }
        except Exception:
            return {}

    # -------------------------------------------------------------
    # Moderation
    # -------------------------------------------------------------
    def verify_moderator_key(self, passkey: str) -> bool:
        """Authenticate moderator passkey."""
        try:
            resp = requests.post(
                f"{self.base_url}/moderation/auth",
                json={"passkey": passkey},
                timeout=TIMEOUT,
            )
            if resp.status_code == 200:
                return bool(resp.json().get("authenticated", False))
        except Exception:
            pass

        # Local fallback
        try:
            from Backend.utils.moderation_utils import verify_moderator_key
            return verify_moderator_key(passkey)
        except Exception:
            return False

    def get_pending_proverbs(self) -> List[Dict[str, Any]]:
        """Fetch all pending submissions."""
        try:
            resp = requests.get(f"{self.base_url}/moderation/pending", timeout=TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

        try:
            from Backend.database import get_pending_proverbs
            return get_pending_proverbs()
        except Exception:
            return []

    def get_approved_proverbs(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Fetch approved proverbs."""
        try:
            resp = requests.get(f"{self.base_url}/moderation/approved?limit={limit}", timeout=TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

        try:
            from Backend.database import get_approved_proverbs
            return get_approved_proverbs(limit=limit)
        except Exception:
            return []

    def get_rejected_proverbs(self) -> List[Dict[str, Any]]:
        """Fetch rejected submissions."""
        try:
            resp = requests.get(f"{self.base_url}/moderation/rejected", timeout=TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

        try:
            from Backend.database import get_rejected_proverbs
            return get_rejected_proverbs()
        except Exception:
            return []

    def approve_proverb(self, proverb_id: int, moderator: str = "Maintainer") -> bool:
        """Approve a proverb."""
        try:
            resp = requests.post(
                f"{self.base_url}/moderation/{proverb_id}/approve",
                json={"moderator_name": moderator},
                timeout=TIMEOUT,
            )
            if resp.status_code == 200:
                return True
        except Exception:
            pass

        try:
            from Backend.database import approve_proverb
            return approve_proverb(proverb_id, moderator=moderator)
        except Exception:
            return False

    def reject_proverb(self, proverb_id: int, reason: str, moderator: str = "Maintainer") -> bool:
        """Reject a proverb with reason."""
        try:
            resp = requests.post(
                f"{self.base_url}/moderation/{proverb_id}/reject",
                json={"reason": reason, "moderator_name": moderator},
                timeout=TIMEOUT,
            )
            if resp.status_code == 200:
                return True
        except Exception:
            pass

        try:
            from Backend.database import reject_proverb
            return reject_proverb(proverb_id, reason=reason, moderator=moderator)
        except Exception:
            return False

    def update_proverb(
        self,
        proverb_id: int,
        proverb_data: Dict[str, Any],
        moderator: str = "Maintainer",
    ) -> bool:
        """Edit proverb contents."""
        try:
            resp = requests.put(
                f"{self.base_url}/moderation/{proverb_id}",
                params={"moderator": moderator},
                json=proverb_data,
                timeout=TIMEOUT,
            )
            if resp.status_code == 200:
                return True
        except Exception:
            pass

        try:
            from Backend.database import update_proverb
            return update_proverb(
                proverb_id=proverb_id,
                proverb=proverb_data.get("proverb"),
                language=proverb_data.get("language"),
                english_translation=proverb_data.get("english_translation"),
                meaning=proverb_data.get("meaning"),
                cultural_context=proverb_data.get("cultural_context"),
                category=proverb_data.get("category"),
                contributor_name=proverb_data.get("contributor_name"),
                moderator=moderator,
            )
        except Exception:
            return False

    def restore_proverb(self, proverb_id: int, moderator: str = "Maintainer") -> bool:
        """Restore rejected proverb to pending."""
        try:
            resp = requests.post(
                f"{self.base_url}/moderation/{proverb_id}/restore",
                json={"moderator_name": moderator},
                timeout=TIMEOUT,
            )
            if resp.status_code == 200:
                return True
        except Exception:
            pass

        try:
            from Backend.database import restore_proverb
            return restore_proverb(proverb_id, moderator=moderator)
        except Exception:
            return False

    def delete_proverb(self, proverb_id: int, moderator: str = "Maintainer", reason: Optional[str] = None) -> bool:
        """Permanently delete a proverb."""
        params = {"moderator": moderator}
        if reason:
            params["reason"] = reason
        try:
            resp = requests.delete(
                f"{self.base_url}/moderation/{proverb_id}",
                params=params,
                timeout=TIMEOUT,
            )
            if resp.status_code == 200:
                return True
        except Exception:
            pass

        try:
            from Backend.database import delete_proverb
            return delete_proverb(proverb_id, moderator=moderator, reason=reason)
        except Exception:
            return False

    def get_moderation_logs(self, proverb_id: Optional[int] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch moderation audit logs."""
        params: Dict[str, Any] = {"limit": limit}
        if proverb_id:
            params["proverb_id"] = proverb_id
        try:
            resp = requests.get(f"{self.base_url}/moderation/logs", params=params, timeout=TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

        try:
            from Backend.database import get_moderation_logs
            return get_moderation_logs(proverb_id=proverb_id, limit=limit)
        except Exception:
            return []

    # -------------------------------------------------------------
    # Exports
    # -------------------------------------------------------------
    def get_export_csv(self, is_maintainer: bool = False) -> bytes:
        """Fetch CSV export bytes."""
        endpoint = "/exports/maintainer/csv" if is_maintainer else "/exports/csv"
        try:
            resp = requests.get(f"{self.base_url}{endpoint}", timeout=TIMEOUT)
            if resp.status_code == 200:
                return resp.content
        except Exception:
            pass

        # Local fallback
        try:
            from Backend.database import export_proverbs
            from Backend.utils.export_utils import generate_csv_export
            records = export_proverbs(approved_only=not is_maintainer, include_maintainer_meta=is_maintainer)
            return generate_csv_export(records, is_maintainer=is_maintainer)
        except Exception:
            return b""

    def get_export_json(self, is_maintainer: bool = False) -> str:
        """Fetch JSON export string."""
        endpoint = "/exports/maintainer/json" if is_maintainer else "/exports/json"
        try:
            resp = requests.get(f"{self.base_url}{endpoint}", timeout=TIMEOUT)
            if resp.status_code == 200:
                return resp.text
        except Exception:
            pass

        # Local fallback
        try:
            from Backend.database import export_proverbs
            from Backend.utils.export_utils import generate_json_export
            records = export_proverbs(approved_only=not is_maintainer, include_maintainer_meta=is_maintainer)
            return generate_json_export(records, is_maintainer=is_maintainer)
        except Exception:
            return "[]"


# Singleton instance for easy import across Frontend
api_client = BhashaverseAPIClient()

