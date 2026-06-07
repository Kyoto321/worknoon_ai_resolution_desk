"""Support Policy model."""

import json
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SupportPolicy(Base):
    __tablename__ = "support_policies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    policy_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    rules: Mapped[str] = mapped_column(Text, nullable=False)  # stored as JSON string
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=10)  # higher = evaluated first
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def get_rules(self) -> dict:
        """Deserialize rules JSON."""
        return json.loads(self.rules)

    def __repr__(self) -> str:
        return f"<SupportPolicy {self.policy_id} — {self.name}>"
