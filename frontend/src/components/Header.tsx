"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Layers, History, Zap } from "lucide-react";
import ThemeToggle from "./ThemeToggle";

export default function Header() {
  const pathname = usePathname();

  return (
    <header className="header">
      <div className="header__inner">
        <Link href="/" className="header__logo">
          <div className="header__logo-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none" style={{ width: "20px", height: "20px" }}>
              <path d="M7 11L12 21L16 13L20 21L25 11" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <span className="header__logo-text">
            Worknoon <span>Desk</span>
          </span>
        </Link>

        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <nav className="header__nav">
            <Link
              href="/"
              className={`nav-link ${pathname === "/" ? "nav-link--active" : ""}`}
            >
              <Zap size={14} style={{ display: "inline", marginRight: "0.375rem" }} />
              Support
            </Link>
            <Link
              href="/history"
              className={`nav-link ${pathname === "/history" ? "nav-link--active" : ""}`}
            >
              <History size={14} style={{ display: "inline", marginRight: "0.375rem" }} />
              History
            </Link>
          </nav>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
