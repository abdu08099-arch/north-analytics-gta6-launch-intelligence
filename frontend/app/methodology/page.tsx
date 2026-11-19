import { PageHead } from "@/components/Cards";
import { docUrl } from "@/lib/view";

export default function MethodologyPage() {
  return (
    <>
      <PageHead title="Methodology">Definitions, assumptions, attribution and limitations.</PageHead>
      <div className="prose">
        <p className="callout">
          This project measures public attention, not commercial results. Nothing here measures sales,
          revenue, players or market share.
        </p>

        <h2>What each number means</h2>
        <ul>
          <li>
            <b>Google Trends</b>: relative search interest, 0–100, scaled within one export. It is not search
            volume. Different exports are separate snapshots.
          </li>
          <li>
            <b>News coverage share</b>: articles mentioning GTA VI ÷ all articles GDELT monitored that day.
            It is media attention, not audience size or consumer demand.
          </li>
          <li>
            <b>Events</b>: hand-curated milestones. A change near an event is an association, not proof of
            cause.
          </li>
          <li>
            <b>Forecasts</b> (later): estimates with uncertainty, always shown next to simple baselines.
          </li>
        </ul>

        <h2>Data kinds</h2>
        <p>
          <b>Observed</b> values come straight from a source. <b>Derived</b> values are calculated from
          observed values with a documented method. <b>Predictions</b> are model outputs. Each chart is
          labelled with its kind.
        </p>

        <h2>Traceability</h2>
        <p>
          Every raw response is stored unchanged with a SHA-256 checksum. Every row in the database points
          to the file it came from, and records that fail validation are quarantined with a reason, never
          dropped silently. Missing values stay missing; they are never filled with zero.
        </p>

        <h2>Time</h2>
        <p>All timestamps are UTC. The observation period started on 19 November 2026, GTA VI's release day.</p>

        <h2>Limitations</h2>
        <ul>
          <li>Reddit is not available (public API closed to new applications in 2026).</li>
          <li>YouTube and X are not collected yet (policy and cost decisions pending).</li>
          <li>GDELT's set of monitored outlets changes over time; shares are more comparable than counts.</li>
          <li>Google Trends exports are manual, so a missed export is a gap.</li>
        </ul>

        <h2>Documents</h2>
        <ul>
          <li><a href={docUrl("docs/methodology/gdelt-news-coverage.md")}>GDELT news coverage method</a></li>
          <li><a href={docUrl("docs/methodology/google-trends-protocol.md")}>Google Trends export protocol</a></li>
          <li><a href={docUrl("docs/data/source-register.md")}>Source register</a></li>
          <li><a href={docUrl("docs/data/data-dictionary.md")}>Data dictionary</a></li>
          <li><a href={docUrl("PRD.md")}>Product requirements</a></li>
        </ul>

        <h2>Attribution</h2>
        <p>
          Search data: Google Trends (trends.google.com). News coverage: The GDELT Project
          (gdeltproject.org). GTA VI is a trademark of Take-Two Interactive; this is an independent
          project, not affiliated with Rockstar Games or Take-Two.
        </p>
      </div>
    </>
  );
}
