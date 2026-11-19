"use client";

import { useEffect, useRef } from "react";
import { LineChart as ELine } from "echarts/charts";
import {
  GridComponent,
  MarkLineComponent,
  TooltipComponent,
} from "echarts/components";
import * as echarts from "echarts/core";
import { SVGRenderer } from "echarts/renderers";

echarts.use([ELine, GridComponent, TooltipComponent, MarkLineComponent, SVGRenderer]);

export interface LinePoint {
  x: string; // ISO date or datetime (UTC)
  y: number | null; // null = gap, never drawn as 0
  note?: string; // shown in the tooltip instead of the value, e.g. "<1" or "missing"
}

export interface EventMarker {
  date: string;
  name: string;
}

function cssVar(name: string, fallback: string): string {
  if (typeof window === "undefined") return fallback;
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
}

/**
 * One-series line chart with a crosshair tooltip and optional event markers.
 * Gaps stay gaps. One y-axis only. Colors come from CSS tokens, so dark mode
 * uses its own validated steps.
 */
export function LineChart({
  points,
  seriesName,
  format,
  events = [],
  height = 300,
  yMax,
  ariaLabel,
}: {
  points: LinePoint[];
  seriesName: string;
  format: "percent" | "int";
  events?: EventMarker[];
  height?: number;
  yMax?: number;
  ariaLabel: string;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const chart = echarts.init(el, undefined, { renderer: "svg" });

    const render = () => {
      const text = cssVar("--text-secondary", "#52514e");
      const muted = cssVar("--text-muted", "#77766f");
      const grid = cssVar("--grid", "#ebeae6");
      const surface = cssVar("--surface-1", "#fcfcfb");
      const series = cssVar("--series-1", "#2a78d6");
      const eventColor = cssVar("--event-mark", "#77766f");
      const fmt = (v: number, digits = 3) =>
        format === "percent" ? `${(v * 100).toFixed(digits)}%` : new Intl.NumberFormat("en-GB").format(v);

      chart.setOption(
        {
          animation: false,
          grid: { left: 8, right: 16, top: 28, bottom: 8, containLabel: true },
          tooltip: {
            trigger: "axis",
            axisPointer: { type: "line", lineStyle: { color: muted, width: 1 } },
            backgroundColor: surface,
            borderColor: grid,
            textStyle: { color: cssVar("--text-primary", "#0b0b0b"), fontSize: 12 },
            formatter: (params: unknown) => {
              const p = (params as { dataIndex: number }[])[0];
              const point = points[p.dataIndex];
              const value = point.y === null ? point.note ?? "no data" : fmt(point.y);
              const evs = events.filter((e) => point.x.startsWith(e.date)).map((e) => `<br/>◆ ${e.name}`);
              return `${point.x.replace("T", " ").replace(/:00(\+00:00|Z)$/, " UTC")}<br/><b>${seriesName}: ${value}</b>${evs.join("")}`;
            },
          },
          xAxis: {
            type: "category",
            data: points.map((p) => p.x),
            boundaryGap: false,
            axisLine: { lineStyle: { color: grid } },
            axisTick: { show: false },
            axisLabel: {
              color: text,
              fontSize: 11,
              hideOverlap: true,
              formatter: (v: string) => v.slice(5, 10),
            },
          },
          yAxis: {
            type: "value",
            min: 0,
            max: yMax,
            splitLine: { lineStyle: { color: grid } },
            axisLabel: { color: text, fontSize: 11, formatter: (v: number) => fmt(v, 2) },
          },
          series: [
            {
              name: seriesName,
              type: "line",
              data: points.map((p) => p.y),
              connectNulls: false,
              showSymbol: points.length <= 31,
              symbolSize: 8,
              itemStyle: { color: series, borderColor: surface, borderWidth: 2 },
              lineStyle: { color: series, width: 2 },
              markLine: events.length
                ? {
                    symbol: ["none", "diamond"],
                    symbolSize: 8,
                    silent: true,
                    label: { show: false },
                    lineStyle: { color: eventColor, type: "dashed", width: 1 },
                    data: events
                      .map((e) => points.findIndex((p) => p.x.startsWith(e.date)))
                      .filter((i) => i >= 0)
                      .map((i) => ({ xAxis: points[i].x })),
                  }
                : undefined,
            },
          ],
        },
        true,
      );
    };

    render();
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const onResize = () => chart.resize();
    media.addEventListener("change", render);
    window.addEventListener("resize", onResize);
    return () => {
      media.removeEventListener("change", render);
      window.removeEventListener("resize", onResize);
      chart.dispose();
    };
  }, [points, seriesName, format, events, yMax]);

  return <div ref={ref} style={{ width: "100%", height }} role="img" aria-label={ariaLabel} />;
}
