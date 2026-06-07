"""Conversation history model."""

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    support_request_id: Mapped[int] = mapped_column(ForeignKey("support_requests.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "user" | "assistant" | "system"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    support_request: Mapped["SupportRequest"] = relationship(  # noqa: F821
        "SupportRequest", back_populates="conversation"
    )

    def __repr__(self) -> str:
        return f"<ConversationHistory req={self.support_request_id} role={self.role}>"
