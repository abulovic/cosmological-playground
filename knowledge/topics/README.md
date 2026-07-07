# Topic knowledge store

Reusable "cosmology-adjacent" notes produced by analyses and dry runs: doctrine
profiles, analysis findings, transferable concepts, and contract observations.
The store exists so that worked-out material is searched, not re-derived.

## What lives here

Canonical content is this directory's git-tracked markdown files, one topic per
file. The search index (`var/topics.sqlite3`) is **derived and disposable**;
rebuild it at any time with:

```bash
python3 scripts/topics.py index          # rebuild index (embeddings if available)
python3 scripts/topics.py search "karma and objective moral order"
python3 scripts/topics.py list
python3 scripts/topics.py show <topic-id>
```

Search combines SQLite FTS5 keyword ranking with local static embeddings
(model2vec `potion-base-8M`) merged by reciprocal rank fusion. Embedding is
fully local; no text leaves the machine. When the embedding stack is not
installed, search degrades deterministically to keyword-only and says so.

## Front matter contract

Every topic file must begin with:

```
---
id: <kebab-case slug, must equal the filename stem>
title: <one-line title>
type: doctrine-profile | analysis-finding | concept | contract-note
primitives: [<zero or more of the twelve frozen primitive ids>]
related_cards: [<zero or more card ids from knowledge/cosmologies/cards>]
source_report: <repo-relative path to the report this topic distills>
created: <YYYY-MM-DD>
status: unreviewed | reviewed
---
```

Body is ordinary markdown. `##` sections are the retrieval unit: search returns
`topic-id § section`, so keep sections self-contained.

## Types

- `doctrine-profile` — a school or strain profiled across the twelve primitives.
- `analysis-finding` — what a specific dry run or pipeline run revealed.
- `concept` — a named, transferable analytic idea.
- `contract-note` — an observed gap or proposed clarification to a frozen contract.

## Status and epistemic standing

Topics are working notes, not reviewed scholarship. They default to
`status: unreviewed` and never substitute for card provenance: a claim that
enters a cosmology card must be re-sourced under the card schema's citation
rules regardless of what a topic file says.
