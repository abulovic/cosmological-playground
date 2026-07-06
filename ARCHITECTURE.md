# Architecture

```text
Next.js web client
       │
       ▼
FastAPI analysis service
       │
       ├── bounded ingestion: text / URL / PDF / DOCX
       ├── segmentation, voice, quotation, negation, stance
       ├── primitive extraction with exact spans
       ├── hybrid retrieval over cosmology claims and MAI cards
       ├── primitive-level comparison and ranking
       ├── confidence and abstention layer
       └── evidence-bearing report
               │
               ▼
       PostgreSQL + pgvector in deployment
       deterministic local fixtures in tests
```

## Boundaries

- The web client renders and submits; it does not own analysis truth.
- The API owns normalized schemas, evidence offsets, rankings, and exports.
- `knowledge/` owns versioned reference data and provenance.
- `evals/` owns reviewed cases and metric outputs.
- External model providers sit behind an adapter so prompts and models can be changed without rewriting domain logic.

## Reliability strategy

- Strict structured outputs at model boundaries.
- Deterministic validation after every model response.
- Exact source offsets preserved through normalization.
- Retrieval is candidate generation, never final classification.
- A verifier checks entailment and stance independently of initial extraction.
- Provider timeouts, retries, size limits, and budget caps are explicit.
- A keyword-only fallback keeps core retrieval testable without network access.
