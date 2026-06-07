"""Order service — data access layer for order operations."""

import logging
from sqlalchemy.orm import Session

from app.models.order import Order

logger = logging.getLogger(__name__)


class OrderService:
    """Handles all order-related database operations."""

    def get_by_order_id(self, db: Session, order_id: str) -> Order | None:
        """Fetch order by string order ID (e.g. ORD001)."""
        return db.query(Order).filter(Order.order_id == order_id.upper()).first()

    def get_by_id(self, db: Session, id: int) -> Order | None:
        """Fetch order by internal PK."""
        return db.query(Order).filter(Order.id == id).first()

    def get_customer_orders(
        self,
        db: Session,
        customer_db_id: int,
        limit: int = 10,
    ) -> list[Order]:
        """
        Get orders for a customer, most recent first.
        Limits to recent orders to keep AI context manageable.
        """
        return (
            db.query(Order)
            .filter(Order.customer_id == customer_db_id)
            .order_by(Order.purchase_date.desc())
            .limit(limit)
            .all()
        )

    def get_by_order_id_for_customer(
        self, db: Session, order_id: str, customer_db_id: int
    ) -> Order | None:
        """Security check: only return order if it belongs to the customer."""
        return (
            db.query(Order)
            .filter(Order.order_id == order_id.upper(), Order.customer_id == customer_db_id)
            .first()
        )


order_service = OrderService()
