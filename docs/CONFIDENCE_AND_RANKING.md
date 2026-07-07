# Confidence and ranking — version 1 contract

Status: **frozen for prototype implementation**
Version: `1.0.0`
Frozen: 2026-07-06
Owner: confidence and evaluation
Calibration status: **all thresholds and weights are provisional until D6-002 calibrates them against a held-out human-reviewed split**

## Purpose and scope

This contract fixes the semantics of the system's three confidence-related outputs, the primitive-comparison vocabulary, and the abstention policy, so that downstream implementation (D4-001, D4-002), interface work (D5-001), and evaluation (D6-002) build against one stable meaning. It freezes *what the quantities mean and when the system must abstain*, not the numeric threshold values, which remain configuration.

## Three separate outputs

The analysis report always carries three distinct quantities. They must never be merged into a single number, and no one of them may be presented as if it were another.

1. **Evidence coverage** (`evidence_coverage`, range 0–1): the weighted share of the twelve primitives for which the text supplies usable evidence — a claim at strength `explicit`, `strongly_implied`, or `weakly_implied` from a voice whose stance makes it attributable. Primitive weights are discriminativeness configuration (default: uniform). Coverage describes *how much the text says*, not whether it matches anything.
2. **Candidate fit** (`candidate_fit`, range −1 to 1, per candidate): the compatibility of the extracted evidence with one reference cosmology, aggregated primitive by primitive as specified below. Fit describes *how well a candidate matches what was said*, independent of how much was said.
3. **Calibrated confidence** (`calibrated_confidence`, range 0–1 or null): the observed correctness frequency for comparable cases on held-out, human-reviewed data. Until D6-002 produces that data, this field is `null` and `calibration_status` is `uncalibrated`. No model-generated self-rating is ever a calibrated probability.

## Primitive comparison and fit aggregation

Each candidate-card claim is compared with the extracted evidence for the same primitive using exactly one of:

- `entails`
- `compatible`
- `unspecified`
- `tension`
- `contradicts`

Raw fit aggregates, over primitives with a non-`unspecified` comparison, the product of:

- **relation score** (provisional defaults: `entails` +1.0, `compatible` +0.5, `tension` −0.5, `contradicts` −1.0);
- **evidence-strength weight** (provisional defaults: `explicit` 1.0, `strongly_implied` 0.7, `weakly_implied` 0.35; `unobserved` contributes nothing);
- **stance weight** (provisional defaults: `endorsed` 1.0, `unclear` 0.25; `quoted`, `reported`, `criticized`, and `fictional` contribute 0 to author-level fit — voice-scoped analyses aggregate per voice);
- **primitive discriminativeness weight** (default: uniform),

normalized by the total applicable weight. `unspecified` pairs are excluded from fit and reported separately, following the primitives contract: absence of a card claim from the text is `unspecified`, not `contradicts`.

The report must retain every component (per-primitive relation, strength, stance, weights) so any aggregate score can be audited. Relation scores and weights are provisional configuration, not frozen truths.

## Abstention policy

The system returns an abstention outcome instead of a single-card result when any gate fires. Gates are evaluated exhaustively (no short-circuit); the report lists every fired gate with the threshold values used.

| Gate | Fires when | Default | Outcome |
|---|---|---|---|
| `coverage_floor` | `evidence_coverage` < threshold | 0.25 | `insufficient_evidence` |
| `verifier_disagreement` | extraction/verifier disagreement rate > ceiling | 0.34 | `insufficient_evidence` |
| `out_of_distribution` | ingestion flags the text as out-of-distribution | true | `insufficient_evidence` |
| `fit_floor` | top `candidate_fit` < threshold, or there are no candidates | 0.35 | `no_good_reference_match` |
| `margin_floor` | `top_fit − second_fit` < threshold (two or more candidates) | 0.10 | `no_good_reference_match` |
| `contradiction_block` | unresolved strong contradictions with the top candidate ≥ limit | 1 | `no_good_reference_match` |

Boundary semantics are strict and testable: floors fire on values strictly below the threshold (a value equal to the threshold passes); the disagreement ceiling fires on values strictly above it; the contradiction limit fires at or above the limit.

Decision procedure, in order of precedence:

1. If any `insufficient_evidence` gate fired, the outcome is `insufficient_evidence` — the text does not say enough, regardless of fit.
2. Otherwise, if any `no_good_reference_match` gate fired, the outcome is `no_good_reference_match`.
3. Otherwise the outcome is `proceed`.

A `margin_floor` abstention should surface the indistinct top candidates as a possible mixture rather than forcing a single label. Threshold values are configuration and remain provisional until D6-002; changing a value is a configuration change, while adding, removing, or changing the meaning, boundary semantics, or outcome of a gate is a contract change.

## Provisional confidence visibility

- Every rendered confidence carries `calibration_status`: `uncalibrated` or `calibrated`.
- While `uncalibrated`, interfaces and exports must label the value **“provisional — uncalibrated”**, must not render it as a percentage or probability, and must not use the word “probability” for it.
- The only uncalibrated display form is a qualitative **heuristic band** (`low`, `medium`, `high`) derived from coverage and fit, explicitly labeled as a heuristic.
- What evidence would most change the result is reported alongside, per the operating contract.

## Calibration evaluation

Report top-1 accuracy, recall@3, Brier score, expected calibration error, abstention coverage, and selective accuracy. Results must be broken out for canonical, hybrid, quoted, negated, fictional, sparse, and out-of-distribution cases. The calibration split stays held out from prompt and threshold tuning.

## Reference implementation

The frozen policy is implemented, dependency-free, in
`services/api/src/cosmology_api/confidence.py` and exercised by
`services/api/tests/test_confidence_policy.py`, which also asserts that the
gate ids, defaults, and outcomes in this document match the code.

## Freeze and change control

Version 1 freezes the three output meanings, the comparison relation set, the gate ids with their boundary semantics and outcome mapping, the decision precedence, and the provisional-visibility rules. Threshold and weight *values* are configuration. Any contract change requires an entry in `DECISIONS.md`, migration notes for dependent code and evaluation labels, and a version bump.
