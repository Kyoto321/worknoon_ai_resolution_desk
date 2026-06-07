"use client";

import { CheckCircle2, XCircle, ArrowUpCircle, RotateCcw, ExternalLink } from "lucide-react";
import { useSupportStore } from "@/store/supportStore";
import type { SupportDecision, SupportRequestResponse } from "@/lib/types";

const DECISION_CONFIG: Record<SupportDecision, {
  icon: React.ElementType;
  label: string;
  description: string;
  color: string;
}> = {
  approved: {
    icon: CheckCircle2,
    label: "Approved",
    description: "Request has been approved per company policy.",
    color: "var(--color-approved)",
  },
  denied: {
    icon: XCircle,
    label: "Denied",
    description: "Request cannot be fulfilled per current policy.",
    color: "var(--color-denied)",
  },
  escalated: {
    icon: ArrowUpCircle,
    label: "Escalated",
    description: "Requires review by a human support agent.",
    color: "var(--color-escalated)",
  },
};

function ConfidenceBar({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 80 ? "var(--color-approved)"
    : pct >= 50 ? "var(--color-escalated)"
    : "var(--color-denied)";

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.375rem" }}>
        <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--color-text-muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
          Confidence Score
        </span>
        <span style={{ fontSize: "0.875rem", fontWeight: 700, color }}>
          {pct}%
        </span>
      </div>
      <div className="confidence-bar">
        <div
          className="confidence-fill"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
    </div>
  );
}

function ResponseDetail({ label, content }: { label: string; content: string }) {
  return (
    <div>
      <div className="response-section__label">{label}</div>
      <div className="response-section__content">{content}</div>
    </div>
  );
}

export default function ResponseDisplay() {
  const { lastResponse, submitLoadingState, resetForm, resetAll } = useSupportStore();

  if (submitLoadingState === "loading") {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "3rem",
          gap: "1rem",
          background: "var(--color-bg-card)",
          borderRadius: "var(--radius-lg)",
          border: "1px solid var(--color-border)",
          animation: "pulse-glow 2s infinite",
        }}
      >
        <span className="spinner spinner--lg spinner--accent" />
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "0.9375rem", fontWeight: 600, color: "var(--color-text-primary)", marginBottom: "0.25rem" }}>
            Analyzing Request...
          </div>
          <div style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
            Evaluating policies and calculating resolution pathway
          </div>
        </div>
      </div>
    );
  }

  if (!lastResponse) {
    return (
      <div className="empty-state" style={{ background: "var(--color-bg-card)", borderRadius: "var(--radius-lg)", border: "1px solid var(--color-border)" }}>
        <div className="empty-state__icon">📋</div>
        <div className="empty-state__title">Resolution details will appear here</div>
        <div className="empty-state__text">
          Submit a support request to get an approved, denied, or escalated decision.
        </div>
      </div>
    );
  }

  const config = DECISION_CONFIG[lastResponse.decision as SupportDecision] || DECISION_CONFIG.escalated;
  const Icon = config.icon;

  return (
    <div className={`response-card response-card--${lastResponse.decision}`}>
      {/* Header */}
      <div className={`response-header response-header--${lastResponse.decision}`}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.875rem" }}>
          <Icon size={36} color={config.color} strokeWidth={1.5} />
          <div>
            <div style={{ fontSize: "1.375rem", fontWeight: 800, color: config.color }}>
              {config.label}
            </div>
            <div style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
              {config.description}
            </div>
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: "0.7rem", color: "var(--color-text-muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Request ID</div>
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)", fontFamily: "monospace" }}>
            {lastResponse.request_id.slice(0, 8)}...
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="response-body">
        {/* Customer Message */}
        <div>
          <div className="response-section__label">Message to Customer</div>
          <div className="customer-message">{lastResponse.customer_response}</div>
        </div>

        <div className="divider" />

        <ResponseDetail label="Policy Audit & Reasoning" content={lastResponse.reasoning} />
        <ResponseDetail label="Recommended Action" content={lastResponse.recommended_action} />

        <div className="divider" />

        <ConfidenceBar score={lastResponse.confidence_score} />

        {/* Policies */}
        {lastResponse.policies_applied.length > 0 && (
          <div>
            <div className="response-section__label">Policies Applied</div>
            <div style={{ display: "flex", gap: "0.375rem", flexWrap: "wrap", marginTop: "0.375rem" }}>
              {lastResponse.policies_applied.map((pid) => (
                <span key={pid} className="policy-tag">{pid.replace(/_/g, " ")}</span>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div style={{ display: "flex", gap: "0.75rem", paddingTop: "0.5rem", flexWrap: "wrap" }}>
          <button
            className="btn btn--secondary btn--sm"
            onClick={resetForm}
            id="new-request-btn"
          >
            <RotateCcw size={13} />
            New Request
          </button>
          <a
            href="/history"
            className="btn btn--ghost btn--sm"
            id="view-history-btn"
          >
            <ExternalLink size={13} />
            View History
          </a>
        </div>
      </div>
    </div>
  );
}
