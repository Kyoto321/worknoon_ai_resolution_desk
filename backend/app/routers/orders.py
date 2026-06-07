"""Orders API router."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.order import OrderResponse, OrderListResponse
from app.services.customer_service import customer_service
from app.services.order_service import order_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])


@router.get(
    "/customer/{customer_id}",
    response_model=OrderListResponse,
    summary="Get all orders for a customer",
)
def get_customer_orders(
    customer_id: str,
    db: Session = Depends(get_db),
):
    """
    Get all orders for a customer, most recent first.
    Returns 404 if the customer is not found.
    """
    customer = customer_service.get_by_customer_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found.")

    orders = order_service.get_customer_orders(db, customer.id)
    return OrderListResponse(
        orders=[OrderResponse.model_validate(o) for o in orders],
        total=len(orders),
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get a single order by order ID",
)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve a single order by its order ID (e.g. ORD001).
    Returns 404 if the order is not found.
    """
    order = order_service.get_by_order_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")
    return OrderResponse.model_validate(order)
