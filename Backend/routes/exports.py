"""
BhashaVerse - Corpus Export API Routes
Provides downloadable dataset exports in UTF-8 BOM CSV (Excel-compatible)
and UTF-8 formatted JSON format.
"""

from fastapi import APIRouter, Response
from Backend.database import export_proverbs
from Backend.utils.export_utils import (
    generate_csv_export,
    generate_json_export,
    get_export_filename,
)

router = APIRouter(prefix="/exports", tags=["Exports"])


@router.get("/csv")
def download_public_csv():
    """
    Download public verified corpus as UTF-8 BOM CSV.
    """
    records = export_proverbs(approved_only=True, include_maintainer_meta=False)
    csv_bytes = generate_csv_export(records, is_maintainer=False)
    filename = get_export_filename(dataset_name="bhashaverse_corpus", extension="csv")

    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/json")
def download_public_json():
    """
    Download public verified corpus as UTF-8 formatted JSON.
    """
    records = export_proverbs(approved_only=True, include_maintainer_meta=False)
    json_str = generate_json_export(records, is_maintainer=False)
    filename = get_export_filename(dataset_name="bhashaverse_corpus", extension="json")

    return Response(
        content=json_str,
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/maintainer/csv")
def download_maintainer_csv():
    """
    Download maintainer export including submission metadata and audit info.
    """
    records = export_proverbs(approved_only=False, include_maintainer_meta=True)
    csv_bytes = generate_csv_export(records, is_maintainer=True)
    filename = get_export_filename(dataset_name="bhashaverse_maintainer_corpus", extension="csv")

    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/maintainer/json")
def download_maintainer_json():
    """
    Download maintainer export including submission metadata and audit info in JSON.
    """
    records = export_proverbs(approved_only=False, include_maintainer_meta=True)
    json_str = generate_json_export(records, is_maintainer=True)
    filename = get_export_filename(dataset_name="bhashaverse_maintainer_corpus", extension="json")

    return Response(
        content=json_str,
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

