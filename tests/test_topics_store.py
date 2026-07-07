from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import topics  # noqa: E402

FIXTURE_FRONT = """---
id: {id}
title: {title}
type: {type}
primitives: [{primitives}]
related_cards: []
source_report: report.md
created: 2026-07-06
status: unreviewed
---

{body}
"""


def fake_embedder(texts: list[str]) -> list[list[float]]:
    """Deterministic toy embedder: 'cat' and 'feline' share a semantic axis."""
    vocabulary = {"cat": (1.0, 0.0), "feline": (1.0, 0.0), "rocket": (0.0, 1.0)}
    vectors = []
    for text in texts:
        x = y = 0.0
        for word in re.findall(r"[a-z]+", text.lower()):
            dx, dy = vocabulary.get(word, (0.0, 0.0))
            x, y = x + dx, y + dy
        vectors.append([x, y])
    return vectors


class FixtureStore(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.topics_dir = self.root / "topics"
        self.topics_dir.mkdir()
        self.db = self.root / "index.sqlite3"
        (self.root / "report.md").write_text("fixture report", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_topic(self, topic_id: str, body: str, *, type_: str = "concept",
                    primitives: str = "time", title: str | None = None) -> None:
        (self.topics_dir / f"{topic_id}.md").write_text(
            FIXTURE_FRONT.format(
                id=topic_id, title=title or topic_id, type=type_,
                primitives=primitives, body=body,
            ),
            encoding="utf-8",
        )

    def build(self, embedder=None) -> dict:
        return topics.build_index(
            topics_dir=self.topics_dir, db_path=self.db, root=self.root,
            embedder=embedder,
        )

    def test_keyword_fallback_returns_provenance(self) -> None:
        self.write_topic("feline-doc", "## Fur\n\nThe feline sat.\n\n## Purring\n\nPurring is a mystery.")
        self.write_topic("rocket-doc", "## Thrust\n\nThe rocket rose.")
        summary = self.build(embedder=None)
        self.assertEqual(summary, {"topics": 2, "chunks": 3, "embeddings": False})
        outcome = topics.search("purring mystery", db_path=self.db, embedder=None)
        self.assertIn("keyword-only fallback", outcome["mode"])
        hit = outcome["results"][0]
        self.assertEqual(hit["topic_id"], "feline-doc")
        self.assertEqual(hit["section"], "Purring")
        self.assertEqual(hit["source_report"], "report.md")
        self.assertEqual(hit["channels"], ["keyword"])

    def test_hybrid_finds_semantic_match_keyword_misses(self) -> None:
        self.write_topic("feline-doc", "## Fur\n\nThe feline sat on the mat.")
        self.write_topic("rocket-doc", "## Thrust\n\nThe rocket rose.")
        self.build(embedder=fake_embedder)
        outcome = topics.search("cat", db_path=self.db, embedder=fake_embedder)
        self.assertIn("hybrid", outcome["mode"])
        top = outcome["results"][0]
        self.assertEqual(top["topic_id"], "feline-doc")
        self.assertIn("embedding", top["channels"])

    def test_index_with_embeddings_still_searchable_without_them(self) -> None:
        self.write_topic("feline-doc", "## Fur\n\nThe feline sat on the mat.")
        self.build(embedder=fake_embedder)
        outcome = topics.search("feline", db_path=self.db, embedder=None)
        self.assertIn("keyword-only fallback", outcome["mode"])
        self.assertEqual(outcome["results"][0]["topic_id"], "feline-doc")

    def test_invalid_front_matter_is_rejected(self) -> None:
        self.write_topic("bad-type", "body", type_="essay")
        self.write_topic("bad-primitive", "body", primitives="karma_field")
        (self.topics_dir / "mismatched.md").write_text(
            FIXTURE_FRONT.format(
                id="other-name", title="x", type="concept", primitives="time", body="body",
            ),
            encoding="utf-8",
        )
        _, errors = topics.load_topics(self.topics_dir, self.root)
        text = "\n".join(errors)
        self.assertIn("bad-type.md", text)
        self.assertIn("karma_field", text)
        self.assertIn("mismatched.md", text)
        with self.assertRaises(topics.TopicError):
            self.build()

    def test_missing_source_report_is_rejected(self) -> None:
        (self.topics_dir / "orphan.md").write_text(
            FIXTURE_FRONT.format(
                id="orphan", title="x", type="concept", primitives="time", body="body",
            ).replace("report.md", "nonexistent.md"),
            encoding="utf-8",
        )
        _, errors = topics.load_topics(self.topics_dir, self.root)
        self.assertTrue(any("nonexistent.md" in error for error in errors))

    def test_chunking_splits_on_sections(self) -> None:
        chunks = topics.chunk_body("intro text\n\n## One\n\nalpha\n\n## Two\n\nbeta")
        self.assertEqual(
            chunks, [("(intro)", "intro text"), ("One", "alpha"), ("Two", "beta")]
        )


class SeedStore(unittest.TestCase):
    """The committed knowledge/topics content must stay valid and searchable."""

    def test_seed_topics_validate(self) -> None:
        loaded, errors = topics.load_topics()
        self.assertEqual(errors, [])
        self.assertGreaterEqual(len(loaded), 6)
        ids = [topic["meta"]["id"] for topic in loaded]
        self.assertEqual(len(ids), len(set(ids)))
        for topic in loaded:
            self.assertEqual(topic["meta"]["status"], "unreviewed")

    def test_seed_store_keyword_search(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "topics.sqlite3"
            topics.build_index(db_path=db, embedder=None)
            outcome = topics.search("floating beliefs deadbeat evict", db_path=db)
            top_ids = [hit["topic_id"] for hit in outcome["results"][:3]]
            self.assertIn("making-beliefs-pay-rent-findings", top_ids)


if __name__ == "__main__":
    unittest.main()
