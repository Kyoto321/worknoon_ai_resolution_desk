"""Routers package."""

from app.routers.customers import router as customers_router
from app.routers.orders import router as orders_router
from app.routers.support import router as support_router
from app.routers.policies import router as policies_router

__all__ = ["customers_router", "orders_router", "support_router", "policies_router"]
