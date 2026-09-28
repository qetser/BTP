# Updates

Meaningful project changes are recorded newest first. Entries describe the change and evidence; the Git history supplies the exact commit hash.

## 2026-09-28 — Keep agent tooling local

**Phase:** Project workflow setup
**Type:** Configuration

- Removed `.agents/skills` and `.codex` from Git tracking while preserving their local files.
- Added ignore rules and updated the setup guide and Git scope lesson.

**Why:** The project's agent tooling should remain specific to this checkout, as requested.

**Impact:** Fresh clones will need to recreate local skills and Codex configuration if wanted.

## 2026-09-28 — Codex project setup

**Phase:** Project workflow setup
**Type:** Configuration and documentation

- Added the project charter, living logs, current task plan, research prompt, observation checklist, and Codex-native skills, agents, and session-start reminder.
- Kept `AGENTS.md` and `codex.md` local and ignored; added a local Git hook to reject Claude/Codex co-author trailers.

**Why:** Preserve scientific decisions and operational context across sessions while keeping the requested local instructions out of Git.

**Impact:** No scientific data or model outputs changed. Project hooks require trust in a fresh Codex session.

## 2026-09-28 — Initial IIRS research and archive inventory

**Phase:** M1 planning
**Type:** Documentation

- Added the M1–M3 README and implementation plan, inventoried four raw IIRS archives, and extracted all four locally.

**Why:** Establish the calibration and evaluation gates before reporting scientific baselines.

**Impact:** Data remain ignored by Git; no calibrated reflectance or scores exist yet.
