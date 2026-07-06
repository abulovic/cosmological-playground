from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "knowledge" / "sources.json"


class SourceRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.sources = cls.registry["sources"]

    def test_ids_are_unique_and_stable_shaped(self) -> None:
        ids = [source["id"] for source in self.sources]
        self.assertEqual(len(ids), len(set(ids)))
        for source_id in ids:
            self.assertRegex(source_id, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    def test_public_records_are_website_ready(self) -> None:
        required = {
            "title",
            "creators",
            "year",
            "source_type",
            "publisher",
            "url",
            "accessed_at",
            "relevant_locators",
            "used_in",
            "review",
            "website",
        }
        for source in self.sources:
            with self.subTest(source=source["id"]):
                self.assertFalse(required - source.keys())
                self.assertEqual(urlparse(source["url"]).scheme, "https")
                self.assertRegex(source["accessed_at"], r"^\d{4}-\d{2}-\d{2}$")
                self.assertTrue(source["relevant_locators"])
                self.assertTrue(source["website"]["citation"])
                self.assertTrue(source["website"]["link_label"])
                for usage in source["used_in"]:
                    self.assertTrue((ROOT / usage["artifact"]).exists())

    def test_document_source_ids_resolve(self) -> None:
        registered = {source["id"] for source in self.sources}
        cited = set()
        for path in ROOT.glob("docs/*.md"):
            cited.update(re.findall(r"\[source:([a-z0-9-]+)\]", path.read_text()))
        self.assertTrue(cited)
        self.assertEqual(cited - registered, set())


if __name__ == "__main__":
    unittest.main()
