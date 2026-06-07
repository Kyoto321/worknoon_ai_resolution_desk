/**
 * Zustand store — global state for the support request flow.
 * Keeps UI state and API responses organized in one place.
 */

import { create } from "zustand";
import type {
  Customer,
  Order,
  SupportRequestResponse,
  LoadingState,
} from "@/lib/types";

interface SupportStore {
  // ── Customer State ──────────────────────────────────────────────────
  selectedCustomer: Customer | null;
  customerOrders: Order[];
  selectedOrder: Order | null;
  customerLoadingState: LoadingState;
  customerError: string | null;

  // ── Request State ───────────────────────────────────────────────────
  requestText: string;
  submitLoadingState: LoadingState;
  submitError: string | null;
  lastResponse: SupportRequestResponse | null;

  // ── Actions ─────────────────────────────────────────────────────────
  setSelectedCustomer: (customer: Customer | null) => void;
  setCustomerOrders: (orders: Order[]) => void;
  setSelectedOrder: (order: Order | null) => void;
  setCustomerLoadingState: (state: LoadingState) => void;
  setCustomerError: (error: string | null) => void;

  setRequestText: (text: string) => void;
  setSubmitLoadingState: (state: LoadingState) => void;
  setSubmitError: (error: string | null) => void;
  setLastResponse: (response: SupportRequestResponse | null) => void;

  resetForm: () => void;
  resetAll: () => void;
}

export const useSupportStore = create<SupportStore>((set) => ({
  // ── Initial State ────────────────────────────────────────────────────
  selectedCustomer: null,
  customerOrders: [],
  selectedOrder: null,
  customerLoadingState: "idle",
  customerError: null,

  requestText: "",
  submitLoadingState: "idle",
  submitError: null,
  lastResponse: null,

  // ── Actions ──────────────────────────────────────────────────────────
  setSelectedCustomer: (customer) => set({ selectedCustomer: customer }),
  setCustomerOrders: (orders) => set({ customerOrders: orders }),
  setSelectedOrder: (order) => set({ selectedOrder: order }),
  setCustomerLoadingState: (state) => set({ customerLoadingState: state }),
  setCustomerError: (error) => set({ customerError: error }),

  setRequestText: (text) => set({ requestText: text }),
  setSubmitLoadingState: (state) => set({ submitLoadingState: state }),
  setSubmitError: (error) => set({ submitError: error }),
  setLastResponse: (response) => set({ lastResponse: response }),

  resetForm: () =>
    set({
      requestText: "",
      submitLoadingState: "idle",
      submitError: null,
      lastResponse: null,
    }),

  resetAll: () =>
    set({
      selectedCustomer: null,
      customerOrders: [],
      selectedOrder: null,
      customerLoadingState: "idle",
      customerError: null,
      requestText: "",
      submitLoadingState: "idle",
      submitError: null,
      lastResponse: null,
    }),
}));
