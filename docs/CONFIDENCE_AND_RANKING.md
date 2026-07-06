# Confidence and ranking — draft contract

Status: **defined, awaiting D1-003 verification**.

## Separate outputs

1. **Evidence coverage:** weighted share of primitives supported by usable text evidence.
2. **Candidate fit:** compatibility of that evidence with a reference cosmology.
3. **Calibrated confidence:** observed correctness frequency for comparable held-out cases.

No model-generated self-rating is a calibrated probability.

## Primitive comparison

Each candidate claim is compared with extracted evidence as:

- `entails`
- `compatible`
- `unspecified`
- `tension`
- `contradicts`

The raw fit is a weighted aggregation of comparison value, evidence strength, stance reliability, and primitive discriminativeness. The report must retain the components so the score can be audited.

## Abstention

Return `insufficient evidence` or `no good reference match` when any configured gate fails, including:

- evidence coverage below threshold;
- top fit below threshold;
- top-two margin too small;
- strong unresolved contradictions;
- extraction/verifier disagreement;
- out-of-distribution evidence.

Thresholds are configuration, not universal truths. They remain provisional until D6-002 calibrates them against a held-out human-reviewed split.

## Calibration evaluation

Report top-1 accuracy, recall@3, Brier score, expected calibration error, abstention coverage, and selective accuracy. Results must be broken out for canonical, hybrid, quoted, negated, fictional, sparse, and out-of-distribution cases.
