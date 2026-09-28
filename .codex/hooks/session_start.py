#!/usr/bin/env python3
"""Provide the small project-memory reminder for a Codex session."""

import json


print(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": (
                    "For substantive IIRS work, read project.md, tasks/task_plan.md, "
                    "recent tasks/progress.md, tasks/lessons.md, and relevant "
                    "improvements.md items. Preserve the scientific gates in "
                    "docs/m1_m3_plan.md. Do not add Claude or Codex co-author attribution."
                ),
            }
        }
    )
)
