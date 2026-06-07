"""
Policy Engine — deterministic rule evaluation before AI invocation.

Architecture Decision:
  The policy engine runs BEFORE the AI call. It:
  1. Identifies which policies apply to this request.
  2. Adds hard-stop guards (e.g., final-sale items can never be refunded).
  3. Passes full policy context to the AI so it can reason about them.

  This prevents hallucination by grounding the AI in concrete, checked facts
  rather than asking it to independently determine policy applicability.
"""

import logging
from datetime import datetime, timezone

from app.models.customer import Customer
from app.models.order import Order
from app.models.support_policy import SupportPolicy
from app.schemas.ai_response import PolicyContext

logger = logging.getLogger(__name__)

# Days threshold for standard refund window
STANDARD_REFUND_WINDOW_DAYS = 30
VIP_REFUND_WINDOW_DAYS = 60
DELIVERY_COMPLAINT_WINDOW_DAYS = 14
LARGE_TRANSACTION_THRESHOLD = 500.0


class PolicyEvaluation:
    """Result of policy engine evaluation."""

    def __init__(self):
        self.applicable_policies: list[PolicyContext] = []
        self.hard_deny: bool = False  # Certain deny regardless of AI
        self.hard_escalate: bool = False  # Must escalate regardless of AI
        self.deny_reasons: list[str] = []
        self.escalate_reasons: list[str] = []
        self.context_notes: list[str] = []

    def add_policy(self, policy: SupportPolicy) -> None:
        self.applicable_policies.append(
            PolicyContext(
                policy_id=policy.policy_id,
                name=policy.name,
                description=policy.description,
                rules=policy.get_rules(),
            )
        )

    def force_deny(self, reason: str) -> None:
        self.hard_deny = True
        self.deny_reasons.append(reason)

    def force_escalate(self, reason: str) -> None:
        self.hard_escalate = True
        self.escalate_reasons.append(reason)

    def add_context(self, note: str) -> None:
        self.context_notes.append(note)


class PolicyEngine:
    """
    Evaluates support policies against a customer request.

    Each evaluate_* method checks one specific policy and updates
    the PolicyEvaluation object. This makes policy logic auditable
    and independently testable.
    """

    def evaluate(
        self,
        customer: Customer,
        orders: list[Order],
        target_order: Order | None,
        request_text: str,
        all_policies: list[SupportPolicy],
    ) -> PolicyEvaluation:
        """
        Main evaluation method. Runs all policy checks and returns
        a consolidated PolicyEvaluation.
        """
        evaluation = PolicyEvaluation()

        # Build a policy lookup dict for easy access
        policy_map = {p.policy_id: p for p in all_policies}

        # ── 1. Customer Tier Context ──────────────────────────────────────
        if customer.tier == "vip":
            evaluation.add_context(f"Customer is VIP tier (extended {VIP_REFUND_WINDOW_DAYS}-day refund window).")
            if "VIP_CUSTOMER_POLICY" in policy_map:
                evaluation.add_policy(policy_map["VIP_CUSTOMER_POLICY"])
        elif customer.tier == "enterprise":
            evaluation.add_context("Customer is Enterprise tier — auto-escalate all disputes.")
            evaluation.force_escalate("Enterprise customer — requires account manager review.")
            if "VIP_CUSTOMER_POLICY" in policy_map:
                evaluation.add_policy(policy_map["VIP_CUSTOMER_POLICY"])
        else:
            evaluation.add_context(f"Customer is standard tier ({STANDARD_REFUND_WINDOW_DAYS}-day refund window).")

        # ── 2. Target Order Checks ────────────────────────────────────────
        if target_order:
            self._evaluate_order_policies(customer, target_order, policy_map, evaluation)
        else:
            evaluation.add_context("No specific order referenced — applying general policies.")

        # ── 3. Escalation Policy (catch-all) ─────────────────────────────
        if "ESCALATION_POLICY" in policy_map:
            evaluation.add_policy(policy_map["ESCALATION_POLICY"])

        logger.info(
            "Policy evaluation complete: hard_deny=%s, hard_escalate=%s, policies=%s",
            evaluation.hard_deny,
            evaluation.hard_escalate,
            [p.policy_id for p in evaluation.applicable_policies],
        )
        return evaluation

    def _evaluate_order_policies(
        self,
        customer: Customer,
        order: Order,
        policy_map: dict[str, SupportPolicy],
        evaluation: PolicyEvaluation,
    ) -> None:
        """Evaluate all order-specific policies."""
        now = datetime.now(timezone.utc)
        purchase_date = order.purchase_date
        if purchase_date.tzinfo is None:
            purchase_date = purchase_date.replace(tzinfo=timezone.utc)

        days_since_purchase = (now - purchase_date).days
        refund_window = VIP_REFUND_WINDOW_DAYS if customer.tier in ("vip", "enterprise") else STANDARD_REFUND_WINDOW_DAYS

        # ── Final Sale ────────────────────────────────────────────────────
        if order.is_final_sale:
            evaluation.force_deny(
                f"Order {order.order_id} is marked as final sale — refunds are not permitted."
            )
            evaluation.add_context(f"Order {order.order_id} is a FINAL SALE item.")
            if "FINAL_SALE_POLICY" in policy_map:
                evaluation.add_policy(policy_map["FINAL_SALE_POLICY"])

        # ── Damaged Product ───────────────────────────────────────────────
        if order.is_damaged:
            evaluation.add_context(
                f"Order {order.order_id} is flagged as DAMAGED — eligible for refund/replacement regardless of time window."
            )
            if "DAMAGED_PRODUCT_POLICY" in policy_map:
                evaluation.add_policy(policy_map["DAMAGED_PRODUCT_POLICY"])

        # ── Refund Window ─────────────────────────────────────────────────
        if not order.is_damaged:
            if days_since_purchase > refund_window:
                evaluation.force_deny(
                    f"Order {order.order_id} is {days_since_purchase} days old "
                    f"(exceeds {refund_window}-day refund window)."
                )
            else:
                evaluation.add_context(
                    f"Order is {days_since_purchase} days old — within {refund_window}-day refund window."
                )

        if "REFUND_POLICY" in policy_map:
            evaluation.add_policy(policy_map["REFUND_POLICY"])

        # ── Large Transaction ─────────────────────────────────────────────
        if float(order.amount) > LARGE_TRANSACTION_THRESHOLD:
            evaluation.force_escalate(
                f"Order {order.order_id} amount (${order.amount:.2f}) exceeds "
                f"${LARGE_TRANSACTION_THRESHOLD:.0f} — requires manager approval."
            )
            if "LARGE_TRANSACTION_POLICY" in policy_map:
                evaluation.add_policy(policy_map["LARGE_TRANSACTION_POLICY"])

        # ── Delivery ──────────────────────────────────────────────────────
        if order.status == "shipped" and order.expected_delivery_date:
            expected = order.expected_delivery_date
            if expected.tzinfo is None:
                expected = expected.replace(tzinfo=timezone.utc)
            if now < expected:
                evaluation.add_context(
                    f"Order {order.order_id} is still within expected delivery window "
                    f"(expected by {expected.date()})."
                )
            else:
                evaluation.add_context(
                    f"Order {order.order_id} is OVERDUE — expected by {expected.date()}."
                )
            if "DELIVERY_POLICY" in policy_map:
                evaluation.add_policy(policy_map["DELIVERY_POLICY"])

        # ── Order Status Context ──────────────────────────────────────────
        evaluation.add_context(f"Order {order.order_id} status: {order.status.upper()}.")


policy_engine = PolicyEngine()
