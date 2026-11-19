import type { ReactNode } from "react";
import type { Kind } from "@/lib/types";
import { KindBadge } from "./Badges";

export interface ChartMeta {
  metric: string;
  unit: string;
  range: string;
  geography: string;
  source: string;
}

/** Every chart states metric, unit, date range, geography and source (PRD F9). */
export function ChartCard({
  title,
  sub,
  kind,
  meta,
  children,
}: {
  title: string;
  sub?: string;
  kind: Kind;
  meta: ChartMeta;
  children: ReactNode;
}) {
  return (
    <section className="card" aria-label={title}>
      <div className="chart-head">
        <div>
          <h2>{title}</h2>
          {sub ? <p className="sub">{sub}</p> : null}
        </div>
        <KindBadge kind={kind} />
      </div>
      {children}
      <div className="chart-meta">
        <span>
          <b>Metric</b> {meta.metric}
        </span>
        <span>
          <b>Unit</b> {meta.unit}
        </span>
        <span>
          <b>Period</b> {meta.range}
        </span>
        <span>
          <b>Geography</b> {meta.geography}
        </span>
        <span>
          <b>Source</b> {meta.source}
        </span>
      </div>
    </section>
  );
}

/** Honest empty state: says why there is no data and what would change that. */
export function EmptyState({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="empty" role="status">
      <strong>{title}</strong>
      {children}
    </div>
  );
}

export function Tile({ label, value, note }: { label: string; value: string; note?: string }) {
  return (
    <div className="card">
      <div className="tile-label">{label}</div>
      <div className="tile-value">{value}</div>
      {note ? <div className="tile-note">{note}</div> : null}
    </div>
  );
}

export function PageHead({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <header className="page-head">
      <h1>{title}</h1>
      {children ? <p>{children}</p> : null}
    </header>
  );
}
