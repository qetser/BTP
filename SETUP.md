# Codex project setup

This is the Codex adaptation of the supplied Grand Setup v2 for the Chandrayaan-2 IIRS research project. It records the working system and how to maintain it. The scientific plan is [docs/m1_m3_plan.md](docs/m1_m3_plan.md); this file governs project workflow.

## Principles

- Put stable project facts in `project.md`, current work in `tasks/task_plan.md`, and verified findings in `tasks/findings.md`.
- Plan substantial work, then implement and verify it. The plan is a working record, not a permission gate for routine changes.
- Challenge scientific claims with calibration, independent labels, held-out geography, and uncertainty. A failed gate is a finding.
- Record recurring corrections as specific lessons and actionable improvements. Keep logs useful rather than recording every trivial action.
- Use another model for an independent review of a high-impact scientific decision when one is available; record the disagreement and evidence. Do not claim cross-model verification when none occurred.

## Codex-native layout

| Supplied scaffold | This repository | Status |
| --- | --- | --- |
| `CLAUDE.md` | Local `AGENTS.md` plus `codex.md` | Present, ignored by Git as requested |
| `.claude/skills` | Local `.agents/skills/{plan,commit,verify}` | Present, ignored by Git |
| `.claude/settings.json` hooks | Local `.codex/hooks.json` | Present, ignored by Git; requires project and hook trust |
| `.claude/agents` | Local `.codex/agents` | Present, ignored by Git |
| `tasks/todo.md` / `task_plan.md` | `tasks/task_plan.md` | One current-task file |
| Four living files | `project.md`, `improvements.md`, `updates.md`, `error-maintainer.md` | Present, tracked |

Codex reads `AGENTS.md` automatically in a project and discovers repository skills under `.agents/skills`. `codex.md` is supplementary and is read through `AGENTS.md`; it is not an automatic instruction filename. Project hooks and custom agents are loaded by Codex in trusted projects. See the [official AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [skills](https://learn.chatgpt.com/docs/build-skills), [hooks](https://learn.chatgpt.com/docs/hooks), and [subagent](https://learn.chatgpt.com/docs/agent-configuration/subagents) docs.

The supplied setup's TypeScript skill package does not apply to this Python-oriented hyperspectral research project. No TypeScript package was installed. The [research-digest prompt](docs/research_digest_prompt.md) and [observation checklist](tasks/observations.md) are ready, but no research schedule, telemetry service, or second-model check has been activated: those need a cadence, destination, and evaluation criteria. [Scheduled tasks](https://learn.chatgpt.com/docs/automations) can be configured in ChatGPT or the desktop app when those details are chosen.

## Working loop

1. At session start, read `project.md`, `tasks/task_plan.md`, recent `tasks/progress.md`, and relevant open `improvements.md` items. Read `tasks/lessons.md` for known mistakes. The session-start hook reminds Codex to do this.
2. Select a concrete phase. Record its goal, evidence, and exit checks in `tasks/task_plan.md`. Scientific gates in `docs/m1_m3_plan.md` remain unchanged unless the user approves a scope change.
3. Work in small units. Add source-backed research to `tasks/findings.md`; add implementation decisions and outcomes to `tasks/progress.md`.
4. Verify actual outputs. Use the `verify` skill for code and data work. Do not claim a test or source check that did not run.
5. After a meaningful change, update `updates.md` in the same logical unit. Record resolved, non-routine errors in `error-maintainer.md`. Capture recurring patterns in `tasks/lessons.md` and proposed process changes in `improvements.md`.
6. Commit only intended files. `data/`, `AGENTS.md`, `codex.md`, `.agents/skills`, and `.codex` stay untracked. The local Git commit-message hook rejects Claude/Codex co-author trailers.

## Onboarding facts and unanswered choices

The proposal and existing repo already answer the project, domain, research, core risks, and M1–M3 milestones. `project.md` records these with their evidence. Before adding a model training stack or recurring automation, resolve:

1. Which mineral classes or geologic units form the first reviewed label set?
2. Which calibrated IIRS products and calibration guide are accessible for the four current scenes?
3. What compute budget, review cadence, and research-digest schedule should be used?
4. Which independent model or reviewer should check major scientific decisions?

Do not fill these gaps with invented answers. Record each decision in `project.md` when made.

## Setup checks

- [x] Git repository and `main` exist; raw data are ignored.
- [x] Project charter, task plan, findings, progress, lessons, improvements, updates, and error registry exist.
- [x] Research-digest prompt and M1–M3 observation checklist exist; no autonomous schedule or telemetry is enabled.
- [x] Plan, commit, and verify skills exist locally in Codex's repository skill path and are ignored by Git.
- [x] Local `AGENTS.md` and `codex.md` are ignored and carry the no-co-author rule.
- [x] A Git commit-message hook protects the co-author rule in this checkout.
- [ ] In a fresh Codex session, inspect and trust the project hook with `/hooks`; this cannot be tested as active from the current session.
- [ ] Obtain official calibrated IIRS products and product guide for M2.
- [ ] Set any research schedule, observation metrics, or cross-model review only after specifying cadence and success criteria.

## Local research Python environment

Use Python 3.11 and `uv` to create the ignored project environment and install the pinned research stack:

```sh
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements-research.lock
```

`requirements-research.txt` records supported dependency ranges. The lock file records the exact versions used for the M1 WAC 2D tie-grid diagnostic. Keep `.venv/` local and do not add it to Git.

To enable the Git hook in another checkout, run `git config --local core.hooksPath .githooks`. The ignored instruction, skill, and Codex configuration files exist only in this checkout; recreate them locally in a fresh clone using this setup and the repository's project files. Do not add them to Git.
