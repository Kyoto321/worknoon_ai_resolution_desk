"""Customer API router."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.customer import CustomerResponse, CustomerSearchResponse
from app.services.customer_service import customer_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/customers", tags=["customers"])


@router.get(
    "/search",
    response_model=CustomerSearchResponse,
    summary="Search customers by name or ID",
)
def search_customers(
    q: str = Query(..., min_length=1, max_length=100, description="Search term (name or customer ID)"),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Search for customers by name or customer ID.
    Returns up to `limit` matching active customers.
    """
    customers = customer_service.search(db, q, limit=limit)
    return CustomerSearchResponse(
        customers=[CustomerResponse.model_validate(c) for c in customers],
        total=len(customers),
    )


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Get customer by customer ID",
)
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve a customer profile by their customer ID (e.g. CUST001).
    Returns 404 if the customer does not exist.
    """
    customer = customer_service.get_by_customer_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found.")
    return CustomerResponse.model_validate(customer)
