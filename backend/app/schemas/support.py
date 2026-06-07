"""Pydantic schemas for Support Requests."""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class SupportRequestCreate(BaseModel):
    """Incoming request from the frontend."""

    customer_identifier: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Customer ID (e.g. CUST001) or customer name",
        examples=["CUST001", "Alice Johnson"],
    )
    order_id: str | None = Field(
        default=None,
        description="Optional order ID to scope the request",
        examples=["ORD001"],
    )
    request_text: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="The support request message from the customer",
    )

    @field_validator("request_text")
    @classmethod
    def sanitize_request_text(cls, v: str) -> str:
        """Strip leading/trailing whitespace and basic sanitization."""
        return v.strip()


class SupportRequestResponse(BaseModel):
    """Full response including AI decision."""

    request_id: str
    customer_id: str
    customer_name: str
    order_id: str | None
    request_text: str
    decision: str  # approved | denied | escalated
    reasoning: str
    recommended_action: str
    customer_response: str
    policies_applied: list[str]
    confidence_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class SupportHistoryItem(BaseModel):
    """Lightweight item for the history list."""

    request_id: str
    customer_id: str
    customer_name: str
    decision: str
    request_text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SupportHistoryResponse(BaseModel):
    requests: list[SupportHistoryItem]
    total: int
    page: int
    page_size: int
