"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { Search, X, Loader2 } from "lucide-react";
import { customerApi, ordersApi } from "@/lib/api";
import { useSupportStore } from "@/store/supportStore";
import type { Customer } from "@/lib/types";

export default function CustomerLookup() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Customer[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const {
    selectedCustomer,
    customerLoadingState,
    setSelectedCustomer,
    setCustomerOrders,
    setSelectedOrder,
    setCustomerLoadingState,
    setCustomerError,
    resetForm,
  } = useSupportStore();

  // Click-outside handler
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleSearch = useCallback((value: string) => {
    setQuery(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (value.trim().length < 1) {
      setResults([]);
      setShowDropdown(false);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      setIsSearching(true);
      try {
        const response = await customerApi.search(value);
        setResults(response.customers);
        setShowDropdown(true);
      } catch {
        setResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);
  }, []);

  const selectCustomer = async (customer: Customer) => {
    setShowDropdown(false);
    setQuery(customer.name);
    setResults([]);
    setCustomerLoadingState("loading");
    setCustomerError(null);
    resetForm();
    setSelectedOrder(null);

    try {
      setSelectedCustomer(customer);
      const ordersResponse = await ordersApi.getCustomerOrders(customer.customer_id);
      setCustomerOrders(ordersResponse.orders);
      setCustomerLoadingState("success");
    } catch (err) {
      setCustomerError(err instanceof Error ? err.message : "Failed to load orders.");
      setCustomerLoadingState("error");
    }
  };

  const clearSelection = () => {
    setQuery("");
    setResults([]);
    setShowDropdown(false);
    setSelectedCustomer(null);
    setCustomerOrders([]);
    setSelectedOrder(null);
    resetForm();
  };

  const tierLabel = (tier: string) =>
    tier.charAt(0).toUpperCase() + tier.slice(1);

  return (
    <div className="field-group">
      <label className="label" htmlFor="customer-search">
        Customer
      </label>

      <div className="search-wrapper" ref={searchRef}>
        <div style={{ position: "relative" }}>
          <Search
            size={16}
            color="var(--color-text-muted)"
            style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)" }}
          />
          <input
            id="customer-search"
            type="text"
            className="input"
            style={{ paddingLeft: "2.5rem", paddingRight: selectedCustomer ? "2.5rem" : "1rem" }}
            placeholder="Search by name or customer ID..."
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            onFocus={() => results.length > 0 && setShowDropdown(true)}
            autoComplete="off"
          />
          {isSearching && (
            <Loader2
              size={14}
              color="var(--color-accent-primary)"
              style={{
                position: "absolute",
                right: "12px",
                top: "50%",
                transform: "translateY(-50%)",
                animation: "spin 0.7s linear infinite",
              }}
            />
          )}
          {selectedCustomer && !isSearching && (
            <button
              onClick={clearSelection}
              style={{
                position: "absolute",
                right: "8px",
                top: "50%",
                transform: "translateY(-50%)",
                background: "transparent",
                border: "none",
                cursor: "pointer",
                padding: "4px",
                color: "var(--color-text-muted)",
                display: "flex",
                alignItems: "center",
              }}
            >
              <X size={14} />
            </button>
          )}
        </div>

        {showDropdown && results.length > 0 && (
          <div className="search-results">
            {results.map((customer) => (
              <div
                key={customer.id}
                className="search-result-item"
                onClick={() => selectCustomer(customer)}
              >
                <div className="search-result-avatar">
                  {customer.name.charAt(0)}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: "0.875rem",
                      fontWeight: 600,
                      color: "var(--color-text-primary)",
                    }}
                  >
                    {customer.name}
                  </div>
                  <div
                    style={{
                      fontSize: "0.75rem",
                      color: "var(--color-text-muted)",
                    }}
                  >
                    {customer.customer_id} · {customer.email}
                  </div>
                </div>
                <span className={`badge badge--${customer.tier}`}>
                  {tierLabel(customer.tier)}
                </span>
              </div>
            ))}
          </div>
        )}

        {showDropdown && results.length === 0 && !isSearching && query.trim() && (
          <div className="search-results">
            <div
              style={{
                padding: "1rem",
                textAlign: "center",
                color: "var(--color-text-muted)",
                fontSize: "0.875rem",
              }}
            >
              No customers found for &quot;{query}&quot;
            </div>
          </div>
        )}
      </div>

      {selectedCustomer && (
        <div className="customer-card" style={{ marginTop: "0.75rem" }}>
          <div className="customer-avatar">{selectedCustomer.name.charAt(0)}</div>
          <div className="customer-info">
            <div className="customer-name">{selectedCustomer.name}</div>
            <div className="customer-email">{selectedCustomer.email}</div>
            <div style={{ marginTop: "0.375rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              <span className={`badge badge--${selectedCustomer.tier}`}>
                {tierLabel(selectedCustomer.tier)}
              </span>
              <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>
                ${Number(selectedCustomer.total_spend).toLocaleString()} lifetime spend
              </span>
            </div>
          </div>
          {customerLoadingState === "loading" && (
            <span className="spinner spinner--accent" />
          )}
        </div>
      )}
    </div>
  );
}
