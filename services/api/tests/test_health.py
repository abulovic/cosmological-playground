from __future__ import annotations

import sys
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

try:
    from fastapi.testclient import TestClient
    from cosmology_api.main import app
except ImportError:
    TestClient = None
    app = None


@unittest.skipIf(TestClient is None, "API development dependencies are not installed")
class HealthTests(unittest.TestCase):
    def test_health_contract(self) -> None:
        response = TestClient(app).get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "service": "cosmology-lens-api", "version": "0.1.0"},
        )


if __name__ == "__main__":
    unittest.main()
