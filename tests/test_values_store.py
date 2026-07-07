from __future__ import annotations

import json
import random
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from values import (  # noqa: E402
    EDGES_OUT,
    SOURCE_TAG,
    VALUES_OUT,
    _dump_jsonl,
    normalize_edges,
    normalize_values,
    validate_store,
)

MANIFEST_PATH = ROOT / "knowledge" / "values" / "manifest.json"

# Fields that must live in exactly one of the two files.
CARD_ONLY = {"title", "summary", "detail", "attention_policies"}
EDGE_RANKING = {"wiser_value_id", "counts", "wiser_likelihood", "entropy"}


def _raw_fixture() -> dict:
    """A fully synthetic MAI-shaped export — no MAI content, safe to commit."""
    return {
        "values": [
            {
                "id": 2,
                "title": "Bravery",
                "instructionsShort": "short two",
                "instructionsDetailed": "detailed two",
                "evaluationCriteria": ["SIGNS of resolve"],
                "createdAt": "2026-01-02T00:00:00Z",
                "updatedAt": "2026-01-02T00:00:00Z",
            },
            {
                "id": 1,
                "title": "Care",
                "instructionsShort": "short one",
                "instructionsDetailed": "detailed one",
                "evaluationCriteria": ["UNDERSTANDING of need", "SIGNS of trust"],
                "createdAt": "2026-01-01T00:00:00Z",
                "updatedAt": "2026-01-01T00:00:00Z",
            },
        ],
        "edges": [
            {
                "sourceValueId": 1,
                "wiserValueId": 2,
                "contexts": ["When a choice is frightening"],
                "counts": {
                    "markedWiser": 5,
                    "markedNotWiser": 1,
                    "markedLessWise": 0,
                    "markedUnsure": 2,
                    "impressions": 8,
                },
                "summary": {"wiserLikelihood": 0.83, "entropy": 0.4},
            }
        ],
    }


class NormalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raw = _raw_fixture()

    def test_value_record_shape(self) -> None:
        values = normalize_values(self.raw)
        self.assertEqual(
            set(values[0]),
            {"id", "title", "summary", "detail", "attention_policies", "source"},
        )
        care = next(v for v in values if v["id"] == 1)
        self.assertEqual(care["summary"], "short one")
        self.assertEqual(care["detail"], "detailed one")
        self.assertEqual(care["attention_policies"], ["UNDERSTANDING of need", "SIGNS of trust"])
        self.assertEqual(care["source"], SOURCE_TAG)

    def test_edge_record_shape(self) -> None:
        edge = normalize_edges(self.raw)[0]
        self.assertEqual(
            set(edge),
            {
                "source_value_id",
                "wiser_value_id",
                "contexts",
                "counts",
                "wiser_likelihood",
                "entropy",
                "source",
            },
        )
        self.assertEqual(edge["wiser_likelihood"], 0.83)
        self.assertEqual(edge["entropy"], 0.4)
        self.assertEqual(edge["source"], SOURCE_TAG)

    def test_values_sorted_by_id(self) -> None:
        self.assertEqual([v["id"] for v in normalize_values(self.raw)], [1, 2])

    def test_normalization_is_reproducible_regardless_of_input_order(self) -> None:
        """Reproducibility: shuffling the raw arrays must not change the output."""
        canonical = (
            _dump_jsonl(normalize_values(self.raw)),
            _dump_jsonl(normalize_edges(self.raw)),
        )
        rng = random.Random(0)
        for _ in range(5):
            shuffled = {
                "values": rng.sample(self.raw["values"], len(self.raw["values"])),
                "edges": list(self.raw["edges"]),
            }
            self.assertEqual(
                (_dump_jsonl(normalize_values(shuffled)), _dump_jsonl(normalize_edges(shuffled))),
                canonical,
            )


class FirewallInvariantTests(unittest.TestCase):
    """validate_store must keep cards and edges from bleeding into each other."""

    def setUp(self) -> None:
        raw = _raw_fixture()
        self.values = normalize_values(raw)
        self.edges = normalize_edges(raw)

    def test_clean_store_is_valid(self) -> None:
        self.assertEqual(validate_store(self.values, self.edges), [])

    def test_card_carrying_ranking_field_is_rejected(self) -> None:
        self.values[0]["wiser_likelihood"] = 0.9
        errors = validate_store(self.values, self.edges)
        self.assertTrue(any("edge-only fields" in e for e in errors))

    def test_edge_carrying_card_text_is_rejected(self) -> None:
        self.edges[0]["title"] = "leaked title"
        errors = validate_store(self.values, self.edges)
        self.assertTrue(any("card-only fields" in e for e in errors))

    def test_edge_to_unknown_value_is_rejected(self) -> None:
        self.edges[0]["wiser_value_id"] = 999
        errors = validate_store(self.values, self.edges)
        self.assertTrue(any("does not resolve to a value" in e for e in errors))

    def test_self_edge_is_rejected(self) -> None:
        self.edges[0]["wiser_value_id"] = self.edges[0]["source_value_id"]
        errors = validate_store(self.values, self.edges)
        self.assertTrue(any("self-edge" in e for e in errors))

    def test_out_of_range_likelihood_is_rejected(self) -> None:
        self.edges[0]["wiser_likelihood"] = 1.5
        errors = validate_store(self.values, self.edges)
        self.assertTrue(any("outside [0, 1]" in e for e in errors))

    def test_duplicate_value_id_is_rejected(self) -> None:
        self.values.append(dict(self.values[0]))
        errors = validate_store(self.values, self.edges)
        self.assertTrue(any("duplicate value id" in e for e in errors))


class ManifestProvenanceTests(unittest.TestCase):
    """The committed manifest records provenance and mirrors the firewall."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_records_required_provenance(self) -> None:
        m = self.manifest
        self.assertIn("dft.meaningalignment.org", m["access"]["export_url"])
        self.assertRegex(m["revision"]["sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(m["revision"]["downloaded_at"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertIsInstance(m["license"]["status"], str)
        self.assertIsInstance(m["row_count"]["values"], int)
        self.assertIsInstance(m["row_count"]["edges"], int)

    def test_manifest_keeps_the_two_objects_distinct(self) -> None:
        cards = set(self.manifest["objects"]["value_cards"]["normalized_fields"])
        edges = set(self.manifest["objects"]["moral_graph_edges"]["normalized_fields"])
        # Card text must not be listed among edge fields, and the ranking must
        # not be listed among card fields.
        self.assertEqual(CARD_ONLY & edges, set())
        self.assertEqual(EDGE_RANKING & cards, set())

    def test_usage_records_internal_only_posture(self) -> None:
        self.assertEqual(self.manifest["usage"]["scope"], "internal use only")


@unittest.skipUnless(
    VALUES_OUT.exists() and EDGES_OUT.exists(),
    "normalized MAI data is gitignored; run scripts/values.py normalize to materialize it",
)
class RealCorpusTests(unittest.TestCase):
    """Guarded checks over the real normalized files when they are present."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.values = [json.loads(line) for line in VALUES_OUT.read_text().splitlines() if line.strip()]
        cls.edges = [json.loads(line) for line in EDGES_OUT.read_text().splitlines() if line.strip()]
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_real_store_satisfies_invariants(self) -> None:
        self.assertEqual(validate_store(self.values, self.edges), [])

    def test_counts_match_manifest(self) -> None:
        self.assertEqual(len(self.values), self.manifest["row_count"]["values"])
        self.assertEqual(len(self.edges), self.manifest["row_count"]["edges"])


if __name__ == "__main__":
    unittest.main()
