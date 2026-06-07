"""Support Request model."""

import json
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SupportRequest(Base):
    __tablename__ = "support_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    request_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)  # UUID
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"), nullable=True)

    request_text: Mapped[str] = mapped_column(Text, nullable=False)

    # AI-generated fields
    decision: Mapped[str | None] = mapped_column(String(20), nullable=True)  # approved | denied | escalated
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    customer_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    policies_applied: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of policy IDs
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="support_requests")  # noqa: F821
    order: Mapped["Order | None"] = relationship("Order", back_populates="support_requests")  # noqa: F821
    conversation: Mapped[list["ConversationHistory"]] = relationship(  # noqa: F821
        "ConversationHistory", back_populates="support_request", lazy="select"
    )

    def get_policies_applied(self) -> list[str]:
        if not self.policies_applied:
            return []
        return json.loads(self.policies_applied)

    def __repr__(self) -> str:
        return f"<SupportRequest {self.request_id} — {self.decision}>"
