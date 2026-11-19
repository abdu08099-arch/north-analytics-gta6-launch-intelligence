// Shapes of the JSON data products written by `gta6 publish`
// (src/gta6_intelligence/reporting/products.py). Keep the two in step.

export type Kind = "observed" | "derived" | "predicted";

export interface Envelope<T> {
  product: string;
  kind: Kind;
  description: string;
  generated_at: string;
  code_version: string;
  source?: string;
  unit?: string;
  method?: string;
  data: T;
}

export interface SourceStatus {
  source_id: string;
  name: string;
  status: "enabled" | "planned" | "conditional" | "deferred" | "blocked" | "disabled";
  connector_available: boolean;
  notes: string | null;
  last_run: { status: "running" | "success" | "partial" | "failed"; started_at: string; error: string | null } | null;
  last_success_at: string | null;
  raw_artifacts: number;
  processing: Partial<Record<"processed" | "partial" | "failed", number>>;
  quarantined_records: number;
}

export interface EventMilestone {
  event_id: string;
  event_name: string;
  event_type: string;
  event_date: string;
  published_at: string | null;
  source_url: string;
  source_kind: "official" | "secondary";
  summary: string;
  verification_status: "verified" | "unverified" | "disputed";
}

export interface CoverageDay {
  date: string;
  matching_articles: number | null;
  total_monitored: number | null;
  coverage_share: number | null;
  points: number;
  resolution: string | null;
  complete: boolean;
  snapshot_artifact_id: string;
  snapshot_retrieved_at: string;
}

export interface TrendsPoint {
  t: string;
  value: number | null;
  flag: "<1" | "missing" | null;
}

export interface TrendsSnapshot {
  snapshot_id: string;
  file: string | null;
  exported_on: string | null;
  imported_at: string;
  geo: string;
  query: string;
  query_kind: "term" | "topic";
  window: string;
  granularity: string;
  series: { label: string; points: TrendsPoint[] }[];
}

export interface Products {
  status: Envelope<SourceStatus[]> | null;
  events: Envelope<EventMilestone[]> | null;
  coverage: Envelope<CoverageDay[]> | null;
  search: Envelope<TrendsSnapshot[]> | null;
}
