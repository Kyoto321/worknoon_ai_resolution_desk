"""
Support Service — orchestrates the full support request workflow.

This is the main business logic layer. It coordinates:
  Customer Service → Order Service → Policy Engine → AI Service → DB save
"""

import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models.support_request import SupportRequest
from app.models.conversation import ConversationHistory
from app.schemas.support import (
    SupportRequestCreate,
    SupportRequestResponse,
    SupportHistoryItem,
    SupportHistoryResponse,
)
from app.services.customer_service import customer_service
from app.services.order_service import order_service
from app.services.policy_engine import policy_engine
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class SupportService:
    """Orchestrates the end-to-end support request workflow."""

    def process_request(
        self, db: Session, request: SupportRequestCreate
    ) -> SupportRequestResponse:
        """
        Full pipeline:
        1. Resolve customer
        2. Fetch orders
        3. Resolve target order
        4. Load active policies
        5. Run policy engine
        6. Call AI service
        7. Persist result
        8. Return structured response
        """
        from app.models.support_policy import SupportPolicy

        # ── Step 1: Resolve Customer ──────────────────────────────────────
        customer = customer_service.resolve_identifier(db, request.customer_identifier)
        if not customer:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"Customer not found: '{request.customer_identifier}'",
            )

        # ── Step 2: Fetch Recent Orders ───────────────────────────────────
        orders = order_service.get_customer_orders(db, customer.id)

        # ── Step 3: Resolve Target Order ──────────────────────────────────
        target_order = None
        if request.order_id:
            target_order = order_service.get_by_order_id_for_customer(
                db, request.order_id, customer.id
            )
            if not target_order:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=404,
                    detail=f"Order '{request.order_id}' not found for this customer.",
                )

        # ── Step 4: Load Active Policies ──────────────────────────────────
        all_policies = (
            db.query(SupportPolicy)
            .filter(SupportPolicy.is_active == True)  # noqa: E712
            .order_by(SupportPolicy.priority.desc())
            .all()
        )

        # ── Step 5: Policy Engine Evaluation ─────────────────────────────
        evaluation = policy_engine.evaluate(
            customer=customer,
            orders=orders,
            target_order=target_order,
            request_text=request.request_text,
            all_policies=all_policies,
        )

        # ── Step 6: AI Decision Generation ───────────────────────────────
        ai_decision = ai_service.generate_decision(
            customer=customer,
            orders=orders,
            target_order=target_order,
            request_text=request.request_text,
            evaluation=evaluation,
        )

        # ── Step 7: Persist to Database ───────────────────────────────────
        request_id = str(uuid.uuid4())
        support_req = SupportRequest(
            request_id=request_id,
            customer_id=customer.id,
            order_id=target_order.id if target_order else None,
            request_text=request.request_text,
            decision=ai_decision.decision,
            reasoning=ai_decision.reasoning,
            recommended_action=ai_decision.recommended_action,
            customer_response=ai_decision.customer_response,
            policies_applied=json.dumps(ai_decision.policies_applied),
            confidence_score=ai_decision.confidence_score,
            resolved_at=datetime.now(timezone.utc),
        )
        db.add(support_req)
        db.flush()  # Get the ID without committing

        # Save conversation history
        db.add(ConversationHistory(
            support_request_id=support_req.id,
            role="user",
            content=request.request_text,
        ))
        db.add(ConversationHistory(
            support_request_id=support_req.id,
            role="assistant",
            content=ai_decision.customer_response,
        ))
        db.commit()
        db.refresh(support_req)

        logger.info(
            "Support request %s processed: decision=%s, customer=%s",
            request_id,
            ai_decision.decision,
            customer.customer_id,
        )

        # ── Step 8: Return Response ───────────────────────────────────────
        return SupportRequestResponse(
            request_id=request_id,
            customer_id=customer.customer_id,
            customer_name=customer.name,
            order_id=target_order.order_id if target_order else None,
            request_text=request.request_text,
            decision=ai_decision.decision,
            reasoning=ai_decision.reasoning,
            recommended_action=ai_decision.recommended_action,
            customer_response=ai_decision.customer_response,
            policies_applied=ai_decision.policies_applied,
            confidence_score=ai_decision.confidence_score,
            created_at=support_req.created_at,
        )

    def get_history(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
    ) -> SupportHistoryResponse:
        """Paginated support request history with customer details."""
        offset = (page - 1) * page_size
        total = db.query(SupportRequest).count()
        requests = (
            db.query(SupportRequest)
            .options(joinedload(SupportRequest.customer))
            .order_by(SupportRequest.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        items = []
        for req in requests:
            items.append(
                SupportHistoryItem(
                    request_id=req.request_id,
                    customer_id=req.customer.customer_id,
                    customer_name=req.customer.name,
                    decision=req.decision or "pending",
                    request_text=req.request_text[:120] + "..." if len(req.request_text) > 120 else req.request_text,
                    created_at=req.created_at,
                )
            )

        return SupportHistoryResponse(
            requests=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_request_detail(self, db: Session, request_id: str) -> SupportRequestResponse | None:
        """Get full detail of a single support request."""
        req = (
            db.query(SupportRequest)
            .options(joinedload(SupportRequest.customer), joinedload(SupportRequest.order))
            .filter(SupportRequest.request_id == request_id)
            .first()
        )
        if not req:
            return None

        return SupportRequestResponse(
            request_id=req.request_id,
            customer_id=req.customer.customer_id,
            customer_name=req.customer.name,
            order_id=req.order.order_id if req.order else None,
            request_text=req.request_text,
            decision=req.decision or "pending",
            reasoning=req.reasoning or "",
            recommended_action=req.recommended_action or "",
            customer_response=req.customer_response or "",
            policies_applied=req.get_policies_applied(),
            confidence_score=req.confidence_score or 0.0,
            created_at=req.created_at,
        )


support_service = SupportService()
