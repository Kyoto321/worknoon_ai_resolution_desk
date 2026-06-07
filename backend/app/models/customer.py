"""Customer model."""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    tier: Mapped[str] = mapped_column(String(20), default="standard")  # standard | vip | enterprise
    total_spend: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="customer", lazy="select")  # noqa: F821
    support_requests: Mapped[list["SupportRequest"]] = relationship(  # noqa: F821
        "SupportRequest", back_populates="customer", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Customer {self.customer_id} — {self.name} ({self.tier})>"
