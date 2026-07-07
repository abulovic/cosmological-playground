"""Dependency-free validator for cosmology cards.

Implements exactly the JSON Schema subset used by
``knowledge/cosmologies/card.schema.json`` (draft 2020-12 keywords: type,
required, properties, additionalProperties, enum, pattern, minLength,
minItems, items), plus assertive checks for the ``date`` and ``uri``
formats, which draft 2020-12 treats as non-asserting annotations.

Beyond JSON Schema, ``validate_card`` enforces referential integrity the
schema cannot express: claim ``source_ids`` must resolve to the card's own
``sources``, and source ids must be unique within a card.

Usage:
    python3 scripts/validate_cards.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "knowledge" / "cosmologies" / "card.schema.json"
CARDS_DIR = ROOT / "knowledge" / "cosmologies" / "cards"
MANIFEST_PATH = ROOT / "knowledge" / "cosmologies" / "manifest.json"

_TYPE_CHECKS = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def _format_errors(value: str, fmt: str, path: str) -> list[str]:
    if fmt == "date":
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return [f"{path}: {value!r} is not a valid date (expected YYYY-MM-DD)"]
    elif fmt == "uri":
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            return [f"{path}: {value!r} is not a valid absolute URI"]
    return []


def validate(instance: object, schema: dict, path: str = "$") -> list[str]:
    """Return a list of human-readable errors; empty means valid."""
    errors: list[str] = []

    declared = schema.get("type")
    if declared is not None:
        allowed = declared if isinstance(declared, list) else [declared]
        if not any(_TYPE_CHECKS[t](instance) for t in allowed):
            got = "null" if instance is None else type(instance).__name__
            errors.append(f"{path}: expected type {'/'.join(allowed)}, got {got}")
            return errors

    if instance is None:
        # A null that passed the type check has no further constraints.
        return errors

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} is not one of {schema['enum']}")

    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} does not match pattern {schema['pattern']!r}")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "format" in schema:
            errors.extend(_format_errors(instance, schema["format"], path))

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"{path}: unknown property {key!r}")
        for key, subschema in properties.items():
            if key in instance:
                errors.extend(validate(instance[key], subschema, f"{path}.{key}"))

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems {schema['minItems']}")
        if "items" in schema:
            for index, item in enumerate(instance):
                errors.extend(validate(item, schema["items"], f"{path}[{index}]"))

    return errors


def validate_card(card: object, schema: dict) -> list[str]:
    """Schema validation plus card-level referential integrity."""
    errors = validate(card, schema)
    if errors:
        return errors

    source_ids = [source["id"] for source in card["sources"]]
    for source_id in sorted({s for s in source_ids if source_ids.count(s) > 1}):
        errors.append(f"$.sources: duplicate source id {source_id!r}")

    known = set(source_ids)
    for index, claim in enumerate(card["claims"]):
        for source_id in claim["source_ids"]:
            if source_id not in known:
                errors.append(
                    f"$.claims[{index}]: source_id {source_id!r} does not resolve "
                    "to an entry in this card's sources"
                )
    return errors


def validate_manifest(manifest: dict, cards: dict[str, dict]) -> list[str]:
    """The manifest must list exactly the card files, flag every card that
    still needs review, and keep the curated + planned roster at target size."""
    errors: list[str] = []

    entries = {entry["id"]: entry for entry in manifest.get("cards", [])}
    if set(entries) != set(cards):
        missing = sorted(set(cards) - set(entries))
        extra = sorted(set(entries) - set(cards))
        if missing:
            errors.append(f"manifest: card files missing from manifest: {missing}")
        if extra:
            errors.append(f"manifest: entries without card files: {extra}")

    for card_id, entry in sorted(entries.items()):
        card = cards.get(card_id)
        if card is None:
            continue
        review_status = card["review"]["status"]
        if entry.get("review_status") != review_status:
            errors.append(
                f"manifest: {card_id} review_status {entry.get('review_status')!r} "
                f"does not match card {review_status!r}"
            )
        review_needed = review_status != "domain_reviewed"
        if entry.get("review_needed") is not review_needed:
            errors.append(
                f"manifest: {card_id} review_needed must be {review_needed} "
                f"for review status {review_status!r}"
            )
        if entry.get("label") != card["label"]:
            errors.append(f"manifest: {card_id} label does not match card label")

    planned_ids = [entry["id"] for entry in manifest.get("planned", [])]
    overlap = sorted(set(planned_ids) & set(entries))
    if overlap:
        errors.append(f"manifest: planned entries already curated: {overlap}")
    if len(planned_ids) != len(set(planned_ids)):
        errors.append("manifest: duplicate planned ids")

    target = manifest.get("target_count", 0)
    roster = len(entries) + len(set(planned_ids) - set(entries))
    if roster < target:
        errors.append(f"manifest: roster lists {roster} cards, below target_count {target}")
    return errors


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    card_paths = sorted(CARDS_DIR.glob("*.json"))
    if not card_paths:
        print(f"No cards found in {CARDS_DIR}")
        return 1

    failures = 0
    cards: dict[str, dict] = {}
    for card_path in card_paths:
        card = json.loads(card_path.read_text(encoding="utf-8"))
        errors = validate_card(card, schema)
        if isinstance(card, dict) and card.get("id") != card_path.stem:
            errors.append(f"$.id: {card.get('id')!r} does not match filename {card_path.stem!r}")
        if errors:
            failures += 1
            print(f"FAIL {card_path.relative_to(ROOT)}")
            for error in errors:
                print(f"  {error}")
        else:
            cards[card_path.stem] = card
            print(f"ok   {card_path.relative_to(ROOT)}")

    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest_errors = validate_manifest(manifest, cards)
        if manifest_errors:
            failures += 1
            print(f"FAIL {MANIFEST_PATH.relative_to(ROOT)}")
            for error in manifest_errors:
                print(f"  {error}")
        else:
            print(f"ok   {MANIFEST_PATH.relative_to(ROOT)}")
    else:
        failures += 1
        print(f"FAIL {MANIFEST_PATH.relative_to(ROOT)}: manifest is missing")

    if failures:
        print(f"{failures} of {len(card_paths) + 1} checks failed.")
        return 1
    print(f"All {len(card_paths)} cards and the manifest validate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
