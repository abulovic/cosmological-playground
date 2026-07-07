#!/usr/bin/env python3
"""Topic knowledge store: validation, derived SQLite index, hybrid search.

Canonical content: git-tracked markdown with front matter in knowledge/topics/.
Derived index: var/topics.sqlite3 (gitignored, rebuild at will).
Search: FTS5 keyword ranking fused with local static embeddings when the
optional model2vec stack is installed; otherwise a deterministic keyword-only
fallback. Embedding is fully local; no text leaves the machine.
"""

from __future__ import annotations

import argparse
import math
import re
import sqlite3
import sys
from array import array
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
TOPICS_DIR = ROOT / "knowledge" / "topics"
DB_PATH = ROOT / "var" / "topics.sqlite3"
EMBED_MODEL = "minishlab/potion-base-8M"
RRF_K = 60

PRIMITIVES = (
    "ultimate_reality",
    "constituents",
    "origin",
    "causality_and_agency",
    "cosmic_structure",
    "time",
    "human_place",
    "self_and_consciousness",
    "fundamental_problem",
    "transformation",
    "destiny",
    "epistemic_access",
)
TOPIC_TYPES = ("doctrine-profile", "analysis-finding", "concept", "contract-note")
STATUSES = ("unreviewed", "reviewed")
REQUIRED_KEYS = (
    "id", "title", "type", "primitives", "related_cards",
    "source_report", "created", "status",
)

Embedder = Callable[[list[str]], list[list[float]]]


class TopicError(RuntimeError):
    pass


# ---------------------------------------------------------------- front matter

def parse_front_matter(text: str, origin: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise TopicError(f"{origin}: missing front matter opening '---'")
    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        raise TopicError(f"{origin}: unterminated front matter") from None
    meta: dict[str, Any] = {}
    for raw in lines[1:end]:
        if not raw.strip():
            continue
        if ":" not in raw:
            raise TopicError(f"{origin}: malformed front matter line {raw!r}")
        key, _, value = raw.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            meta[key] = [item.strip() for item in inner.split(",") if item.strip()]
        else:
            meta[key] = value
    body = "\n".join(lines[end + 1:]).strip()
    return meta, body


def validate_topic(meta: dict[str, Any], path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    origin = path.name
    missing = [key for key in REQUIRED_KEYS if key not in meta]
    if missing:
        errors.append(f"{origin}: missing front matter keys {missing}")
        return errors
    if meta["id"] != path.stem:
        errors.append(f"{origin}: id {meta['id']!r} must equal filename stem {path.stem!r}")
    if meta["type"] not in TOPIC_TYPES:
        errors.append(f"{origin}: type {meta['type']!r} not in {TOPIC_TYPES}")
    if meta["status"] not in STATUSES:
        errors.append(f"{origin}: status {meta['status']!r} not in {STATUSES}")
    if not isinstance(meta["primitives"], list):
        errors.append(f"{origin}: primitives must be a list")
    else:
        unknown = [p for p in meta["primitives"] if p not in PRIMITIVES]
        if unknown:
            errors.append(f"{origin}: unknown primitives {unknown}")
    if not isinstance(meta["related_cards"], list):
        errors.append(f"{origin}: related_cards must be a list")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(meta["created"])):
        errors.append(f"{origin}: created must be YYYY-MM-DD")
    if not (root / str(meta["source_report"])).exists():
        errors.append(f"{origin}: source_report does not exist: {meta['source_report']}")
    return errors


def load_topics(
    topics_dir: Path = TOPICS_DIR, root: Path = ROOT
) -> tuple[list[dict[str, Any]], list[str]]:
    topics: list[dict[str, Any]] = []
    errors: list[str] = []
    seen: set[str] = set()
    for path in sorted(topics_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        try:
            meta, body = parse_front_matter(path.read_text(encoding="utf-8"), path.name)
        except TopicError as exc:
            errors.append(str(exc))
            continue
        errors.extend(validate_topic(meta, path, root))
        topic_id = meta.get("id", path.stem)
        if topic_id in seen:
            errors.append(f"{path.name}: duplicate topic id {topic_id!r}")
        seen.add(topic_id)
        topics.append({"meta": meta, "body": body, "path": path})
    return topics, errors


def chunk_body(body: str) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    section = "(intro)"
    buffer: list[str] = []

    def flush() -> None:
        text = "\n".join(buffer).strip()
        if text:
            chunks.append((section, text))

    for line in body.splitlines():
        if line.startswith("## "):
            flush()
            section = line[3:].strip()
            buffer = []
        else:
            buffer.append(line)
    flush()
    return chunks


# ------------------------------------------------------------------ embeddings

def load_embedder(model_name: str = EMBED_MODEL) -> Embedder | None:
    try:
        from model2vec import StaticModel  # type: ignore[import-not-found]
    except Exception:
        return None
    try:
        model = StaticModel.from_pretrained(model_name)
    except Exception:
        return None

    def embed(texts: list[str]) -> list[list[float]]:
        return [[float(x) for x in row] for row in model.encode(texts)]

    return embed


def vector_to_blob(vector: list[float]) -> bytes:
    return array("f", vector).tobytes()


def blob_to_vector(blob: bytes) -> list[float]:
    vec = array("f")
    vec.frombytes(blob)
    return list(vec)


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


# ----------------------------------------------------------------------- index

SCHEMA = """
CREATE TABLE topics (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    source_report TEXT NOT NULL,
    created TEXT NOT NULL,
    status TEXT NOT NULL,
    path TEXT NOT NULL,
    primitives TEXT NOT NULL,
    related_cards TEXT NOT NULL
);
CREATE TABLE chunks (
    id INTEGER PRIMARY KEY,
    topic_id TEXT NOT NULL REFERENCES topics(id),
    section TEXT NOT NULL,
    text TEXT NOT NULL
);
CREATE VIRTUAL TABLE chunks_fts USING fts5(text);
CREATE TABLE embeddings (
    chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id),
    vector BLOB NOT NULL
);
CREATE TABLE index_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def build_index(
    topics_dir: Path = TOPICS_DIR,
    db_path: Path = DB_PATH,
    root: Path = ROOT,
    embedder: Embedder | None = None,
) -> dict[str, Any]:
    topics, errors = load_topics(topics_dir, root)
    if errors:
        raise TopicError("invalid topics:\n" + "\n".join(f"  {e}" for e in errors))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        chunk_texts: list[str] = []
        chunk_ids: list[int] = []
        next_id = 1
        for topic in topics:
            meta = topic["meta"]
            conn.execute(
                "INSERT INTO topics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    meta["id"], meta["title"], meta["type"], meta["source_report"],
                    meta["created"], meta["status"],
                    str(topic["path"].relative_to(root)) if topic["path"].is_relative_to(root)
                    else str(topic["path"]),
                    ",".join(meta["primitives"]), ",".join(meta["related_cards"]),
                ),
            )
            for section, text in chunk_body(topic["body"]):
                indexed = f"{meta['title']}\n{section}\n{text}"
                conn.execute(
                    "INSERT INTO chunks (id, topic_id, section, text) VALUES (?, ?, ?, ?)",
                    (next_id, meta["id"], section, text),
                )
                conn.execute(
                    "INSERT INTO chunks_fts (rowid, text) VALUES (?, ?)", (next_id, indexed)
                )
                chunk_texts.append(indexed)
                chunk_ids.append(next_id)
                next_id += 1
        embedded = False
        if embedder is not None and chunk_texts:
            vectors = embedder(chunk_texts)
            conn.executemany(
                "INSERT INTO embeddings (chunk_id, vector) VALUES (?, ?)",
                [(cid, vector_to_blob(vec)) for cid, vec in zip(chunk_ids, vectors)],
            )
            embedded = True
        conn.execute(
            "INSERT INTO index_meta VALUES ('embeddings', ?)",
            ("present" if embedded else "absent",),
        )
        conn.execute(
            "INSERT INTO index_meta VALUES ('indexed_at', ?)",
            (datetime.now().astimezone().isoformat(timespec="seconds"),),
        )
        conn.commit()
        return {"topics": len(topics), "chunks": len(chunk_ids), "embeddings": embedded}
    finally:
        conn.close()


# ---------------------------------------------------------------------- search

def fts_ranking(conn: sqlite3.Connection, query: str, limit: int) -> list[int]:
    tokens = re.findall(r"[A-Za-z0-9_]+", query)
    if not tokens:
        return []
    match = " OR ".join(f'"{token}"' for token in tokens)
    rows = conn.execute(
        "SELECT rowid FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY rank LIMIT ?",
        (match, limit),
    ).fetchall()
    return [row[0] for row in rows]


def vector_ranking(
    conn: sqlite3.Connection, query_vector: list[float], limit: int
) -> list[int]:
    scored = [
        (cosine(query_vector, blob_to_vector(blob)), chunk_id)
        for chunk_id, blob in conn.execute("SELECT chunk_id, vector FROM embeddings")
    ]
    scored.sort(key=lambda pair: (-pair[0], pair[1]))
    return [chunk_id for _, chunk_id in scored[:limit]]


def fuse_rankings(rankings: dict[str, list[int]]) -> list[tuple[int, float, list[str]]]:
    scores: dict[int, float] = {}
    channels: dict[int, list[str]] = {}
    for channel, ranking in rankings.items():
        for rank, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank)
            channels.setdefault(chunk_id, []).append(channel)
    fused = [(chunk_id, score, channels[chunk_id]) for chunk_id, score in scores.items()]
    fused.sort(key=lambda item: (-item[1], item[0]))
    return fused


def search(
    query: str,
    limit: int = 5,
    db_path: Path = DB_PATH,
    embedder: Embedder | None = None,
) -> dict[str, Any]:
    if not db_path.exists():
        raise TopicError(f"index missing: {db_path} — run 'topics.py index' first")
    conn = sqlite3.connect(db_path)
    try:
        pool = max(limit * 4, 20)
        rankings: dict[str, list[int]] = {"keyword": fts_ranking(conn, query, pool)}
        has_vectors = conn.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0] > 0
        mode = "keyword-only fallback (embeddings unavailable)"
        if has_vectors and embedder is not None:
            rankings["embedding"] = vector_ranking(conn, embedder([query])[0], pool)
            mode = "hybrid (keyword + embedding)"
        results = []
        for chunk_id, score, via in fuse_rankings(rankings)[:limit]:
            row = conn.execute(
                """
                SELECT c.topic_id, c.section, c.text, t.source_report, t.type, t.status
                FROM chunks c JOIN topics t ON t.id = c.topic_id WHERE c.id = ?
                """,
                (chunk_id,),
            ).fetchone()
            results.append({
                "topic_id": row[0],
                "section": row[1],
                "snippet": re.sub(r"\s+", " ", row[2])[:220],
                "source_report": row[3],
                "type": row[4],
                "status": row[5],
                "score": round(score, 5),
                "channels": via,
            })
        return {"mode": mode, "results": results}
    finally:
        conn.close()


# -------------------------------------------------------------------- commands

def cmd_validate(_: argparse.Namespace) -> None:
    topics, errors = load_topics()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"{len(topics)} topic documents are valid.")


def cmd_index(args: argparse.Namespace) -> None:
    embedder = None if args.no_embeddings else load_embedder()
    if not args.no_embeddings and embedder is None:
        print("note: embedding stack unavailable; building keyword-only index")
    summary = build_index(embedder=embedder)
    print(
        f"Indexed {summary['topics']} topics / {summary['chunks']} chunks "
        f"(embeddings: {'yes' if summary['embeddings'] else 'no'}) -> "
        f"{DB_PATH.relative_to(ROOT)}"
    )


def cmd_search(args: argparse.Namespace) -> None:
    embedder = None if args.no_embeddings else load_embedder()
    outcome = search(args.query, limit=args.k, embedder=embedder)
    print(f"mode: {outcome['mode']}")
    if not outcome["results"]:
        print("no matches")
        return
    for rank, hit in enumerate(outcome["results"], start=1):
        print(
            f"{rank}. {hit['topic_id']} § {hit['section']}  "
            f"[{hit['type']}, {hit['status']}; via {'+'.join(hit['channels'])}]"
        )
        print(f"   {hit['snippet']}")
        print(f"   source: {hit['source_report']}")


def cmd_list(_: argparse.Namespace) -> None:
    topics, errors = load_topics()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    for topic in topics:
        meta = topic["meta"]
        primitives = ", ".join(meta["primitives"]) or "—"
        print(f"{meta['id']}  [{meta['type']}, {meta['status']}]  primitives: {primitives}")


def cmd_show(args: argparse.Namespace) -> None:
    path = TOPICS_DIR / f"{args.topic_id}.md"
    if not path.exists():
        raise TopicError(f"unknown topic: {args.topic_id}")
    print(path.read_text(encoding="utf-8"))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(required=True)
    validate = sub.add_parser("validate", help="Validate topic front matter")
    validate.set_defaults(func=cmd_validate)
    index = sub.add_parser("index", help="Rebuild the derived search index")
    index.add_argument("--no-embeddings", action="store_true")
    index.set_defaults(func=cmd_index)
    search_cmd = sub.add_parser("search", help="Hybrid search over topic chunks")
    search_cmd.add_argument("query")
    search_cmd.add_argument("-k", type=int, default=5)
    search_cmd.add_argument("--no-embeddings", action="store_true")
    search_cmd.set_defaults(func=cmd_search)
    list_cmd = sub.add_parser("list", help="List topics")
    list_cmd.set_defaults(func=cmd_list)
    show = sub.add_parser("show", help="Print one topic document")
    show.add_argument("topic_id")
    show.set_defaults(func=cmd_show)
    return result


def main() -> None:
    args = parser().parse_args()
    try:
        args.func(args)
    except TopicError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
