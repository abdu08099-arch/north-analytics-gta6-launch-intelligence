import { describe, expect, it } from "vitest";
import { formatDate, formatPercent, freshness, observationDay, trendsCell } from "./format";
import { loadProducts } from "./data";

describe("format", () => {
  it("counts observation days from 19 Nov 2026 as day 1", () => {
    expect(observationDay(new Date("2026-11-19T12:00:00Z"))).toBe(1);
    expect(observationDay(new Date("2026-11-26T00:00:00Z"))).toBe(8);
  });

  it("formats dates in UTC", () => {
    expect(formatDate("2026-11-19")).toBe("19 Nov 2026");
    expect(formatDate(null)).toBe("—");
  });

  it("shows a share as a percentage and missing as a dash, never 0", () => {
    expect(formatPercent(0.00123)).toBe("0.123%");
    expect(formatPercent(null)).toBe("—");
  });

  it("marks sources stale after 36 hours and never-run sources as never", () => {
    const now = new Date("2026-11-20T12:00:00Z");
    expect(freshness("2026-11-20T06:00:00Z", now)).toBe("fresh");
    expect(freshness("2026-11-18T06:00:00Z", now)).toBe("stale");
    expect(freshness(null, now)).toBe("never");
  });

  it("never shows a Trends gap as zero", () => {
    expect(trendsCell(0, null)).toBe("0");
    expect(trendsCell(null, "<1")).toBe("<1");
    expect(trendsCell(null, "missing")).toBe("missing");
  });
});

describe("data loading", () => {
  it("returns null for every product when nothing has been published", () => {
    expect(loadProducts("/nonexistent-folder")).toEqual({
      status: null,
      events: null,
      coverage: null,
      search: null,
    });
  });
});
