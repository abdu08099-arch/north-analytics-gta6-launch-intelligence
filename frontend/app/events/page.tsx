import { ChartCard, EmptyState, PageHead } from "@/components/Cards";
import { LineChart } from "@/components/LineChart";
import { StatusLabel } from "@/components/Badges";
import { loadProducts } from "@/lib/data";
import { formatDate, formatDateTime } from "@/lib/format";
import { coveragePoints, docUrl, eventMarkers, rangeLabel } from "@/lib/view";

export default function EventsPage() {
  const { events, coverage } = loadProducts();
  const evs = events?.data ?? [];
  const days = coverage?.data ?? [];

  return (
    <>
      <PageHead title="Events">
        Official milestones from Rockstar and other official channels, curated by hand. An event is
        “verified” only when it links to an official source and a named reviewer has checked it.
      </PageHead>

      <ChartCard
        title="News coverage around events"
        sub="Descriptive only: coverage moving near an event does not show that the event caused it."
        kind="derived"
        meta={{
          metric: "coverage share",
          unit: "% of monitored articles",
          range: rangeLabel(days[0]?.date, days.at(-1)?.date),
          geography: "Global",
          source: "GDELT DOC 2.0; event ledger",
        }}
      >
        {days.some((d) => d.complete) ? (
          <LineChart
            points={coveragePoints(days)}
            seriesName="Coverage share"
            format="percent"
            events={eventMarkers(evs)}
            ariaLabel="News coverage share with event markers"
          />
        ) : (
          <EmptyState title="No coverage data to set events against yet">
            The event list below is available; the chart appears once GDELT data has been processed.
          </EmptyState>
        )}
      </ChartCard>

      <section className="card">
        <h2>Event ledger</h2>
        <p className="sub">
          Source file: <a href={docUrl("data/reference/event_milestones.csv")}>data/reference/event_milestones.csv</a>.
          Changes go through pull requests.
        </p>
        {evs.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Event</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                {evs.map((e) => (
                  <tr key={e.event_id}>
                    <td style={{ whiteSpace: "nowrap" }}>
                      {formatDate(e.event_date)}
                      {e.published_at ? <div className="muted" style={{ fontSize: 12 }}>{formatDateTime(e.published_at)}</div> : null}
                    </td>
                    <td>
                      {e.event_name}
                      <div className="muted" style={{ fontSize: 12 }}>{e.summary}</div>
                    </td>
                    <td>{e.event_type}</td>
                    <td>
                      <StatusLabel
                        tone={e.verification_status === "verified" ? "good" : e.verification_status === "disputed" ? "critical" : "warning"}
                        label={e.verification_status}
                      />
                    </td>
                    <td>
                      <a href={e.source_url} rel="noreferrer">
                        {e.source_kind === "official" ? "Official" : "Press"}
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState title="No events published">Run <code>gta6 collect --source event_ledger</code>, <code>gta6 process --all</code> and <code>gta6 publish</code>.</EmptyState>
        )}
        <p className="muted" style={{ fontSize: 12, marginTop: 10 }}>
          GTA VI Online launch date: not announced. It is added only when an official source confirms it.
        </p>
      </section>
    </>
  );
}
