"""Frozen confidence semantics and abstention policy (D1-003).

Reference implementation of ``docs/CONFIDENCE_AND_RANKING.md`` v1.0.0.
Pure standard library so the policy is testable without API dependencies.

Threshold *values* in ``AbstentionConfig`` are provisional configuration,
uncalibrated until D6-002; gate ids, boundary semantics, outcome mapping,
and decision precedence are frozen contract.
"""

from __future__ import annotations

from dataclasses import dataclass

# Calibration status for any rendered confidence.
CALIBRATION_UNCALIBRATED = "uncalibrated"
CALIBRATION_CALIBRATED = "calibrated"

# Decision outcomes.
PROCEED = "proceed"
INSUFFICIENT_EVIDENCE = "insufficient_evidence"
NO_GOOD_REFERENCE_MATCH = "no_good_reference_match"

# Frozen gate ids and their outcome class.
GATE_OUTCOMES: dict[str, str] = {
    "coverage_floor": INSUFFICIENT_EVIDENCE,
    "verifier_disagreement": INSUFFICIENT_EVIDENCE,
    "out_of_distribution": INSUFFICIENT_EVIDENCE,
    "fit_floor": NO_GOOD_REFERENCE_MATCH,
    "margin_floor": NO_GOOD_REFERENCE_MATCH,
    "contradiction_block": NO_GOOD_REFERENCE_MATCH,
}

HEURISTIC_BANDS = ("low", "medium", "high")


@dataclass(frozen=True)
class AbstentionConfig:
    """Provisional thresholds; values are configuration, not frozen truths."""

    coverage_floor: float = 0.25
    disagreement_ceiling: float = 0.34
    fit_floor: float = 0.35
    margin_floor: float = 0.10
    contradiction_limit: int = 1
    thresholds_provisional: bool = True


@dataclass(frozen=True)
class AnalysisSignals:
    """Inputs to the abstention decision, produced by extraction and ranking."""

    evidence_coverage: float
    top_fit: float | None
    second_fit: float | None
    unresolved_contradictions: int
    verifier_disagreement: float
    out_of_distribution: bool


@dataclass(frozen=True)
class AbstentionDecision:
    outcome: str
    fired_gates: tuple[str, ...]
    thresholds_provisional: bool


def evaluate_abstention(
    signals: AnalysisSignals, config: AbstentionConfig | None = None
) -> AbstentionDecision:
    """Evaluate every gate (no short-circuit) and apply outcome precedence.

    Boundary semantics per contract: floors fire strictly below threshold,
    the disagreement ceiling fires strictly above, the contradiction limit
    fires at or above.
    """
    config = config or AbstentionConfig()
    fired: list[str] = []

    if signals.evidence_coverage < config.coverage_floor:
        fired.append("coverage_floor")
    if signals.verifier_disagreement > config.disagreement_ceiling:
        fired.append("verifier_disagreement")
    if signals.out_of_distribution:
        fired.append("out_of_distribution")
    if signals.top_fit is None or signals.top_fit < config.fit_floor:
        fired.append("fit_floor")
    if (
        signals.top_fit is not None
        and signals.second_fit is not None
        and signals.top_fit - signals.second_fit < config.margin_floor
    ):
        fired.append("margin_floor")
    if signals.unresolved_contradictions >= config.contradiction_limit:
        fired.append("contradiction_block")

    if any(GATE_OUTCOMES[gate] == INSUFFICIENT_EVIDENCE for gate in fired):
        outcome = INSUFFICIENT_EVIDENCE
    elif fired:
        outcome = NO_GOOD_REFERENCE_MATCH
    else:
        outcome = PROCEED
    return AbstentionDecision(
        outcome=outcome,
        fired_gates=tuple(fired),
        thresholds_provisional=config.thresholds_provisional,
    )


def heuristic_confidence_band(evidence_coverage: float, top_fit: float) -> str:
    """Qualitative uncalibrated display band. Never a probability.

    The only permitted uncalibrated confidence display; interfaces must
    label it "provisional — uncalibrated".
    """
    if evidence_coverage >= 0.6 and top_fit >= 0.7:
        return "high"
    if evidence_coverage >= 0.4 and top_fit >= 0.5:
        return "medium"
    return "low"
