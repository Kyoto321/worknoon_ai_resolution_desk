import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";
import Header from "@/components/Header";

export const metadata: Metadata = {
  title: "WorkNoon AI Support Assistant",
  description:
    "AI-powered customer support system that evaluates requests against company policies using Google Gemini. Instant decisions: approved, denied, or escalated.",
  keywords: ["customer support", "AI", "Gemini", "support assistant"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Script id="theme-loader" strategy="beforeInteractive">
          {`
            (function() {
              const theme = localStorage.getItem('theme') || 'light';
              document.documentElement.setAttribute('data-theme', theme);
            })();
          `}
        </Script>
        <Header />
        <main>{children}</main>
      </body>
    </html>
  );
}
