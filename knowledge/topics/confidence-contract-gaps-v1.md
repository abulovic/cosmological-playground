---
id: confidence-contract-gaps-v1
title: Four contract gaps found by the first dry run
type: contract-note
primitives: []
related_cards: []
source_report: reports/dry-runs/2026-07-06_making-beliefs-pay-rent.md
created: 2026-07-06
status: unreviewed
---

## Gap 1 — rival non-exclusive answers

The relation vocabulary has no rule for two answers to the same primitive that
rival each other without excluding each other (floating beliefs versus
estrangement from God as the fundamental problem). Neither compatible nor
contradicts fits; annotators will diverge. See also two-truths-relation-gap for
the level-indexed variant of this problem.

## Gap 2 — per-claim versus per-primitive unspecified

The contracts do not say whether unspecified is assessed per card claim or per
primitive when a card has multiple claims under one primitive and the text
addresses only some. The Madhyamaka emptiness-of-emptiness claim forced a
per-claim reading in the dry run; this should be written down.

## Gap 3 — coverage is strength-blind

evidence_coverage counts a weakly_implied primitive the same as an explicit
one. Two texts with coverage 0.667 can differ enormously in evidential quality.
Candidate fix at calibration time (D6-002): strength-weighted coverage as a
diagnostic companion, never a silent replacement for the frozen definition.

## Gap 4 — verifier_disagreement lacks an operational definition

The abstention gate is frozen with threshold 0.34 but nothing defines what the
disagreement score measures (disagreement between which verifiers, over what
units, aggregated how). Must be defined before D4-001 can emit the signal.
