import Link from "next/link";
import { runTone, StatusLabel } from "@/components/Badges";
import { ChartCard, EmptyState, PageHead, Tile } from "@/components/Cards";
import { LineChart } from "@/components/LineChart";
import { loadProducts } from "@/lib/data";
import { formatDate, formatDateTime, formatPercent, freshness, observationDay } from "@/lib/format";
import { coveragePoints, eventMarkers, rangeLabel } from "@/lib/view";

export default function OverviewPage() {
  const { status, events, coverage } = loadProducts();
  const now = new Date();
  const sources = status?.data ?? [];
  const collecting = sources.filter((s) => s.connector_available && s.status !== "blocked");
  const fresh = collecting.filter((s) => freshness(s.last_success_at, now) === "fresh");
  const evs = events?.data ?? [];
  const verified = evs.filter((e) => e.verification_status === "verified").length;
  const days = coverage?.data ?? [];
  const lastComplete = [...days].reverse().find((d) => d.complete);
  const warnings = sources.filter(
    (s) =>
      s.last_run?.status === "failed" ||
      s.last_run?.status === "partial" ||
      (s.connector_available && freshness(s.last_success_at, now) !== "fresh") ||
      s.quarantined_records > 0,
  );

  return (
    <>
      <PageHead title="Overview">
        Public signals about GTA VI from 19 November 2026 until the verified launch of GTA VI Online
        (date not announced). We measure relative search interest and media coverage, not sales or
        player counts.
      </PageHead>

      <div className="grid grid-4">
        <Tile label="Observation day" value={String(Math.max(observationDay(now), 1))} note={`Started 19 Nov 2026 · as of ${formatDate(now.toISOString())}`} />
        <Tile
          label="Sources up to date"
          value={status ? `${fresh.length} / ${collecting.length}` : "—"}
          note="Successful run in the last 36 h"
        />
        <Tile
          label="Events in ledger"
          value={events ? String(evs.length) : "—"}
          note={events ? `${verified} verified against official sources` : "Not published yet"}
        />
        <Tile
          label="News coverage share"
          value={formatPercent(lastComplete?.coverage_share)}
          note={lastComplete ? `Share of GDELT-monitored articles, ${formatDate(lastComplete.date)}` : "No complete day yet"}
        />
      </div>

      <ChartCard
          title="Daily news coverage of GTA VI"
          sub="Share of all articles monitored by GDELT that mention GTA VI. Dashed lines mark events from the ledger."
          kind="derived"
          meta={{
            metric: "coverage share",
            unit: "% of monitored articles",
            range: rangeLabel(days[0]?.date, days.at(-1)?.date),
            geography: "Global (65 languages)",
            source: "GDELT DOC 2.0",
          }}
        >
          {days.some((d) => d.complete) ? (
            <LineChart
              points={coveragePoints(days)}
              seriesName="Coverage share"
              format="percent"
              events={eventMarkers(evs)}
              ariaLabel="Line chart of daily GTA VI news coverage share"
            />
          ) : (
            <EmptyState title="No news coverage data yet">
              Run <code>gta6 collect --source gdelt</code>, then <code>gta6 process --all</code> and{" "}
              <code>gta6 publish</code>. Days only appear once a snapshot covers the full UTC day.
            </EmptyState>
          )}
        </ChartCard>

      <div className="grid grid-2">
        <section className="card">
          <h2>Recent events</h2>
          <p className="sub">From the curated ledger. Unverified events come from press reports.</p>
          {evs.length ? (
            <table>
              <tbody>
                {[...evs].reverse().slice(0, 5).map((e) => (
                  <tr key={e.event_id}>
                    <td style={{ whiteSpace: "nowrap" }}>{formatDate(e.event_date)}</td>
                    <td>
                      {e.event_name}
                      <div className="muted" style={{ fontSize: 12 }}>{e.verification_status}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState title="No events published">Load the ledger with <code>gta6 collect --source event_ledger</code>.</EmptyState>
          )}
          <p style={{ marginTop: 10, fontSize: 13 }}>
            <Link href="/events/">All events →</Link>
          </p>
        </section>

        <section className="card">
          <h2>Data-quality warnings</h2>
          <p className="sub">Failed or partial runs, stale sources and quarantined records.</p>
          {!status ? (
            <EmptyState title="No status published">Run <code>gta6 publish</code>.</EmptyState>
          ) : warnings.length === 0 ? (
            <StatusLabel tone="good" label="No warnings" />
          ) : (
            <table>
              <tbody>
                {warnings.map((s) => (
                  <tr key={s.source_id}>
                    <td>{s.name}</td>
                    <td>
                      <StatusLabel
                        tone={s.last_run ? runTone(s.last_run.status) : "warning"}
                        label={s.last_run ? `last run ${s.last_run.status}` : "never run"}
                      />
                      <div className="muted" style={{ fontSize: 12 }}>
                        Last success: {formatDateTime(s.last_success_at)}
                        {s.quarantined_records ? ` · ${s.quarantined_records} quarantined` : ""}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <p style={{ marginTop: 10, fontSize: 13 }}>
            <Link href="/quality/">Data quality & sources →</Link>
          </p>
        </section>
      </div>
    </>
  );
}
