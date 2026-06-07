"""Policies API router."""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.support_policy import SupportPolicy

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/policies", tags=["policies"])


class PolicyResponse(BaseModel):
    policy_id: str
    name: str
    description: str
    is_active: bool
    priority: int

    model_config = {"from_attributes": True}


class PoliciesListResponse(BaseModel):
    policies: list[PolicyResponse]
    total: int


@router.get(
    "",
    response_model=PoliciesListResponse,
    summary="List all active support policies",
)
def get_policies(db: Session = Depends(get_db)):
    """
    Returns all active support policies ordered by priority (highest first).
    These are the rules the AI uses to evaluate support requests.
    """
    policies = (
        db.query(SupportPolicy)
        .filter(SupportPolicy.is_active == True)  # noqa: E712
        .order_by(SupportPolicy.priority.desc())
        .all()
    )
    return PoliciesListResponse(
        policies=[PolicyResponse.model_validate(p) for p in policies],
        total=len(policies),
    )
