import { EmptyState, PageHead } from "@/components/Cards";
import { KindBadge } from "@/components/Badges";
import { docUrl } from "@/lib/view";

export default function ModelsPage() {
  return (
    <>
      <PageHead title="Forecasting & Models">
        Short-term forecasts of public interest, always compared with simple baselines and evaluated on
        data the model has not seen. Forecasts are estimates, not facts.
      </PageHead>
      <EmptyState title="No forecasts yet">
        A forecast needs enough history to test honestly. The plan: naive and seasonal-naive baselines
        first, evaluated with rolling-origin backtests (MAE, RMSE, MASE), and only then more complex models.
        This page will show each model's target, horizon, backtest results and prediction intervals.
      </EmptyState>
      <section className="card">
        <h2>How predictions will be shown</h2>
        <p className="sub">
          Predictions get their own label and dashed styling so they can never be mistaken for observed
          data: <KindBadge kind="predicted" /> vs <KindBadge kind="observed" />.
        </p>
        <p className="muted" style={{ fontSize: 13 }}>
          Standards: <a href={docUrl("PRD.md")}>PRD F7</a> · model cards in <code>docs/model-cards/</code>.
        </p>
      </section>
    </>
  );
}
