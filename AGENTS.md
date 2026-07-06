# Cosmology Lens — Agent Operating Contract

## Mission

Build an evidence-bearing system that analyzes text, extracts cosmological primitives, compares them with historically situated reference cosmologies, maps implied values to Meaning Alignment Institute (MAI) value cards, and reports calibrated uncertainty.

The seven-day target is a research prototype, not a universal or authoritative classifier. Prefer inspectable evidence, abstention, and honest uncertainty over forced labels.

## Truth sources

Read these in order at the start of every run:

1. `AGENTS.md` — operating rules.
2. `.agent/state.json` — canonical task and readiness state.
3. `reports/CURRENT_STATUS.md` — generated human overview.
4. The newest two files in `reports/runs/`, if any.
5. The files named by the selected task.

If prose and `.agent/state.json` disagree, verify reality and reconcile both during the same run. Never fix only the chat explanation.

## Required start sequence

Run:

```bash
python3 scripts/project.py validate
python3 scripts/project.py status --write
python3 scripts/project.py next
```

Then select exactly one unblocked task. Start it before editing:

```bash
python3 scripts/project.py start TASK_ID
```

Do not start a second task while another is `in_progress`, except to repair a framework failure that prevents the active task from proceeding.

## Execution loop

For the selected task:

1. Restate its deliverable and acceptance criteria internally.
2. Inspect only the files and evidence needed for that deliverable.
3. Make the smallest coherent implementation that advances acceptance.
4. Run the narrowest relevant check, then the broader project check.
5. Review once for evidence, regressions, and unsupported claims.
6. Complete or block the task and write a run report.
7. Regenerate `reports/CURRENT_STATUS.md`.

Every successful run must produce at least one of:

- a new or improved project artifact;
- a verified completed task;
- a concrete blocker containing evidence and the exact unblocking action.

## Anti-loop and forward-motion rules

- A check-only cycle is an inspection, audit, or test run that produces no artifact change, new evidence, task transition, or blocker.
- Allow at most **two consecutive check-only cycles** per run.
- After the second, implement the smallest reversible improvement or mark the task blocked with evidence.
- Spend no more than roughly 20% of a run assessing general quality before acting on the selected task.
- Once acceptance checks pass, perform at most one final review. Do not reopen the task without a new failed check, changed requirement, or user correction.
- Do not rewrite working artifacts merely to make them stylistically different.
- Do not expand scope to improve unrelated areas.
- When blocked externally, continue only with independent unblocked work if the active task can be safely blocked first.
- Three repeated attempts with the same failure and no new evidence require `blocked`, not a fourth retry.

## Task states

- `queued`: defined but waiting for dependencies or priority.
- `ready`: dependencies satisfied; eligible for work.
- `in_progress`: the sole active task.
- `blocked`: cannot advance without a named external change or decision.
- `done`: acceptance criteria verified and evidence recorded.

Do not mark work `done` because files exist. The task's `required_artifacts` must exist, its acceptance criteria must be checked, and its `completion_evidence` must explain what was verified.

## Readiness levels

Each workstream uses the rubric in `.agent/READINESS.md`:

0. Not started
1. Defined
2. Implemented
3. Verified
4. Pilot-ready
5. Production-ready

Readiness is not task completion percentage. Promote a workstream only when its gate is met and add evidence paths. Overall readiness is the lowest critical workstream readiness, not an average.

## Research and evidence rules

- Distinguish sourced fact, model inference, and project decision.
- Use primary or scholarly sources for cosmology-card claims. Wikidata may provide identifiers and links, not doctrinal authority.
- Scope traditions by school, period, geography, or lineage; never flatten a diverse religion into one timeless position.
- Preserve source URLs, titles, access dates, and relevant passages.
- Treat MAI value-card matches and moral-graph edges separately. Never invent graph relationships.
- Label uncertainty and contested claims explicitly.
- For current APIs, models, libraries, licenses, and hosted services, verify the current documentation before relying on them.

## Analysis product rules

The system must:

- separate author endorsement from quotation, criticism, reported speech, and fictional voices;
- extract claims with exact source spans;
- use `explicit`, `strongly_implied`, `weakly_implied`, or `unobserved` evidence strength;
- compare candidates primitive by primitive using `entails`, `compatible`, `unspecified`, `tension`, or `contradicts`;
- permit mixtures, novel cosmologies, and `insufficient evidence`;
- keep evidence coverage, candidate fit, and calibrated confidence as separate outputs;
- never present an uncalibrated model self-rating as probability;
- expose what evidence would most change the result.

## Verification order

Use the cheapest relevant checks first:

1. Schema or targeted unit test.
2. Component test.
3. `make check` for the full local verification suite.
4. Manual evidence review for claims that code cannot establish.

Tests must cover negation, quotation, multiple voices, sparse evidence, hybrid cosmologies, and out-of-distribution text—not only canonical examples.

## File ownership

- `.agent/state.json`: task status, dependencies, readiness, evidence.
- `reports/CURRENT_STATUS.md`: generated overview; do not hand-edit.
- `reports/runs/`: append-only run reports.
- `docs/`: durable product, methodology, architecture, and evaluation decisions.
- `knowledge/cosmologies/`: versioned cosmology cards and schema.
- `knowledge/values/`: MAI source manifests and normalized value data.
- `evals/`: reviewed evaluation cases and metrics.
- `apps/web/`: browser interface.
- `services/api/`: ingestion and analysis API.
- `DECISIONS.md`: consequential choices and reversals.

Avoid duplicating the same fact across files. Link to the owning file.

## Completion and reporting

Complete a task with:

```bash
python3 scripts/project.py complete TASK_ID \
  --summary "What now works and how it was checked" \
  --evidence path/to/artifact path/to/test
```

Block it with:

```bash
python3 scripts/project.py block TASK_ID \
  --reason "Specific cause; evidence; exact unblocking action"
```

For every substantive run, create `reports/runs/YYYY-MM-DD_HHMM_TASK_ID.md` from `.agent/RUN_REPORT_TEMPLATE.md`. Report:

- outcome first;
- changed artifacts;
- checks and results;
- readiness before and after;
- unresolved risks;
- exact next task.

Finish with:

```bash
make check
python3 scripts/project.py status --write
```

## Human review gates

Do not autonomously:

- claim scholarly authority for cosmology cards without review;
- promote calibration to validated status without held-out human labels;
- publish private submitted texts;
- recursively crawl websites;
- deploy publicly, incur paid API costs, or send data externally without authorization;
- describe the prototype as determining an author's actual beliefs.

The product analyzes the cosmological commitments represented in a selected text, not the private identity or definitive worldview of its author.
