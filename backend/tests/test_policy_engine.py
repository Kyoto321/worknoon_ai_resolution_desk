"""
Tests for the Policy Engine — the deterministic rule layer.

These tests verify that hard-stops work correctly BEFORE any AI call is made.
This is the most critical unit test suite in the application.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from app.services.policy_engine import (
    PolicyEngine,
    STANDARD_REFUND_WINDOW_DAYS,
    VIP_REFUND_WINDOW_DAYS,
    LARGE_TRANSACTION_THRESHOLD,
)
from app.models.customer import Customer
from app.models.order import Order
from app.models.support_policy import SupportPolicy


def make_customer(tier: str = "standard", **kwargs) -> Customer:
    c = Customer()
    c.id = 1
    c.customer_id = "CUST001"
    c.name = "Test Customer"
    c.email = "test@example.com"
    c.tier = tier
    c.total_spend = 500.0
    c.is_active = True
    for k, v in kwargs.items():
        setattr(c, k, v)
    return c


def make_order(days_old: int = 10, amount: float = 99.99, **kwargs) -> Order:
    o = Order()
    o.id = 1
    o.order_id = "ORD001"
    o.product_name = "Test Product"
    o.amount = amount
    o.status = "delivered"
    o.purchase_date = datetime.now(timezone.utc) - timedelta(days=days_old)
    o.delivery_date = datetime.now(timezone.utc) - timedelta(days=days_old - 5)
    o.expected_delivery_date = datetime.now(timezone.utc) - timedelta(days=days_old - 6)
    o.is_final_sale = False
    o.is_damaged = False
    o.refund_eligible = True
    o.notes = None
    for k, v in kwargs.items():
        setattr(o, k, v)
    return o


def make_policy(policy_id: str, name: str = "Test Policy", rules: dict | None = None) -> SupportPolicy:
    p = SupportPolicy()
    p.id = 1
    p.policy_id = policy_id
    p.name = name
    p.description = "Test policy description"
    p.rules = '{}' if rules is None else __import__('json').dumps(rules)
    p.is_active = True
    p.priority = 50
    return p


engine = PolicyEngine()
all_policies = [
    make_policy("REFUND_POLICY", "Standard Refund Policy"),
    make_policy("FINAL_SALE_POLICY", "Final Sale Policy"),
    make_policy("DAMAGED_PRODUCT_POLICY", "Damaged Product Policy"),
    make_policy("VIP_CUSTOMER_POLICY", "VIP Customer Policy"),
    make_policy("LARGE_TRANSACTION_POLICY", "Large Transaction Policy"),
    make_policy("DELIVERY_POLICY", "Delivery Policy"),
    make_policy("ESCALATION_POLICY", "Escalation Policy"),
]


class TestRefundPolicy:
    def test_within_standard_window_no_deny(self):
        """Order within 30-day window should NOT trigger hard_deny."""
        customer = make_customer("standard")
        order = make_order(days_old=15)
        result = engine.evaluate(customer, [order], order, "I want a refund", all_policies)
        assert not result.hard_deny, "Should not hard-deny within refund window"

    def test_outside_standard_window_hard_deny(self):
        """Order older than 30 days for standard customer should hard-deny."""
        customer = make_customer("standard")
        order = make_order(days_old=35)
        result = engine.evaluate(customer, [order], order, "I want a refund", all_policies)
        assert result.hard_deny, "Should hard-deny — outside 30-day window"

    def test_vip_within_extended_window_no_deny(self):
        """VIP customer 45-day-old order should NOT hard-deny (60-day window)."""
        customer = make_customer("vip")
        order = make_order(days_old=45)
        result = engine.evaluate(customer, [order], order, "I want a refund", all_policies)
        assert not result.hard_deny, "VIP should have 60-day window"

    def test_vip_outside_extended_window_hard_deny(self):
        """VIP customer 65-day-old order should hard-deny."""
        customer = make_customer("vip")
        order = make_order(days_old=65)
        result = engine.evaluate(customer, [order], order, "I want a refund", all_policies)
        assert result.hard_deny, "VIP outside 60-day window should hard-deny"


class TestFinalSalePolicy:
    def test_final_sale_triggers_hard_deny(self):
        """Final sale item must always hard-deny."""
        customer = make_customer("standard")
        order = make_order(days_old=5, is_final_sale=True)
        result = engine.evaluate(customer, [order], order, "I want a refund", all_policies)
        assert result.hard_deny, "Final sale should always hard-deny"

    def test_final_sale_deny_reason_in_result(self):
        """Hard-deny reasons should mention final sale."""
        customer = make_customer("standard")
        order = make_order(days_old=5, is_final_sale=True)
        result = engine.evaluate(customer, [order], order, "Refund please", all_policies)
        assert any("final sale" in r.lower() for r in result.deny_reasons)


class TestDamagedProductPolicy:
    def test_damaged_not_denied_even_outside_window(self):
        """
        Damaged item outside normal refund window should NOT be hard-denied.
        The damaged policy overrides the window check.
        """
        customer = make_customer("standard")
        order = make_order(days_old=60, is_damaged=True)
        result = engine.evaluate(customer, [order], order, "Item arrived broken", all_policies)
        # Damaged overrides refund window — so hard_deny should be False
        assert not result.hard_deny, "Damaged product should override refund window"

    def test_damaged_policy_included_in_result(self):
        """Damaged product evaluation should include DAMAGED_PRODUCT_POLICY."""
        customer = make_customer("standard")
        order = make_order(days_old=10, is_damaged=True)
        result = engine.evaluate(customer, [order], order, "Item broken", all_policies)
        policy_ids = [p.policy_id for p in result.applicable_policies]
        assert "DAMAGED_PRODUCT_POLICY" in policy_ids


class TestLargeTransactionPolicy:
    def test_large_transaction_triggers_escalation(self):
        """Orders over $500 must hard-escalate."""
        customer = make_customer("standard")
        order = make_order(days_old=5, amount=750.00)
        result = engine.evaluate(customer, [order], order, "I want a refund", all_policies)
        assert result.hard_escalate, "Large transaction should hard-escalate"

    def test_small_transaction_no_escalation(self):
        """Orders under $500 should NOT escalate on amount alone."""
        customer = make_customer("standard")
        order = make_order(days_old=5, amount=100.00)
        result = engine.evaluate(customer, [order], order, "I want a refund", all_policies)
        assert not result.hard_escalate, "Small transaction should not auto-escalate"


class TestEnterpriseEscalation:
    def test_enterprise_always_escalates(self):
        """Enterprise customers must always trigger hard_escalate."""
        customer = make_customer("enterprise")
        order = make_order(days_old=5)
        result = engine.evaluate(customer, [order], order, "Simple question", all_policies)
        assert result.hard_escalate, "Enterprise customer should always escalate"

    def test_no_order_no_crash(self):
        """Evaluation without a target order should not raise exceptions."""
        customer = make_customer("standard")
        result = engine.evaluate(customer, [], None, "General inquiry", all_policies)
        assert result is not None
