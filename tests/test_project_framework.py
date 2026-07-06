from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("project", ROOT / "scripts" / "project.py")
project = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(project)


class ProjectFrameworkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = project.load_state()

    def test_repository_state_is_valid(self) -> None:
        self.assertEqual(project.validate_state(self.state), [])

    def test_only_expected_next_task_is_first(self) -> None:
        state = copy.deepcopy(self.state)
        project.task_index(state)["D1-001"]["status"] = "ready"
        self.assertEqual(project.eligible_tasks(state)[0]["id"], "D1-001")

    def test_queued_task_becomes_effectively_ready_after_dependencies(self) -> None:
        state = copy.deepcopy(self.state)
        index = project.task_index(state)
        index["D1-001"]["status"] = "ready"
        index["D1-002"]["status"] = "queued"
        task = index["D1-002"]
        self.assertEqual(project.effective_status(task, index), "queued")
        index["D1-001"]["status"] = "done"
        self.assertEqual(project.effective_status(task, index), "ready")

    def test_multiple_active_tasks_are_rejected(self) -> None:
        state = copy.deepcopy(self.state)
        state["tasks"][1]["status"] = "in_progress"
        state["tasks"][2]["status"] = "in_progress"
        errors = project.validate_state(state)
        self.assertTrue(any("only one task" in error for error in errors))

    def test_done_task_requires_evidence(self) -> None:
        state = copy.deepcopy(self.state)
        task = state["tasks"][1]
        task["status"] = "done"
        task["completion_summary"] = None
        task["completion_evidence"] = []
        task["verified_at"] = None
        errors = project.validate_state(state)
        self.assertTrue(any("completion_summary" in error for error in errors))
        self.assertTrue(any("completion_evidence" in error for error in errors))

    def test_status_contains_readiness_and_forward_work(self) -> None:
        state = copy.deepcopy(self.state)
        project.task_index(state)["D1-001"]["status"] = "ready"
        report = project.render_status(state)
        self.assertIn("Overall readiness", report)
        self.assertIn("D1-001", report)
        self.assertIn("lowest critical workstream", report)


if __name__ == "__main__":
    unittest.main()
