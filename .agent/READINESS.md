# Readiness rubric

Readiness is evidence-based and must not be inferred from optimism or task count.

| Level | Name | Required evidence |
|---:|---|---|
| 0 | Not started | No usable artifact exists. |
| 1 | Defined | Scope, contract, owner, dependencies, and acceptance criteria exist. |
| 2 | Implemented | The core path works on at least one representative fixture. Known gaps are recorded. |
| 3 | Verified | Automated checks pass and representative edge cases have been manually reviewed. |
| 4 | Pilot-ready | A user can complete the workflow; provenance, abstention, privacy, and recovery behavior are visible; pilot limitations are documented. |
| 5 | Production-ready | Operational monitoring, security review, backups, cost limits, incident recovery, representative calibration, and sustained real-world evaluation exist. |

## Promotion rules

- Record evidence paths for every promotion.
- A failing gate caps readiness even if later-stage features exist.
- `Pilot-ready` requires human review of the relevant knowledge and evaluation artifacts.
- `Production-ready` is outside the seven-day prototype unless explicitly resourced.
- Overall readiness equals the minimum level among critical workstreams.

## Critical workstreams

The default critical workstreams are:

- research framework
- reference knowledge base
- ingestion and stance extraction
- comparison and ranking
- values integration
- confidence and evaluation
- web experience
- operations and safety
