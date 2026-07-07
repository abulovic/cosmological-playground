# Cosmology knowledge base

Cards are versioned, historically scoped reference objects. Each claim records its primitive, formulation, provenance, confidence, and contested status. Cards are comparison aids, not declarations that every member of a tradition believes the same thing.

`card.schema.json` is the structural contract. D1-002 validated it against three contrasting draft cards in `cards/`; D2-001 expands the reviewed set to at least 24.

Validate all cards with `python3 scripts/validate_cards.py` (also enforced by `tests/test_cosmology_cards.py`). Absent primitives are represented by omission and documented in `scope.limitations`; contested claims set `"contested": true`.

`manifest.json` tracks the curated corpus and the planned remainder of the 24-card roster; each curated entry carries a `review_needed` flag that must stay `true` until a card reaches `domain_reviewed`. The validator enforces manifest–card consistency.
