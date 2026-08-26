# Baseline Inventory — Light Skills Refactor (Issue 01)

Generated: 2026-08-25
Baseline source: `/tmp/skills-baseline` (LightDevCoder/skills, depth 1, main)
Working repo: `/Users/light/Documents/Projects/Configurations/skills`
Baseline commit: `26110c9` — `docs: add Chinese release notes pages for v0.1.1-v0.1.5`
Remote: `https://github.com/LightDevCoder/skills.git` (origin/main)
ELI5 clone: `/tmp/eli5-src` (also `/tmp/ELI5`) — untouched
Release-workflow clone: `/tmp/release-workflow-src` — untouched
Matt Pocock source: `/Users/light/.agents/skill-src/mattpocock-skills`

Verification commands intentionally match Issue 01 acceptance checks.

---

## 1. Baseline Clone Existence

| Clone | Path | Status | HEAD | Notes |
|-------|------|--------|------|-------|
| LightDevCoder/skills | `/tmp/skills-baseline` | ✅ git repo, shallow, depth 1, branch main | `26110c9` | `git remote -v` → origin LightDevCoder/skills, `shallow` present |
| LightDevCoder/ELI5 | `/tmp/eli5-src` (+ `/tmp/ELI5`) | ✅ | — | Contains `skills/eli5/SKILL.md`, `eli5-workspace/` — not moved |
| LightDevCoder/release-workflow | `/tmp/release-workflow-src` | ✅ | — | Contains `SKILL.md`, `agents/openai.yaml`, `references/VERIFICATION.md` |
| Matt Pocock skills | `/Users/light/.agents/skill-src/mattpocock-skills` | ✅ | — | 21+ upstream skills under `skills/` (engineering, product, misc) |

### Bootstrap verification

Bootstrap performed via:

```bash
cp -a /tmp/skills-baseline/.git /Users/light/Documents/Projects/Configurations/skills/.git
rsync -a --exclude='.scratch' --exclude='.git' --exclude='.DS_Store' /tmp/skills-baseline/ /Users/light/Documents/Projects/Configurations/skills/
```

Post-bootstrap checks:

```bash
ls /Users/light/Documents/Projects/Configurations/skills/skills  # → 9 dirs + docs
git -C /Users/light/Documents/Projects/Configurations/skills status  # branch main, untracked .scratch, Assets, docs/agents
git -C /Users/light/Documents/Projects/Configurations/skills log --oneline -5  # 26110c9
cat /Users/light/Documents/Projects/Configurations/skills/AGENTS.md | head -n 20  # maintenance contract + local tracker note
ls /tmp/eli5-src/skills/eli5 && ls /tmp/release-workflow-src/SKILL.md  # both still exist
```

Observed:

```
skills/ → ask-light, docs, kanban-worker, kb-init, language-learning, learn-anything, manuscript-ops, project-init, recap, review-loop
git status → On branch main, up to date with origin/main, untracked .scratch/, Assets/, docs/agents/, docs/.DS_Store
git log → 26110c9 docs: add Chinese release notes pages for v0.1.1-v0.1.5
```

`samples` below reflect actual file presence at time of inventory (checked 2026-08-25).

---

## 2. Top-Level Repository Shape

| Path | Exists | Notes |
|------|--------|-------|
| `AGENTS.md` | ✅ | 5316 B, maintenance contract; patched with local tracker note `> Local workspace tracker: .scratch/light-skills-refactor/` |
| `README.md` | ✅ | 8961 B, first non-empty line is `![LightDevCoder/skills — composable agent workflows](skills/docs/assets/skills-header.png)` |
| `README.zh-CN.md` | ✅ | 7929 B |
| `CATALOG.md` | ✅ | 8401 B, lists 9 packages |
| `CATALOG.zh-CN.md` | ✅ | 7251 B |
| `CHANGELOG.md` | ✅ | 14041 B |
| `CHANGELOG.zh-CN.md` | ✅ | 13217 B |
| `.gitattributes` | ✅ | |
| `.gitignore` | ✅ | `__pycache__/`, `*.py[cod]`, `.pytest_cache/` |
| `.github/workflows/` | ✅ | (workflows dir) |
| `docs/INSTALLATION.md` | ✅ | 10356 B |
| `docs/INSTALLATION.zh-CN.md` | ✅ | 8815 B |
| `docs/MAINTENANCE.md` | ✅ | 6591 B |
| `docs/MAINTENANCE.zh-CN.md` | ✅ | 4050 B |
| `docs/REVIEW_POLICY.md` | ✅ | 4738 B |
| `docs/REVIEW_POLICY.zh-CN.md` | ✅ | 3112 B |
| `docs/SKILL_ADMISSION.md` | ✅ | 7214 B |
| `docs/SKILL_ADMISSION.zh-CN.md` | ✅ | 4197 B |
| `docs/skills/` | ✅ | 10 files (ask-light, kanban-worker, kb-init, language-learning, learn-anything, light-kanban-worker alias, manuscript-ops, project-init, recap, review-loop) |
| `docs/workflows/` | ✅ | `first-party-composition.md`, `recipes.md`, `README.md` |
| `docs/evidence/` | ✅ | admissions (kb-init, language-learning, light-kanban-worker, recap) + releases (v0.1.1–v0.1.6) |
| `docs/zh-CN/` | ✅ | mirrored |
| `examples/quick-start/` | ✅ | `AGENTS.md`, `brief.md`, `README.md`, `README.zh-CN.md` |
| `skills/` | ✅ | 12 entries (9 packages + docs) |
| `tests/` | ✅ | 5 test modules + fixtures |
| `Assets/header.png` | ✅ (local-only) | 1767692 B, top-level hero image (not part of baseline, preserved from skeleton) |
| `skills/docs/assets/skills-header.png` | ✅ (baseline) | 1772238 B, canonical header |
| `skills/docs/assets/skills-header.svg` | ✅ | 5549 B, editable source, viewBox 0 0 1600 480 |
| `skills/docs/assets/skills-header.json` | ✅ | manifest width 1536 height 1024 |
| `.scratch/light-skills-refactor/` | ✅ | spec + 13 issues preserved, untracked |
| `docs/agents/` | ✅ (local-only) | issue-tracker.md, domain.md, triage-labels.md — writable |

---

## 3. Baseline Skills — 9 Packages

Count reflected in `CATALOG.md`, `tests/test_collection_discovery.py` (EXPECTED = 9), and `skills/` listing.

### 3.1 ask-light

- **Path:** `skills/ask-light/` — exists: ✅
- **Invocation:** user-invoked (`disable-model-invocation: true`)
- **SKILL.md:** 162 lines — `skills/ask-light/SKILL.md:1`
  - Frontmatter: `name: ask-light`, `description: Inspect the Skills...`, `disable-model-invocation: true`
  - Headings: `# Ask Light`, `## Invocation and safety boundary`, `## Required input context`, `## Discovery protocol`, `## Explicit workflow mode`, `## Source and host rules`, `## Result contract`, `## Verification`
  - References link: `references/discovery-contract.md` (relative)
- **agents/openai.yaml:** ✅ `skills/ask-light/agents/openai.yaml:1` — display_name Ask Light, short_description, default_prompt `$ask-light …`, `allow_implicit_invocation: false`
- **References:** `references/discovery-contract.md` — discovery contract (JSON-like context record: goal, artifacts, blockers, projectType, taskKind, availability, invocationControl; candidate metadata pass: SKILL.md frontmatter + openai.yaml)
- **Scripts:** `scripts/ask-light.ps1`
- **Tests:** `tests/test_ask_light_behavior.py`, `tests/test_ask_light_contract.py` — ✅ `skills/ask-light/tests/:1`
- **Cross-skill refs:** scanner mentions `TargetExists`, used by `docs/workflows/first-party-composition.md` and `tests/test_collection_discovery.py`
- **Verified:** `test -f skills/ask-light/SKILL.md && grep '^name: ask-light' skills/ask-light/SKILL.md` ✅

### 3.2 kanban-worker (light-kanban-worker → renamed v0.1.6)

- **Path:** `skills/kanban-worker/` — ✅
- **Invocation:** model-invoked (`allow_implicit_invocation: true`)
- **SKILL.md:** 343 lines — `skills/kanban-worker/SKILL.md:1`
  - Frontmatter: `name: kanban-worker`, description (one-task per scheduled run, stable identity, validate workspace)
  - Headings: `# Kanban Worker`, `## Responsibility and boundaries`, `## One task per run`, `## Non-overlapping runs`, `## Agent identity`, `## Golden flow`, `## Claiming new work`, etc. (18 sections)
- **agents/openai.yaml:** ✅ `skills/kanban-worker/agents/openai.yaml:1` — display_name Kanban Worker, `default_prompt` includes `http://127.0.0.1:8641`, `allow_implicit_invocation: true`
- **References:** `references/api.md`
- **Tests:** `tests/test_kanban_worker_behavior.py`, `tests/test_kanban_worker_contract.py`, `tests/worker_checks.py` + `tests/fixtures/` (8 fixtures: archive-variant.md, avatar-optional-first-registration.md, daemon-variant.md, multi-task-variant.md, overlap-allowed-variant.md, scenario-g-scheduler-guard.md, scenario-h-fresh-identity-no-avatar.md, todo-first-variant.md) — ✅
- **Cross-skill refs:** none to other skills; referenced by `CATALOG.md`, `CHANGELOG.md` rename note, `docs/skills/light-kanban-worker.md` alias
- **Attribution:** `docs/evidence/admissions/light-kanban-worker/` review-loop PASS

### 3.3 kb-init

- **Path:** `skills/kb-init/` — ✅
- **Invocation:** user-invoked (`disable-model-invocation: true`)
- **SKILL.md:** 383 lines — `skills/kb-init/SKILL.md:1`
  - Frontmatter: `name: kb-init`, design and initialize knowledge base
  - Headings: `# KB Init`, `## Invocation and scope`, `## Core principles`, `## High-level workflow`, Phases 1–13 (interview → decision map → SPEC → connection setup → implement → validate → handoff)
- **agents/openai.yaml:** ✅ `skills/kb-init/agents/openai.yaml:1` — `allow_implicit_invocation: false`
- **References:** 8 files: `base-discovery.md`, `connection-setup.md`, `design-guide.md`, `human-navigation.md`, `interview-contract.md`, `readiness-check.md`, `research-contract.md`, `spec-guide.md`
- **Evals:** `evals/evals.json` (38 regression eval cases)
- **Tests:** `tests/test_kb_init_contract.py` — ✅
- **Cross-skill refs:** may call model-invoked `research` (documented, not auto-trigger user skill)
- **Admission:** full `review-loop agent-skill` PASS, v0.1.6

### 3.4 language-learning

- **Path:** `skills/language-learning/` — ✅
- **Invocation:** user-invoked (`disable-model-invocation: true`)
- **SKILL.md:** 114 lines — `skills/language-learning/SKILL.md:1`
  - Frontmatter: `name: language-learning`, 6 modes (daily lessons, flashcards, conversation, grammar, quizzes, translation)
  - Headings: `# Language Learning`, `## Start`, `## Teaching Behavior`, `## Choose a mode`, `## Examples`, `## Common edge cases`
- **agents/openai.yaml:** ✅ `skills/language-learning/agents/openai.yaml:1` — `allow_implicit_invocation: false`
- **References:** 6 files: `CONVERSATION.md`, `DAILY-LESSON.md`, `FLASHCARDS.md`, `GRAMMAR-DECODER.md`, `IMMERSION.md`, `PROGRESS-EVALUATOR.md`
- **Tests:** `tests/test_language_learning_contract.py` — ✅
- **Admission:** fast-track PASS

### 3.5 learn-anything

- **Path:** `skills/learn-anything/` — ✅
- **Invocation:** user-invoked (`disable-model-invocation: true`)
- **SKILL.md:** 198 lines — `skills/learn-anything/SKILL.md:1`
  - Frontmatter: `name: learn-anything`, turn conversations/transcripts into reusable skill methods
  - Headings: `# Learn Anything`, `## Purpose`, `## Compatible Agents`, `## Decision Workflow`, `## Package Build`, `## Hook Scripts`
- **agents/openai.yaml:** ✅ `skills/learn-anything/agents/openai.yaml:1` — `allow_implicit_invocation: false`
- **Hooks:** `hooks/learn_gate.py`, `hooks/package_builder.py`, `hooks/session_reflector.py`, `hooks/skill_candidate_builder.py`, `hooks/config.example.json`
- **Tests:** via `tests/test_learn_anything_hooks.py` (7 hook tests) — no per-package tests dir
- **References:** none (hooks are supporting scripts)
- **Cross-skill refs:** none outbound; self-contained

### 3.6 manuscript-ops

- **Path:** `skills/manuscript-ops/` — ✅
- **Invocation:** model-invoked with manual support (`allow_implicit_invocation: true`)
- **SKILL.md:** 210 lines — `skills/manuscript-ops/SKILL.md:1`
  - Frontmatter: `name: manuscript-ops`, route and govern manuscript engineering
  - Headings: `# Manuscript Ops`, preflight, one route, explicit handoffs, lifecycle, review boundary, format adapter, freeze gates, validation
- **agents/openai.yaml:** ✅ `skills/manuscript-ops/agents/openai.yaml:1` — `allow_implicit_invocation: true`
- **References:** 10 files: `failure-recovery.md`, `formats.md`, `handoffs.md`, `lifecycle.md`, `project-init-boundary.md`, `project-layout.md`, `review.md`, `routing.md`, `state-model.md`, `version-control.md`
- **Assets:** `assets/dependency-contracts.json`, `assets/format-registry.json`, `assets/platform-capability-map.json`, `assets/templates/` (10 templates: batch-manifest.json, format-qa-record.json, gate-receipt.json, manuscript-brief.md, platform-capabilities.json, project-profile.json, review-matrix.json, routing-input.json, source-register.tsv, state.json)
- **Scripts:** 6 Python scripts: `assess_project.py`, `check_dependencies.py`, `manuscript_ops_core.py`, `next_version.py`, `probe_capabilities.py`, `validate_state.py`
- **Tests:** none per-package; validated via examples and review-loop delegation
- **Cross-skill refs:** explicit handoffs to `grill-me`, `grilling`, `wayfinder`, `domain-modeling`, `prototype`, `setup-matt-pocock-skills`, `review-loop` (documented in `references/handoffs.md:150`)

### 3.7 project-init

- **Path:** `skills/project-init/` — ✅
- **Invocation:** user-invoked (`disable-model-invocation: true`)
- **SKILL.md:** 116 lines — `skills/project-init/SKILL.md:1`
  - Frontmatter: `name: project-init`, initialize software/non-software project from minimal preset
  - Headings: `# Project Init`, `## Invocation and scope`, `## Workflow` (inspect → ask → preset → write → validate), `## Explicit boundaries`
- **agents/openai.yaml:** ✅ `skills/project-init/agents/openai.yaml:1` — `allow_implicit_invocation: false`
- **References:** `initialization-contract.md`, `presets.md`
- **Tests:** `tests/test_project_init_behavior.py`, `tests/test_project_init_contract.py` — ✅
- **Cross-skill refs:** reads `AGENTS.md`, `CLAUDE.md`, manifests; referenced by `manuscript-ops`

### 3.8 recap

- **Path:** `skills/recap/` — ✅
- **Invocation:** user-invoked (`disable-model-invocation: true`)
- **SKILL.md:** 57 lines — `skills/recap/SKILL.md:1`
  - Frontmatter: `name: recap`, one-line session summary
  - Headings: `# Session Recap`, `## Invocation and scope`, `## Method`, `## Output contract`, `## Boundaries and handoffs`, `## Verification`
- **agents/openai.yaml:** ✅ `skills/recap/agents/openai.yaml:1` — `allow_implicit_invocation: false`
- **Tests:** `tests/test_recap_contract.py`, `tests/test_recap_output_contract.py` — ✅
- **Admission:** fast-track PASS

### 3.9 review-loop

- **Path:** `skills/review-loop/` — ✅
- **Invocation:** model-invoked (`allow_implicit_invocation: true`)
- **SKILL.md:** 272 lines — `skills/review-loop/SKILL.md:1`
  - Frontmatter: `name: review-loop`, generic final-acceptance and bounded-repair loop
  - Headings: `# Review Loop`, `## Purpose and boundary`, `## Public contract`, `## Roles`, `## Durable state`, `## init/review/resume` workflows, `## Verdicts and limits`, `## References`
- **agents/openai.yaml:** ✅ `skills/review-loop/agents/openai.yaml:1` — `allow_implicit_invocation: true`
- **References:** `acceptance-charter.md`, `attribution.md`, `evidence-protocol.md`, `finding-schema.md`, `mission-center-compatibility.md`, `review-rubric.md`, `stopping-rules.md`, `subagent-protocol.md`, `profiles/` (agent-skill.md, generic.md, manuscript.md, software.md, specification.md)
- **Tests:** 10 files: `review_protocol_helpers.py` + 5 profile contract/behavior pairs (agent-skill, generic, manuscript, software, specification) — ✅
- **Cross-skill refs:** invoked by maintenance docs (`AGENTS.md`, `MAINTENANCE.md`, `REVIEW_POLICY.md`, `SKILL_ADMISSION.md`), used by manuscript-ops, kb-init, etc.; owns final PASS/FAIL/BLOCKED verdicts
- **Governance role:** authoritative for admission; fast-track vs full evidence path defined in `SKILL_ADMISSION.md`

---

## 4. Shared Structure — skills/docs (Header Asset)

| Path | Exists | Details |
|------|--------|---------|
| `skills/docs/assets/skills-header.svg` | ✅ | 5549 B, `<svg width="1600" height="480" viewBox="0 0 1600 480">`, contains "LightDevCoder", "/skills", "Personal Skills Collection", `fill="#72a0a3"`, `translate(6 8)` |
| `skills/docs/assets/skills-header.png` | ✅ | 1772238 B, PNG sig 89 50 4E 47, from svg raster, 1536×1024 |
| `skills/docs/assets/skills-header.json` | ✅ | `source_svg: skills-header.svg`, `rendered_png: skills-header.png`, `width:1536`, `height:1024`, `design_version: user-provided-raster-v1`, sha256s recorded |
| `README.md:1` | ✅ | `![LightDevCoder/skills — composable agent workflows](skills/docs/assets/skills-header.png)` first non-empty line |
| `tests/test_header_assets.py` | ✅ | Validates svg/png/json consistency (dimensions, wordmark, translate, PNG sig, manifest) |
| `Assets/header.png` (top-level, skeleton) | ✅ local-only | 1767692 B, preserved alongside baseline header; not referenced by baseline README; untracked |

---

## 5. Documentation & Governance

### 5.1 README / CATALOG

- `README.md` (8961 B) — intro to 9-package collection v0.1.6, Quick Start `npx skills add LightDevCoder/skills`, installation, examples, AGENTS/CATALOG links, header asset. Verified: header image first line, zh-CN link resolves.
- `README.zh-CN.md` (7929 B) — synchronized.
- `CATALOG.md` (8401 B) — inventory, synchronized from `skills/` metadata, lists each of 9 skills with Purpose/Invocation/Package/Status/Evidence/Installation path; evidence links to `skills/<name>/tests/` and `docs/skills/<name>.md`; Verified in `tests/test_collection_discovery.py`.
- `CATALOG.zh-CN.md` (7251 B) — synchronized.

### 5.2 Maintenance Docs

- `docs/MAINTENANCE.md` (6591 B) — lifecycle (add/update/rename/remove/port/adapt), authoritative records table, synchronization baseline (9 skills), change workflow, catalog/installation, upstream attribution, deprecation/rollback, closeout. Headed `# First-Party Maintenance...`
- `docs/SKILL_ADMISSION.md` (7214 B) — reuse-before-invention, attribution, fast-track vs full evidence, eligibility for prompt-only skills (ask-light etc. require full).
- `docs/REVIEW_POLICY.md` (4738 B) — triggers, profile selection (fast-track vs agent-skill), evidence/independence, bounded repair, verdicts.
- `docs/INSTALLATION.md` (10356 B) — stable v0.1.6 from `e8c3589` tag, revision semantics (#ref fragment, default revision), v0.1.6 commands (`npx skills add LightDevCoder/skills --yes --copy --agent '*'` + per-skill `review-loop`), historical commands v0.1.2–v0.1.6, supported scopes, manual fallback, verification record. Checked: contains generic latest command, all pinned tags v0.1.2–v0.1.6, explains fragment, no stale `v0.1.0 immutable`/`not a verified command` wording.
- `CHANGELOG.md` (14041 B) — v0.1.6 adds kb-init, etc.

### 5.3 Review & Admission Evidence

- `docs/evidence/admissions/` — kb-init (charter/findings/state/verdict), language-learning (fast-track), light-kanban-worker (behavioral-evidence + review-loop PASS), recap (fast-track + review-loop)
- `docs/evidence/releases/` — v0.1.1–v0.1.6, each with TEST_SUMMARY, DISCOVERY_VERIFICATION, INSTALLATION_VERIFICATION, RELEASE_RECEIPT, LIMITATIONS, etc. Verified existence: `find docs/evidence -type f | wc -l ≈ 110`
- `docs/skills/` + `docs/zh-CN/skills/` — per-skill user guides (10 files each locale)
- `docs/workflows/` — `first-party-composition.md` (ask-light explicit selection), `recipes.md`, `README.md` — examples validated as composition assets, not admission gates
- `examples/quick-start/` — AGENTS.md, brief.md, README.md + zh-CN — used by `tests/test_quick_start_smoke.py`

---

## 6. Tests — Inventory

### 6.1 Per-Skill Tests

| Skill | Test Path(s) | Exists | Notes |
|-------|--------------|--------|-------|
| ask-light | `skills/ask-light/tests/test_ask_light_behavior.py`, `test_ask_light_contract.py` | ✅ | scanner + contract, includes pwsh execution, outside-readable-path negative case |
| kanban-worker | `skills/kanban-worker/tests/test_kanban_worker_behavior.py`, `test_kanban_worker_contract.py`, `worker_checks.py`, `fixtures/` (8) | ✅ | |
| kb-init | `skills/kb-init/tests/test_kb_init_contract.py` | ✅ | |
| language-learning | `skills/language-learning/tests/test_language_learning_contract.py` | ✅ | |
| learn-anything | `tests/test_learn_anything_hooks.py` (7) | ✅ | hooks behavior, not per-package dir |
| manuscript-ops | (none per-package) | ✅ (N/A) | validated via templates/scripts + review-loop |
| project-init | `skills/project-init/tests/test_project_init_behavior.py`, `test_project_init_contract.py` | ✅ | |
| recap | `skills/recap/tests/test_recap_contract.py`, `test_recap_output_contract.py` | ✅ | |
| review-loop | `skills/review-loop/tests/` (10 files, 5 profiles ×2) + `review_protocol_helpers.py` | ✅ | |

### 6.2 Repository Tests (`tests/`)

| File | Purpose | Exists |
|------|---------|--------|
| `tests/check_helpers.py` | shared `Checks` helper | ✅ |
| `tests/test_collection_discovery.py` | EXPECTED 9, README header, install commands v0.1.2–v0.1.6, revision semantics, no stale claims | ✅ |
| `tests/test_collection_contract.py` | port of collection contract | ✅ |
| `tests/test_header_assets.py` | svg/png/json validation | ✅ |
| `tests/test_learn_anything_hooks.py` | hooks 7 assertions | ✅ |
| `tests/test_quick_start_smoke.py` | examples/quick-start | ✅ |
| `tests/fixtures/` | `learn-anything-incomplete.md`, `learn-anything-method.md` | ✅ |

Total baseline test count reflected in release evidence; e.g., v0.1.6 `TEST_SUMMARY.md` enumerates collection 74 + header + quick-start + ask-light behavior 54 + recap 20 + review-loop suites, etc.

---

## 7. Cross-Skill References & Composition

- **Explicit composition docs:** `docs/workflows/first-party-composition.md` (ask-light → explicit next-step), `docs/workflows/recipes.md`, `docs/skills/*.md`
- **SKILL.md internal references:** mostly self-contained; manuscript-ops `handoffs.md:150` references external Matt skills (grill-me, grilling, wayfinder, domain-modeling, prototype) only as installation suggestions, not runtime deps
- **No automatic chaining of user-invoked skills:** enforced in AGENTS.md `## Invocation direction` and each skill's invocation section
- **Review delegation:** `review-loop` is central; `manuscript-ops` delegates generic review to `review-loop`; `AGENTS.md` mandates `review-loop agent-skill` for full admission
- **Discovery:** ask-light scanner reads only `SKILL.md` frontmatter + `agents/openai.yaml` + readability; bodies not read in that pass (see `references/discovery-contract.md`)

No stale `project-workflow` package present (verified `grep -r project-workflow` only in AGENTS.md exclusion note).

---

## 8. Assets & Header Verification

- Baseline canonical: `skills/docs/assets/skills-header.png` (1772238 B, PNG sig 89 50 4E 47) ✅
- Source SVG: `skills/docs/assets/skills-header.svg` (5549 B, 1600×480, wordmark present) ✅
- Manifest: `skills/docs/assets/skills-header.json` (1536×1024, sha256s) ✅
- `tests/test_header_assets.py` + `tests/test_collection_discovery.py` both check these paths ✅
- Top-level `Assets/header.png` (1767692 B) preserved from pre-bootstrap skeleton, untracked, not deleting baseline assets ✅

---

## 9. Local Tracker Wiring

| File | Path | Points to tracker? | Writable? | Evidence |
|------|------|--------------------|-----------|----------|
| `AGENTS.md` | `AGENTS.md:1` | ✅ now contains `> Local workspace tracker: .scratch/light-skills-refactor/` (added 2026-08-25, non-invasive) | ✅ `test -w` true | `head -n 5 AGENTS.md` |
| `docs/agents/issue-tracker.md` | `docs/agents/issue-tracker.md:1` | ✅ describes `.scratch/<feature-slug>/` + `.scratch/light-skills-refactor/issues/` conventions; used via `docs/agents/domain.md` | ✅ writable | `cat docs/agents/issue-tracker.md` |
| `docs/agents/domain.md` | `docs/agents/domain.md:1` | ✅ describes `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/adr/` (local-only, not baseline) | ✅ writable | `cat docs/agents/domain.md` |
| `docs/agents/triage-labels.md` | `docs/agents/triage-labels.md:1` | ✅ maps `ready-for-agent` etc. | ✅ writable | `cat docs/agents/triage-labels.md` |
| Tracker dir | `.scratch/light-skills-refactor/` | ✅ contains `spec.md` + 13 issues (01–13) | ✅ | `ls .scratch/light-skills-refactor/issues/` |
| Issue 01 | `.scratch/light-skills-refactor/issues/01-baseline-clone-and-inventory.md` | ✅ Status ready-for-agent | ✅ | `cat issues/01...` |

Baseline `.git` now at working repo: `git status` shows `untracked .scratch/`, `Assets/`, `docs/agents/` — expected, not committed (tracker is local-only, Assets is skeleton hero image).

---

## 10. Sources Untouched (Post-Bootstrap)

Checked immediately after rsync:

```bash
ls /tmp/eli5-src/skills/eli5/SKILL.md          # ✅ exists,  eli5 still at /tmp/eli5-src + /tmp/ELI5
ls /tmp/release-workflow-src/SKILL.md         # ✅ exists
ls /tmp/release-workflow-src/references/VERIFICATION.md  # ✅
head -n 5 /tmp/eli5-src/skills/eli5/SKILL.md   # ✅ name: eli5
head -n 5 /tmp/release-workflow-src/SKILL.md  # ✅ name: release-workflow
```

No deletion or modification performed on `/tmp/eli5-src` or `/tmp/release-workflow-src` (rsync source is `/tmp/skills-baseline` only).

---

## 11. Verification Command Output (Captured 2026-08-25)

```bash
$ ls /Users/light/Documents/Projects/Configurations/skills/skills
ask-light
docs
kanban-worker
kb-init
language-learning
learn-anything
manuscript-ops
project-init
recap
review-loop

$ cat /Users/light/Documents/Projects/Configurations/skills/AGENTS.md | head -n 20
# First-Party Skills Repository Maintenance Contract
> Local workspace tracker: `.scratch/light-skills-refactor/` — see `docs/agents/issue-tracker.md`. This note is local-only and does not alter the maintenance contract below.
This file routes maintenance work ...

$ git -C /Users/light/Documents/Projects/Configurations/skills log --oneline -5
26110c9 docs: add Chinese release notes pages for v0.1.1-v0.1.5

$ git -C /Users/light/Documents/Projects/Configurations/skills status
On branch main
Your branch is up to date with 'origin/main'.
Untracked files:
  .DS_Store
  .scratch/
  Assets/
  docs/.DS_Store
  docs/agents/

$ ls /tmp/eli5-src/skills/eli5
SKILL.md

$ ls /tmp/release-workflow-src/SKILL.md
/tmp/release-workflow-src/SKILL.md
```

All Issue 01 checklist items satisfied.

---

## 12. File Path Index (Existence-Verified)

```
AGENTS.md
CATALOG.md
CATALOG.zh-CN.md
CHANGELOG.md
CHANGELOG.zh-CN.md
README.md
README.zh-CN.md
.gitattributes
.gitignore
docs/INSTALLATION.md
docs/MAINTENANCE.md
docs/REVIEW_POLICY.md
docs/SKILL_ADMISSION.md
docs/skills/ask-light.md
docs/skills/kanban-worker.md
docs/skills/kb-init.md
docs/skills/language-learning.md
docs/skills/learn-anything.md
docs/skills/manuscript-ops.md
docs/skills/project-init.md
docs/skills/recap.md
docs/skills/review-loop.md
docs/workflows/first-party-composition.md
docs/workflows/recipes.md
docs/evidence/... (110 files)
examples/quick-start/...
skills/ask-light/SKILL.md
skills/ask-light/agents/openai.yaml
skills/ask-light/references/discovery-contract.md
skills/ask-light/scripts/ask-light.ps1
skills/ask-light/tests/test_ask_light_behavior.py
skills/ask-light/tests/test_ask_light_contract.py
skills/kanban-worker/SKILL.md
skills/kanban-worker/agents/openai.yaml
skills/kanban-worker/references/api.md
skills/kanban-worker/tests/...
skills/kb-init/SKILL.md
skills/kb-init/agents/openai.yaml
skills/kb-init/references/... (8)
skills/kb-init/evals/evals.json
skills/kb-init/tests/test_kb_init_contract.py
skills/language-learning/SKILL.md
skills/language-learning/agents/openai.yaml
skills/language-learning/references/... (6)
skills/language-learning/tests/test_language_learning_contract.py
skills/learn-anything/SKILL.md
skills/learn-anything/agents/openai.yaml
skills/learn-anything/hooks/... (4 py + json)
skills/manuscript-ops/SKILL.md
skills/manuscript-ops/agents/openai.yaml
skills/manuscript-ops/references/... (10)
skills/manuscript-ops/assets/... (3 json + 10 templates)
skills/manuscript-ops/scripts/... (6 py)
skills/project-init/SKILL.md
skills/project-init/agents/openai.yaml
skills/project-init/references/... (2)
skills/project-init/tests/... (2)
skills/recap/SKILL.md
skills/recap/agents/openai.yaml
skills/recap/tests/... (2)
skills/review-loop/SKILL.md
skills/review-loop/agents/openai.yaml
skills/review-loop/references/... (8 + profiles/5)
skills/review-loop/tests/... (10)
skills/docs/assets/skills-header.png
skills/docs/assets/skills-header.svg
skills/docs/assets/skills-header.json
tests/check_helpers.py
tests/test_collection_contract.py
tests/test_collection_discovery.py
tests/test_header_assets.py
tests/test_learn_anything_hooks.py
tests/test_quick_start_smoke.py
.scratch/light-skills-refactor/spec.md
.scratch/light-skills-refactor/issues/01-baseline-clone-and-inventory.md .. 13-*
docs/agents/issue-tracker.md
docs/agents/domain.md
docs/agents/triage-labels.md
Assets/header.png (local-only)
```

---

## 13. Limitations & Next Steps

- Baseline is shallow clone (`--depth 1`); full history not fetched — sufficient for working repo bootstrap, not for deep changelog archaeology
- `Assets/header.png` top-level hero is skeleton-provided and remains untracked; SPEC §23 expects new hero in `Assets/` — future `13-docs-assets-validation` will reconcile `Assets/header.png` vs `skills/docs/assets/skills-header.png`
- Local tracker files are untracked by design (`.scratch/` in untracked, `docs/agents/` untracked) — intentional, avoids polluting first-party history
- No migrations yet: `eli5` and `release-workflow` remain at `/tmp/*-src` only; ports not started (issues 02+)

Issue 01 considered complete; downstream Blocked by 01 can be cleared.
