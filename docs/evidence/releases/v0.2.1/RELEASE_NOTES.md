# v0.2.1 — Improved Workflow, Agent-Config Refactoring & Light-TravelPage

[中文发布说明](https://github.com/LightDevCoder/skills/blob/main/docs/evidence/releases/v0.2.1/RELEASE_NOTES.zh-CN.md) · [Release Receipt](https://github.com/LightDevCoder/skills/blob/main/docs/evidence/releases/v0.2.1/RELEASE_RECEIPT.md)

## What's new in v0.2.1

Light Skills v0.2.1 introduces 36 admitted first-party Skills, featuring an intelligent workflow retrospective capability (`project-retro`), a comprehensive profile-driven refactoring of `agent-config` supporting 10 native agent harnesses, and the newly admitted `light-travelpage`.

### 1. Improved Workflow with Autonomous Retrospective (`project-retro`)
- **End-of-Workflow Self-Evaluation:** After `project-review` issues final acceptance or `release-workflow` completes, the Agent autonomously evaluates whether execution friction occurred:
  - Navigation delays or unindexed dependencies.
  - Automated check / guardrail gaps (errors that lint/typecheck/pre-commit could have prevented).
  - Reviewer misses or misplaced mechanical rules in prose.
  - Steering bloat or no-op instructions in `AGENTS.md` / `CLAUDE.md`.
  - Tool economy and token waste.
  - Missing telemetry or logs.
- **Noise-Free Execution:** If the session ran smoothly without friction, `project-retro` is skipped cleanly without token overhead. If friction was observed, actionable recommendations are ranked by severity.
- **Ported from Matt Pocock `retro`:** Adapted into a model-invoked first-party capability with full attribution, six core categories, and structured progressive disclosure.

### 2. `agent-config` Refactoring & Companion MCP Runtime
- **Profile Authority:** Tier assignments and reasoning effort are authorized exclusively through user-confirmed profiles against evidenced host models, eliminating heuristic model ranking (`routing_rank`) and name-based intelligence assumptions.
- **10 Native Harnesses:** Native support for Codex, Claude Code, Antigravity (`agy`), DeepSeek Harness (`DSH`), OpenCode, ZCode, Cursor, Grok Build, Hermes, and Pi (via MCP extension), plus a generic plan-only fallback.
- **Companion MCP Server:** Integrated optional companion MCP protocol (`LightDevCoder/agent-config`) offering 8 canonical tools, non-blocking setup gates, health probe semantics (`agent-config setup --check`), and safe preview before apply.
- **Canonical Contracts:** Normalized `AgentConfigResult` (`READY`, `NEED_INPUT`, `NEED_PROJECT_TICKETS`, `BLOCKED`, `UNSUPPORTED`) consumed downstream by `implement` and `ask-light`.

### 3. Newly Admitted `light-travelpage`
- **Mobile-First Travel Page Generator:** Generate and maintain interactive, responsive travel itineraries and expense ledgers.
- **Rich Visual Elements:** Bilingual (English/Chinese) switching, flight/stay cards, serif typography, anchored navigation menu, and interactive route maps with 10 terrain templates.
- **Collaborative Backend:** Offline-first state with shared Cloudflare Pages, Functions, and D1 database synchronization.

### 4. Stage Autonomy & Completion Clarifications
- Clarified authorization reuse and stage-local completion across `tdd`, `clarify`, `implement`, `review-loop`, and `manuscript-ops`.

### 5. TypeSafe Jev System One Semantic Acceleration
- **`ask-light` Semantic Routing:** Introduced compact token-efficient state extraction (<350 bytes) and bounded Jev Choice/Noul/Score judgments for intent calibration (`p >= 0.80` for immediate execution), material ambiguity routing (`p >= 0.65` to `project-clarify`), and readiness scoring, while strictly enforcing code-owned fail-closed boundaries (unknown tickets, multiple efforts, stale/dirty review).
- **`agent-config` Abstract Task Profiling & Calibration:** Replaced coupled heuristic keyword matching with abstract task profiling (routine, standard, high) and reasoning needs assessment without hardcoding vendor model names, preserving host evidence adaptation and preview approval gates. Evaluated via independent, label-clean live fixtures; authoritative inputs (`explicit-user`, `verified-ticket`, `deterministic-policy`) are strictly code-owned with 0 Jev complexity calls. Includes a provisional asymmetric downgrade policy requiring strong evidence (`confidence >= 0.75` and boundary margin `>= 0.15`) before reducing model capability below baseline.
- **`project-init` Canonical CLI Integration & Jev Ecosystem Onboarding:** Interactive opt-in gate (`--jev` / `--no-jev`) for initializing TypeSafe Jev System One semantic acceleration into newly scaffolded repositories. Built on official `vercel-labs/skills` v1.7.0 CLI canonical agent mappings (`pi`, `claude-code`, `cursor`, `codex`, `antigravity`, `grok`, `hermes-agent`) and canonical project scopes (`.agents/skills` for Cursor, Codex, and AGY), while unsupported targets (such as DSH) strictly fail closed with 0 installer calls. Includes automated `TYPESAFE_API_KEY` detection, strict `.env` gitignore protection before local writing, and global skill reuse.
- **Fail-Closed & Zero-Dependency Fallback:** Soft-imported via `try...except ImportError`; when `TYPESAFE_API_KEY` is not present or in case of network/timeout failure, all skills gracefully degrade to deterministic baselines with zero regression across all test cases.

## Installation

```bash
# Recommended interactive install from latest main:
npx skills add LightDevCoder/skills

# Pinned v0.2.1 release snapshot:
npx skills add LightDevCoder/skills#v0.2.1

# Install individual skills:
npx skills add LightDevCoder/skills --skill project-retro
npx skills add LightDevCoder/skills --skill agent-config
npx skills add LightDevCoder/skills --skill light-travelpage
```

---

## 中文说明

完整中文发布说明请访问：[RELEASE_NOTES.zh-CN.md](https://github.com/LightDevCoder/skills/blob/main/docs/evidence/releases/v0.2.1/RELEASE_NOTES.zh-CN.md)
