"use client";

import { Package, AlertTriangle, Tag, CheckCircle, Clock, Truck } from "lucide-react";
import { useSupportStore } from "@/store/supportStore";
import type { Order } from "@/lib/types";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  pending: { label: "Pending", color: "var(--color-text-muted)" },
  processing: { label: "Processing", color: "#6366f1" },
  shipped: { label: "Shipped", color: "#3b82f6" },
  delivered: { label: "Delivered", color: "var(--color-approved)" },
  cancelled: { label: "Cancelled", color: "var(--color-denied)" },
  refunded: { label: "Refunded", color: "#8b5cf6" },
};

function StatusIcon({ status }: { status: string }) {
  const size = 12;
  switch (status) {
    case "delivered": return <CheckCircle size={size} />;
    case "shipped": return <Truck size={size} />;
    case "pending":
    case "processing": return <Clock size={size} />;
    default: return <Package size={size} />;
  }
}

function OrderCard({ order, isSelected, onClick }: {
  order: Order;
  isSelected: boolean;
  onClick: () => void;
}) {
  const statusConfig = STATUS_CONFIG[order.status] || { label: order.status, color: "var(--color-text-muted)" };
  const purchaseDate = new Date(order.purchase_date).toLocaleDateString("en-US", {
    month: "short", day: "numeric", year: "numeric",
  });
  const daysAgo = Math.floor((Date.now() - new Date(order.purchase_date).getTime()) / (1000 * 60 * 60 * 24));

  return (
    <div
      className={`order-card ${isSelected ? "order-card--selected" : ""}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onClick()}
      id={`order-${order.order_id}`}
    >
      <div className="order-card__header">
        <span className="order-id">{order.order_id}</span>
        <span className="order-amount">${Number(order.amount).toFixed(2)}</span>
      </div>
      <div className="order-product">{order.product_name}</div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span
          style={{
            fontSize: "0.75rem",
            fontWeight: 600,
            color: statusConfig.color,
            display: "flex",
            alignItems: "center",
            gap: "0.25rem",
          }}
        >
          <StatusIcon status={order.status} />
          {statusConfig.label}
        </span>
        <span style={{ fontSize: "0.7rem", color: "var(--color-text-muted)" }}>
          {purchaseDate} · {daysAgo}d ago
        </span>
      </div>
      <div className="order-flags" style={{ marginTop: "0.5rem" }}>
        {order.is_final_sale && (
          <span className="order-flag order-flag--final-sale">
            <Tag size={9} style={{ display: "inline" }} /> Final Sale
          </span>
        )}
        {order.is_damaged && (
          <span className="order-flag order-flag--damaged">
            <AlertTriangle size={9} style={{ display: "inline" }} /> Damaged
          </span>
        )}
        {order.refund_eligible && !order.is_final_sale && (
          <span className="order-flag order-flag--refundable">
            <CheckCircle size={9} style={{ display: "inline" }} /> Refundable
          </span>
        )}
      </div>
    </div>
  );
}

export default function OrderSelector() {
  const { customerOrders, selectedOrder, setSelectedOrder, customerLoadingState } = useSupportStore();

  if (customerLoadingState === "loading") {
    return (
      <div className="field-group">
        <div className="label">Related Order (Optional)</div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", padding: "1rem 0", color: "var(--color-text-muted)", fontSize: "0.875rem" }}>
          <span className="spinner spinner--accent" />
          Loading orders...
        </div>
      </div>
    );
  }

  if (!customerOrders.length) {
    return null;
  }

  return (
    <div className="field-group">
      <label className="label">Related Order (Optional)</label>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {customerOrders.map((order) => (
          <OrderCard
            key={order.id}
            order={order}
            isSelected={selectedOrder?.order_id === order.order_id}
            onClick={() =>
              setSelectedOrder(
                selectedOrder?.order_id === order.order_id ? null : order
              )
            }
          />
        ))}
      </div>
      {selectedOrder && (
        <p style={{ fontSize: "0.75rem", color: "var(--color-accent-primary)", marginTop: "0.375rem" }}>
          ✓ Order {selectedOrder.order_id} selected
        </p>
      )}
    </div>
  );
}
