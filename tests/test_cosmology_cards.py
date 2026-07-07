from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_cards import (  # noqa: E402
    CARDS_DIR,
    MANIFEST_PATH,
    SCHEMA_PATH,
    validate,
    validate_card,
    validate_manifest,
)

EXPECTED_CARDS = {
    "scientific-naturalism",
    "christian-classical-theism",
    "buddhist-madhyamaka",
}


def _minimal_valid_card() -> dict:
    return {
        "id": "test-card",
        "label": "Test card",
        "version": "0.1.0",
        "scope": {
            "tradition": "Test tradition",
            "school": None,
            "period": "test period",
            "region": "test region",
            "limitations": ["fixture only"],
        },
        "claims": [
            {
                "primitive": "ultimate_reality",
                "claim": "A fixture claim long enough to pass.",
                "source_ids": ["src-1"],
                "contested": False,
                "confidence": "low",
            }
        ],
        "sources": [
            {
                "id": "src-1",
                "title": "Fixture source",
                "author": None,
                "url": "https://example.org/fixture",
                "source_type": "other",
                "accessed_at": "2026-07-06",
                "passage": None,
            }
        ],
        "review": {"status": "draft", "reviewer": None, "reviewed_at": None},
    }


class CardCorpusTests(unittest.TestCase):
    """The D1-002 acceptance checks over the real card files."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.cards = {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(CARDS_DIR.glob("*.json"))
        }
        cls.primitives = set(
            cls.schema["properties"]["claims"]["items"]["properties"]["primitive"]["enum"]
        )

    def test_expected_contrasting_cards_exist(self) -> None:
        self.assertTrue(EXPECTED_CARDS <= set(self.cards))

    def test_all_cards_validate_against_schema(self) -> None:
        for name, card in self.cards.items():
            with self.subTest(card=name):
                self.assertEqual(validate_card(card, self.schema), [])

    def test_card_ids_match_filenames(self) -> None:
        for name, card in self.cards.items():
            with self.subTest(card=name):
                self.assertEqual(card["id"], name)

    def test_claims_carry_provenance_and_scope_notes(self) -> None:
        for name, card in self.cards.items():
            with self.subTest(card=name):
                self.assertTrue(card["scope"]["limitations"])
                source_ids = {source["id"] for source in card["sources"]}
                for claim in card["claims"]:
                    self.assertTrue(claim["source_ids"])
                    self.assertTrue(set(claim["source_ids"]) <= source_ids)
                for source in card["sources"]:
                    self.assertTrue(source["url"].startswith("https://"))
                    self.assertRegex(source["accessed_at"], r"^\d{4}-\d{2}-\d{2}$")

    def test_contested_claims_are_representable_and_present(self) -> None:
        for name, card in self.cards.items():
            with self.subTest(card=name):
                self.assertTrue(any(claim["contested"] for claim in card["claims"]))

    def test_absent_claims_are_representable(self) -> None:
        """A card may leave primitives unclaimed and still validate; absence
        is representable as omission, documented in scope limitations."""
        cards_with_absences = 0
        claimed_union: set[str] = set()
        for name, card in self.cards.items():
            claimed = {claim["primitive"] for claim in card["claims"]}
            claimed_union |= claimed
            if claimed < self.primitives:
                cards_with_absences += 1
                with self.subTest(card=name):
                    self.assertEqual(validate_card(card, self.schema), [])
        self.assertGreaterEqual(cards_with_absences, 2)
        self.assertEqual(claimed_union, self.primitives)

    def test_related_cards_resolve(self) -> None:
        for name, card in self.cards.items():
            for related in card.get("related_cards", []):
                with self.subTest(card=name, related=related):
                    self.assertIn(related, self.cards)

    def test_drafts_are_marked_as_drafts(self) -> None:
        """Human-review gate: unreviewed cards must not claim review status."""
        for name, card in self.cards.items():
            with self.subTest(card=name):
                if card["review"]["reviewer"] is None:
                    self.assertEqual(card["review"]["status"], "draft")


class ManifestTests(unittest.TestCase):
    """The D2-001 manifest must track the curated corpus and review flags."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.cards = {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(CARDS_DIR.glob("*.json"))
        }

    def test_manifest_is_consistent_with_card_files(self) -> None:
        self.assertEqual(validate_manifest(self.manifest, self.cards), [])

    def test_manifest_lists_exactly_the_card_files(self) -> None:
        listed = {entry["id"] for entry in self.manifest["cards"]}
        self.assertEqual(listed, set(self.cards))

    def test_unreviewed_cards_are_flagged_review_needed(self) -> None:
        for entry in self.manifest["cards"]:
            card = self.cards[entry["id"]]
            with self.subTest(card=entry["id"]):
                if card["review"]["status"] != "domain_reviewed":
                    self.assertTrue(entry["review_needed"])

    def test_roster_meets_target_count(self) -> None:
        curated = {entry["id"] for entry in self.manifest["cards"]}
        planned = {entry["id"] for entry in self.manifest["planned"]}
        self.assertEqual(planned & curated, set())
        self.assertGreaterEqual(
            len(curated | planned), self.manifest["target_count"]
        )

    def test_manifest_validator_rejects_unflagged_draft(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["cards"][0]["review_needed"] = False
        errors = validate_manifest(manifest, self.cards)
        self.assertTrue(any("review_needed" in error for error in errors))

    def test_manifest_validator_rejects_missing_card(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["cards"] = manifest["cards"][1:]
        errors = validate_manifest(manifest, self.cards)
        self.assertTrue(any("missing from manifest" in error for error in errors))


class ValidatorNegativeFixtureTests(unittest.TestCase):
    """The validator must reject malformed cards, not merely accept good ones."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def setUp(self) -> None:
        self.card = _minimal_valid_card()

    def assert_invalid(self, fragment: str) -> None:
        errors = validate_card(self.card, self.schema)
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected an error mentioning {fragment!r}, got {errors}",
        )

    def test_fixture_baseline_is_valid(self) -> None:
        self.assertEqual(validate_card(self.card, self.schema), [])

    def test_missing_required_root_property(self) -> None:
        del self.card["review"]
        self.assert_invalid("review")

    def test_unknown_root_property_rejected(self) -> None:
        self.card["extra"] = "not allowed"
        self.assert_invalid("unknown property")

    def test_unknown_primitive_rejected(self) -> None:
        self.card["claims"][0]["primitive"] = "vibes"
        self.assert_invalid("is not one of")

    def test_empty_source_ids_rejected(self) -> None:
        self.card["claims"][0]["source_ids"] = []
        self.assert_invalid("minItems")

    def test_dangling_source_id_rejected(self) -> None:
        self.card["claims"][0]["source_ids"] = ["missing-source"]
        self.assert_invalid("does not resolve")

    def test_duplicate_source_ids_rejected(self) -> None:
        self.card["sources"].append(dict(self.card["sources"][0]))
        self.assert_invalid("duplicate source id")

    def test_short_claim_rejected(self) -> None:
        self.card["claims"][0]["claim"] = "too short"
        self.assert_invalid("minLength")

    def test_bad_confidence_rejected(self) -> None:
        self.card["claims"][0]["confidence"] = "certain"
        self.assert_invalid("is not one of")

    def test_bad_card_id_pattern_rejected(self) -> None:
        self.card["id"] = "Not A Slug"
        self.assert_invalid("pattern")

    def test_bad_date_rejected(self) -> None:
        self.card["sources"][0]["accessed_at"] = "06/07/2026"
        self.assert_invalid("not a valid date")

    def test_bad_url_rejected(self) -> None:
        self.card["sources"][0]["url"] = "example.org/no-scheme"
        self.assert_invalid("not a valid absolute URI")

    def test_non_boolean_contested_rejected(self) -> None:
        self.card["claims"][0]["contested"] = "no"
        self.assert_invalid("expected type boolean")

    def test_nullable_fields_accept_null_but_not_wrong_types(self) -> None:
        self.assertEqual(validate(None, {"type": ["string", "null"]}), [])
        self.assertTrue(validate(None, {"type": "string"}))

    def test_missing_scope_limitations_rejected(self) -> None:
        del self.card["scope"]["limitations"]
        self.assert_invalid("limitations")

    def test_empty_claims_rejected(self) -> None:
        self.card["claims"] = []
        self.assert_invalid("minItems")

    def test_wrongly_nested_claim_reported_with_path(self) -> None:
        self.card["claims"][0]["notes"] = 42
        errors = validate_card(self.card, self.schema)
        self.assertTrue(any("$.claims[0].notes" in error for error in errors))

    def test_deep_copy_of_valid_card_stays_valid(self) -> None:
        self.assertEqual(validate_card(copy.deepcopy(self.card), self.schema), [])


if __name__ == "__main__":
    unittest.main()
