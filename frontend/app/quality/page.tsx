import { runTone, sourceTone, StatusLabel } from "@/components/Badges";
import { EmptyState, PageHead } from "@/components/Cards";
import { loadProducts } from "@/lib/data";
import { formatDateTime, formatInt, freshness } from "@/lib/format";
import { docUrl } from "@/lib/view";

export default function QualityPage() {
  const { status } = loadProducts();
  const now = new Date();
  return (
    <>
      <PageHead title="Data Quality & Sources">
        Every source, whether it may be collected, when it last succeeded, and how much was rejected.
        Failed runs are shown, never hidden.
      </PageHead>
      <section className="card">
        <h2>Sources and connector status</h2>
        <p className="sub">
          Status as of {status ? formatDateTime(status.generated_at) : "—"}. A source is stale when its
          last success is more than 36 hours old.
        </p>
        {status ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Source</th>
                  <th>Status</th>
                  <th>Last run</th>
                  <th>Last success</th>
                  <th className="num">Raw files</th>
                  <th className="num">Processed / partial / failed</th>
                  <th className="num">Quarantined</th>
                </tr>
              </thead>
              <tbody>
                {status.data.map((s) => {
                  const f = s.connector_available ? freshness(s.last_success_at, now) : null;
                  return (
                    <tr key={s.source_id}>
                      <td>
                        {s.name}
                        <div className="muted" style={{ fontSize: 12 }}>{s.notes}</div>
                      </td>
                      <td>
                        <StatusLabel tone={sourceTone(s.status)} label={s.status} />
                      </td>
                      <td>
                        {s.last_run ? (
                          <>
                            <StatusLabel tone={runTone(s.last_run.status)} label={s.last_run.status} />
                            <div className="muted" style={{ fontSize: 12 }}>{formatDateTime(s.last_run.started_at)}</div>
                            {s.last_run.error ? <div className="muted" style={{ fontSize: 12 }}>{s.last_run.error}</div> : null}
                          </>
                        ) : (
                          <span className="muted">never</span>
                        )}
                      </td>
                      <td>
                        {formatDateTime(s.last_success_at)}
                        {f === "stale" ? <div><StatusLabel tone="warning" label="stale" /></div> : null}
                      </td>
                      <td className="num">{formatInt(s.raw_artifacts)}</td>
                      <td className="num">
                        {formatInt(s.processing.processed ?? 0)} / {formatInt(s.processing.partial ?? 0)} / {formatInt(s.processing.failed ?? 0)}
                      </td>
                      <td className="num">{formatInt(s.quarantined_records)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState title="No status published yet">
            Run <code>gta6 publish</code> after a collection run.
          </EmptyState>
        )}
        <p className="muted" style={{ fontSize: 12, marginTop: 10 }}>
          Terms, quotas and costs per source: <a href={docUrl("docs/data/source-register.md")}>source register</a>.
        </p>
      </section>
    </>
  );
}
