# Cosmology Lens

Cosmology Lens is a seven-day research prototype for analyzing the cosmological commitments represented in text. It extracts evidence into a shared primitive ontology, compares that evidence with historically scoped cosmology cards, maps implied values to available Meaning Alignment Institute resources, and reports uncertainty without forcing a single label.

## Repository operating system

The project is designed for continued agentic work without losing state or circling indefinitely around quality checks.

```bash
make check       # validate state and run local tests
make status      # regenerate the human-readable status report
make next        # show the active or next eligible task
```

Agents must follow `AGENTS.md`. Canonical progress lives in `.agent/state.json`; `reports/CURRENT_STATUS.md` is generated from it.

Research provenance lives in `knowledge/sources.json`. Its stable source IDs, review status, usage links, and display citations are the canonical input for the future website source interface; see `docs/SOURCE_PROVENANCE.md`.

## Local development

Prerequisites: Node.js 20+, npm 10+, and Python 3.11+.

```bash
cp .env.example .env
npm install
npm run web:dev
```

In a second terminal:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e 'services/api[dev]'
.venv/bin/uvicorn cosmology_api.main:app --reload --port 8000
```

The initial scaffold exposes the web shell at `http://localhost:3000` and API health at `http://localhost:8000/health`.

## Important limitations

- The system analyzes a selected text, not an author's private or definitive beliefs.
- A value-card similarity is not automatically a position in MAI's moral graph.
- Confidence remains provisional until calibrated on held-out human-reviewed examples.
- Cosmology cards require scholarly review before a public pilot.
