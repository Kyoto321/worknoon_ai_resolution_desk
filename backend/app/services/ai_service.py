"""
AI Service — Gemini integration for support decision generation.

Design Decisions:
  1. STRUCTURED OUTPUT: We use Gemini's response_schema parameter to enforce
     a specific JSON schema. This eliminates free-form text hallucinations.

  2. POLICY GROUNDING: All relevant policies are injected verbatim into the
     system prompt. The AI cannot invent rules — it can only apply or deny
     based on provided context.

  3. HARD-STOP BYPASS: If the policy engine issues a hard_deny or hard_escalate,
     we construct the AI response deterministically WITHOUT calling the API.
     This saves cost and ensures policy cannot be overridden by the AI.

  4. CONTEXT INJECTION: Customer profile, order history, and evaluation context
     notes are all included so the AI has full situational awareness.
"""

import json
import logging
from typing import Any

import google.generativeai as genai

from app.config import get_settings
from app.models.customer import Customer
from app.models.order import Order
from app.schemas.ai_response import AIDecisionResponse
from app.services.policy_engine import PolicyEvaluation

logger = logging.getLogger(__name__)
settings = get_settings()


class AIService:
    """Manages AI model configuration and support decision generation."""

    def __init__(self):
        # Gracefully handle empty key or default placeholder value
        has_api_key = (
            settings.gemini_api_key
            and settings.gemini_api_key.strip()
            and settings.gemini_api_key != "your_gemini_api_key_here"
        )
        if has_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self._model = genai.GenerativeModel(
                model_name=settings.gemini_model,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=AIDecisionResponse,
                    temperature=0.2,  # Low temp for consistent, policy-adherent decisions
                ),
            )
        else:
            self._model = None
            logger.warning("GEMINI_API_KEY not set or placeholder used — AI service will use fallback responses.")

    def _build_system_prompt(self) -> str:
        return """You are an expert AI support agent for an e-commerce platform.
Your role is to evaluate customer support requests and make fair, policy-compliant decisions.

CRITICAL RULES:
1. You MUST base every decision on the provided policies and context. Never invent rules.
2. You MUST acknowledge the customer's concern empathetically.
3. If context is ambiguous or the request falls outside clear policy, choose "escalated".
4. Your reasoning must explicitly reference the policy names that apply.
5. The customer_response must be warm, professional, and jargon-free.
6. Never promise actions you cannot guarantee (e.g., "your refund will arrive in 2 days").
7. For damaged items, always prioritize customer satisfaction within policy limits.

DECISION GUIDE:
- "approved": Clear policy permits the request. All conditions satisfied.
- "denied": Clear policy prohibits the request. Explain why empathetically.
- "escalated": Requires human review. Amount too high, ambiguous case, or special circumstance.
"""

    def _build_user_prompt(
        self,
        customer: Customer,
        orders: list[Order],
        target_order: Order | None,
        request_text: str,
        evaluation: PolicyEvaluation,
    ) -> str:
        """Build the full context prompt for the AI model."""

        # Customer context
        customer_section = f"""
=== CUSTOMER PROFILE ===
Customer ID: {customer.customer_id}
Name: {customer.name}
Email: {customer.email}
Tier: {customer.tier.upper()}
Total Lifetime Spend: ${float(customer.total_spend):,.2f}
Account Status: {"Active" if customer.is_active else "Inactive"}
"""

        # Order history
        order_lines = []
        for o in orders[:5]:  # Cap at 5 most recent orders
            order_lines.append(
                f"  - {o.order_id}: {o.product_name} | ${float(o.amount):,.2f} | "
                f"Status: {o.status} | Purchased: {o.purchase_date.date()} | "
                f"Final Sale: {o.is_final_sale} | Damaged: {o.is_damaged} | "
                f"Refund Eligible: {o.refund_eligible}"
            )
        orders_section = "=== RECENT ORDERS ===\n" + ("\n".join(order_lines) if order_lines else "No orders found.")

        # Target order detail
        target_order_section = ""
        if target_order:
            target_order_section = f"""
=== ORDER IN QUESTION ===
Order ID: {target_order.order_id}
Product: {target_order.product_name}
Amount: ${float(target_order.amount):,.2f}
Status: {target_order.status}
Purchase Date: {target_order.purchase_date.date()}
Delivery Date: {target_order.delivery_date.date() if target_order.delivery_date else "Not yet delivered"}
Expected Delivery: {target_order.expected_delivery_date.date() if target_order.expected_delivery_date else "N/A"}
Final Sale: {target_order.is_final_sale}
Damaged: {target_order.is_damaged}
Refund Eligible Flag: {target_order.refund_eligible}
Notes: {target_order.notes or "None"}
"""

        # Policy context
        policy_lines = []
        for p in evaluation.applicable_policies:
            policy_lines.append(
                f"\n  [{p.policy_id}] {p.name}\n"
                f"  Description: {p.description}\n"
                f"  Rules: {json.dumps(p.rules, indent=2)}"
            )
        policies_section = "=== APPLICABLE POLICIES ===" + ("".join(policy_lines) if policy_lines else "\n  No specific policies matched.")

        # Engine context notes
        context_notes = "\n".join(f"  • {note}" for note in evaluation.context_notes)
        notes_section = f"=== POLICY ENGINE EVALUATION NOTES ===\n{context_notes or '  None'}"

        # The actual request
        request_section = f"""
=== CUSTOMER REQUEST ===
"{request_text}"
"""

        return "\n".join([
            customer_section,
            orders_section,
            target_order_section,
            policies_section,
            notes_section,
            request_section,
            "Based on all the above context and policies, make your support decision.",
        ])

    def generate_decision(
        self,
        customer: Customer,
        orders: list[Order],
        target_order: Order | None,
        request_text: str,
        evaluation: PolicyEvaluation,
    ) -> AIDecisionResponse:
        """
        Generate an AI support decision.

        If the policy engine has issued a hard-stop (deny or escalate),
        we skip the API call and construct a deterministic response.
        """

        # ── Hard-Stop Bypass (save API cost + ensure policy compliance) ──
        if evaluation.hard_deny and not evaluation.hard_escalate:
            deny_reason = " ".join(evaluation.deny_reasons)
            logger.info("Hard-deny triggered — skipping AI call. Reason: %s", deny_reason)
            return AIDecisionResponse(
                decision="denied",
                reasoning=f"Automatic denial based on policy evaluation: {deny_reason}",
                recommended_action="No action required — request automatically denied per policy.",
                customer_response=(
                    f"Thank you for reaching out, {customer.name}. "
                    "After reviewing your request and order details, I'm unable to process "
                    f"this request at this time. {deny_reason} "
                    "If you believe this is an error or have additional information, "
                    "please don't hesitate to contact us and we'll be happy to assist further."
                ),
                policies_applied=[p.policy_id for p in evaluation.applicable_policies],
                confidence_score=0.95,
            )

        if evaluation.hard_escalate:
            escalate_reason = " ".join(evaluation.escalate_reasons)
            logger.info("Hard-escalate triggered — skipping AI call. Reason: %s", escalate_reason)
            return AIDecisionResponse(
                decision="escalated",
                reasoning=f"Automatic escalation based on policy evaluation: {escalate_reason}",
                recommended_action="Assign to Tier-2 support agent for manual review.",
                customer_response=(
                    f"Thank you for contacting us, {customer.name}. "
                    "Your request requires review by one of our senior support specialists. "
                    "A team member will reach out to you within 24 hours. "
                    "We appreciate your patience."
                ),
                policies_applied=[p.policy_id for p in evaluation.applicable_policies],
                confidence_score=0.90,
            )

        # ── AI Call ────────────────────────────────────────────────────────
        if not self._model:
            logger.warning("AI model not configured — returning demo response.")
            return self._demo_response(customer, evaluation)

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(customer, orders, target_order, request_text, evaluation)

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        logger.info("Calling Gemini API for customer %s", customer.customer_id)

        try:
            response = self._model.generate_content(full_prompt)
            raw_json = response.text

            # Parse and validate with Pydantic
            data = json.loads(raw_json)
            decision = AIDecisionResponse(**data)

            # ── Post-validation: prevent AI from overriding hard denials ──
            # (Double-safety in case structured output still returns "approved")
            if evaluation.hard_deny and decision.decision == "approved":
                logger.warning("AI attempted to approve a hard-denied request — overriding.")
                decision.decision = "denied"
                decision.reasoning += " [Note: Decision overridden by policy engine — hard deny rule applied.]"

            logger.info(
                "AI decision: %s (confidence=%.2f) for customer %s",
                decision.decision,
                decision.confidence_score,
                customer.customer_id,
            )
            return decision

        except Exception as e:
            logger.error("AI service error: %s", str(e), exc_info=True)
            # Safe fallback — escalate rather than deny or approve on error
            return AIDecisionResponse(
                decision="escalated",
                reasoning=f"AI processing encountered an error. Escalating for manual review. Error: {type(e).__name__}",
                recommended_action="Manually review this request — AI service temporarily unavailable.",
                customer_response=(
                    f"Thank you for contacting us, {customer.name}. "
                    "We're experiencing a brief technical issue and have escalated your request "
                    "to our support team. You'll hear from us within 24 hours."
                ),
                policies_applied=[],
                confidence_score=0.0,
            )

    def _demo_response(self, customer: Customer, evaluation: PolicyEvaluation) -> AIDecisionResponse:
        """Fallback response when no API key is configured (demo mode)."""
        return AIDecisionResponse(
            decision="escalated",
            reasoning="[DEMO MODE] API key not configured. This is a demonstration response.",
            recommended_action="Configure GEMINI_API_KEY to enable live AI decisions.",
            customer_response=(
                f"Hello {customer.name}, thank you for your support request. "
                "[This is a demo response — configure your API key for live AI decisions.]"
            ),
            policies_applied=[p.policy_id for p in evaluation.applicable_policies],
            confidence_score=0.5,
        )


ai_service = AIService()
