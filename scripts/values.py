"""Normalize the Meaning Alignment Institute (MAI) moral graph export.

The export is one JSON object with two arrays, ``values`` and ``edges``. This
script splits them into two normalized JSONL files that are kept deliberately
SEPARATE, because they answer different questions:

  * value cards (attention policies) -> knowledge/values/normalized_values.jsonl
      may be retrieved by semantic relevance.
  * moral-graph edges ("wiser than")  -> knowledge/values/normalized_edges.jsonl
      contextual, human-voted judgments; looked up only by value id and never
      inferred from card similarity.

Keeping them in two files is the firewall made physical: card text lives only in
the values file and the wiser-than ranking lives only in the edges file, so
neither can be reconstructed from the other.

Output is deterministic (stable ordering and key order), so re-running the
normalization reproduces byte-identical files.

Source data is unlicensed MAI content. The raw export and the normalized outputs
are gitignored; only this script and the provenance manifest are committed. Do
not publish derived data until cleared. See knowledge/values/README.md and
knowledge/values/manifest.json.

Usage:
    python3 scripts/values.py normalize   # raw export -> two JSONL files
    python3 scripts/values.py validate    # check invariants on the JSONL files
    python3 scripts/values.py stats       # summarize the raw export
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUES_DIR = ROOT / "knowledge" / "values"
RAW_PATH = VALUES_DIR / "raw" / "moral-graph-edges.json"
VALUES_OUT = VALUES_DIR / "normalized_values.jsonl"
EDGES_OUT = VALUES_DIR / "normalized_edges.jsonl"

SOURCE_TAG = "mai-moral-graph"

# A value card carries only these descriptive fields; an edge carries only these
# ranking fields. The two sets must never mix within a record.
_CARD_ONLY = {"title", "summary", "detail", "attention_policies"}
_EDGE_ONLY = {"wiser_value_id", "counts", "wiser_likelihood", "entropy"}


def _id_key(value_id: object) -> tuple[int, object]:
    """Deterministic sort key that tolerates int or string ids."""
    return (0, value_id) if isinstance(value_id, int) else (1, str(value_id))


def normalize_values(raw: dict) -> list[dict]:
    """Map raw value objects to card records, sorted by id."""
    rows = [
        {
            "id": value["id"],
            "title": value.get("title"),
            "summary": value.get("instructionsShort"),
            "detail": value.get("instructionsDetailed"),
            "attention_policies": value.get("evaluationCriteria", []),
            "source": SOURCE_TAG,
        }
        for value in raw.get("values", [])
    ]
    rows.sort(key=lambda r: _id_key(r["id"]))
    return rows


def normalize_edges(raw: dict) -> list[dict]:
    """Map raw edge objects to wiser-than records, sorted by endpoints."""
    rows = []
    for edge in raw.get("edges", []):
        summary = edge.get("summary") or {}
        rows.append(
            {
                "source_value_id": edge["sourceValueId"],
                "wiser_value_id": edge["wiserValueId"],
                "contexts": edge.get("contexts", []),
                "counts": edge.get("counts", {}),
                "wiser_likelihood": summary.get("wiserLikelihood"),
                "entropy": summary.get("entropy"),
                "source": SOURCE_TAG,
            }
        )
    rows.sort(key=lambda r: (_id_key(r["source_value_id"]), _id_key(r["wiser_value_id"])))
    return rows


def validate_store(values: list[dict], edges: list[dict]) -> list[str]:
    """Firewall and referential-integrity invariants; empty list means valid."""
    errors: list[str] = []

    known: set = set()
    for value in values:
        vid = value["id"]
        if vid in known:
            errors.append(f"values: duplicate value id {vid!r}")
        known.add(vid)

    # Cards must not carry ranking fields; edges must not carry card text.
    for index, value in enumerate(values):
        leaked = _EDGE_ONLY & set(value)
        if leaked:
            errors.append(f"values[{index}]: card carries edge-only fields {sorted(leaked)}")
    for index, edge in enumerate(edges):
        leaked = _CARD_ONLY & set(edge)
        if leaked:
            errors.append(f"edges[{index}]: edge carries card-only fields {sorted(leaked)}")

    # Every edge endpoint must resolve to a known value.
    for index, edge in enumerate(edges):
        for role in ("source_value_id", "wiser_value_id"):
            if edge[role] not in known:
                errors.append(f"edges[{index}]: {role} {edge[role]!r} does not resolve to a value")
        if edge["source_value_id"] == edge["wiser_value_id"]:
            errors.append(f"edges[{index}]: self-edge on value {edge['source_value_id']!r}")
        likelihood = edge.get("wiser_likelihood")
        if likelihood is not None and not 0.0 <= likelihood <= 1.0:
            errors.append(f"edges[{index}]: wiser_likelihood {likelihood!r} outside [0, 1]")

    return errors


def _dump_jsonl(rows: list[dict]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)


def _read_jsonl(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def cmd_normalize(args: argparse.Namespace) -> int:
    raw_path = Path(args.raw) if args.raw else RAW_PATH
    if not raw_path.exists():
        print(f"raw export not found: {raw_path}")
        print("Download it from the source URL in knowledge/values/manifest.json into that path.")
        return 1
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    values = normalize_values(raw)
    edges = normalize_edges(raw)
    errors = validate_store(values, edges)
    if errors:
        print(f"FAIL normalization produced {len(errors)} invariant violations:")
        for error in errors:
            print(f"  {error}")
        return 1
    VALUES_OUT.write_text(_dump_jsonl(values), encoding="utf-8")
    EDGES_OUT.write_text(_dump_jsonl(edges), encoding="utf-8")
    print(f"ok   {VALUES_OUT.relative_to(ROOT)} ({len(values)} value cards)")
    print(f"ok   {EDGES_OUT.relative_to(ROOT)} ({len(edges)} wiser-than edges)")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    if not VALUES_OUT.exists() or not EDGES_OUT.exists():
        print("normalized files not found; run: python3 scripts/values.py normalize")
        return 1
    values = _read_jsonl(VALUES_OUT)
    edges = _read_jsonl(EDGES_OUT)
    errors = validate_store(values, edges)
    if errors:
        print(f"FAIL {len(errors)} invariant violations:")
        for error in errors:
            print(f"  {error}")
        return 1
    print(f"ok   {len(values)} value cards, {len(edges)} edges; firewall invariants hold")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    raw_path = Path(args.raw) if args.raw else RAW_PATH
    if not raw_path.exists():
        print(f"raw export not found: {raw_path}")
        return 1
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    values = raw.get("values", [])
    edges = raw.get("edges", [])
    print(f"values: {len(values)}")
    if values:
        print(f"  fields: {sorted(values[0].keys())}")
    print(f"edges: {len(edges)}")
    if edges:
        print(f"  fields: {sorted(edges[0].keys())}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_norm = sub.add_parser("normalize", help="normalize the raw export into two JSONL files")
    p_norm.add_argument("--raw", help="path to the raw export (default: knowledge/values/raw/moral-graph-edges.json)")
    p_norm.set_defaults(func=cmd_normalize)

    p_val = sub.add_parser("validate", help="check firewall and integrity invariants on the JSONL files")
    p_val.set_defaults(func=cmd_validate)

    p_stats = sub.add_parser("stats", help="summarize the raw export")
    p_stats.add_argument("--raw")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
