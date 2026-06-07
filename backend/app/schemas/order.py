"""Pydantic schemas for Order."""

from datetime import datetime
from pydantic import BaseModel, Field


class OrderBase(BaseModel):
    order_id: str = Field(..., examples=["ORD001"])
    product_name: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    status: str = Field(
        default="pending",
        pattern="^(pending|processing|shipped|delivered|cancelled|refunded)$",
    )
    purchase_date: datetime
    delivery_date: datetime | None = None
    expected_delivery_date: datetime | None = None
    is_final_sale: bool = False
    is_damaged: bool = False
    refund_eligible: bool = True
    notes: str | None = None


class OrderCreate(OrderBase):
    customer_id: int


class OrderResponse(OrderBase):
    id: int
    customer_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int
