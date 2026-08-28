# v0.2.0 — Light Workflow 33-Skill Architecture

[中文发布说明](https://github.com/LightDevCoder/skills/blob/main/docs/evidence/releases/v0.2.0/RELEASE_NOTES.zh-CN.md) · [Release Receipt](https://github.com/LightDevCoder/skills/blob/main/docs/evidence/releases/v0.2.0/RELEASE_RECEIPT.md)

## What's new

Light Skills v0.2.0 introduces the complete 33 first-party Skill architecture (expanded from 9 packages in v0.1.6 to 33 packages), covering end-to-end project development workflows, the Socratic clarification engine, execution and review subsystems, and the comprehensive collection advisor `ask-light`.

## Core Architecture Evolution

1. **Project Workflow Lifecycle:**
   - Standardized lifecycle: `project-init` → `project-clarify` → `project-spec` → `project-tickets` → `implement` → `project-review` → `release-workflow`.
   - Clear input/output contracts and artifact handoff boundaries at each stage, supporting both end-to-end delivery and single-stage invocation.

2. **Socratic Clarification & Decision Engine:**
   - Core engine `socratic` powers independent multi-round questions and option frontier exploration.
   - Powers lightweight clarification `clarify`, engineering-aware `project-clarify`, and multi-session `decision-map`.

3. **Execution & Specialist Review Subsystems:**
   - `agent-config` inspects host environment evidence to plan safe execution paths.
   - `review-loop` provides lightweight review-repair convergence; `generic-review` and `code-review` act as read-only specialist reviewers; `project-review` governs frozen baselines and final verdicts (`PASS`/`FAIL`/`BLOCKED`).

4. **Self-Contained Approved Ports & Provenance:**
   - 11 approved self-contained Matt Ports with `ATTRIBUTION.md` and zero upstream runtime dependencies.
   - Incorporated `eli5` (from `DreambigOu/ELI5`) and `release-workflow` (from `LightDevCoder/release-workflow`) into unified collection governance with complete migration and retirement records.

5. **Collection Advisor:**
   - `ask-light` serves as the read-only router and workflow advisor across all 33 Skills, suggesting next actions based on workspace context.

## Installation & Verification

- **Interactive Install (Recommended):**
  ```bash
  npx skills add LightDevCoder/skills
  ```
- **Pinned Stable Release:**
  ```bash
  npx skills add LightDevCoder/skills#v0.2.0
  ```
- **Single Skill Example:**
  ```bash
  npx skills add LightDevCoder/skills --skill project-review
  ```

**Verification:** Local automated test suites (309 pytest, 27 unittest, compileall, git diff check) and GitHub Actions CI (Run ID `33137041472`) all PASS. Fresh isolated environment tests verified generic latest and pinned `#v0.2.0` across whole-collection and all 33 individual package install matrices (66/66 PASS).

---

## 中文说明

完整中文发布说明请访问：[RELEASE_NOTES.zh-CN.md](https://github.com/LightDevCoder/skills/blob/main/docs/evidence/releases/v0.2.0/RELEASE_NOTES.zh-CN.md)
