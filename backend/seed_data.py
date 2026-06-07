"""
Seed script — populates the database with realistic mock data.

Run: python seed_data.py

Generates:
  - 7 support policies
  - 10 customers (mix of standard, VIP, enterprise tiers)
  - 10 orders (covering all edge cases: refundable, non-refundable,
    final sale, damaged, large transactions, overdue delivery)
"""

import json
import sys
import os
from datetime import datetime, timedelta, timezone

# Ensure app is importable
sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, Base, SessionLocal
from app.models import (  # noqa: F401 - imports register models with metadata
    Customer,
    Order,
    SupportPolicy,
    SupportRequest,
    ConversationHistory,
)

# ─────────────────────────────────────────────────────────────────────────────

def now() -> datetime:
    return datetime.now(timezone.utc)


def days_ago(n: int) -> datetime:
    return now() - timedelta(days=n)


def days_from_now(n: int) -> datetime:
    return now() + timedelta(days=n)


# ── Policies ──────────────────────────────────────────────────────────────────

POLICIES = [
    {
        "policy_id": "REFUND_POLICY",
        "name": "Standard Refund Policy",
        "description": (
            "Customers may request a full refund within 30 days of purchase "
            "for delivered, non-final-sale items in original condition."
        ),
        "rules": {
            "refund_window_days": 30,
            "eligible_statuses": ["delivered"],
            "excludes_final_sale": True,
            "requires_original_condition": True,
            "store_credit_option": True,
        },
        "priority": 80,
        "is_active": True,
    },
    {
        "policy_id": "DELIVERY_POLICY",
        "name": "Delivery Complaint Policy",
        "description": (
            "Delivery complaints are accepted within 14 days after the expected delivery date. "
            "Orders not yet past their expected delivery date are not eligible for complaint resolution."
        ),
        "rules": {
            "complaint_window_after_expected_days": 14,
            "eligible_statuses": ["shipped", "delivered"],
            "late_delivery_compensation": "store_credit_5_percent",
            "missing_delivery_compensation": "full_refund_or_reship",
        },
        "priority": 70,
        "is_active": True,
    },
    {
        "policy_id": "DAMAGED_PRODUCT_POLICY",
        "name": "Damaged Product Policy",
        "description": (
            "Products confirmed as damaged upon delivery are eligible for full refund "
            "or free replacement, regardless of purchase date or final-sale status."
        ),
        "rules": {
            "requires_damage_confirmation": True,
            "options": ["full_refund", "replacement"],
            "overrides_refund_window": True,
            "overrides_final_sale": False,
            "photo_evidence_preferred": True,
        },
        "priority": 90,
        "is_active": True,
    },
    {
        "policy_id": "FINAL_SALE_POLICY",
        "name": "Final Sale Policy",
        "description": (
            "Items marked as final sale at time of purchase are not eligible for refunds. "
            "Store credit may be offered at management discretion for undamaged items."
        ),
        "rules": {
            "refund_allowed": False,
            "exchange_allowed": False,
            "store_credit_at_discretion": True,
            "exception_for_damaged": False,
            "applies_to": "items_marked_final_sale_at_purchase",
        },
        "priority": 95,
        "is_active": True,
    },
    {
        "policy_id": "VIP_CUSTOMER_POLICY",
        "name": "VIP & Enterprise Customer Policy",
        "description": (
            "VIP customers receive an extended 60-day refund window and priority support. "
            "Enterprise customers require account manager involvement for all disputes."
        ),
        "rules": {
            "vip_refund_window_days": 60,
            "enterprise_escalation_required": True,
            "priority_response_time_hours": 4,
            "dedicated_agent_preferred": True,
        },
        "priority": 85,
        "is_active": True,
    },
    {
        "policy_id": "LARGE_TRANSACTION_POLICY",
        "name": "Large Transaction Policy",
        "description": (
            "Any refund or adjustment for orders exceeding $500 requires approval "
            "from a support manager before processing."
        ),
        "rules": {
            "threshold_amount": 500.0,
            "requires_manager_approval": True,
            "manager_response_time_hours": 24,
            "auto_escalation": True,
        },
        "priority": 88,
        "is_active": True,
    },
    {
        "policy_id": "ESCALATION_POLICY",
        "name": "Escalation Policy",
        "description": (
            "Cases involving safety concerns, legal threats, ambiguous situations, "
            "or unresolvable disputes must be escalated to a human support agent."
        ),
        "rules": {
            "triggers": [
                "safety_concern",
                "legal_threat",
                "ambiguous_case",
                "repeated_contact",
                "unresolvable_dispute",
                "enterprise_customer",
                "amount_over_500",
            ],
            "escalation_target": "tier_2_support",
            "response_time_hours": 24,
            "notify_customer": True,
        },
        "priority": 100,
        "is_active": True,
    },
]

# ── Customers ─────────────────────────────────────────────────────────────────

CUSTOMERS = [
    # Standard customers
    {
        "customer_id": "CUST001",
        "name": "Alice Johnson",
        "email": "alice.johnson@email.com",
        "tier": "standard",
        "total_spend": 345.50,
        "phone": "+1-555-0101",
    },
    {
        "customer_id": "CUST002",
        "name": "Bob Martinez",
        "email": "bob.martinez@email.com",
        "tier": "standard",
        "total_spend": 89.99,
        "phone": "+1-555-0102",
    },
    {
        "customer_id": "CUST003",
        "name": "Carol Williams",
        "email": "carol.williams@email.com",
        "tier": "standard",
        "total_spend": 1250.00,
        "phone": "+1-555-0103",
    },
    {
        "customer_id": "CUST004",
        "name": "David Chen",
        "email": "david.chen@email.com",
        "tier": "standard",
        "total_spend": 620.75,
        "phone": "+1-555-0104",
    },
    {
        "customer_id": "CUST005",
        "name": "Emma Thompson",
        "email": "emma.thompson@email.com",
        "tier": "standard",
        "total_spend": 178.25,
        "phone": "+1-555-0105",
    },
    # VIP customers
    {
        "customer_id": "CUST006",
        "name": "Frank Rivera",
        "email": "frank.rivera@email.com",
        "tier": "vip",
        "total_spend": 5430.00,
        "phone": "+1-555-0106",
    },
    {
        "customer_id": "CUST007",
        "name": "Grace Kim",
        "email": "grace.kim@email.com",
        "tier": "vip",
        "total_spend": 3200.50,
        "phone": "+1-555-0107",
    },
    # Enterprise customer
    {
        "customer_id": "CUST008",
        "name": "Horizon Tech Corp",
        "email": "procurement@horizontech.com",
        "tier": "enterprise",
        "total_spend": 45000.00,
        "phone": "+1-555-0108",
    },
    # Standard customers (edge cases)
    {
        "customer_id": "CUST009",
        "name": "Hannah Patel",
        "email": "hannah.patel@email.com",
        "tier": "standard",
        "total_spend": 55.00,
        "phone": "+1-555-0109",
    },
    {
        "customer_id": "CUST010",
        "name": "Isaac Brown",
        "email": "isaac.brown@email.com",
        "tier": "standard",
        "total_spend": 299.99,
        "phone": "+1-555-0110",
    },
]

# ── Orders ────────────────────────────────────────────────────────────────────
# customer_id here refers to the CUST### identifier for matching after insert

ORDERS = [
    # ORD001: Standard refund-eligible (delivered, within 30 days) → should APPROVE
    {
        "order_id": "ORD001",
        "customer_id": "CUST001",
        "product_name": "Wireless Noise-Cancelling Headphones",
        "amount": 89.99,
        "status": "delivered",
        "purchase_date": days_ago(15),
        "delivery_date": days_ago(10),
        "expected_delivery_date": days_ago(8),
        "is_final_sale": False,
        "is_damaged": False,
        "refund_eligible": True,
        "notes": "Customer reported product not meeting expectations.",
    },
    # ORD002: Outside refund window (45 days ago) → should DENY
    {
        "order_id": "ORD002",
        "customer_id": "CUST002",
        "product_name": "Leather Wallet",
        "amount": 45.00,
        "status": "delivered",
        "purchase_date": days_ago(45),
        "delivery_date": days_ago(40),
        "expected_delivery_date": days_ago(38),
        "is_final_sale": False,
        "is_damaged": False,
        "refund_eligible": False,
        "notes": "Order outside standard 30-day refund window.",
    },
    # ORD003: Final sale item → should DENY
    {
        "order_id": "ORD003",
        "customer_id": "CUST003",
        "product_name": "Designer Handbag (Clearance)",
        "amount": 199.99,
        "status": "delivered",
        "purchase_date": days_ago(5),
        "delivery_date": days_ago(2),
        "expected_delivery_date": days_ago(1),
        "is_final_sale": True,
        "is_damaged": False,
        "refund_eligible": False,
        "notes": "Final clearance sale — no returns.",
    },
    # ORD004: Damaged product → should APPROVE (damaged overrides window)
    {
        "order_id": "ORD004",
        "customer_id": "CUST004",
        "product_name": "Smart Watch Series X",
        "amount": 299.99,
        "status": "delivered",
        "purchase_date": days_ago(20),
        "delivery_date": days_ago(15),
        "expected_delivery_date": days_ago(14),
        "is_final_sale": False,
        "is_damaged": True,
        "refund_eligible": True,
        "notes": "Customer reported cracked screen upon delivery.",
    },
    # ORD005: Large transaction (>$500) → should ESCALATE
    {
        "order_id": "ORD005",
        "customer_id": "CUST003",
        "product_name": "Professional 4K Camera Bundle",
        "amount": 1249.99,
        "status": "delivered",
        "purchase_date": days_ago(10),
        "delivery_date": days_ago(5),
        "expected_delivery_date": days_ago(4),
        "is_final_sale": False,
        "is_damaged": False,
        "refund_eligible": True,
        "notes": "High-value item requiring manager review.",
    },
    # ORD006: VIP customer, 45 days old (within VIP 60-day window) → should APPROVE
    {
        "order_id": "ORD006",
        "customer_id": "CUST006",
        "product_name": "Premium Espresso Machine",
        "amount": 450.00,
        "status": "delivered",
        "purchase_date": days_ago(45),
        "delivery_date": days_ago(40),
        "expected_delivery_date": days_ago(38),
        "is_final_sale": False,
        "is_damaged": False,
        "refund_eligible": True,
        "notes": "VIP customer — 60-day window applies.",
    },
    # ORD007: Still in transit, overdue → should address delivery complaint
    {
        "order_id": "ORD007",
        "customer_id": "CUST005",
        "product_name": "Ergonomic Office Chair",
        "amount": 320.00,
        "status": "shipped",
        "purchase_date": days_ago(20),
        "delivery_date": None,
        "expected_delivery_date": days_ago(7),
        "is_final_sale": False,
        "is_damaged": False,
        "refund_eligible": True,
        "notes": "Package tracking shows no updates for 5 days.",
    },
    # ORD008: Enterprise customer → should ESCALATE (enterprise auto-escalate)
    {
        "order_id": "ORD008",
        "customer_id": "CUST008",
        "product_name": "Enterprise Laptop Fleet (x20)",
        "amount": 24000.00,
        "status": "delivered",
        "purchase_date": days_ago(8),
        "delivery_date": days_ago(3),
        "expected_delivery_date": days_ago(2),
        "is_final_sale": False,
        "is_damaged": False,
        "refund_eligible": True,
        "notes": "Enterprise bulk order — account manager required.",
    },
    # ORD009: Recently delivered, standard customer, within window → APPROVE
    {
        "order_id": "ORD009",
        "customer_id": "CUST009",
        "product_name": "Running Shoes",
        "amount": 55.00,
        "status": "delivered",
        "purchase_date": days_ago(7),
        "delivery_date": days_ago(3),
        "expected_delivery_date": days_ago(2),
        "is_final_sale": False,
        "is_damaged": False,
        "refund_eligible": True,
        "notes": "Wrong size delivered.",
    },
    # ORD010: VIP, large AND damaged — ESCALATE (large transaction overrides approve)
    {
        "order_id": "ORD010",
        "customer_id": "CUST007",
        "product_name": "High-End DSLR Camera",
        "amount": 899.99,
        "status": "delivered",
        "purchase_date": days_ago(12),
        "delivery_date": days_ago(7),
        "expected_delivery_date": days_ago(6),
        "is_final_sale": False,
        "is_damaged": True,
        "refund_eligible": True,
        "notes": "VIP customer — camera arrived with damaged lens.",
    },
]


# ─────────────────────────────────────────────────────────────────────────────

def seed():
    print("🌱 Starting database seed...")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # ── Clear existing data ───────────────────────────────────────────
        db.query(ConversationHistory).delete()
        db.query(SupportRequest).delete()
        db.query(Order).delete()
        db.query(Customer).delete()
        db.query(SupportPolicy).delete()
        db.commit()
        print("  ✓ Cleared existing data")

        # ── Seed Policies ─────────────────────────────────────────────────
        for p_data in POLICIES:
            rules = p_data.pop("rules")
            policy = SupportPolicy(**p_data, rules=json.dumps(rules))
            db.add(policy)
        db.commit()
        print(f"  ✓ Seeded {len(POLICIES)} policies")

        # ── Seed Customers ────────────────────────────────────────────────
        customer_map: dict[str, Customer] = {}
        for c_data in CUSTOMERS:
            customer = Customer(**c_data)
            db.add(customer)
            db.flush()
            customer_map[c_data["customer_id"]] = customer
        db.commit()
        print(f"  ✓ Seeded {len(CUSTOMERS)} customers")

        # ── Seed Orders ───────────────────────────────────────────────────
        for o_data in ORDERS:
            cust_id_str = o_data.pop("customer_id")
            customer = customer_map[cust_id_str]

            # Remove timezone info for SQLite compatibility
            for date_field in ["purchase_date", "delivery_date", "expected_delivery_date"]:
                if o_data.get(date_field) and o_data[date_field].tzinfo:
                    o_data[date_field] = o_data[date_field].replace(tzinfo=None)

            order = Order(**o_data, customer_id=customer.id)
            db.add(order)
        db.commit()
        print(f"  ✓ Seeded {len(ORDERS)} orders")

        print("\n✅ Seed complete! Database ready.")
        print("\nSample customer IDs to test with:")
        for cid in ["CUST001", "CUST002", "CUST003", "CUST004", "CUST006", "CUST008"]:
            c = customer_map[cid]
            print(f"  {c.customer_id}: {c.name} ({c.tier})")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
