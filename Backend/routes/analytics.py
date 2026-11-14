"""
BhashaVerse - Analytics API Routes
Provides corpus metrics, language distribution, category breakdown, and recent contributions.
"""

from fastapi import APIRouter
from Backend.schemas import AnalyticsResponse
from Backend.database import get_statistics

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/stats", response_model=AnalyticsResponse)
def get_analytics_stats():
    """
    Retrieve comprehensive corpus statistics and distributions.
    """
    stats = get_statistics()
    return AnalyticsResponse(
        total_approved=stats.get("approved_proverbs", 0),
        total_pending=stats.get("pending_submissions", 0),
        total_rejected=stats.get("rejected_submissions", 0),
        total_all=stats.get("total_submissions", 0),
        languages_represented=stats.get("active_languages", 0),
        language_counts=stats.get("language_distribution", {}),
        category_counts=stats.get("category_distribution", {}),
        recent_approved=stats.get("recent_proverbs", []),
    )
