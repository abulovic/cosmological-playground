#!/usr/bin/env python3
"""Small, dependency-free control plane for the Cosmology Lens project."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / ".agent" / "state.json"
STATUS_PATH = ROOT / "reports" / "CURRENT_STATUS.md"
VALID_STATES = {"queued", "ready", "in_progress", "blocked", "done"}
READINESS_NAMES = {
    0: "Not started",
    1: "Defined",
    2: "Implemented",
    3: "Verified",
    4: "Pilot-ready",
    5: "Production-ready",
}


class StateError(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_state(path: Path = STATE_PATH) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StateError(f"Missing canonical state: {path}") from exc
    except json.JSONDecodeError as exc:
        raise StateError(f"Invalid JSON in {path}: {exc}") from exc


def save_state(state: dict[str, Any], path: Path = STATE_PATH) -> None:
    state["project"]["updated_at"] = now_iso()
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def task_index(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {task["id"]: task for task in state["tasks"]}


def dependencies_done(task: dict[str, Any], index: dict[str, dict[str, Any]]) -> bool:
    return all(index[dep]["status"] == "done" for dep in task["depends_on"])


def effective_status(task: dict[str, Any], index: dict[str, dict[str, Any]]) -> str:
    if task["status"] == "queued" and dependencies_done(task, index):
        return "ready"
    return task["status"]


def eligible_tasks(state: dict[str, Any]) -> list[dict[str, Any]]:
    index = task_index(state)
    eligible = [
        task
        for task in state["tasks"]
        if effective_status(task, index) == "ready"
    ]
    return sorted(eligible, key=lambda task: (task["priority"], task["id"]))


def validate_state(state: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if state.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    tasks = state.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return errors + ["tasks must be a non-empty list"]

    ids = [task.get("id") for task in tasks]
    duplicates = sorted(task_id for task_id, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append(f"duplicate task ids: {', '.join(duplicates)}")

    index = task_index(state)
    active = []
    for task in tasks:
        task_id = task.get("id", "<missing>")
        missing = {
            "id", "day", "workstream", "title", "status", "priority",
            "depends_on", "required_artifacts", "acceptance", "attempts",
        } - task.keys()
        if missing:
            errors.append(f"{task_id}: missing fields {sorted(missing)}")
        if task.get("status") not in VALID_STATES:
            errors.append(f"{task_id}: invalid status {task.get('status')!r}")
        if task.get("status") == "in_progress":
            active.append(task_id)
        for dep in task.get("depends_on", []):
            if dep not in index:
                errors.append(f"{task_id}: unknown dependency {dep}")
            elif dep == task_id:
                errors.append(f"{task_id}: cannot depend on itself")
        if task.get("status") == "done":
            for artifact in task.get("required_artifacts", []):
                if not (root / artifact).exists():
                    errors.append(f"{task_id}: done but required artifact is missing: {artifact}")
            if not task.get("completion_summary"):
                errors.append(f"{task_id}: done without completion_summary")
            if not task.get("completion_evidence"):
                errors.append(f"{task_id}: done without completion_evidence")
            if not task.get("verified_at"):
                errors.append(f"{task_id}: done without verified_at")
        if task.get("status") == "blocked" and not task.get("blocker"):
            errors.append(f"{task_id}: blocked without blocker evidence")

    if len(active) > 1:
        errors.append(f"only one task may be in_progress; found {', '.join(active)}")

    readiness = state.get("readiness", {})
    for name, item in readiness.items():
        level = item.get("level")
        if level not in READINESS_NAMES:
            errors.append(f"readiness.{name}: level must be 0..5")
        if level and not item.get("evidence"):
            errors.append(f"readiness.{name}: level {level} requires evidence")
        for evidence in item.get("evidence", []):
            if not (root / evidence).exists():
                errors.append(f"readiness.{name}: missing evidence path {evidence}")

    return errors


def readiness_label(level: int) -> str:
    return f"{level} — {READINESS_NAMES[level]}"


def render_status(state: dict[str, Any]) -> str:
    index = task_index(state)
    effective = Counter(effective_status(task, index) for task in state["tasks"])
    critical_levels = [
        item["level"] for item in state["readiness"].values() if item.get("critical")
    ]
    overall = min(critical_levels) if critical_levels else 0
    active = [task for task in state["tasks"] if task["status"] == "in_progress"]
    next_tasks = eligible_tasks(state)
    blocked = [task for task in state["tasks"] if task["status"] == "blocked"]

    lines = [
        "# Current project status",
        "",
        f"_Generated from `.agent/state.json` at {now_iso()}._",
        "",
        f"**Overall readiness:** {readiness_label(overall)}",
        f"**Current phase:** `{state['project']['current_phase']}`",
        f"**Tasks:** {effective['done']} done · {effective['in_progress']} active · "
        f"{effective['ready']} ready · {effective['queued']} waiting · {effective['blocked']} blocked",
        "",
        "Overall readiness is the lowest critical workstream level, not an average.",
        "",
        "## Active and next work",
        "",
    ]
    if active:
        task = active[0]
        lines.append(f"- Active: **{task['id']}** — {task['title']} (attempt {task['attempts']})")
    else:
        lines.append("- Active: none")
    if next_tasks:
        for task in next_tasks[:3]:
            lines.append(f"- Next: **{task['id']}** — {task['title']}")
    else:
        lines.append("- Next: no eligible task")

    lines.extend([
        "",
        "## Workstream readiness",
        "",
        "| Workstream | Readiness | Critical | Evidence |",
        "|---|---:|:---:|---|",
    ])
    for name, item in state["readiness"].items():
        evidence = ", ".join(f"`{path}`" for path in item.get("evidence", [])) or "—"
        lines.append(
            f"| {name.replace('_', ' ').title()} | {readiness_label(item['level'])} | "
            f"{'yes' if item.get('critical') else 'no'} | {evidence} |"
        )

    lines.extend([
        "",
        "## Seven-day delivery",
        "",
        "| Day | Done | Active | Ready | Waiting | Blocked |",
        "|---:|---:|---:|---:|---:|---:|",
    ])
    for day in sorted({task["day"] for task in state["tasks"]}):
        counts = Counter(
            effective_status(task, index) for task in state["tasks"] if task["day"] == day
        )
        lines.append(
            f"| {day} | {counts['done']} | {counts['in_progress']} | "
            f"{counts['ready']} | {counts['queued']} | {counts['blocked']} |"
        )

    lines.extend(["", "## Blockers", ""])
    if blocked:
        for task in blocked:
            lines.append(f"- **{task['id']}**: {task['blocker']}")
    else:
        lines.append("No recorded blockers.")

    lines.extend([
        "",
        "## Readiness interpretation",
        "",
        "- Level 1 means the workstream is defined, not implemented.",
        "- Level 2 means a representative core path works.",
        "- Level 3 requires passing checks and edge-case review.",
        "- Level 4 additionally requires a usable, bounded pilot and human review.",
        "- See `.agent/READINESS.md` for promotion gates.",
        "",
    ])
    return "\n".join(lines)


def find_task(state: dict[str, Any], task_id: str) -> dict[str, Any]:
    try:
        return task_index(state)[task_id]
    except KeyError as exc:
        raise StateError(f"Unknown task: {task_id}") from exc


def cmd_validate(_: argparse.Namespace) -> None:
    errors = validate_state(load_state())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    print("State and evidence paths are valid.")


def cmd_status(args: argparse.Namespace) -> None:
    state = load_state()
    report = render_status(state)
    if args.write:
        STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATUS_PATH.write_text(report, encoding="utf-8")
        print(f"Wrote {STATUS_PATH.relative_to(ROOT)}")
    else:
        print(report)


def cmd_next(_: argparse.Namespace) -> None:
    state = load_state()
    active = [task for task in state["tasks"] if task["status"] == "in_progress"]
    if active:
        task = active[0]
        print(f"ACTIVE {task['id']}: {task['title']}")
        return
    tasks = eligible_tasks(state)
    if not tasks:
        print("No eligible task. Inspect blockers and dependencies.")
        return
    task = tasks[0]
    print(f"NEXT {task['id']}: {task['title']}")
    print("Acceptance:")
    for item in task["acceptance"]:
        print(f"- {item}")


def cmd_start(args: argparse.Namespace) -> None:
    state = load_state()
    active = [task for task in state["tasks"] if task["status"] == "in_progress"]
    if active:
        raise StateError(f"{active[0]['id']} is already in_progress")
    task = find_task(state, args.task_id)
    index = task_index(state)
    if task["status"] not in {"queued", "ready"}:
        raise StateError(f"{task['id']} cannot start from status {task['status']}")
    if not dependencies_done(task, index):
        waiting = [dep for dep in task["depends_on"] if index[dep]["status"] != "done"]
        raise StateError(f"{task['id']} is waiting for: {', '.join(waiting)}")
    task["status"] = "in_progress"
    task["attempts"] += 1
    task["started_at"] = now_iso()
    task["blocker"] = None
    save_state(state)
    print(f"Started {task['id']}: {task['title']}")


def cmd_complete(args: argparse.Namespace) -> None:
    state = load_state()
    task = find_task(state, args.task_id)
    if task["status"] != "in_progress":
        raise StateError(f"{task['id']} must be in_progress before completion")
    missing = [path for path in task["required_artifacts"] if not (ROOT / path).exists()]
    if missing:
        raise StateError(f"required artifacts missing: {', '.join(missing)}")
    evidence = list(dict.fromkeys(args.evidence))
    absent_evidence = [path for path in evidence if not (ROOT / path).exists()]
    if absent_evidence:
        raise StateError(f"completion evidence missing: {', '.join(absent_evidence)}")
    task["status"] = "done"
    task["completion_summary"] = args.summary
    task["completion_evidence"] = evidence
    task["verified_at"] = now_iso()
    task["blocker"] = None
    save_state(state)
    print(f"Completed {task['id']}: {task['title']}")


def cmd_block(args: argparse.Namespace) -> None:
    state = load_state()
    task = find_task(state, args.task_id)
    if task["status"] != "in_progress":
        raise StateError(f"{task['id']} must be in_progress before blocking")
    if len(args.reason.strip()) < 20:
        raise StateError("blocker reason must name cause, evidence, and unblocking action")
    task["status"] = "blocked"
    task["blocker"] = args.reason.strip()
    task["blocked_at"] = now_iso()
    save_state(state)
    print(f"Blocked {task['id']}: {task['blocker']}")


def cmd_unblock(args: argparse.Namespace) -> None:
    state = load_state()
    task = find_task(state, args.task_id)
    if task["status"] != "blocked":
        raise StateError(f"{task['id']} is not blocked")
    task["status"] = "ready" if dependencies_done(task, task_index(state)) else "queued"
    task["blocker"] = None
    task["unblocked_at"] = now_iso()
    save_state(state)
    print(f"Unblocked {task['id']} to {task['status']}")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(required=True)
    validate = sub.add_parser("validate", help="Validate canonical state and evidence")
    validate.set_defaults(func=cmd_validate)
    status = sub.add_parser("status", help="Render current project status")
    status.add_argument("--write", action="store_true", help="Write reports/CURRENT_STATUS.md")
    status.set_defaults(func=cmd_status)
    next_cmd = sub.add_parser("next", help="Show active task or highest-priority eligible task")
    next_cmd.set_defaults(func=cmd_next)
    start = sub.add_parser("start", help="Start one eligible task")
    start.add_argument("task_id")
    start.set_defaults(func=cmd_start)
    complete = sub.add_parser("complete", help="Complete the active task with evidence")
    complete.add_argument("task_id")
    complete.add_argument("--summary", required=True)
    complete.add_argument("--evidence", nargs="+", required=True)
    complete.set_defaults(func=cmd_complete)
    block = sub.add_parser("block", help="Block the active task with an actionable reason")
    block.add_argument("task_id")
    block.add_argument("--reason", required=True)
    block.set_defaults(func=cmd_block)
    unblock = sub.add_parser("unblock", help="Return a blocked task to the queue")
    unblock.add_argument("task_id")
    unblock.set_defaults(func=cmd_unblock)
    return result


def main() -> None:
    args = parser().parse_args()
    try:
        args.func(args)
    except StateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
