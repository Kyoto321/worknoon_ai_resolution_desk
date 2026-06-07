"use client";

import { useState, useEffect, useCallback } from "react";
import { History, RefreshCw, ChevronLeft, ChevronRight, Clock } from "lucide-react";
import { supportApi } from "@/lib/api";
import type { SupportHistoryItem, SupportDecision } from "@/lib/types";

const DECISION_COLORS: Record<SupportDecision, string> = {
  approved: "var(--color-approved)",
  denied: "var(--color-denied)",
  escalated: "var(--color-escalated)",
};

const PAGE_SIZE = 15;

export default function HistoryPage() {
  const [requests, setRequests] = useState<SupportHistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(async (p: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await supportApi.getHistory(p, PAGE_SIZE);
      setRequests(data.requests);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load history.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory(page);
  }, [page, fetchHistory]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  const decisionCounts = requests.reduce(
    (acc, r) => {
      acc[r.decision as SupportDecision] = (acc[r.decision as SupportDecision] || 0) + 1;
      return acc;
    },
    {} as Record<SupportDecision, number>
  );

  const formatDate = (dateStr: string) =>
    new Date(dateStr).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem 1.5rem 3rem" }}>
      {/* Header */}
      <div style={{ marginBottom: "2rem" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <History size={24} color="var(--color-accent-primary)" />
            <div>
              <h1 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--color-text-primary)" }}>
                Support History
              </h1>
              <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
                {total} total requests processed
              </p>
            </div>
          </div>
          <button
            className="btn btn--secondary btn--sm"
            onClick={() => fetchHistory(page)}
            disabled={isLoading}
            id="refresh-history"
          >
            <RefreshCw size={13} style={{ animation: isLoading ? "spin 0.7s linear infinite" : "none" }} />
            Refresh
          </button>
        </div>

        {/* Summary Stats */}
        {total > 0 && (
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            {(["approved", "denied", "escalated"] as SupportDecision[]).map((decision) => (
              <div
                key={decision}
                style={{
                  padding: "0.5rem 1rem",
                  background: "var(--color-bg-card)",
                  border: `1px solid var(--color-${decision === "approved" ? "approved" : decision === "denied" ? "denied" : "escalated"}-border)`,
                  borderRadius: "var(--radius-sm)",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                }}
              >
                <span
                  style={{
                    width: "8px",
                    height: "8px",
                    borderRadius: "50%",
                    background: DECISION_COLORS[decision],
                    flexShrink: 0,
                  }}
                />
                <span style={{ fontSize: "0.875rem", fontWeight: 700, color: DECISION_COLORS[decision] }}>
                  {decisionCounts[decision] || 0}
                </span>
                <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", textTransform: "capitalize" }}>
                  {decision}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Table */}
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        {error && (
          <div className="alert alert--error" style={{ margin: "1rem" }}>
            {error}
          </div>
        )}

        {isLoading && (
          <div style={{ display: "flex", justifyContent: "center", padding: "3rem" }}>
            <span className="spinner spinner--lg spinner--accent" />
          </div>
        )}

        {!isLoading && requests.length === 0 && !error && (
          <div className="empty-state">
            <div className="empty-state__icon">📋</div>
            <div className="empty-state__title">No support requests yet</div>
            <div className="empty-state__text">
              Submit a request from the main page to see it here.
            </div>
          </div>
        )}

        {!isLoading && requests.length > 0 && (
          <table className="history-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Request</th>
                <th>Decision</th>
                <th>
                  <span style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
                    <Clock size={11} />
                    Time
                  </span>
                </th>
              </tr>
            </thead>
            <tbody>
              {requests.map((req) => (
                <tr key={req.request_id}>
                  <td>
                    <div style={{ fontWeight: 600, color: "var(--color-text-primary)" }}>
                      {req.customer_name}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>
                      {req.customer_id}
                    </div>
                  </td>
                  <td style={{ maxWidth: "350px" }}>
                    <span
                      style={{
                        display: "-webkit-box",
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: "vertical",
                        overflow: "hidden",
                        lineHeight: "1.5",
                      }}
                    >
                      {req.request_text}
                    </span>
                  </td>
                  <td>
                    <span
                      className={`badge badge--${req.decision}`}
                    >
                      <span
                        style={{
                          width: "6px",
                          height: "6px",
                          borderRadius: "50%",
                          background: DECISION_COLORS[req.decision as SupportDecision] || "gray",
                          flexShrink: 0,
                        }}
                      />
                      {req.decision}
                    </span>
                  </td>
                  <td style={{ whiteSpace: "nowrap" }}>
                    <span style={{ fontSize: "0.8125rem" }}>
                      {formatDate(req.created_at)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "1rem 1.5rem",
              borderTop: "1px solid var(--color-border)",
              fontSize: "0.8125rem",
              color: "var(--color-text-muted)",
            }}
          >
            <span>
              Page {page} of {totalPages} · {total} total
            </span>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button
                className="btn btn--secondary btn--sm"
                onClick={() => setPage((p) => p - 1)}
                disabled={page === 1 || isLoading}
                id="prev-page"
              >
                <ChevronLeft size={14} />
              </button>
              <button
                className="btn btn--secondary btn--sm"
                onClick={() => setPage((p) => p + 1)}
                disabled={page === totalPages || isLoading}
                id="next-page"
              >
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
