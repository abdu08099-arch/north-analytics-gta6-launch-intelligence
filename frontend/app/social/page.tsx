import { sourceTone, StatusLabel } from "@/components/Badges";
import { EmptyState, PageHead } from "@/components/Cards";
import { loadProducts } from "@/lib/data";
import { docUrl } from "@/lib/view";

const WHY: Record<string, string> = {
  youtube:
    "YouTube's API policies require stored data to be deleted or refreshed within 30 days and restrict derived metrics. That conflicts with a long-term time series, so no data is collected until the policy question is decided.",
  reddit:
    "Reddit stopped accepting new public Data API requests on 31 October 2026, and public access ends in March 2027. The project has no permitted access route, so Reddit is blocked. We do not scrape.",
  x: "The X API has no free tier. A daily counts-only request would cost under $1 a month, but any paid service needs the product owner's approval and a spend cap first.",
};

export default function SocialPage() {
  const { status } = loadProducts();
  const rows = (status?.data ?? []).filter((s) => ["youtube", "reddit", "x"].includes(s.source_id));

  return (
    <>
      <PageHead title="Social & Community">
        Public activity on video and social platforms. Platform samples never represent all players.
      </PageHead>
      <EmptyState title="No social or community data is collected yet">
        None of the three platforms below can be used under its current terms without a decision or
        approval. This page fills in once a source is enabled.
      </EmptyState>
      <div className="grid">
        {(rows.length ? rows : (["youtube", "reddit", "x"] as const).map((id) => ({ source_id: id, name: id, status: "planned" as const }))).map(
          (s) => (
            <section className="card" key={s.source_id}>
              <div className="chart-head">
                <h2>{s.name}</h2>
                <StatusLabel tone={sourceTone(s.status)} label={s.status} />
              </div>
              <p className="sub" style={{ marginTop: 6 }}>{WHY[s.source_id]}</p>
            </section>
          ),
        )}
      </div>
      <p className="muted" style={{ fontSize: 13, marginTop: 12 }}>
        Details: <a href={docUrl("docs/data/source-register.md")}>source register</a>.
      </p>
    </>
  );
}
