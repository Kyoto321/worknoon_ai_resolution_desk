/**
 * Shared TypeScript types — mirrors backend Pydantic schemas.
 * These types are the contract between frontend and backend.
 */

// ── Customer ──────────────────────────────────────────────────────────────────

export type CustomerTier = "standard" | "vip" | "enterprise";

export interface Customer {
  id: number;
  customer_id: string;
  name: string;
  email: string;
  tier: CustomerTier;
  total_spend: number;
  phone: string | null;
  is_active: boolean;
  created_at: string;
}

export interface CustomerSearchResponse {
  customers: Customer[];
  total: number;
}

// ── Order ─────────────────────────────────────────────────────────────────────

export type OrderStatus =
  | "pending"
  | "processing"
  | "shipped"
  | "delivered"
  | "cancelled"
  | "refunded";

export interface Order {
  id: number;
  order_id: string;
  customer_id: number;
  product_name: string;
  amount: number;
  status: OrderStatus;
  purchase_date: string;
  delivery_date: string | null;
  expected_delivery_date: string | null;
  is_final_sale: boolean;
  is_damaged: boolean;
  refund_eligible: boolean;
  notes: string | null;
  created_at: string;
}

export interface OrderListResponse {
  orders: Order[];
  total: number;
}

// ── Support ───────────────────────────────────────────────────────────────────

export type SupportDecision = "approved" | "denied" | "escalated";

export interface SupportRequestCreate {
  customer_identifier: string;
  order_id?: string;
  request_text: string;
}

export interface SupportRequestResponse {
  request_id: string;
  customer_id: string;
  customer_name: string;
  order_id: string | null;
  request_text: string;
  decision: SupportDecision;
  reasoning: string;
  recommended_action: string;
  customer_response: string;
  policies_applied: string[];
  confidence_score: number;
  created_at: string;
}

export interface SupportHistoryItem {
  request_id: string;
  customer_id: string;
  customer_name: string;
  decision: SupportDecision;
  request_text: string;
  created_at: string;
}

export interface SupportHistoryResponse {
  requests: SupportHistoryItem[];
  total: number;
  page: number;
  page_size: number;
}

// ── Policy ────────────────────────────────────────────────────────────────────

export interface Policy {
  policy_id: string;
  name: string;
  description: string;
  is_active: boolean;
  priority: number;
}

export interface PoliciesListResponse {
  policies: Policy[];
  total: number;
}

// ── UI State ──────────────────────────────────────────────────────────────────

export type LoadingState = "idle" | "loading" | "success" | "error";
