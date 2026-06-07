"""Support API router — the core endpoint for AI-powered support decisions."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.support import (
    SupportRequestCreate,
    SupportRequestResponse,
    SupportHistoryResponse,
)
from app.services.support_service import support_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/support", tags=["support"])


@router.post(
    "/request",
    response_model=SupportRequestResponse,
    status_code=201,
    summary="Submit a support request for AI evaluation",
)
def submit_support_request(
    request: SupportRequestCreate,
    db: Session = Depends(get_db),
):
    """
    Submit a customer support request.

    **Workflow:**
    1. Resolves customer by ID or name
    2. Fetches customer orders
    3. Evaluates applicable support policies
    4. Calls Gemini AI with full context
    5. Returns structured decision (approved/denied/escalated)

    **Example Request:**
    ```json
    {
        "customer_identifier": "CUST001",
        "order_id": "ORD001",
        "request_text": "I would like to request a refund for my damaged item."
    }
    ```
    """
    return support_service.process_request(db, request)


@router.get(
    "/history",
    response_model=SupportHistoryResponse,
    summary="Get paginated support request history",
)
def get_support_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of all support requests, most recent first.
    """
    return support_service.get_history(db, page=page, page_size=page_size)


@router.get(
    "/request/{request_id}",
    response_model=SupportRequestResponse,
    summary="Get full detail of a single support request",
)
def get_request_detail(
    request_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve the full detail of a single support request by its UUID.
    Returns 404 if not found.
    """
    result = support_service.get_request_detail(db, request_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Support request '{request_id}' not found.")
    return result
