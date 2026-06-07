"""
Integration tests for the Support API endpoints.
Uses FastAPI TestClient with an in-memory SQLite database.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from seed_data import seed as run_seed


# ── Test Database Setup ───────────────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite:///./test_support_assistant.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create tables and seed test data once for the entire test session."""
    # Temporarily point seed to test DB
    import app.database as db_module
    import seed_data
    original_engine = db_module.engine
    original_session = db_module.SessionLocal

    db_module.engine = test_engine
    db_module.SessionLocal = TestSessionLocal
    seed_data.engine = test_engine
    seed_data.SessionLocal = TestSessionLocal

    Base.metadata.create_all(bind=test_engine)
    run_seed()

    yield

    db_module.engine = original_engine
    db_module.SessionLocal = original_session
    seed_data.engine = original_engine
    seed_data.SessionLocal = original_session
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)


# ── Health Check Tests ────────────────────────────────────────────────────────

class TestHealthCheck:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status_healthy(self, client):
        data = response = client.get("/health").json()
        assert data["status"] == "healthy"


# ── Customer API Tests ────────────────────────────────────────────────────────

class TestCustomerAPI:
    def test_get_existing_customer(self, client):
        response = client.get("/customers/CUST001")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "CUST001"
        assert data["name"] == "Alice Johnson"

    def test_get_nonexistent_customer_returns_404(self, client):
        response = client.get("/customers/CUST999")
        assert response.status_code == 404

    def test_search_customers_by_name(self, client):
        response = client.get("/customers/search?q=Alice")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(c["name"] == "Alice Johnson" for c in data["customers"])

    def test_search_customers_by_id(self, client):
        response = client.get("/customers/search?q=CUST002")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_search_requires_query_param(self, client):
        response = client.get("/customers/search")
        assert response.status_code == 422  # Unprocessable entity


# ── Orders API Tests ──────────────────────────────────────────────────────────

class TestOrdersAPI:
    def test_get_existing_order(self, client):
        response = client.get("/orders/ORD001")
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "ORD001"

    def test_get_nonexistent_order_returns_404(self, client):
        response = client.get("/orders/ORD999")
        assert response.status_code == 404

    def test_get_customer_orders(self, client):
        response = client.get("/orders/customer/CUST001")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1


# ── Policies API Tests ────────────────────────────────────────────────────────

class TestPoliciesAPI:
    def test_get_policies(self, client):
        response = client.get("/policies")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 7
        assert any(p["policy_id"] == "REFUND_POLICY" for p in data["policies"])


# ── Support Request API Tests ─────────────────────────────────────────────────

class TestSupportRequestAPI:
    def test_submit_request_with_valid_customer_id(self, client):
        response = client.post("/support/request", json={
            "customer_identifier": "CUST001",
            "order_id": "ORD001",
            "request_text": "I would like to request a refund for my headphones.",
        })
        assert response.status_code == 201
        data = response.json()
        assert "request_id" in data
        assert data["decision"] in ("approved", "denied", "escalated")
        assert data["customer_id"] == "CUST001"

    def test_submit_request_by_customer_name(self, client):
        response = client.post("/support/request", json={
            "customer_identifier": "Alice Johnson",
            "request_text": "I have a general inquiry about my account.",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["customer_name"] == "Alice Johnson"

    def test_final_sale_order_gets_denied(self, client):
        """ORD003 is final sale — should always be denied."""
        response = client.post("/support/request", json={
            "customer_identifier": "CUST003",
            "order_id": "ORD003",
            "request_text": "I want to return this handbag.",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["decision"] == "denied"

    def test_enterprise_customer_gets_escalated(self, client):
        """CUST008 is enterprise — should always escalate."""
        response = client.post("/support/request", json={
            "customer_identifier": "CUST008",
            "order_id": "ORD008",
            "request_text": "We need to discuss our order.",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["decision"] == "escalated"

    def test_large_order_gets_escalated(self, client):
        """ORD005 is $1249.99 — should escalate for manager approval."""
        response = client.post("/support/request", json={
            "customer_identifier": "CUST003",
            "order_id": "ORD005",
            "request_text": "I want to return this camera bundle.",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["decision"] == "escalated"

    def test_nonexistent_customer_returns_404(self, client):
        response = client.post("/support/request", json={
            "customer_identifier": "CUST_FAKE",
            "request_text": "Need help please.",
        })
        assert response.status_code == 404

    def test_request_too_short_returns_422(self, client):
        response = client.post("/support/request", json={
            "customer_identifier": "CUST001",
            "request_text": "Hi",  # too short (min 10 chars)
        })
        assert response.status_code == 422

    def test_support_history_paginated(self, client):
        # First submit a request to populate history
        client.post("/support/request", json={
            "customer_identifier": "CUST009",
            "order_id": "ORD009",
            "request_text": "Wrong size delivered — need exchange.",
        })
        response = client.get("/support/history?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert "requests" in data
        assert "total" in data
        assert data["page"] == 1

    def test_get_request_detail(self, client):
        # Create a request first
        create_response = client.post("/support/request", json={
            "customer_identifier": "CUST001",
            "request_text": "Detailed inquiry about my order status.",
        })
        request_id = create_response.json()["request_id"]

        # Fetch by ID
        detail_response = client.get(f"/support/request/{request_id}")
        assert detail_response.status_code == 200
        assert detail_response.json()["request_id"] == request_id
