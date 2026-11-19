import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Nav } from "@/components/Nav";
import { loadProducts } from "@/lib/data";
import { formatDateTime } from "@/lib/format";
import "./globals.css";

export const metadata: Metadata = {
  title: "GTA VI Launch Intelligence · North Analytics",
  description:
    "Public search, news and event signals about GTA VI from 19 November 2026 until GTA VI Online. Relative interest and coverage, not sales or player counts.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  const { status } = loadProducts();
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <aside className="sidebar">
            <div className="brand">
              <div className="brand-name">North Analytics</div>
              <div className="brand-sub">GTA VI Launch Intelligence</div>
            </div>
            <Nav />
            <div className="sidebar-foot">
              <div>Data published: {status ? formatDateTime(status.generated_at) : "not yet"}</div>
              <div style={{ marginTop: 6 }}>All times UTC.</div>
            </div>
          </aside>
          <main className="main">{children}</main>
        </div>
      </body>
    </html>
  );
}
