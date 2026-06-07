"""Customer service — data access layer for customer operations."""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate

logger = logging.getLogger(__name__)


class CustomerService:
    """Handles all customer-related database operations."""

    def get_by_customer_id(self, db: Session, customer_id: str) -> Customer | None:
        """Fetch customer by their alphanumeric customer ID (e.g. CUST001)."""
        return db.query(Customer).filter(Customer.customer_id == customer_id.upper()).first()

    def get_by_id(self, db: Session, id: int) -> Customer | None:
        """Fetch customer by internal database PK."""
        return db.query(Customer).filter(Customer.id == id).first()

    def search(self, db: Session, query: str, limit: int = 10) -> list[Customer]:
        """
        Search customers by customer_id OR name (case-insensitive partial match).
        Returns up to `limit` results.
        """
        search_term = f"%{query.lower()}%"
        customers = (
            db.query(Customer)
            .filter(
                Customer.is_active == True,  # noqa: E712
                or_(
                    func.lower(Customer.name).like(search_term),
                    func.lower(Customer.customer_id).like(search_term),
                    func.lower(Customer.email).like(search_term),
                ),
            )
            .limit(limit)
            .all()
        )
        logger.info("Customer search for '%s' returned %d results", query, len(customers))
        return customers

    def resolve_identifier(self, db: Session, identifier: str) -> Customer | None:
        """
        Resolve a customer from either a customer_id string or a name.
        Priority: exact customer_id match → name search (first result).
        """
        # Try exact customer_id match first
        customer = self.get_by_customer_id(db, identifier)
        if customer:
            return customer

        # Fall back to name search
        results = self.search(db, identifier, limit=1)
        return results[0] if results else None

    def create(self, db: Session, data: CustomerCreate) -> Customer:
        """Create a new customer record."""
        customer = Customer(**data.model_dump())
        db.add(customer)
        db.commit()
        db.refresh(customer)
        logger.info("Created customer %s", customer.customer_id)
        return customer

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> list[Customer]:
        return db.query(Customer).filter(Customer.is_active == True).offset(skip).limit(limit).all()  # noqa: E712


customer_service = CustomerService()
