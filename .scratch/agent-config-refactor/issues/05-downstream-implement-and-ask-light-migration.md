# 05 — Downstream implement & ask-light Compatibility Migration

**What to build:** Update `implement` trigger guidelines to cover model right-sizing and reasoning effort while preserving explicit opt-in and single-ticket boundaries; update `ask-light` discovery patterns and skill maps to accurately route model/effort execution planning while preserving canonical workflow ownership; verify `project-tickets` and review family compatibility.

**Blocked by:** 03 — Core SKILL.md Refactor & openai.yaml Agent Definition, 04 — Four-Quadrant Behavior Fixtures & Unit Test Suite

**Status:** resolved

- [x] `skills/implement/SKILL.md`, `references/WORKFLOW.md`, and `references/EXAMPLES.md` update `agent-config` trigger criteria to include tiered model right-sizing, effort tuning, and delegated implementation/review, while continuing to skip solo/trivial tasks.
- [x] `implement` strictly preserves optional opt-in (declining never blocks implementation) and bounded single-ticket execution (`Scope: current-item`).
- [x] `skills/ask-light/references/light-skill-map.json` and `SKILL.md` add discovery patterns for model choice, effort tuning, single-model planning, and multi-model routing, while keeping ready ticket implementation routed to `implement` and spec splitting routed to `project-tickets`.
- [x] `skills/ask-light/tests/test_ask_light_behavior.py` passes and verifies updated discovery and routing boundaries.
- [x] Verification confirms `project-tickets` ticket contract remains provider-neutral with no mandatory model/effort fields.
- [x] Verification confirms `review-loop`, `code-review`, and `project-review` retain sole ownership over rubrics, repair cycles, and final acceptance.

## Comments

Source: .scratch/agent-config-refactor/spec.md. §4, §22, §23, §24, §25, §35.

## Answer

Updated `skills/implement/SKILL.md`, `references/WORKFLOW.md`, and `references/EXAMPLES.md` to trigger on model right-sizing and effort tuning while preserving explicit user opt-in and single-item scope. Updated `skills/ask-light/` discovery patterns, contract, and skill map for model/effort queries while preserving canonical workflow routing. Confirmed `project-tickets` and review family integrity. All 12 implement tests and 85 ask-light tests pass.
