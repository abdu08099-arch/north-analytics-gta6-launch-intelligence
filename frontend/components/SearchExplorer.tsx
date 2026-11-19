"use client";

import { useMemo, useState } from "react";
import type { TrendsSnapshot } from "@/lib/types";
import { trendsCell } from "@/lib/format";
import { LineChart, type EventMarker } from "./LineChart";

/** Pick one Trends snapshot at a time: snapshots are scaled separately and never joined. */
export function SearchExplorer({ snapshots, events }: { snapshots: TrendsSnapshot[]; events: EventMarker[] }) {
  const geos = useMemo(() => [...new Set(snapshots.map((s) => s.geo))].sort(), [snapshots]);
  const [geo, setGeo] = useState(geos[0]);
  const forGeo = snapshots.filter((s) => s.geo === geo);
  const [snapId, setSnapId] = useState<string | undefined>(forGeo[0]?.snapshot_id);
  const snap = forGeo.find((s) => s.snapshot_id === snapId) ?? forGeo[0];
  const series = snap?.series[0];

  return (
    <div>
      <div className="controls">
        <label>
          Geography
          <select
            value={geo}
            onChange={(e) => {
              setGeo(e.target.value);
              setSnapId(snapshots.find((s) => s.geo === e.target.value)?.snapshot_id);
            }}
          >
            {geos.map((g) => (
              <option key={g} value={g}>
                {g === "WW" ? "Worldwide" : g}
              </option>
            ))}
          </select>
        </label>
        <label>
          Snapshot (export)
          <select value={snap?.snapshot_id} onChange={(e) => setSnapId(e.target.value)}>
            {forGeo.map((s) => (
              <option key={s.snapshot_id} value={s.snapshot_id}>
                {s.exported_on ?? s.imported_at.slice(0, 10)} · {s.window} · {s.query_kind} {s.query}
              </option>
            ))}
          </select>
        </label>
      </div>
      {series ? (
        <>
          <LineChart
            points={series.points.map((p) => ({ x: p.t, y: p.value, note: trendsCell(p.value, p.flag) }))}
            seriesName={series.label}
            format="int"
            yMax={100}
            events={events}
            ariaLabel={`Google Trends relative interest, ${series.label}`}
          />
          <details className="table-view">
            <summary>Show as table</summary>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Period start (UTC)</th>
                    <th className="num">Interest (0–100)</th>
                  </tr>
                </thead>
                <tbody>
                  {series.points.map((p) => (
                    <tr key={p.t}>
                      <td>{p.t.replace("T00:00:00+00:00", "").replace("+00:00", " UTC")}</td>
                      <td className="num">{trendsCell(p.value, p.flag)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
          <p className="muted" style={{ fontSize: 12, marginTop: 8 }}>
            File: {snap.file} · granularity: {snap.granularity}. “&lt;1” means above zero but below 1;
            “missing” means Trends gave no value. Neither is drawn as 0.
          </p>
        </>
      ) : null}
    </div>
  );
}
