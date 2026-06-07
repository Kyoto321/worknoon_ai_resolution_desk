"use client";

import { Sparkles, Shield, Zap } from "lucide-react";
import CustomerLookup from "@/components/CustomerLookup";
import OrderSelector from "@/components/OrderSelector";
import SupportForm from "@/components/SupportForm";
import ResponseDisplay from "@/components/ResponseDisplay";

export default function HomePage() {
  return (
    <>
      {/* ── Dashboard Header ────────────────────────────────────────── */}
      <section className="hero" style={{ padding: "2.5rem 1.5rem", textAlign: "left" }}>
        <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
          <div className="hero__eyebrow" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }}>
            Operations Control
          </div>
          <h1 className="hero__title" style={{ fontSize: "2rem", fontWeight: 800, margin: "0.5rem 0 0.75rem", letterSpacing: "-0.02em" }}>
            Customer Support Panel
          </h1>
          <p className="hero__subtitle" style={{ margin: 0, fontSize: "0.9375rem", maxWidth: "700px", textAlign: "left" }}>
            Identify a customer, select an order, and submit their ticket. The system evaluates the request against active refund, return, and transaction policies with detailed audit trails.
          </p>
        </div>
      </section>

      {/* ── Stats Bar ────────────────────────────────────────────────── */}
      <div className="stats-bar">
        {[
          { value: "7", label: "Active Policies" },
          { value: "<2s", label: "Avg Response Time" },
          { value: "3", label: "Decision Types" },
          { value: "100%", label: "Policy-Grounded" },
        ].map((stat) => (
          <div key={stat.label} className="stat-item">
            <div className="stat-item__value">{stat.value}</div>
            <div className="stat-item__label">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* ── Main Layout ──────────────────────────────────────────────── */}
      <div className="main-layout">
        {/* Left: Form */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <div className="card">
            <div className="section-title">
              <Shield size={12} />
              Step 1 — Identify Customer
            </div>
            <CustomerLookup />
          </div>

          <div className="card">
            <div className="section-title">
              <Zap size={12} />
              Step 2 — Select Order & Describe Issue
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
              <OrderSelector />
              <SupportForm />
            </div>
          </div>
        </div>

        {/* Right: Response */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div className="section-title" style={{ flex: 1, marginBottom: 0 }}>
              <Sparkles size={12} />
              Policy-Grounded Resolution
            </div>
          </div>
          <ResponseDisplay />

          {/* System Protocol */}
          <div className="card" style={{ fontSize: "0.8125rem", color: "var(--color-text-secondary)" }}>
            <div style={{ fontWeight: 700, color: "var(--color-text-primary)", marginBottom: "0.75rem", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em" }}>
              System Processing Flow
            </div>
            {[
              ["1", "Resolve customer profile details"],
              ["2", "Query recent transaction records"],
              ["3", "Evaluate rules in active company policies"],
              ["4", "Synthesize findings using grounded AI models"],
              ["5", "Log decision outcome to audit trail"],
            ].map(([num, text]) => (
              <div key={num} style={{ display: "flex", gap: "0.75rem", padding: "0.5rem 0", borderBottom: "1px solid var(--color-border)" }}>
                <span style={{
                  width: "18px", height: "18px", borderRadius: "50%",
                  background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "0.6875rem", fontWeight: 700, color: "var(--color-text-primary)",
                  flexShrink: 0,
                }}>
                  {num}
                </span>
                <span>{text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
