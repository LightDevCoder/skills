# 06 — Repository Governance, Catalog & Workflow Documentation Sync

**What to build:** Synchronize repository governance documents, catalog entries, and workflow guides to reflect agent-config's updated core purpose as a model-aware execution configurator across four execution modes, updating changelogs without modifying stable release tags.

**Blocked by:** 03 — Core SKILL.md Refactor & openai.yaml Agent Definition, 05 — Downstream implement & ask-light Migration

**Status:** resolved

- [x] `AGENTS.md` updates reference rule 2 to describe `agent-config` as provider-neutral routing by evidenced model capability, effort control, and execution topology with safe fixed-model fallback, retaining the prohibition against guessing host capabilities.
- [x] `CATALOG.md` and `CATALOG.zh-CN.md` update `agent-config` entry to "Host-aware model and execution configurator" with purpose reflecting model tier right-sizing, reasoning effort, and topology.
- [x] `README.md` and `README.zh-CN.md` update descriptions of `agent-config` in execution tables and workflows.
- [x] `docs/workflows/execution.md` and `docs/zh-CN/workflows/execution.md` document the updated interaction: optional `implement → agent-config` right-sizing, ticket graph planning after `project-tickets`, and four execution modes.
- [x] Four distinct quadrant examples (Multi+Small, Multi+Large, Single+Small, Single+Large) are documented in `agent-config` references or execution docs.
- [x] `CHANGELOG.md` and `CHANGELOG.zh-CN.md` document the architecture refactor under unreleased changes without modifying released version numbers or tags.

## Comments

Source: .scratch/agent-config-refactor/spec.md. §26, §27, §28, §39.

## Answer

Updated governance documents: `AGENTS.md` rule 2, `CATALOG.md`, `CATALOG.zh-CN.md`, `docs/workflows/execution.md`, and `docs/zh-CN/workflows/execution.md`. Added `skills/agent-config/references/examples.md` detailing the four execution quadrants. Recorded unreleased changes in `CHANGELOG.md` and `CHANGELOG.zh-CN.md` without modifying release tags.
