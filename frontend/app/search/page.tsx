import { ChartCard, EmptyState, PageHead } from "@/components/Cards";
import { SearchExplorer } from "@/components/SearchExplorer";
import { loadProducts } from "@/lib/data";
import { docUrl, eventMarkers } from "@/lib/view";

export default function SearchPage() {
  const { search, events } = loadProducts();
  const snapshots = search?.data ?? [];
  const first = snapshots.flatMap((s) => s.series.flatMap((x) => x.points)).map((p) => p.t).sort();

  return (
    <>
      <PageHead title="Search Intelligence">
        Google Trends relative search interest. 100 is the peak within one export; values from different
        exports or geographies are not comparable unless they come from the same comparison export.
      </PageHead>
      <ChartCard
        title="Relative search interest"
        sub="One export (snapshot) at a time. Exports are never joined into a single series."
        kind="observed"
        meta={{
          metric: "relative search interest",
          unit: "index 0–100 within the export",
          range: first.length ? `${first[0].slice(0, 10)} – ${first.at(-1)!.slice(0, 10)}` : "—",
          geography: "per export (see selector)",
          source: "Google Trends, manual CSV export",
        }}
      >
        {snapshots.length ? (
          <SearchExplorer snapshots={snapshots} events={eventMarkers(events?.data ?? [])} />
        ) : (
          <EmptyState title="No Google Trends exports imported yet">
            Trends data is exported by hand following the{" "}
            <a href={docUrl("docs/methodology/google-trends-protocol.md")}>export protocol</a>, then
            imported with <code>gta6 collect --source google_trends</code>. The official Trends API is
            alpha-only and needs an approved application.
          </EmptyState>
        )}
      </ChartCard>
    </>
  );
}
