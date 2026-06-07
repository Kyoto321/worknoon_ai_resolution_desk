"""Order model."""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Status: pending | processing | shipped | delivered | cancelled | refunded
    status: Mapped[str] = mapped_column(String(30), default="pending")

    purchase_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    delivery_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expected_delivery_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Policy flags — set at order creation, drive AI decisions
    is_final_sale: Mapped[bool] = mapped_column(Boolean, default=False)
    is_damaged: Mapped[bool] = mapped_column(Boolean, default=False)
    refund_eligible: Mapped[bool] = mapped_column(Boolean, default=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")  # noqa: F821
    support_requests: Mapped[list["SupportRequest"]] = relationship(  # noqa: F821
        "SupportRequest", back_populates="order", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Order {self.order_id} — {self.product_name} ({self.status})>"
