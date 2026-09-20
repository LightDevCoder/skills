# First-Party Skill Catalog

[中文目录](CATALOG.zh-CN.md)

This catalog is synchronized from the 36 admitted package directories under `skills/`. It is an inventory — not a static workflow router and not a record of what is installed on a particular Agent host. The package's `SKILL.md` remains the behavior authority.

[Browse by category](skills/README.md) · [Path migration](docs/CATEGORY_MIGRATION.md)

## Collection status

| Field | Value |
| --- | --- |
| Collection | Light Skills — Composable Agent Workflows |
| Package count | 36 admitted first-party Skills |
| Current state | 36 packages on main; v0.2.3 is the current stable release |
| Stable release | [v0.2.3](https://github.com/LightDevCoder/skills/releases/tag/v0.2.3) (36 packages; previous stable was v0.2.2) |
| Installation authority | [docs/INSTALLATION.md](docs/INSTALLATION.md) |
| Discovery check | [tests/test_collection_discovery.py](tests/test_collection_discovery.py) · [tests/test_composition.py](tests/test_composition.py) |
| Evidence | [v0.2.3 release manifest](docs/evidence/releases/v0.2.3/RELEASE_MANIFEST.md) · [v0.2.3 release receipt](docs/evidence/releases/v0.2.3/RELEASE_RECEIPT.md) |

`v0.1.1` shipped five packages; `v0.1.2` added `recap` and `language-learning` (seven); `v0.1.3` migrated the test toolchain; `v0.1.4` added `kanban-worker`; `v0.1.5` tightened kanban scheduling and identity; `v0.1.6` added `kb-init` (nine). `v0.2.0` released the full 33-package architecture across project workflow, clarification, execution, review, and specialized tools, and the v0.2.0 line was extended with the `humanizer` admission (34 packages; see [CHANGELOG.md](CHANGELOG.md)). `v0.2.1` added `light-travelpage` and `project-retro` (36 packages). `v0.2.2` finalized TypeSafe Jev semantic acceleration, category layout, and immutable release integrity. `v0.2.3` separated immutable release manifests from post-publication receipts, added v0.2.2 historical attestation, refactored project-retro into positive state-driven instructions, and formalized the six-stage release lifecycle.

No package in this table is an unmodified upstream copy. Approved Matt PORTs carry `ATTRIBUTION.md` and no upstream runtime dependency.

## Admitted Skills

### agent-config

- **Purpose:** Inspect current host capabilities and task requirements to configure appropriate model tiers, reasoning effort, and execution topology, with optional MCP support across 10 agent harnesses.
- **When to use:** Execution configuration or setup intent where model tier, reasoning effort, or execution topology affects the result.
- **Invocation:** Model-invoked.
- **Package:** [skills/engineering/agent-config/](skills/engineering/agent-config)
- **Status:** Admitted first-party; REFACTOR (Sol Advisor design reference, profile-driven cross-harness execution configurator covering primary coding-agent harnesses [10 native adapters + 1 generic fallback]).
- **Evidence:** [references/host-evidence-schema.md](skills/engineering/agent-config/references/host-evidence-schema.md), [plan-schema.md](skills/engineering/agent-config/references/plan-schema.md), [task-assessment.md](skills/engineering/agent-config/references/task-assessment.md), [profile-schema.md](skills/engineering/agent-config/references/profile-schema.md), [companion-contract.md](skills/engineering/agent-config/references/companion-contract.md), [harness-support.md](skills/engineering/agent-config/references/harness-support.md), [provider-adapter-contract.md](skills/engineering/agent-config/references/provider-adapter-contract.md); companion runtime maintained at [LightDevCoder/agent-config](https://github.com/LightDevCoder/agent-config).
- **Installation path:** `<skills-root>/agent-config/`.

### ask-light

- **Purpose:** Act as the Light workflow advisor, navigator, and router: inspect project/workflow state, recommend the next Skill with reasoning, and transition safely after user approval (enhanced with optional TypeSafe Jev System One semantic acceleration).
- **When to use:** The next step is unclear; you need project-aware routing, collection navigation, or standalone routing.
- **Invocation:** User-invoked only; read-only before approval. After approval, model-invoked targets may begin where supported; user-invoked targets follow Host transition policy and render the exact invocation when direct transition is unavailable.
- **Package:** [skills/productivity/ask-light/](skills/productivity/ask-light)
- **Status:** Admitted first-party; REFACTOR (router built last after the full map).
- **Evidence:** Semantic-map, provenance, availability, and top-result tests under [skills/productivity/ask-light/tests/](skills/productivity/ask-light/tests); [user guide](docs/skills/ask-light.md).
- **Installation path:** `<skills-root>/ask-light/`.

### clarify

- **Purpose:** Clarify vague ideas or feature proposals in a conversational round of targeted choices, without setting up a full project.
- **When to use:** Idea/brainstorm is foggy and no project context is required.
- **Invocation:** User-invoked only.
- **Package:** [skills/thinking/clarify/](skills/thinking/clarify)
- **Status:** Admitted first-party; ADAPT (Matt `grill-me` → Light, via `socratic`).
- **Evidence:** [SKILL.md](skills/thinking/clarify/SKILL.md), [references/WORKFLOW.md](skills/thinking/clarify/references/WORKFLOW.md), [ATTRIBUTION.md](skills/thinking/clarify/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/clarify/`.

### code-review

- **Purpose:** Read-only specialist reviewer for a bounded `git diff` along Standards and Spec axes.
- **When to use:** Reviewing a branch/PR diff, or when `review-loop` / `project-review` requests a software check.
- **Invocation:** Model-invoked (read-only; never repairs or verdicts).
- **Package:** [skills/review/code-review/](skills/review/code-review)
- **Status:** Admitted first-party; ADAPT (Matt `code-review`, two-axis method preserved).
- **Evidence:** [references/WORKFLOW.md](skills/review/code-review/references/WORKFLOW.md), [SMELL-BASELINE.md](skills/review/code-review/references/SMELL-BASELINE.md), [ATTRIBUTION.md](skills/review/code-review/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/code-review/`.

### decision-map

- **Purpose:** Plan a large, foggy, multi-session effort as a persistent decision map of tickets.
- **When to use:** Many dependent decisions; work spans sessions; fog must clear before `project-spec`.
- **Invocation:** User-invoked only.
- **Package:** [skills/thinking/decision-map/](skills/thinking/decision-map)
- **Status:** Admitted first-party; ADAPT (Matt `wayfinder`).
- **Evidence:** [references/MAP-CONTRACT.md](skills/thinking/decision-map/references/MAP-CONTRACT.md), [ATTRIBUTION.md](skills/thinking/decision-map/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/decision-map/`.

### diagnosing-bugs

- **Purpose:** Diagnosis loop for hard bugs and performance regressions with a tight feedback signal.
- **When to use:** Something broken/throwing/failing/slow and the cause is not obvious.
- **Invocation:** Model-invoked.
- **Package:** [skills/engineering/diagnosing-bugs/](skills/engineering/diagnosing-bugs)
- **Status:** Admitted first-party; PORT — NO REDESIGN (Matt baseline preserved).
- **Evidence:** [SKILL.md](skills/engineering/diagnosing-bugs/SKILL.md), [ATTRIBUTION.md](skills/engineering/diagnosing-bugs/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/diagnosing-bugs/`.

### eli5

- **Purpose:** Explain any topic, code, or error at a chosen audience level.
- **When to use:** User asks "explain like I'm 5", "to my boss", or needs a non-technical framing.
- **Invocation:** Model-invoked (explain on explicit request).
- **Package:** [skills/knowledge/eli5/](skills/knowledge/eli5)
- **Status:** Admitted first-party; MIGRATE — NO REWRITE (from upstream `DreambigOu/ELI5` @ `a766623`, via temporary migration fork `LightDevCoder/ELI5`).
- **Evidence:** [SKILL.md](skills/knowledge/eli5/SKILL.md), [ATTRIBUTION.md](skills/knowledge/eli5/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/eli5/`.

### generic-review

- **Purpose:** Read-only default reviewer for ordinary artifacts — finds omissions, wrong output, contradictions, usability gaps.
- **When to use:** No specialist reviewer is more appropriate.
- **Invocation:** Model-invoked (read-only; never verdicts).
- **Package:** [skills/review/generic-review/](skills/review/generic-review)
- **Status:** Admitted first-party; NEW.
- **Evidence:** [SKILL.md](skills/review/generic-review/SKILL.md).
- **Installation path:** `<skills-root>/generic-review/`.

### handoff

- **Purpose:** Compact the current conversation into a handoff document for the next agent.
- **When to use:** Closeout or resumption across sessions/agents.
- **Invocation:** User-invoked only.
- **Package:** [skills/productivity/handoff/](skills/productivity/handoff)
- **Status:** Admitted first-party; PORT — NO REDESIGN (Matt `handoff`).
- **Evidence:** [SKILL.md](skills/productivity/handoff/SKILL.md), [ATTRIBUTION.md](skills/productivity/handoff/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/handoff/`.

### humanizer

- **Purpose:** Rewrite AI-sounding English or Chinese text so it reads naturally without changing what it says.
- **When to use:** Editing or reviewing prose with inflated claims, sales language, vague sources, stock AI words, filler, or chatbot artifacts.
- **Invocation:** Model-invoked.
- **Package:** [skills/writing/humanizer/](skills/writing/humanizer)
- **Status:** Admitted first-party via full-path `PASS`; released on the v0.2.0 line; ADAPT of blader/humanizer (2.11.2) plus a thin zh adaptation, MIT attribution preserved.
- **Evidence:** [SKILL.md](skills/writing/humanizer/SKILL.md), [ATTRIBUTION.md](skills/writing/humanizer/ATTRIBUTION.md), [admission record](docs/evidence/admissions/humanizer/README.md).
- **Installation path:** `<skills-root>/humanizer/`.

### implement

- **Purpose:** Execute one bounded, already-decided work item (code, doc, config, Skill, generic task) with verification and review handoff.
- **When to use:** A ticket or SPEC slice is ready and unambiguous.
- **Invocation:** User-invoked only.
- **Package:** [skills/project/implement/](skills/project/implement)
- **Status:** Admitted first-party; ADAPT (Matt `implement` → general-purpose executor).
- **Evidence:** [references/WORKFLOW.md](skills/project/implement/references/WORKFLOW.md), [ATTRIBUTION.md](skills/project/implement/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/implement/`.

### kanban-worker

- **Purpose:** Pick up and execute one Light-Kanban task per scheduled run; resumes owned work and `reviewFeedback` before new claims.
- **When to use:** Scheduled Light-Kanban board work.
- **Invocation:** Model-invoked; manual entry point is supported.
- **Package:** [skills/project/kanban-worker/](skills/project/kanban-worker)
- **Status:** Admitted first-party via full path (`review-loop agent-skill` PASS); renamed from `light-kanban-worker` in v0.1.6.
- **Evidence:** Contract and behavior tests under [skills/project/kanban-worker/tests/](skills/project/kanban-worker/tests), [user guide](docs/skills/kanban-worker.md).
- **Installation path:** `<skills-root>/kanban-worker/`.

### kb-init

- **Purpose:** Design and initialize a maintainable knowledge base via interview, then implement only after approval.
- **When to use:** Creating or rebuilding a wiki, reference library, or research archive.
- **Invocation:** User-invoked only.
- **Package:** [skills/knowledge/kb-init/](skills/knowledge/kb-init)
- **Status:** Admitted first-party via full path (`review-loop agent-skill` PASS); released in v0.1.6.
- **Evidence:** Contract tests under [skills/knowledge/kb-init/tests/](skills/knowledge/kb-init/tests), [user guide](docs/skills/kb-init.md).
- **Installation path:** `<skills-root>/kb-init/`.

### language-learning

- **Purpose:** Tutor any language through six modes — lessons, flashcards, conversation, grammar, quizzes, translation.
- **When to use:** Learning or practicing a foreign language.
- **Invocation:** User-invoked only.
- **Package:** [skills/knowledge/language-learning/](skills/knowledge/language-learning)
- **Status:** Admitted first-party via prompt-only fast-track `PASS`; released in v0.1.2.
- **Evidence:** Contract tests under [skills/knowledge/language-learning/tests/](skills/knowledge/language-learning/tests), [user guide](docs/skills/language-learning.md).
- **Installation path:** `<skills-root>/language-learning/`.

### learn-anything

- **Purpose:** Turn sufficiently evidenced conversations, notes, or workflows into reusable Agent Skill methods.
- **When to use:** Source material may contain a repeatable, evidence-backed method.
- **Invocation:** User-invoked only.
- **Package:** [skills/knowledge/learn-anything/](skills/knowledge/learn-anything)
- **Status:** Admitted first-party; PRESERVE — NO REWRITE.
- **Evidence:** [package contract](skills/knowledge/learn-anything/SKILL.md), [user guide](docs/skills/learn-anything.md).
- **Installation path:** `<skills-root>/learn-anything/`.

### light-travelpage

- **Purpose:** Generate or update a bilingual mobile travel page with flight/stay cards, regional map navigation, shared members, expenses, currency settings, tasks and ticket status.
- **When to use:** Create or maintain a travel webpage from supplied materials; not ordinary travel advice or booking purchases.
- **Invocation:** Model-invoked.
- **Package:** [skills/productivity/light-travelpage/](skills/productivity/light-travelpage)
- **Installation path:** `<skills-root>/light-travelpage/`.
- **Status:** Admitted first-party transformation; included in the current stable collection. Default deployment: GitHub + Cloudflare Pages, Functions and D1; one equal-access group per deployment.
- **Evidence:** [Admission](docs/evidence/admissions/light-travelpage/README.md) · [Latest update](docs/evidence/maintenance/2026-09-15-light-travelpage.md) · [Attribution](skills/productivity/light-travelpage/ATTRIBUTION.md).

### manuscript-ops

- **Purpose:** Route and govern manuscript engineering from notes to multilingual, multi-format deliverables.
- **When to use:** Manuscript scope, risk, batches, reviews, or formats need governing.
- **Invocation:** Model-invoked; manual entry point is supported.
- **Package:** [skills/writing/manuscript-ops/](skills/writing/manuscript-ops)
- **Status:** Admitted first-party; PRESERVE — NO REWRITE.
- **Evidence:** [package contract](skills/writing/manuscript-ops/SKILL.md), [user guide](docs/skills/manuscript-ops.md).
- **Installation path:** `<skills-root>/manuscript-ops/`.

### project-clarify

- **Purpose:** Inspect repository files and ask targeted questions only about remaining open decisions before writing a spec.
- **When to use:** Existing project has unclear requirements; facts already in repo should not be re-asked.
- **Invocation:** User-invoked only.
- **Package:** [skills/project/project-clarify/](skills/project/project-clarify)
- **Status:** Admitted first-party; ADAPT (Matt `grill-with-docs`).
- **Evidence:** [references/project-clarification-contract.md](skills/project/project-clarify/references/project-clarification-contract.md), [ATTRIBUTION.md](skills/project/project-clarify/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/project-clarify/`.

### project-init

- **Purpose:** Set up workspace layout and task tracker settings for a new or existing project so planning and coding start from a shared foundation.
- **When to use:** New project needs a minimal, confirmed starting point.
- **Invocation:** User-invoked only.
- **Package:** [skills/project/project-init/](skills/project/project-init)
- **Status:** Admitted first-party; REFACTOR (repository bootstrap; full clarification remains in `project-clarify`).
- **Evidence:** Contract and behavior tests under [skills/project/project-init/tests/](skills/project/project-init/tests); [user guide](docs/skills/project-init.md).
- **Installation path:** `<skills-root>/project-init/`.

### project-review

- **Purpose:** Project-level final acceptance — evaluate deliverables against agreed requirements to issue a clear `PASS`, `FAIL`, or `BLOCKED` decision.
- **When to use:** Completed project needs acceptance before `release-workflow`.
- **Invocation:** Model-invoked; manual entry supported.
- **Package:** [skills/review/project-review/](skills/review/project-review)
- **Status:** Admitted first-party; NEW (migrated final-acceptance logic from old `review-loop`).
- **Evidence:** [SKILL.md](skills/review/project-review/SKILL.md), [references/profiles/](skills/review/project-review/references/profiles).
- **Installation path:** `<skills-root>/project-review/`.

### project-retro

- **Purpose:** Review completed sessions to find friction in project layout, automated checks, instruction clarity, or tool usage, then suggest concrete fixes.
- **When to use:** Workflow final step (Agent self-evaluates whether friction occurred) or user-invoked for a session post-mortem.
- **Invocation:** Model-invoked (Agent self-evaluation at workflow conclusion); manual entry supported.
- **Package:** [skills/project/project-retro/](skills/project/project-retro)
- **Status:** Admitted first-party; PORT & LIGHT WORKFLOW ADAPTATION (Matt Pocock `retro`).
- **Evidence:** Contract and behavior tests under [skills/project/project-retro/tests/](skills/project/project-retro/tests); [SKILL.md](skills/project/project-retro/SKILL.md), [ATTRIBUTION.md](skills/project/project-retro/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/project-retro/`.

### project-spec

- **Purpose:** Turn clarified decisions into a technical specification (SPEC) without re-asking settled questions.
- **When to use:** Decisions are clarified and a SPEC is needed for `project-tickets`.
- **Invocation:** User-invoked only.
- **Package:** [skills/project/project-spec/](skills/project/project-spec)
- **Status:** Admitted first-party; ADAPT (Matt `to-spec`).
- **Evidence:** [references/](skills/project/project-spec/references), [ATTRIBUTION.md](skills/project/project-spec/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/project-spec/`.

### project-tickets

- **Purpose:** Break an approved specification into an ordered list of standalone tasks with clear dependencies, ready for implementation.
- **When to use:** SPEC is approved and executable tasks are needed.
- **Invocation:** User-invoked only.
- **Package:** [skills/project/project-tickets/](skills/project/project-tickets)
- **Status:** Admitted first-party; ADAPT (Matt `to-tickets`).
- **Evidence:** [references/](skills/project/project-tickets/references), [ATTRIBUTION.md](skills/project/project-tickets/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/project-tickets/`.

### prototype

- **Purpose:** Build a throwaway prototype to answer a design question.
- **When to use:** State model or UI logic needs a quick feel-check before commitment.
- **Invocation:** Model-invoked.
- **Package:** [skills/engineering/prototype/](skills/engineering/prototype)
- **Status:** Admitted first-party; PORT — NO REDESIGN (Matt `prototype`).
- **Evidence:** [SKILL.md](skills/engineering/prototype/SKILL.md), [ATTRIBUTION.md](skills/engineering/prototype/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/prototype/`.

### recap

- **Purpose:** Show one concise line about the current session without replacing or compacting conversation history.
- **When to use:** User explicitly invokes `$recap`.
- **Invocation:** User-invoked only; `$recap` is the sole entry.
- **Package:** [skills/productivity/recap/](skills/productivity/recap)
- **Status:** Admitted first-party; manual-only form released on the v0.2.0 stable line; current main tracks active collection updates.
- **Evidence:** Current amendment tests in [tests/test_functional_closure.py](tests/test_functional_closure.py); frozen historical tests remain under [skills/productivity/recap/tests/](skills/productivity/recap/tests); [user guide](docs/skills/recap.md).
- **Installation path:** `<skills-root>/recap/`.

### release-workflow

- **Purpose:** Publish a completed project — synchronize docs, run quality gates, tag, and release.
- **When to use:** Project has passed `project-review` and is ready to publish.
- **Invocation:** Model-invoked (or manual entry where supported).
- **Package:** [skills/project/release-workflow/](skills/project/release-workflow)
- **Status:** Admitted first-party; MIGRATE — NO REWRITE (from `LightDevCoder/release-workflow`).
- **Evidence:** [SKILL.md](skills/project/release-workflow/SKILL.md).
- **Installation path:** `<skills-root>/release-workflow/`.

### research

- **Purpose:** Investigate an external question against high-trust primary sources and capture findings.
- **When to use:** Local preset or facts are insufficient; need external evidence.
- **Invocation:** Model-invoked.
- **Package:** [skills/thinking/research/](skills/thinking/research)
- **Status:** Admitted first-party; PORT — NO REDESIGN (Matt `research`).
- **Evidence:** [SKILL.md](skills/thinking/research/SKILL.md), [ATTRIBUTION.md](skills/thinking/research/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/research/`.

### resolving-merge-conflicts

- **Purpose:** Resolve an in-progress `git` merge or rebase conflict.
- **When to use:** Merge/rebase halted with conflicts.
- **Invocation:** Model-invoked.
- **Package:** [skills/engineering/resolving-merge-conflicts/](skills/engineering/resolving-merge-conflicts)
- **Status:** Admitted first-party; PORT — NO REDESIGN.
- **Evidence:** [SKILL.md](skills/engineering/resolving-merge-conflicts/SKILL.md), [ATTRIBUTION.md](skills/engineering/resolving-merge-conflicts/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/resolving-merge-conflicts/`.

### review-loop

- **Purpose:** Review and repair engine: dispatches artifacts to the right reviewer, collects findings, guides fixes, and repeats until clean.
- **When to use:** Any artifact with a reviewer and a bounded repair window.
- **Invocation:** Model-invoked; manual entry supported.
- **Package:** [skills/review/review-loop/](skills/review/review-loop)
- **Status:** Admitted first-party; REFACTOR + SPLIT (final acceptance moved to `project-review`).
- **Evidence:** [SKILL.md](skills/review/review-loop/SKILL.md), [references/](skills/review/review-loop/references).
- **Installation path:** `<skills-root>/review-loop/`.

### socratic

- **Purpose:** Questioning engine: presents independent choices, provides recommendations, and confirms shared understanding step by step.
- **When to use:** Underlies `clarify`, `project-clarify`, `decision-map`; not a standalone project workflow.
- **Invocation:** Model-invoked (engine for other Skills).
- **Package:** [skills/thinking/socratic/](skills/thinking/socratic)
- **Status:** Admitted first-party; ADAPT (Matt `grilling`).
- **Evidence:** [SKILL.md](skills/thinking/socratic/SKILL.md), [ATTRIBUTION.md](skills/thinking/socratic/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/socratic/`.

### tdd

- **Purpose:** Test-driven development — red → green → refactor loop with real tests.
- **When to use:** Implementing coding features test-first or fixing bugs with regression cover.
- **Invocation:** Model-invoked.
- **Package:** [skills/engineering/tdd/](skills/engineering/tdd)
- **Status:** Admitted first-party; PORT — NO REDESIGN (Matt `tdd`).
- **Evidence:** [SKILL.md](skills/engineering/tdd/SKILL.md), [ATTRIBUTION.md](skills/engineering/tdd/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/tdd/`.

### teach

- **Purpose:** Teach a new skill or concept within the workspace.
- **When to use:** User wants a guided lesson on a topic.
- **Invocation:** User-invoked only.
- **Package:** [skills/knowledge/teach/](skills/knowledge/teach)
- **Status:** Admitted first-party; PORT — NO REDESIGN (Matt `teach`).
- **Evidence:** [SKILL.md](skills/knowledge/teach/SKILL.md), [ATTRIBUTION.md](skills/knowledge/teach/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/teach/`.

### to-questionnaire

- **Purpose:** Turn an undecided question into a questionnaire for the person who holds the information.
- **When to use:** Information is held by another person, not the current user.
- **Invocation:** User-invoked only.
- **Package:** [skills/thinking/to-questionnaire/](skills/thinking/to-questionnaire)
- **Status:** Admitted first-party; PORT — NO REDESIGN.
- **Evidence:** [SKILL.md](skills/thinking/to-questionnaire/SKILL.md), [ATTRIBUTION.md](skills/thinking/to-questionnaire/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/to-questionnaire/`.

### wait-what

- **Purpose:** Re-pitch the last message that did not land.
- **When to use:** User says "wait, what?" or similar confusion.
- **Invocation:** User-invoked only.
- **Package:** [skills/productivity/wait-what/](skills/productivity/wait-what)
- **Status:** Admitted first-party; PORT — NO REDESIGN.
- **Evidence:** [SKILL.md](skills/productivity/wait-what/SKILL.md), [ATTRIBUTION.md](skills/productivity/wait-what/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/wait-what/`.

### wizard

- **Purpose:** Interactive bash wizard for human-only steps (provisioning, secrets, dashboards, cutovers).
- **When to use:** Task needs a guided human walk-through, not an agent-auto step.
- **Invocation:** Model-invoked.
- **Package:** [skills/productivity/wizard/](skills/productivity/wizard)
- **Status:** Admitted first-party; PORT — NO REDESIGN (Matt `wizard`).
- **Evidence:** [SKILL.md](skills/productivity/wizard/SKILL.md), [ATTRIBUTION.md](skills/productivity/wizard/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/wizard/`.

### writing-for-agents

- **Purpose:** Author or edit agent-facing documents (Skills, AGENTS.md, CLAUDE.md) for model consumption.
- **When to use:** Creating or improving agent instructions or Skill packages.
- **Invocation:** Model-invoked.
- **Package:** [skills/writing/writing-for-agents/](skills/writing/writing-for-agents)
- **Status:** Admitted first-party; PORT — NO REDESIGN.
- **Evidence:** [SKILL.md](skills/writing/writing-for-agents/SKILL.md), [ATTRIBUTION.md](skills/writing/writing-for-agents/ATTRIBUTION.md).
- **Installation path:** `<skills-root>/writing-for-agents/`.

## Source-state boundaries

| State | Where it belongs | Catalog treatment |
| --- | --- | --- |
| First-party | This repository | Listed above when admitted. |
| Approved Port (Matt) | This repository with `ATTRIBUTION.md` | Listed above; self-contained, no Matt runtime dependency. |
| Direct upstream | Original upstream repository | Mentioned as dependency; never copied here unmodified. |
| Modified third-party | `skills-3rdParty` | Listed in that private repository's source catalog after fork admission. |
| Deprecated or archived | Released migration record | Listed with replacement and migration guidance. |

See [maintenance](docs/MAINTENANCE.md) for synchronization and [admission](docs/SKILL_ADMISSION.md) for the ownership gate.
