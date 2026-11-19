// Shared view helpers used by several pages (server side).
import type { LinePoint, EventMarker } from "@/components/LineChart";
import type { CoverageDay, EventMilestone } from "./types";

export const REPO_URL = "https://github.com/abdu08099-arch/north-analytics-gta6-launch-intelligence";
export const docUrl = (path: string) => `${REPO_URL}/blob/main/${path}`;

export function coveragePoints(days: CoverageDay[]): LinePoint[] {
  return days.map((d) => ({
    x: d.date,
    // Incomplete days are shown as gaps, not as low values.
    y: d.complete ? d.coverage_share : null,
    note: d.complete ? undefined : "incomplete day",
  }));
}

export function eventMarkers(events: EventMilestone[]): EventMarker[] {
  return events.map((e) => ({ date: e.event_date, name: `${e.event_name} (${e.verification_status})` }));
}

export function rangeLabel(first?: string, last?: string): string {
  if (!first || !last) return "—";
  return `${first} – ${last}`;
}
