# Attribution — project-retro

This package is a Light first-party port and adaptation of an upstream Skill.

- **Source repository:** [https://github.com/mattpocock/skills](https://github.com/mattpocock/skills)
- **Original Skill path:** `skills/in-progress/retro` (contains `SKILL.md`, `agents/openai.yaml`)
- **Pinned revision:** `959a8e9f1edc3adbe2f7e3054bb6fbefa6696260` (short `959a8e9`, 2026-09-15)
- **License:** MIT — Copyright (c) 2026 Matt Pocock — see upstream `LICENSE`. The MIT notice is preserved as required; no original authorship is claimed for unmodified upstream ideas.
- **Transformation summary:** PORT & LIGHT WORKFLOW ADAPTATION:
  1. Renamed package from upstream `retro` to `project-retro` to align with the Light `project-*` lifecycle family (`project-init`, `project-clarify`, `project-spec`, `project-tickets`, `project-review`).
  2. Changed invocation policy: Upstream declared `disable-model-invocation: true` (manual user-only invocation). `project-retro` is model-invoked (`allow_implicit_invocation: true`) so an Agent can autonomously evaluate whether to invoke a retrospective at the final step of a project or complex session, while remaining directly invokable by human users.
  3. Added agent self-evaluation heuristics: Integrated trigger/skip decision criteria (friction detection vs smooth run bypass) so the Agent considers whether to run `project-retro` at workflow conclusion without adding unnecessary overhead.
  4. Structured progressive disclosure: Kept `SKILL.md` concise; extracted detailed inspection checklists, decision heuristics, and output formats into `references/categories.md`, `references/heuristics.md`, and `references/template.md`.
  5. Decoupled from upstream runtime: Self-contained first-party package with zero runtime dependencies on `mattpocock/skills`. Added comprehensive contract and behavior test suites under `tests/`.
  6. Workflow-aware retrospective evolution: Extended Matt's environment improvement focus (navigation, automated checks, coding standards, steering, tool economy, information access) into a workflow-aware retrospective engine incorporating current-state deduplication against repository HEAD, tri-state finding classification (CLOSED / PARTIAL / OPEN), permanent guardrail extraction, test architecture & cross-repo isolation, and release mechanics.

Verification: `SKILL.md` frontmatter `name: project-retro` matches, `agents/openai.yaml` is valid with `allow_implicit_invocation: true`, MIT attribution is preserved, and no external runtime coupling remains.
