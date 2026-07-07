from __future__ import annotations

import re
import sys
import unittest
from dataclasses import replace
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = ROOT / "docs" / "CONFIDENCE_AND_RANKING.md"

from cosmology_api.confidence import (  # noqa: E402
    CALIBRATION_CALIBRATED,
    CALIBRATION_UNCALIBRATED,
    GATE_OUTCOMES,
    HEURISTIC_BANDS,
    INSUFFICIENT_EVIDENCE,
    NO_GOOD_REFERENCE_MATCH,
    PROCEED,
    AbstentionConfig,
    AnalysisSignals,
    evaluate_abstention,
    heuristic_confidence_band,
)


def clean_signals(**overrides) -> AnalysisSignals:
    base = AnalysisSignals(
        evidence_coverage=0.8,
        top_fit=0.8,
        second_fit=0.5,
        unresolved_contradictions=0,
        verifier_disagreement=0.0,
        out_of_distribution=False,
    )
    return replace(base, **overrides)


class AbstentionGateTests(unittest.TestCase):
    def assert_fires(self, signals: AnalysisSignals, gate: str, config=None) -> None:
        decision = evaluate_abstention(signals, config)
        self.assertIn(gate, decision.fired_gates)

    def assert_passes(self, signals: AnalysisSignals, gate: str, config=None) -> None:
        decision = evaluate_abstention(signals, config)
        self.assertNotIn(gate, decision.fired_gates)

    def test_clean_signals_proceed(self) -> None:
        decision = evaluate_abstention(clean_signals())
        self.assertEqual(decision.outcome, PROCEED)
        self.assertEqual(decision.fired_gates, ())

    def test_coverage_floor_boundary(self) -> None:
        self.assert_passes(clean_signals(evidence_coverage=0.25), "coverage_floor")
        self.assert_fires(clean_signals(evidence_coverage=0.2499), "coverage_floor")

    def test_disagreement_ceiling_boundary(self) -> None:
        self.assert_passes(clean_signals(verifier_disagreement=0.34), "verifier_disagreement")
        self.assert_fires(clean_signals(verifier_disagreement=0.3401), "verifier_disagreement")

    def test_out_of_distribution_flag(self) -> None:
        self.assert_passes(clean_signals(), "out_of_distribution")
        self.assert_fires(clean_signals(out_of_distribution=True), "out_of_distribution")

    def test_fit_floor_boundary(self) -> None:
        self.assert_passes(clean_signals(top_fit=0.35, second_fit=0.1), "fit_floor")
        self.assert_fires(clean_signals(top_fit=0.3499, second_fit=0.1), "fit_floor")

    def test_no_candidates_fires_fit_floor(self) -> None:
        self.assert_fires(clean_signals(top_fit=None, second_fit=None), "fit_floor")

    def test_margin_floor(self) -> None:
        self.assert_fires(clean_signals(top_fit=0.5, second_fit=0.45), "margin_floor")
        self.assert_passes(clean_signals(top_fit=0.7, second_fit=0.5), "margin_floor")

    def test_margin_floor_exact_boundary_passes(self) -> None:
        # Binary-exact values so equality at the threshold is representable.
        config = AbstentionConfig(margin_floor=0.25)
        self.assert_passes(clean_signals(top_fit=0.75, second_fit=0.5), "margin_floor", config)
        self.assert_fires(clean_signals(top_fit=0.75, second_fit=0.5625), "margin_floor", config)

    def test_margin_gate_needs_two_candidates(self) -> None:
        self.assert_passes(clean_signals(top_fit=0.8, second_fit=None), "margin_floor")

    def test_contradiction_limit_boundary(self) -> None:
        self.assert_passes(clean_signals(unresolved_contradictions=0), "contradiction_block")
        self.assert_fires(clean_signals(unresolved_contradictions=1), "contradiction_block")

    def test_insufficient_evidence_takes_precedence(self) -> None:
        decision = evaluate_abstention(
            clean_signals(evidence_coverage=0.1, top_fit=0.1, second_fit=None)
        )
        self.assertEqual(decision.outcome, INSUFFICIENT_EVIDENCE)
        self.assertIn("coverage_floor", decision.fired_gates)
        self.assertIn("fit_floor", decision.fired_gates)

    def test_match_gates_alone_yield_no_good_match(self) -> None:
        decision = evaluate_abstention(clean_signals(top_fit=0.3, second_fit=0.1))
        self.assertEqual(decision.outcome, NO_GOOD_REFERENCE_MATCH)
        self.assertEqual(decision.fired_gates, ("fit_floor",))

    def test_all_gates_evaluated_without_short_circuit(self) -> None:
        decision = evaluate_abstention(
            AnalysisSignals(
                evidence_coverage=0.0,
                top_fit=0.0,
                second_fit=0.0,
                unresolved_contradictions=5,
                verifier_disagreement=1.0,
                out_of_distribution=True,
            )
        )
        self.assertEqual(set(decision.fired_gates), set(GATE_OUTCOMES))

    def test_decisions_are_provisional_by_default(self) -> None:
        self.assertTrue(evaluate_abstention(clean_signals()).thresholds_provisional)


class ProvisionalConfidenceTests(unittest.TestCase):
    def test_heuristic_band_values(self) -> None:
        self.assertEqual(heuristic_confidence_band(0.8, 0.8), "high")
        self.assertEqual(heuristic_confidence_band(0.5, 0.6), "medium")
        self.assertEqual(heuristic_confidence_band(0.2, 0.9), "low")
        self.assertEqual(heuristic_confidence_band(0.9, 0.2), "low")
        for band in (
            heuristic_confidence_band(c / 10, f / 10) for c in range(11) for f in range(11)
        ):
            self.assertIn(band, HEURISTIC_BANDS)

    def test_calibration_status_vocabulary(self) -> None:
        self.assertEqual(CALIBRATION_UNCALIBRATED, "uncalibrated")
        self.assertEqual(CALIBRATION_CALIBRATED, "calibrated")


class DocCodeConsistencyTests(unittest.TestCase):
    """The frozen contract document and the implementation must agree."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = CONTRACT_PATH.read_text(encoding="utf-8")
        cls.doc_gates = {
            match[0]: (match[1], match[2])
            for match in re.findall(
                r"^\| `([a-z_]+)` \| .+ \| (\S+) \| `([a-z_]+)` \|$",
                cls.contract,
                flags=re.MULTILINE,
            )
        }

    def test_documented_gates_match_code(self) -> None:
        self.assertEqual(set(self.doc_gates), set(GATE_OUTCOMES))
        for gate, (_, outcome) in self.doc_gates.items():
            with self.subTest(gate=gate):
                self.assertEqual(outcome, GATE_OUTCOMES[gate])

    def test_documented_defaults_match_config(self) -> None:
        config = AbstentionConfig()
        expected = {
            "coverage_floor": config.coverage_floor,
            "verifier_disagreement": config.disagreement_ceiling,
            "fit_floor": config.fit_floor,
            "margin_floor": config.margin_floor,
            "contradiction_block": config.contradiction_limit,
            "out_of_distribution": "true",
        }
        for gate, (default, _) in self.doc_gates.items():
            with self.subTest(gate=gate):
                if isinstance(expected[gate], str):
                    self.assertEqual(default, expected[gate])
                else:
                    self.assertEqual(float(default), float(expected[gate]))

    def test_contract_freezes_key_language(self) -> None:
        for required in (
            "provisional — uncalibrated",
            "`uncalibrated`",
            "`calibrated_confidence`",
            "`evidence_coverage`",
            "`candidate_fit`",
            "No model-generated self-rating is ever a calibrated probability",
        ):
            self.assertIn(required, self.contract)
        for relation in ("entails", "compatible", "unspecified", "tension", "contradicts"):
            self.assertIn(f"`{relation}`", self.contract)
        for band in HEURISTIC_BANDS:
            self.assertIn(f"`{band}`", self.contract)

    def test_outcome_vocabulary_is_documented(self) -> None:
        for outcome in (INSUFFICIENT_EVIDENCE, NO_GOOD_REFERENCE_MATCH, PROCEED):
            self.assertIn(f"`{outcome}`", self.contract)


if __name__ == "__main__":
    unittest.main()
