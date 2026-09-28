---
name: commit
description: Review, verify, and commit an intended logical change in the IIRS repository without staging data.
---

# Commit

Inspect the diff and Git status; confirm intended files and meaningful verification. Update `updates.md` for a meaningful change in the same logical unit. Stage explicit paths, not `data/`, `AGENTS.md`, or `codex.md`.

Use a short imperative subject that states the reason for the change. Do not add Claude or Codex as a co-author anywhere, including `Co-Authored-By` trailers. Check the final staged diff and commit result. Push only when the user requested it or existing authorization covers that push.
