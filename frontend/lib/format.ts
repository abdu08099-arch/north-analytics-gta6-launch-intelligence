// Small, tested formatting helpers. All dates are shown in UTC, like the data.

const DATE = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
const DATETIME = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "short",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  timeZone: "UTC",
});

export const OBSERVATION_START = "2026-11-19";

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  return DATE.format(new Date(iso.length === 10 ? `${iso}T00:00:00Z` : iso));
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  return `${DATETIME.format(new Date(iso))} UTC`;
}

export function formatPercent(share: number | null | undefined, digits = 3): string {
  if (share === null || share === undefined || Number.isNaN(share)) return "—";
  return `${(share * 100).toFixed(digits)}%`;
}

export function formatInt(n: number | null | undefined): string {
  if (n === null || n === undefined) return "—";
  return new Intl.NumberFormat("en-GB").format(n);
}

/** Whole days from the observation start to `now` (day 1 = 19 Nov 2026). */
export function observationDay(now: Date, start = OBSERVATION_START): number {
  const startMs = Date.parse(`${start}T00:00:00Z`);
  return Math.floor((now.getTime() - startMs) / 86_400_000) + 1;
}

/** Hours since an ISO timestamp, or null. Used for freshness warnings. */
export function hoursSince(iso: string | null | undefined, now: Date): number | null {
  if (!iso) return null;
  return (now.getTime() - Date.parse(iso)) / 3_600_000;
}

export type Freshness = "fresh" | "stale" | "never";

/** A source is stale when its last success is more than 36 h old (daily runs + slack). */
export function freshness(lastSuccess: string | null, now: Date, maxHours = 36): Freshness {
  const h = hoursSince(lastSuccess, now);
  if (h === null) return "never";
  return h <= maxHours ? "fresh" : "stale";
}

/** Value shown for one Trends cell: the number, "<1", or "missing". Never 0 for a gap. */
export function trendsCell(value: number | null, flag: string | null): string {
  if (value !== null) return String(value);
  return flag === "<1" ? "<1" : "missing";
}
