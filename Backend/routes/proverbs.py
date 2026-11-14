"""
BhashaVerse - Proverbs API Routes
Provides endpoints to search, filter, paginate, retrieve, and submit proverbs.
"""

import math
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from Backend.schemas import ProverbCreate, ProverbOut, ProverbListResponse
from Backend.database import search_proverbs, get_proverb_by_id, add_proverb
from Backend.utils.validation import validate_proverb_submission

router = APIRouter(prefix="/proverbs", tags=["Proverbs"])


@router.get("", response_model=ProverbListResponse)
def list_proverbs(
    query: Optional[str] = Query(None, description="Search term for proverb, translation, or meaning"),
    language: Optional[str] = Query(None, description="Language filter (e.g. Telugu, Hindi)"),
    category: Optional[str] = Query(None, description="Category filter (e.g. Wisdom, Life Lessons)"),
    sort_by: str = Query("newest", description="Sort order: newest, oldest, or alphabetical"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(12, ge=1, le=100, description="Items per page"),
    status: str = Query("approved", description="Status filter: approved, pending, or rejected"),
):
    """
    Search and filter proverbs with pagination and sorting.
    """
    # Clean filters ("All" or empty string becomes None)
    clean_query = query.strip() if query and query.strip() else None
    clean_lang = language.strip() if language and language.strip() and language.strip() != "All" else None
    clean_cat = category.strip() if category and category.strip() and category.strip() != "All" else None

    offset = (page - 1) * page_size
    items, total_count = search_proverbs(
        query=clean_query,
        language=clean_lang,
        category=clean_cat,
        sort_by=sort_by,
        limit=page_size,
        offset=offset,
        status=status,
    )

    total_pages = max(1, math.ceil(total_count / page_size)) if total_count > 0 else 1

    return ProverbListResponse(
        items=items,
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{proverb_id}", response_model=ProverbOut)
def get_proverb(proverb_id: int):
    """
    Retrieve a single proverb by its database ID.
    """
    proverb = get_proverb_by_id(proverb_id)
    if not proverb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proverb with ID {proverb_id} not found."
        )
    return proverb


@router.post("", response_model=ProverbOut, status_code=status.HTTP_201_CREATED)
def submit_proverb(submission: ProverbCreate):
    """
    Submit a new proverb for community contribution. Validates fields and checks for duplicates.
    """
    submission_dict = submission.model_dump()
    is_valid, validation_result = validate_proverb_submission(submission_dict)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(validation_result)
        )

    # validation_result is the cleaned dictionary
    created_record = add_proverb(**validation_result)
    if not created_record:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record proverb in the database."
        )

    return created_record

