# Project delivery

[简体中文](README.zh-CN.md)

Frame a project, settle its requirements, implement bounded work, then release and learn from the result.

Categories organize browsing; they add no workflow or approval gates. Each package’s `SKILL.md` is the behavior authority.

## User-invoked

- **[project-init](project-init/SKILL.md)** — Idempotently bootstrap the stable Light project and tracker contracts consumed by downstream Project Skills.
- **[project-clarify](project-clarify/SKILL.md)** — Clarify a real project's unresolved decisions from inspected project facts; returns a bounded handoff for `project-spec`. Uses the same frontier-round interaction as `clarify` with project-aware evidence.
- **[project-spec](project-spec/SKILL.md)** — Turn already-clarified outputs into a formal project SPEC without reopening an interview.
- **[project-tickets](project-tickets/SKILL.md)** — Turn an approved SPEC into a dependency-ordered, tracer-bullet ticket graph.
- **[implement](implement/SKILL.md)** — Execute one bounded, already-decided work item (code, doc, config, Skill, generic task) with verification and review handoff.

## Model- or user-invoked

- **[kanban-worker](kanban-worker/SKILL.md)** — Pick up and execute one Light-Kanban task per scheduled run; resumes owned work and `reviewFeedback` before new claims.
- **[release-workflow](release-workflow/SKILL.md)** — Publish a completed project — synchronize docs, run quality gates, tag, and release.
- **[project-retro](project-retro/SKILL.md)** — Conduct a retrospective on a completed project or coding session, identifying environment, guardrail, navigation, tool economy, and workflow improvements.

[All categories](../README.md) · [Full catalog](../../CATALOG.md)
