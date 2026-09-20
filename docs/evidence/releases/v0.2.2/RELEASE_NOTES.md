# v0.2.2 — Jev Integration Stabilization & Release Integrity

[中文发布说明](https://github.com/LightDevCoder/skills/blob/main/docs/evidence/releases/v0.2.2/RELEASE_NOTES.zh-CN.md) · [Release Receipt](https://github.com/LightDevCoder/skills/blob/main/docs/evidence/releases/v0.2.2/RELEASE_RECEIPT.md)

Light Skills v0.2.2 establishes a permanent, immutable release boundary for the 36-package collection, ships the finalized TypeSafe Jev System One semantic acceleration across `ask-light`, `agent-config`, and `project-init`, organizes all packages into seven purpose-based categories, and clarifies release provenance following tag movements in earlier release cycles.

---

## What's new in v0.2.2

### 1. Release Integrity & Immutable Release Boundary
- **Immutable Tag Policy:** Starting with v0.2.2, published release tags are permanently immutable. A published release tag is never force-moved, retargeted, or rewritten. Any post-release maintenance is handled strictly via documented metadata corrections that do not move the tag or via a new patch release.
- **Provenance Resolution:** v0.2.1 was originally released against an earlier commit (`70a48ef`, recorded as `cb17b17c8227b7d7211e4bf5b72223703d987d60`) and its tag was subsequently repointed during the rapid Jev integration stabilization cycle. Release v0.2.2 establishes a clean, immutable release snapshot for all downstream consumers.

### 2. Finalized `ask-light` Semantic Routing & Query Planning
- **Deterministic Workflow Authority:** Python code establishes trustworthy project facts and computes legal workflow candidate actions. Semantic inference never overrides deterministic state machine invariants.
- **Active Consumer Query Planning:** Bounded Jev queries are executed **only** when a semantic judgment has an active consumer that materially influences the outcome:
  - **Choice:** Invoked strictly when multiple legal candidate actions exist (`len(allowed_actions) > 1`). Singleton candidate sets skip Choice completely.
  - **Material Ambiguity (Noul):** Sent only when multiple candidates include `project-clarify` (to disambiguate clarification from execution) or when `implement` is the sole candidate and user phrasing expresses material ambiguity. If `project-clarify` is already the only legal action, the query is skipped as zero-value inference.
  - **Reasoning Escalation (Noul):** Sent only when `implement` is in candidate actions and the user request expresses high architectural complexity, assessing whether escalation to `agent-config` is warranted.
- **Workflow Authority Invariant:** Jev outputs never grant workflow transition authority. Execution intent queries have been removed; workflow transition authority is strictly code-owned and requires explicit user consent.
- **Compact State Builder:** Sanitized compact state representations (<350 bytes) without raw code or file tree leakage.
- **Fail-Closed & Offline Fallback:** When `TYPESAFE_API_KEY` is absent or the SDK is uninstalled, `ask-light` degrades smoothly to its deterministic baseline with zero regression across all test suites.

### 3. `project-init` Canonical Skills CLI Mappings & Optional Jev Onboarding
- **Optional Ecosystem Onboarding:** Interactive opt-in gate (`--jev` / `--no-jev` non-interactive flags) for initializing TypeSafe Jev acceleration into newly scaffolded repositories. When omitted or declined, the standard project initialization flow proceeds unchanged.
- **Official Skills CLI Conventions:** Mappings adhere strictly to `vercel-labs/skills` v1.7.0 CLI conventions:
  - Canonical agent identifiers: `pi`, `claude-code`, `cursor`, `codex`, `antigravity`, `grok`, `hermes-agent`.
  - Canonical project scopes: `.agents/skills` for Cursor, Codex, and Antigravity; `.pi/skills` for Pi; `.claude/skills` for Claude Code; `.grok/skills` for Grok; `.hermes/skills` for Hermes.
- **Fail-Closed Unsupported Hosts:** Unsupported environments (such as DeepSeek Harness / DSH) fail closed deterministically (`TARGET_UNRESOLVED`, zero installer invocations, no guessed CLI IDs).
- **Safe Credential Management:** Resolves `TYPESAFE_API_KEY` first from process environment (`os.environ`), then from the active project `.env`.
- **Gitignore Protection:** Guarantees `.env` is committed to `.gitignore` before writing any project-local credentials. Secrets never appear in logs, receipts, diffs, or release artifacts.
- **Global Skill Reuse:** Reuses existing global `typesafe-ai` installations when available, avoiding redundant downloads.

### 4. `agent-config` Abstract Task Profiling & Provisional Downgrade Guard
- **Clear Authority Split:**
  - **Jev:** Provides vendor-neutral abstract task profiling (complexity level, reasoning need) and advisory judgments.
  - **agent-config Deterministic Policy:** Governs authority boundaries, baseline protection, candidate validation, host capability adaptation, fallback, and preview approval gates.
  - **User / Profile:** Confirmed profiles grant explicit authorization for configuration changes.
- **Vendor-Independent Abstraction:** Abstract tiers (`routine`, `standard`, `high`) and reasoning needs (`low`, `medium`, `high`) decouple task requirements from specific model names.
- **Label-Clean Evaluation:** Authoritative task inputs (`explicit-user`, `verified-ticket`, `explicit-policy`) are strictly code-owned and never queried from Jev. Jev evaluation fixtures never leak ground truth difficulty labels into prompt context.
- **Provisional Asymmetric Downgrade Policy:**
  - Capability upgrades (safe direction): standard threshold `0.50`.
  - Baseline holds: standard threshold `0.50`.
  - Capability downgrades (reducing capability below baseline): requires stronger evidence with confidence threshold `0.75` and boundary margin `0.15`.
  - **Policy Status:** `PROVISIONAL` (empirically grounded; not claiming universal calibration).
  - **Live Evaluation Evidence (AC-02):** A proposed downgrade from baseline `standard` to `routine` was safely rejected due to marginal confidence (0.59 < 0.75) and boundary proximity (score 0.41), correctly retaining the `standard` tier (`claude-3-5-sonnet`).

### 5. Purpose-Based Category Organization (36 Admitted Skills)
All 36 first-party Skills are organized into seven documented categories under `skills/`:
- **`project/` (7):** `project-init`, `project-clarify`, `project-spec`, `project-tickets`, `implement`, `kanban-worker`, `release-workflow`.
- **`thinking/` (5):** `clarify`, `decision-map`, `research`, `socratic`, `to-questionnaire`.
- **`engineering/` (5):** `agent-config`, `diagnosing-bugs`, `prototype`, `resolving-merge-conflicts`, `tdd`.
- **`review/` (4):** `code-review`, `generic-review`, `project-review`, `review-loop`.
- **`knowledge/` (5):** `eli5`, `kb-init`, `language-learning`, `learn-anything`, `teach`.
- **`writing/` (3):** `humanizer`, `manuscript-ops`, `writing-for-agents`.
- **`productivity/` (7):** `ask-light`, `handoff`, `light-travelpage`, `project-retro`, `recap`, `wait-what`, `wizard`.

Host installation remains flat (`<skills-root>/<name>/`), and CLI invocation (`npx skills add ... --skill <name>`) remains unchanged.

---

## Installation

### Stable Pinned Snapshot (v0.2.2)
To install the immutable, reproducible v0.2.2 release snapshot:

```bash
# Entire 36-skill collection:
npx skills add LightDevCoder/skills#v0.2.2 -y

# Individual skills:
npx skills add LightDevCoder/skills#v0.2.2 --skill agent-config -y
npx skills add LightDevCoder/skills#v0.2.2 --skill ask-light -y
npx skills add LightDevCoder/skills#v0.2.2 --skill project-init -y
```

### Latest Default (main)
To install the latest development state from the default branch:

```bash
npx skills add LightDevCoder/skills -y
```

---

## Provenance Note

Release `v0.2.1` was originally published on 2026-09-16 against commit `70a48ef` (receipt recorded `cb17b17c8227b7d7211e4bf5b72223703d987d60`) introducing `project-retro` and `light-travelpage`. During the subsequent TypeSafe Jev integration hardening cycle (2026-09-20), the `v0.2.1` tag was moved to follow ongoing integration commits (`6f9d173`, then `27f16e4`).

Release `v0.2.2` establishes the new immutable release boundary, formally shipping the finalized Jev integration, category layout, and documentation corrections under a permanently stable tag.
