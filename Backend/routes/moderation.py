"""
BhashaVerse - Moderation API Routes
Provides maintainer workflows: authentication, pending queue inspection,
approval, rejection with reason, inline editing, restoration, and deletion.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from Backend.schemas import (
    ModeratorAuthRequest,
    ModeratorAuthResponse,
    ProverbOut,
    ProverbUpdate,
    ApproveRequest,
    RejectRequest,
    RestoreRequest,
    AuditLogOut,
)
from Backend.utils.moderation_utils import verify_moderator_key
from Backend.database import (
    get_pending_proverbs,
    get_approved_proverbs,
    get_rejected_proverbs,
    get_moderation_logs,
    get_proverb_by_id,
    approve_proverb,
    reject_proverb,
    update_proverb,
    restore_proverb,
    delete_proverb,
)

router = APIRouter(prefix="/moderation", tags=["Moderation"])


@router.post("/auth", response_model=ModeratorAuthResponse)
def authenticate_moderator_endpoint(req: ModeratorAuthRequest):
    """
    Authenticate moderator key using timing-attack safe comparison.
    """
    is_valid = verify_moderator_key(req.passkey)
    if is_valid:
        return ModeratorAuthResponse(
            authenticated=True,
            message="Maintainer access granted."
        )
    return ModeratorAuthResponse(
        authenticated=False,
        message="Invalid maintainer passkey."
    )


@router.get("/pending", response_model=List[ProverbOut])
def list_pending_submissions():
    """
    List all pending proverb submissions awaiting review.
    """
    return get_pending_proverbs()


@router.get("/approved", response_model=List[ProverbOut])
def list_approved_submissions(limit: int = Query(200, ge=1, le=1000)):
    """
    List approved proverbs.
    """
    return get_approved_proverbs(limit=limit)


@router.get("/rejected", response_model=List[ProverbOut])
def list_rejected_submissions():
    """
    List rejected submissions with their recorded rejection reasons.
    """
    return get_rejected_proverbs()


@router.get("/logs", response_model=List[AuditLogOut])
def list_moderation_logs(
    proverb_id: Optional[int] = Query(None, description="Optional filter by proverb ID"),
    limit: int = Query(50, ge=1, le=200, description="Max logs to return"),
):
    """
    Retrieve moderation audit logs.
    """
    return get_moderation_logs(proverb_id=proverb_id, limit=limit)


@router.post("/{proverb_id}/approve")
def approve_submission(proverb_id: int, req: Optional[ApproveRequest] = None):
    """
    Approve a pending or rejected proverb.
    """
    mod_name = req.moderator_name if req else "Maintainer"
    success = approve_proverb(proverb_id, moderator=mod_name or "Maintainer")
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proverb with ID {proverb_id} could not be approved."
        )
    return {"message": f"Proverb {proverb_id} approved successfully."}


@router.post("/{proverb_id}/reject")
def reject_submission(proverb_id: int, req: RejectRequest):
    """
    Reject a pending or approved proverb, recording the feedback reason.
    """
    success = reject_proverb(
        proverb_id,
        reason=req.reason,
        moderator=req.moderator_name or "Maintainer"
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proverb with ID {proverb_id} could not be rejected."
        )
    return {"message": f"Proverb {proverb_id} rejected."}


@router.put("/{proverb_id}")
def update_submission(proverb_id: int, req: ProverbUpdate, moderator: str = Query("Maintainer")):
    """
    Update / edit fields of a proverb record.
    """
    existing = get_proverb_by_id(proverb_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proverb with ID {proverb_id} not found."
        )

    success = update_proverb(
        proverb_id=proverb_id,
        proverb=req.proverb,
        language=req.language,
        english_translation=req.english_translation,
        meaning=req.meaning,
        cultural_context=req.cultural_context,
        category=req.category,
        contributor_name=req.contributor_name,
        moderator=moderator,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update proverb {proverb_id}."
        )

    return get_proverb_by_id(proverb_id)


@router.post("/{proverb_id}/restore")
def restore_submission(proverb_id: int, req: Optional[RestoreRequest] = None):
    """
    Restore a rejected proverb back to pending review.
    """
    mod_name = req.moderator_name if req else "Maintainer"
    success = restore_proverb(proverb_id, moderator=mod_name or "Maintainer")
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proverb with ID {proverb_id} could not be restored."
        )
    return {"message": f"Proverb {proverb_id} restored to pending queue."}


@router.delete("/{proverb_id}")
def delete_submission(
    proverb_id: int,
    moderator: str = Query("Maintainer"),
    reason: Optional[str] = Query(None)
):
    """
    Permanently delete a proverb from the database.
    """
    success = delete_proverb(proverb_id, moderator=moderator, reason=reason)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proverb with ID {proverb_id} could not be deleted."
        )
    return {"message": f"Proverb {proverb_id} permanently deleted."}

