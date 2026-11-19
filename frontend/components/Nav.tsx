"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export const PAGES = [
  { href: "/", label: "Overview" },
  { href: "/search/", label: "Search Intelligence" },
  { href: "/social/", label: "Social & Community" },
  { href: "/sentiment/", label: "Sentiment" },
  { href: "/events/", label: "Events" },
  { href: "/models/", label: "Forecasting & Models" },
  { href: "/quality/", label: "Data Quality & Sources" },
  { href: "/methodology/", label: "Methodology" },
];

export function Nav() {
  const pathname = usePathname() || "/";
  const normalised = pathname.endsWith("/") ? pathname : `${pathname}/`;
  return (
    <nav className="nav" aria-label="Pages">
      {PAGES.map((p) => (
        <Link key={p.href} href={p.href} aria-current={normalised === p.href ? "page" : undefined}>
          {p.label}
        </Link>
      ))}
    </nav>
  );
}
