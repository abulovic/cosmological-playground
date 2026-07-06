from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs" / "COSMOLOGY_PRIMITIVES.md"
CARD_SCHEMA_PATH = ROOT / "knowledge" / "cosmologies" / "card.schema.json"


class OntologyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = CONTRACT_PATH.read_text(encoding="utf-8")
        cls.card_schema = json.loads(CARD_SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_frozen_ids_match_card_schema(self) -> None:
        documented_ids = set(
            re.findall(
                r"^### [0-9]+[.] .*[(]`([a-z_]+)`[)]$",
                self.contract,
                flags=re.MULTILINE,
            )
        )
        schema_ids = set(
            self.card_schema["properties"]["claims"]["items"]["properties"]
            ["primitive"]["enum"]
        )
        self.assertEqual(documented_ids, schema_ids)
        self.assertEqual(len(documented_ids), 12)

    def test_each_primitive_has_a_counterexample(self) -> None:
        self.assertEqual(self.contract.count("**Counterexample:**"), 12)

    def test_evidence_states_and_values_boundary_are_explicit(self) -> None:
        for state in ("explicit", "strongly_implied", "weakly_implied", "unobserved"):
            self.assertIn(f"`{state}`", self.contract)
        self.assertIn("## Boundary between cosmology and values", self.contract)

    def test_scholarly_framework_comparison_is_present(self) -> None:
        for framework in ("Aerts, Apostel", "Kearney", "Smart"):
            self.assertIn(framework, self.contract)


if __name__ == "__main__":
    unittest.main()
