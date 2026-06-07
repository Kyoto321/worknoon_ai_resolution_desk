"""Pydantic schemas for AI response — used for structured output parsing."""

from typing import Literal
from pydantic import BaseModel, Field


class AIDecisionResponse(BaseModel):
    """
    Structured output schema for the Gemini AI response.
    This exact schema is sent to the Gemini API as response_schema,
    ensuring the model returns well-formed JSON every time.
    """

    decision: Literal["approved", "denied", "escalated"] = Field(
        ...,
        description="The final support decision.",
    )
    reasoning: str = Field(
        ...,
        description=(
            "Step-by-step reasoning referencing specific policy names. "
            "Must explain WHY this decision was made."
        ),
    )
    recommended_action: str = Field(
        ...,
        description=(
            "Specific action for the support agent or automated system to take. "
            "E.g. 'Process full refund of $89.99' or 'Escalate to Tier-2 manager'."
        ),
    )
    customer_response: str = Field(
        ...,
        description=(
            "The customer-facing response message. "
            "Should be warm, professional, and clearly explain the outcome."
        ),
    )
    policies_applied: list[str] = Field(
        ...,
        description="List of policy IDs that were relevant to this decision.",
    )
    confidence_score: float = Field(
        ...,
        description="Confidence score from 0.0 (uncertain) to 1.0 (certain).",
    )


class PolicyContext(BaseModel):
    """Represents a single policy fed into the AI context."""

    policy_id: str
    name: str
    description: str
    rules: dict
