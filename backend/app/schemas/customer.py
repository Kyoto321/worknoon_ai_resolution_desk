"""Pydantic schemas for Customer."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class CustomerBase(BaseModel):
    customer_id: str = Field(..., examples=["CUST001"])
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    tier: str = Field(default="standard", pattern="^(standard|vip|enterprise)$")
    phone: str | None = None


class CustomerCreate(CustomerBase):
    total_spend: float = Field(default=0.0, ge=0)


class CustomerResponse(CustomerBase):
    id: int
    total_spend: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomerSearchResponse(BaseModel):
    customers: list[CustomerResponse]
    total: int
