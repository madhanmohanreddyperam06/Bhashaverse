"""
BhashaVerse - Pydantic Data Schemas
Defines request and response schemas for all FastAPI endpoints.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProverbBase(BaseModel):
    proverb: str = Field(..., min_length=3, max_length=1000)
    language: str
    meaning: str = Field(..., min_length=5, max_length=2000)
    english_translation: Optional[str] = Field(None, max_length=1000)
    cultural_context: Optional[str] = Field(None, max_length=2500)
    category: Optional[str] = "Other"
    contributor_name: Optional[str] = Field("Anonymous", max_length=100)
    contributor_email: Optional[str] = Field(None, max_length=120)


class ProverbCreate(ProverbBase):
    terms_confirmed: bool = True


class ProverbUpdate(BaseModel):
    proverb: Optional[str] = Field(None, min_length=3, max_length=1000)
    language: Optional[str] = None
    meaning: Optional[str] = Field(None, min_length=5, max_length=2000)
    english_translation: Optional[str] = Field(None, max_length=1000)
    cultural_context: Optional[str] = Field(None, max_length=2500)
    category: Optional[str] = None
    contributor_name: Optional[str] = Field(None, max_length=100)
    contributor_email: Optional[str] = Field(None, max_length=120)
    status: Optional[str] = None
    rejection_reason: Optional[str] = None


class ProverbOut(BaseModel):
    id: int
    submission_uuid: Optional[str] = None
    proverb: str
    language: str
    language_code: Optional[str] = None
    english_translation: Optional[str] = None
    meaning: str
    cultural_context: Optional[str] = None
    category: str
    contributor_name: Optional[str] = None
    contributor_email: Optional[str] = None
    status: str = "approved"
    rejection_reason: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    moderated_at: Optional[str] = None
    moderated_by: Optional[str] = None

    model_config = {"from_attributes": True}


class ProverbListResponse(BaseModel):
    items: List[ProverbOut]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    language_filter: Optional[str] = None
    engine_choice: Optional[str] = "Auto-Detect"
    custom_api_key: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    query: str
    language_filter: Optional[str] = None
    engine_used: str = "Auto-Detect"


class ModeratorAuthRequest(BaseModel):
    passkey: str


class ModeratorAuthResponse(BaseModel):
    authenticated: bool
    message: str


class ApproveRequest(BaseModel):
    moderator_name: Optional[str] = "Maintainer"


class RejectRequest(BaseModel):
    reason: str = Field(..., min_length=2)
    moderator_name: Optional[str] = "Maintainer"


class RestoreRequest(BaseModel):
    moderator_name: Optional[str] = "Maintainer"


class AuditLogOut(BaseModel):
    id: int
    proverb_id: int
    action: str
    actor: str
    notes: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}


class AnalyticsResponse(BaseModel):
    total_approved: int
    total_pending: int
    total_rejected: int
    total_all: int
    languages_represented: int
    language_counts: Dict[str, int]
    category_counts: Dict[str, int]
    recent_approved: List[ProverbOut]


class HealthResponse(BaseModel):
    status: str = "approved"
    app: str
    version: str
    database_connected: bool
    total_proverbs: int
