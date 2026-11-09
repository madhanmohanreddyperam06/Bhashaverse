"""
BhashaVerse 2.0 - Dataset Export Utilities
Handles export of the multilingual corpus to UTF-8 BOM CSV (for full Excel compatibility)
and formatted JSON (with ensure_ascii=False). Enforces privacy by stripping sensitive fields.
"""

import csv
import io
import json
from datetime import datetime
from typing import List, Dict, Any


PUBLIC_EXPORT_FIELDS = [
    "id",
    "proverb",
    "language",
    "language_code",
    "english_translation",
    "meaning",
    "cultural_context",
    "category",
    "contributor_name",
    "created_at"
]

MAINTAINER_EXPORT_FIELDS = PUBLIC_EXPORT_FIELDS + [
    "submission_uuid",
    "contributor_email",
    "status",
    "rejection_reason",
    "updated_at",
    "moderated_at",
    "moderated_by"
]


def sanitize_records_for_public(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ensure public export records only contain permissible non-sensitive fields."""
    sanitized = []
    for r in records:
        clean = {k: r.get(k) for k in PUBLIC_EXPORT_FIELDS}
        sanitized.append(clean)
    return sanitized


def generate_csv_export(records: List[Dict[str, Any]], is_maintainer: bool = False) -> bytes:
    """
    Generate CSV file bytes encoded as UTF-8 with BOM (utf-8-sig)
    for seamless compatibility with Microsoft Excel, LibreOffice, and NLP tools.
    Preserves all Indian language scripts (Devanagari, Telugu, Tamil, Nastaliq, etc.).
    """
    fields = MAINTAINER_EXPORT_FIELDS if is_maintainer else PUBLIC_EXPORT_FIELDS
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()

    for r in records:
        # Standardize None values as empty strings
        row = {f: (r.get(f) if r.get(f) is not None else "") for f in fields}
        writer.writerow(row)

    # Encode with BOM
    return output.getvalue().encode("utf-8-sig")


def generate_json_export(records: List[Dict[str, Any]], is_maintainer: bool = False) -> str:
    """
    Generate formatted JSON string with ensure_ascii=False
    so Indian script Unicode characters remain human-readable and unescaped.
    """
    data = records if is_maintainer else sanitize_records_for_public(records)
    return json.dumps(data, ensure_ascii=False, indent=2)


def get_export_filename(dataset_name: str = "bhashaverse_corpus", extension: str = "csv") -> str:
    """Generate timestamped filename for downloaded dataset."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{dataset_name}_{timestamp}.{extension}"
