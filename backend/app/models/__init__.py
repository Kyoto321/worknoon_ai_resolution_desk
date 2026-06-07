"""Models package — import all models so SQLAlchemy metadata is fully populated."""

from app.models.customer import Customer
from app.models.order import Order
from app.models.support_policy import SupportPolicy
from app.models.support_request import SupportRequest
from app.models.conversation import ConversationHistory

__all__ = [
    "Customer",
    "Order",
    "SupportPolicy",
    "SupportRequest",
    "ConversationHistory",
]
