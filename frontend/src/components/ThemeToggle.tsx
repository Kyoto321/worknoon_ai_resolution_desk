"use client";

import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";

export default function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const savedTheme = document.documentElement.getAttribute("data-theme") as "light" | "dark" | null;
    if (savedTheme) {
      setTheme(savedTheme);
    } else {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      setTheme(systemTheme);
    }
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    document.documentElement.setAttribute("data-theme", nextTheme);
    localStorage.setItem("theme", nextTheme);
  };

  return (
    <button
      onClick={toggleTheme}
      className="btn btn--ghost btn--sm"
      style={{
        padding: "0.5rem",
        borderRadius: "50%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width: "36px",
        height: "36px",
        marginLeft: "0.5rem",
        border: "1px solid var(--color-border)",
        background: "var(--color-bg-secondary)",
        color: "var(--color-text-secondary)",
      }}
      aria-label="Toggle theme"
    >
      {theme === "dark" ? (
        <Sun size={16} className="text-amber-400" style={{ transition: "transform 0.3s ease" }} />
      ) : (
        <Moon size={16} className="text-indigo-600" style={{ transition: "transform 0.3s ease" }} />
      )}
    </button>
  );
}
