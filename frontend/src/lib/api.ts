/**
 * API client — centralized Axios instance for all backend communication.
 * All API calls flow through here so base URL and headers are configured once.
 */

import axios from "axios";
import type {
  Customer,
  CustomerSearchResponse,
  Order,
  OrderListResponse,
  SupportRequestCreate,
  SupportRequestResponse,
  SupportHistoryResponse,
  PoliciesListResponse,
} from "./types";

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30s — AI calls can take a moment
});

// ── Response interceptor — normalize error messages ───────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.message ||
      "An unexpected error occurred.";
    return Promise.reject(new Error(message));
  }
);

// ── Customer API ──────────────────────────────────────────────────────────────

export const customerApi = {
  search: async (query: string): Promise<CustomerSearchResponse> => {
    const { data } = await apiClient.get<CustomerSearchResponse>(
      `/customers/search`,
      { params: { q: query } }
    );
    return data;
  },

  getById: async (customerId: string): Promise<Customer> => {
    const { data } = await apiClient.get<Customer>(`/customers/${customerId}`);
    return data;
  },
};

// ── Orders API ────────────────────────────────────────────────────────────────

export const ordersApi = {
  getCustomerOrders: async (customerId: string): Promise<OrderListResponse> => {
    const { data } = await apiClient.get<OrderListResponse>(
      `/orders/customer/${customerId}`
    );
    return data;
  },

  getOrder: async (orderId: string): Promise<Order> => {
    const { data } = await apiClient.get<Order>(`/orders/${orderId}`);
    return data;
  },
};

// ── Support API ───────────────────────────────────────────────────────────────

export const supportApi = {
  submitRequest: async (
    request: SupportRequestCreate
  ): Promise<SupportRequestResponse> => {
    const { data } = await apiClient.post<SupportRequestResponse>(
      `/support/request`,
      request
    );
    return data;
  },

  getHistory: async (
    page: number = 1,
    pageSize: number = 20
  ): Promise<SupportHistoryResponse> => {
    const { data } = await apiClient.get<SupportHistoryResponse>(
      `/support/history`,
      { params: { page, page_size: pageSize } }
    );
    return data;
  },

  getRequestDetail: async (
    requestId: string
  ): Promise<SupportRequestResponse> => {
    const { data } = await apiClient.get<SupportRequestResponse>(
      `/support/request/${requestId}`
    );
    return data;
  },
};

// ── Policies API ──────────────────────────────────────────────────────────────

export const policiesApi = {
  getAll: async (): Promise<PoliciesListResponse> => {
    const { data } = await apiClient.get<PoliciesListResponse>(`/policies`);
    return data;
  },
};

export default apiClient;
