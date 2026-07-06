# Repository instructions

Read and follow `AGENTS.md` as the canonical operating contract for this project.

Before substantive work, run:

```bash
python3 scripts/project.py validate
python3 scripts/project.py status --write
python3 scripts/project.py next
```

Canonical task state is `.agent/state.json`. Do not create a parallel task ledger in this file.
