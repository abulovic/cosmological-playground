const stages = [
  "Extract cosmological primitives with source spans",
  "Compare historically scoped reference cosmologies",
  "Map implied values without inventing moral-graph edges",
  "Separate evidence coverage, fit, and calibrated confidence",
];

export default function Home() {
  return (
    <main>
      <p className="eyebrow">Seven-day research prototype</p>
      <h1>Cosmology Lens</h1>
      <p className="lede">
        Analyze the cosmological commitments represented in a text—while keeping
        every claim attached to evidence and every uncertainty visible.
      </p>
      <section>
        <h2>Analysis contract</h2>
        <ol>{stages.map((stage) => <li key={stage}>{stage}</li>)}</ol>
      </section>
      <p className="notice">The analysis workflow is scaffolded; implementation proceeds from the canonical project queue.</p>
    </main>
  );
}
