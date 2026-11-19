import { EmptyState, PageHead } from "@/components/Cards";
import { docUrl } from "@/lib/view";

export default function SentimentPage() {
  return (
    <>
      <PageHead title="Sentiment">
        Model-estimated tone of public text. Sentiment is an estimate for a sample, never population
        opinion.
      </PageHead>
      <EmptyState title="No sentiment results">
        Sentiment needs text we are allowed to store, plus a hand-labelled validation sample to report
        precision, recall and F1. Reddit is blocked, and YouTube and X are not enabled. GDELT article
        tone may serve as a first, clearly labelled media-tone measure. No model output is shown until it
        has been validated.
      </EmptyState>
      <p className="muted" style={{ fontSize: 13, marginTop: 12 }}>
        Rules: <a href={docUrl("PRD.md")}>PRD F8</a>.
      </p>
    </>
  );
}
