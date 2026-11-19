import type { Kind, SourceStatus } from "@/lib/types";

const KIND_LABEL: Record<Kind, string> = {
  observed: "Observed",
  derived: "Derived",
  predicted: "Prediction",
};

/** Observed data, derived metrics and predictions must always look different (PRD F9). */
export function KindBadge({ kind }: { kind: Kind }) {
  return (
    <span className={`badge kind-${kind}`} title={`Data kind: ${KIND_LABEL[kind]}`}>
      {KIND_LABEL[kind]}
    </span>
  );
}

type Tone = "good" | "warning" | "serious" | "critical" | "neutral";
const TONE: Record<Tone, { color: string; icon: string }> = {
  good: { color: "var(--good)", icon: "✓" },
  warning: { color: "var(--warning)", icon: "!" },
  serious: { color: "var(--serious)", icon: "!" },
  critical: { color: "var(--critical)", icon: "✕" },
  neutral: { color: "var(--text-muted)", icon: "–" },
};

/** Status is never color alone: dot + icon + label. */
export function StatusLabel({ tone, label }: { tone: Tone; label: string }) {
  const t = TONE[tone];
  return (
    <span className="status">
      <span className="status-dot" style={{ background: t.color }} aria-hidden />
      <span className="status-icon" aria-hidden>
        {t.icon}
      </span>
      {label}
    </span>
  );
}

export function sourceTone(status: SourceStatus["status"]): Tone {
  switch (status) {
    case "enabled":
      return "good";
    case "planned":
      return "neutral";
    case "conditional":
    case "deferred":
      return "warning";
    case "blocked":
    case "disabled":
      return "critical";
  }
}

export function runTone(status: string | undefined): Tone {
  if (status === "success") return "good";
  if (status === "partial") return "serious";
  if (status === "failed") return "critical";
  return "neutral";
}
