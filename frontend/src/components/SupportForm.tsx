"use client";

import { useState } from "react";
import { Send, AlertCircle } from "lucide-react";
import { supportApi } from "@/lib/api";
import { useSupportStore } from "@/store/supportStore";

const MIN_LENGTH = 10;
const MAX_LENGTH = 2000;

const EXAMPLE_REQUESTS = [
  "I received a damaged product and would like a full refund.",
  "My order hasn't arrived yet and it's past the expected delivery date.",
  "I'd like to return this item — it doesn't meet my expectations.",
  "I was charged the wrong amount for my order.",
];

export default function SupportForm() {
  const [charCount, setCharCount] = useState(0);

  const {
    selectedCustomer,
    selectedOrder,
    requestText,
    submitLoadingState,
    submitError,
    setRequestText,
    setSubmitLoadingState,
    setSubmitError,
    setLastResponse,
  } = useSupportStore();

  const isLoading = submitLoadingState === "loading";
  const isValid =
    selectedCustomer && requestText.trim().length >= MIN_LENGTH;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCustomer || !isValid) return;

    setSubmitLoadingState("loading");
    setSubmitError(null);

    try {
      const response = await supportApi.submitRequest({
        customer_identifier: selectedCustomer.customer_id,
        order_id: selectedOrder?.order_id,
        request_text: requestText.trim(),
      });
      setLastResponse(response);
      setSubmitLoadingState("success");
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to submit request.");
      setSubmitLoadingState("error");
    }
  };

  const handleTextChange = (value: string) => {
    setRequestText(value);
    setCharCount(value.length);
  };

  const fillExample = (example: string) => {
    setRequestText(example);
    setCharCount(example.length);
  };

  return (
    <form onSubmit={handleSubmit} className="field-group">
      <div className="field-group">
        <label className="label" htmlFor="request-text">
          Support Request
        </label>

        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "0.625rem" }}>
          {EXAMPLE_REQUESTS.map((ex, i) => (
            <button
              key={i}
              type="button"
              onClick={() => fillExample(ex)}
              style={{
                fontSize: "0.7rem",
                padding: "0.2rem 0.6rem",
                background: "rgba(99,102,241,0.08)",
                border: "1px solid rgba(99,102,241,0.2)",
                borderRadius: "4px",
                color: "var(--color-text-muted)",
                cursor: "pointer",
                fontFamily: "inherit",
                transition: "all 0.15s ease",
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.color = "var(--color-accent-primary)";
                e.currentTarget.style.borderColor = "rgba(99,102,241,0.5)";
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.color = "var(--color-text-muted)";
                e.currentTarget.style.borderColor = "rgba(99,102,241,0.2)";
              }}
            >
              {ex.length > 40 ? ex.slice(0, 40) + "…" : ex}
            </button>
          ))}
        </div>

        <textarea
          id="request-text"
          className="textarea"
          placeholder="Describe the customer's issue in detail. The more context you provide, the better the AI can evaluate against company policies."
          value={requestText}
          onChange={(e) => handleTextChange(e.target.value)}
          maxLength={MAX_LENGTH}
          disabled={isLoading}
          style={{ minHeight: "140px" }}
        />

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            fontSize: "0.75rem",
            color: "var(--color-text-muted)",
            marginTop: "0.25rem",
          }}
        >
          <span>
            {charCount < MIN_LENGTH && charCount > 0 && (
              <span style={{ color: "var(--color-denied)" }}>
                {MIN_LENGTH - charCount} more characters required
              </span>
            )}
          </span>
          <span
            style={{ color: charCount > MAX_LENGTH * 0.9 ? "var(--color-escalated)" : "inherit" }}
          >
            {charCount}/{MAX_LENGTH}
          </span>
        </div>
      </div>

      {submitError && (
        <div className="alert alert--error">
          <AlertCircle size={15} style={{ flexShrink: 0, marginTop: "1px" }} />
          <span>{submitError}</span>
        </div>
      )}

      {!selectedCustomer && (
        <div className="alert alert--info">
          <AlertCircle size={15} style={{ flexShrink: 0, marginTop: "1px" }} />
          <span>Please search and select a customer before submitting.</span>
        </div>
      )}

      <button
        type="submit"
        className="btn btn--primary btn--lg"
        disabled={!isValid || isLoading}
        style={{ width: "100%", justifyContent: "center" }}
        id="submit-support-request"
      >
        {isLoading ? (
          <>
            <span className="spinner" style={{ width: "18px", height: "18px" }} />
            Analyzing with Gemini AI...
          </>
        ) : (
          <>
            <Send size={16} />
            Submit Support Request
          </>
        )}
      </button>

      {selectedOrder && (
        <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", textAlign: "center" }}>
          Evaluating against order {selectedOrder.order_id} · ${Number(selectedOrder.amount).toFixed(2)}
        </p>
      )}
    </form>
  );
}
