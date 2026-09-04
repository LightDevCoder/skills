# First-Party Skill Catalog

[中文目录](CATALOG.zh-CN.md)

This catalog is synchronized from the 34 admitted package directories under `skills/`. It is an inventory — not a static workflow router and not a record of what is installed on a particular Agent host. The package's `SKILL.md` remains the behavior authority.

## Collection status

| Field | Value |
| --- | --- |
| Collection | Light Skills — Composable Agent Workflows |
| Package count | 34 admitted first-party Skills |
| Current state | Released [v0.2.0](https://github.com/LightDevCoder/skills/releases/tag/v0.2.0) with 34 first-party packages |
| Stable release | [v0.2.0](https://github.com/LightDevCoder/skills/releases/tag/v0.2.0) (34 packages; previous stable was v0.1.6 with 9 packages) |
| Installation authority | [docs/INSTALLATION.md](docs/INSTALLATION.md) |
| Discovery check | [tests/test_collection_discovery.py](tests/test_collection_discovery.py) · [tests/test_composition.py](tests/test_composition.py) |
| Evidence | [v0.2.0 release evidence](docs/evidence/releases/v0.2.0/) |

`v0.1.1` shipped five packages; `v0.1.2` added `recap` and `language-learning` (seven); `v0.1.3` migrated the test toolchain; `v0.1.4` added `kanban-worker`; `v0.1.5` tightened kanban scheduling and identity; `v0.1.6` added `kb-init` (nine). `v0.2.0` released the full 33-package architecture across project workflow, clarification, execution, review, and specialized tools, and the v0.2.0 line was extended with the `humanizer` admission (34 packages; see [CHANGELOG.md](CHANGELOG.md)).

No package in this table is an unmodified upstream copy. Approved Matt PORTs carry `ATTRIBUTION.md` and no upstream runtime dependency.

## Admitted Skills

### agent-config

- **Purpose:** Profile-driven cross-harness execution configurator: inspect current Host capabilities, match user-confirmed model-tier profiles and task shape, and right-size execution topology, model tier, and effort with optional companion MCP support and safe single-model peer mode.
- **When to use:** Execution configuration or setup intent where model tier, reasoning effort, or execution topology affects the result.
- **Invocation:** Model-invoked.
- **Package:** [skills/agent-config/](skills/agent-config/)
- **Status:** Admitted first-party; REFACTOR (Sol Advisor design reference, profile-driven cross-harness execution configurator).
- **Evidence:** [references/host-evidence-schema.md](skills/agent-config/references/host-evidence-schema.md), [plan-schema.md](skills/agent-config/references/plan-schema.md), [task-assessment.md](skills/agent-config/references/task-assessment.md), [profile-schema.md](skills/agent-config/references/profile-schema.md), [companion-contract.md](skills/agent-config/references/companion-contract.md), [provider-adapter-contract.md](skills/agent-config/references/provider-adapter-contract.md).
- **Installation path:** `skills/agent-config/` in a host-recognized Skills root.

### ask-light

- **Purpose:** Act as the Light workflow advisor, navigator, and router: inspect project/workflow state, recommend the next Skill with reasoning, and transition safely after user approval.
- **When to use:** The next step is unclear; you need project-aware routing, collection navigation, or standalone routing.
- **Invocation:** User-invoked only; read-only before approval. After approval, model-invoked targets may begin where supported; user-invoked targets follow Host transition policy and render the exact invocation when direct transition is unavailable.
- **Package:** [skills/ask-light/](skills/ask-light/)
- **Status:** Admitted first-party; REFACTOR (router built last after the full map).
- **Evidence:** Semantic-map, provenance, availability, and top-result tests under [skills/ask-light/tests/](skills/ask-light/tests/); [user guide](docs/skills/ask-light.md).
- **Installation path:** `skills/ask-light/` in a host-recognized Skills root.

### clarify

- **Purpose:** One-invocation continuous clarification for a vague idea, requirement, or process — no formal SPEC or project workflow. Asks the current frontier as a round of independent questions and accepts batch replies.
- **When to use:** Idea/brainstorm is foggy and no project context is required.
- **Invocation:** User-invoked only.
- **Package:** [skills/clarify/](skills/clarify/)
- **Status:** Admitted first-party; ADAPT (Matt `grill-me` → Light, via `socratic`).
- **Evidence:** [SKILL.md](skills/clarify/SKILL.md), [references/WORKFLOW.md](skills/clarify/references/WORKFLOW.md), [ATTRIBUTION.md](skills/clarify/ATTRIBUTION.md).
- **Installation path:** `skills/clarify/` in a host-recognized Skills root.

### code-review

- **Purpose:** Read-only specialist reviewer for a bounded `git diff` along Standards and Spec axes.
- **When to use:** Reviewing a branch/PR diff, or when `review-loop` / `project-review` requests a software check.
- **Invocation:** Model-invoked (read-only; never repairs or verdicts).
- **Package:** [skills/code-review/](skills/code-review/)
- **Status:** Admitted first-party; ADAPT (Matt `code-review`, two-axis method preserved).
- **Evidence:** [references/WORKFLOW.md](skills/code-review/references/WORKFLOW.md), [SMELL-BASELINE.md](skills/code-review/references/SMELL-BASELINE.md), [ATTRIBUTION.md](skills/code-review/ATTRIBUTION.md).
- **Installation path:** `skills/code-review/` in a host-recognized Skills root.

### decision-map

- **Purpose:** Plan a large, foggy, multi-session effort as a persistent decision map of tickets.
- **When to use:** Many dependent decisions; work spans sessions; fog must clear before `project-spec`.
- **Invocation:** User-invoked only.
- **Package:** [skills/decision-map/](skills/decision-map/)
- **Status:** Admitted first-party; ADAPT (Matt `wayfinder`).
- **Evidence:** [references/MAP-CONTRACT.md](skills/decision-map/references/MAP-CONTRACT.md), [ATTRIBUTION.md](skills/decision-map/ATTRIBUTION.md).
- **Installation path:** `skills/decision-map/` in a host-recognized Skills root.

### diagnosing-bugs

- **Purpose:** Diagnosis loop for hard bugs and performance regressions with a tight feedback signal.
- **When to use:** Something broken/throwing/failing/slow and the cause is not obvious.
- **Invocation:** Model-invoked.
- **Package:** [skills/diagnosing-bugs/](skills/diagnosing-bugs/)
- **Status:** Admitted first-party; PORT — NO REDESIGN (Matt baseline preserved).
- **Evidence:** [SKILL.md](skills/diagnosing-bugs/SKILL.md), [ATTRIBUTION.md](skills/diagnosing-bugs/ATTRIBUTION.md).
- **Installation path:** `skills/diagnosing-bugs/` in a host-recognized Skills root.

### eli5

- **Purpose:** Explain any topic, code, or error at a chosen audience level.
- **When to use:** User asks "explain like I'm 5", "to my boss", or needs a non-technical framing.
- **Invocation:** Model-invoked (explain on explicit request).
- **Package:** [skills/eli5/](skills/eli5/)
- **Status:** Admitted first-party; MIGRATE — NO REWRITE (from upstream `DreambigOu/ELI5` @ `a766623`, via temporary migration fork `LightDevCoder/ELI5`).
- **Evidence:** [SKILL.md](skills/eli5/SKILL.md), [ATTRIBUTION.md](skills/eli5/ATTRIBUTION.md).
- **Installation path:** `skills/eli5/` in a host-recognized Skills root.

### generic-review

- **Purpose:** Read-only default reviewer for ordinary artifacts — finds omissions, wrong output, contradictions, usability gaps.
- **When to use:** No specialist reviewer is more appropriate.
- **Invocation:** Model-invoked (read-only; never verdicts).
- **Package:** [skills/generic-review/](skills/generic-review/)
- **Status:** Admitted first-party; NEW.
- **Evidence:** [SKILL.md](skills/generic-review/SKILL.md).
- **Installation path:** `skills/generic-review/` in a host-recognized Skills root.

### handoff

- **Purpose:** Compact the current conversation into a handoff document for the next agent.
- **When to use:** Closeout or resumption across sessions/agents.
- **Invocation:** User-invoked only.
- **Package:** [skills/handoff/](skills/handoff/)
- **Status:** Admitted first-party; PORT — NO REDESIGN (Matt `handoff`).
- **Evidence:** [SKILL.md](skills/handoff/SKILL.md), [ATTRIBUTION.md](skills/handoff/ATTRIBUTION.md).
- **Installation path:** `skills/handoff/` in a host-recognized Skills root.

### humanizer

- **Purpose:** Rewrite AI-sounding English or Chinese text so it reads naturally without changing what it says.
- **When to use:** Editing or reviewing prose with inflated claims, sales language, vague sources, stock AI words, filler, or chatbot artifacts.
- **Invocation:** Model-invoked.
- **Package:** [skills/humanizer/](skills/humanizer/)
- **Status:** Admitted first-party via full-path `PASS`; released on the v0.2.0 line; ADAPT of blader/humanizer (2.11.2) plus a thin zh adaptation, MIT attribution preserved.
- **Evidence:** [SKILL.md](skills/humanizer/SKILL.md), [ATTRIBUTION.md](skills/humanizer/ATTRIBUTION.md), [admission record](docs/evidence/admissions/humanizer/README.md).
- **Installation path:** `skills/humanizer/` in a host-recognized Skills root.

### implement

- **Purpose:** Execute one bounded, already-decided work item (code, doc, config, Skill, generic task) with verification and review handoff.
- **When to use:** A ticket or SPEC slice is ready and unambiguous.
- **Invocation:** User-invoked only.
- **Package:** [skills/implement/](skills/implement/)
- **Status:** Admitted first-party; ADAPT (Matt `implement` → general-purpose executor).
- **Evidence:** [references/WORKFLOW.md](skills/implement/references/WORKFLOW.md), [ATTRIBUTION.md](skills/implement/ATTRIBUTION.md).
- **Installation path:** `skills/implement/` in a host-recognized Skills root.

### kanban-worker

- **Purpose:** Pick up and execute one Light-Kanban task per scheduled run; resumes owned work and `reviewFeedback` before new claims.
- **When to use:** Scheduled Light-Kanban board work.
- **Invocation:** Model-invoked; manual entry point is supported.
- **Package:** [skills/kanban-worker/](skills/kanban-worker/)
- **Status:** Admitted first-party via full path (`review-loop agent-skill` PASS); renamed from `light-kanban-worker` in v0.1.6.
- **Evidence:** Contract and behavior tests under [skills/kanban-worker/tests/](skills/kanban-worker/tests/), [user guide](docs/skills/kanban-worker.md).
- **Installation path:** `skills/kanban-worker/` in a host-recognized Skills root.

### kb-init

- **Purpose:** Design and initialize a maintainable knowledge base via interview, then implement only after approval.
- **When to use:** Creating or rebuilding a wiki, reference library, or research archive.
- **Invocation:** User-invoked only.
- **Package:** [skills/kb-init/](skills/kb-init/)
- **Status:** Admitted first-party via full path (`review-loop agent-skill` PASS); released in v0.1.6.
- **Evidence:** Contract tests under [skills/kb-init/tests/](skills/kb-init/tests/), [user guide](docs/skills/kb-init.md).
- **Installation path:** `skills/kb-init/` in a host-recognized Skills root.

### language-learning

- **Purpose:** Tutor any language through six modes — lessons, flashcards, conversation, grammar, quizzes, translation.
- **When to use:** Learning or practicing a foreign language.
- **Invocation:** User-invoked only.
- **Package:** [skills/language-learning/](skills/language-learning/)
- **Status:** Admitted first-party via prompt-only fast-track `PASS`; released in v0.1.2.
- **Evidence:** Contract tests under [skills/language-learning/tests/](skills/language-learning/tests/), [user guide](docs/skills/language-learning.md).
- **Installation path:** `skills/language-learning/` in a host-recognized Skills root.

### learn-anything

- **Purpose:** Turn sufficiently evidenced conversations, notes, or workflows into reusable Agent Skill methods.
- **When to use:** Source material may contain a repeatable, evidence-backed method.
- **Invocation:** User-invoked only.
- **Package:** [skills/learn-anything/](skills/learn-anything/)
- **Status:** Admitted first-party; PRESERVE — NO REWRITE.
- **Evidence:** [package contract](skills/learn-anything/SKILL.md), [user guide](docs/skills/learn-anything.md).
- **Installation path:** `skills/learn-anything/` in a host-recognized Skills root.

### manuscript-ops

- **Purpose:** Route and govern manuscript engineering from notes to multilingual, multi-format deliverables.
- **When to use:** Manuscript scope, risk, batches, reviews, or formats need governing.
- **Invocation:** Model-invoked; manual entry point is supported.
- **Package:** [skills/manuscript-ops/](skills/manuscript-ops/)
- **Status:** Admitted first-party; PRESERVE — NO REWRITE.
- **Evidence:** [package contract](skills/manuscript-ops/SKILL.md), [user guide](docs/skills/manuscript-ops.md).
- **Installation path:** `skills/manuscript-ops/` in a host-recognized Skills root.

### project-clarify

- **Purpose:** Clarify a real project's unresolved decisions from inspected project facts; returns a bounded handoff for `project-spec`. Uses the same frontier-round interaction as `clarify` with project-aware evidence.
- **When to use:** Existing project has unclear requirements; facts already in repo should not be re-asked.
- **Invocation:** User-invoked only.
- **Package:** [skills/project-clarify/](skills/project-clarify/)
- **Status:** Admitted first-party; ADAPT (Matt `grill-with-docs`).
- **Evidence:** [references/project-clarification-contract.md](skills/project-clarify/references/project-clarification-contract.md), [ATTRIBUTION.md](skills/project-clarify/ATTRIBUTION.md).
- **Installation path:** `skills/project-clarify/` in a host-recognized Skills root.

### project-init

- **Purpose:** Idempotently bootstrap the stable Light project and tracker contracts consumed by downstream Project Skills.
- **When to use:** New project needs a minimal, confirmed starting point.
- **Invocation:** User-invoked only.
- **Package:** [skills/project-init/](skills/project-init/)
- **Status:** Admitted first-party; REFACTOR (repository bootstrap; full clarification remains in `project-clarify`).
- **Evidence:** Contract and behavior tests under [skills/project-init/tests/](skills/project-init/tests/); [user guide](docs/skills/project-init.md).
- **Installation path:** `skills/project-init/` in a host-recognized Skills root.

### project-review

- **Purpose:** Project-level final acceptance — freeze a baseline, compose reviewers, issue `PASS`/`FAIL`/`BLOCKED`.
- **When to use:** Completed project needs acceptance before `release-workflow`.
- **Invocation:** Model-invoked; manual entry supported.
- **Package:** [skills/project-review/](skills/project-review/)
- **Status:** Admitted first-party; NEW (migrated final-acceptance logic from old `review-loop`).
- **Evidence:** [SKILL.md](skills/project-review/SKILL.md), [references/profiles/](skills/project-review/references/profiles/).
- **Installation path:** `skills/project-review/` in a host-recognized Skills root.

### project-spec

- **Purpose:** Turn already-clarified outputs into a formal project SPEC without reopening an interview.
- **When to use:** Decisions are clarified and a SPEC is needed for `project-tickets`.
- **Invocation:** User-invoked only.
- **Package:** [skills/project-spec/](skills/project-spec/)
- **Status:** Admitted first-party; ADAPT (Matt `to-spec`).
- **Evidence:** [references/](skills/project-spec/references/), [ATTRIBUTION.md](skills/project-spec/ATTRIBUTION.md).
- **Installation path:** `skills/project-spec/` in a host-recognized Skills root.

### project-tickets

- **Purpose:** Turn an approved SPEC into a dependency-ordered, tracer-bullet ticket graph.
- **When to use:** SPEC is approved and executable tasks are needed.
- **Invocation:** User-invoked only.
- **Package:** [skills/project-tickets/](skills/project-tickets/)
- **Status:** Admitted first-party; ADAPT (Matt `to-tickets`).
- **Evidence:** [references/](skills/project-tickets/references/), [ATTRIBUTION.md](skills/project-tickets/ATTRIBUTION.md).
- **Installation path:** `skills/project-tickets/` in a host-recognized Skills root.

### prototype

- **Purpose:** Build a throwaway prototype to answer a design question.
- **When to use:** State model or UI logic needs a quick feel-check before commitment.
- **Invocation:** Model-invoked.
- **Package:** [skills/prototype/](skills/prototype/)
- **Status:** Admitted first-party; PORT — NO REDESIGN (Matt `prototype`).
- **Evidence:** [SKILL.md](skills/prototype/SKILL.md), [ATTRIBUTION.md](skills/prototype/ATTRIBUTION.md).
- **Installation path:** `skills/prototype/` in a host-recognized Skills root.

### recap

- **Purpose:** Show one concise line about the current session without replacing or compacting conversation history.
- **When to use:** User explicitly invokes `$recap`.
- **Invocation:** User-invoked only; `$recap` is the sole entry.
- **Package:** [skills/recap/](skills/recap/)
- **Status:** Admitted first-party; v0.1.2 released the prior form; the manual-only amendment is unreleased pending current-candidate acceptance.
- **Evidence:** Current amendment tests in [tests/test_functional_closure.py](tests/test_functional_closure.py); frozen historical tests remain under [skills/recap/tests/](skills/recap/tests/); [user guide](docs/skills/recap.md).
- **Installation path:** `skills/recap/` in a host-recognized Skills root.

### release-workflow

- **Purpose:** Publish a completed project — synchronize docs, run quality gates, tag, and release.
- **When to use:** Project has passed `project-review` and is ready to publish.
- **Invocation:** Model-invoked (or manual entry where supported).
- **Package:** [skills/release-workflow/](skills/release-workflow/)
- **Status:** Admitted first-party; MIGRATE — NO REWRITE (from `LightDevCoder/release-workflow`).
- **Evidence:** [SKILL.md](skills/release-workflow/SKILL.md).
- **Installation path:** `skills/release-workflow/` in a host-recognized Skills root.

### research

- **Purpose:** Investigate an external question against high-trust primary sources and capture findings.
- **When to use:** Local preset or facts are insufficient; need external evidence.
- **Invocation:** Model-invoked.
- **Package:** [skills/research/](skills/research/)
- **Status:** Admitted first-party; PORT — NO REDESIGN (Matt `research`).
- **Evidence:** [SKILL.md](skills/research/SKILL.md), [ATTRIBUTION.md](skills/research/ATTRIBUTION.md).
- **Installation path:** `skills/research/` in a host-recognized Skills root.

### resolving-merge-conflicts

- **Purpose:** Resolve an in-progress `git` merge or rebase conflict.
- **When to use:** Merge/rebase halted with conflicts.
- **Invocation:** Model-invoked.
- **Package:** [skills/resolving-merge-conflicts/](skills/resolving-merge-conflicts/)
- **Status:** Admitted first-party; PORT — NO REDESIGN.
- **Evidence:** [SKILL.md](skills/resolving-merge-conflicts/SKILL.md), [ATTRIBUTION.md](skills/resolving-merge-conflicts/ATTRIBUTION.md).
- **Installation path:** `skills/resolving-merge-conflicts/` in a host-recognized Skills root.

### review-loop

- **Purpose:** Lightweight review/repair engine — resolve reviewer, invoke, receive findings, return repair, re-run.
- **When to use:** Any artifact with a reviewer and a bounded repair window.
- **Invocation:** Model-invoked; manual entry supported.
- **Package:** [skills/review-loop/](skills/review-loop/)
- **Status:** Admitted first-party; REFACTOR + SPLIT (final acceptance moved to `project-review`).
- **Evidence:** [SKILL.md](skills/review-loop/SKILL.md), [references/](skills/review-loop/references/).
- **Installation path:** `skills/review-loop/` in a host-recognized Skills root.

### socratic

- **Purpose:** Core clarification engine — internal decision frontier with rounds of independent questions, options, recommendations, batch replies, and shared-understanding confirmation.
- **When to use:** Underlies `clarify`, `project-clarify`, `decision-map`; not a standalone project workflow.
- **Invocation:** Model-invoked (engine for other Skills).
- **Package:** [skills/socratic/](skills/socratic/)
- **Status:** Admitted first-party; ADAPT (Matt `grilling`).
- **Evidence:** [SKILL.md](skills/socratic/SKILL.md), [ATTRIBUTION.md](skills/socratic/ATTRIBUTION.md).
- **Installation path:** `skills/socratic/` in a host-recognized Skills root.

### tdd

- **Purpose:** Test-driven development — red → green → refactor loop with real tests.
- **When to use:** Implementing coding features test-first or fixing bugs with regression cover.
- **Invocation:** Model-invoked.
- **Package:** [skills/tdd/](skills/tdd/)
- **Status:** Admitted first-party; PORT — NO REDESIGN (Matt `tdd`).
- **Evidence:** [SKILL.md](skills/tdd/SKILL.md), [ATTRIBUTION.md](skills/tdd/ATTRIBUTION.md).
- **Installation path:** `skills/tdd/` in a host-recognized Skills root.

### teach

- **Purpose:** Teach a new skill or concept within the workspace.
- **When to use:** User wants a guided lesson on a topic.
- **Invocation:** User-invoked only.
- **Package:** [skills/teach/](skills/teach/)
- **Status:** Admitted first-party; PORT — NO REDESIGN (Matt `teach`).
- **Evidence:** [SKILL.md](skills/teach/SKILL.md), [ATTRIBUTION.md](skills/teach/ATTRIBUTION.md).
- **Installation path:** `skills/teach/` in a host-recognized Skills root.

### to-questionnaire

- **Purpose:** Turn an undecided question into a questionnaire for the person who holds the information.
- **When to use:** Information is held by another person, not the current user.
- **Invocation:** User-invoked only.
- **Package:** [skills/to-questionnaire/](skills/to-questionnaire/)
- **Status:** Admitted first-party; PORT — NO REDESIGN.
- **Evidence:** [SKILL.md](skills/to-questionnaire/SKILL.md), [ATTRIBUTION.md](skills/to-questionnaire/ATTRIBUTION.md).
- **Installation path:** `skills/to-questionnaire/` in a host-recognized Skills root.

### wait-what

- **Purpose:** Re-pitch the last message that did not land.
- **When to use:** User says "wait, what?" or similar confusion.
- **Invocation:** User-invoked only.
- **Package:** [skills/wait-what/](skills/wait-what/)
- **Status:** Admitted first-party; PORT — NO REDESIGN.
- **Evidence:** [SKILL.md](skills/wait-what/SKILL.md), [ATTRIBUTION.md](skills/wait-what/ATTRIBUTION.md).
- **Installation path:** `skills/wait-what/` in a host-recognized Skills root.

### wizard

- **Purpose:** Interactive bash wizard for human-only steps (provisioning, secrets, dashboards, cutovers).
- **When to use:** Task needs a guided human walk-through, not an agent-auto step.
- **Invocation:** Model-invoked.
- **Package:** [skills/wizard/](skills/wizard/)
- **Status:** Admitted first-party; PORT — NO REDESIGN (Matt `wizard`).
- **Evidence:** [SKILL.md](skills/wizard/SKILL.md), [ATTRIBUTION.md](skills/wizard/ATTRIBUTION.md).
- **Installation path:** `skills/wizard/` in a host-recognized Skills root.

### writing-for-agents

- **Purpose:** Author or edit agent-facing documents (Skills, AGENTS.md, CLAUDE.md) for model consumption.
- **When to use:** Creating or improving agent instructions or Skill packages.
- **Invocation:** Model-invoked.
- **Package:** [skills/writing-for-agents/](skills/writing-for-agents/)
- **Status:** Admitted first-party; PORT — NO REDESIGN.
- **Evidence:** [SKILL.md](skills/writing-for-agents/SKILL.md), [ATTRIBUTION.md](skills/writing-for-agents/ATTRIBUTION.md).
- **Installation path:** `skills/writing-for-agents/` in a host-recognized Skills root.

## Source-state boundaries

| State | Where it belongs | Catalog treatment |
| --- | --- | --- |
| First-party | This repository | Listed above when admitted. |
| Approved Port (Matt) | This repository with `ATTRIBUTION.md` | Listed above; self-contained, no Matt runtime dependency. |
| Direct upstream | Original upstream repository | Mentioned as dependency; never copied here unmodified. |
| Modified third-party | `skills-3rdParty` | Listed in that private repository's source catalog after fork admission. |
| Deprecated or archived | Released migration record | Listed with replacement and migration guidance. |

See [maintenance](docs/MAINTENANCE.md) for synchronization and [admission](docs/SKILL_ADMISSION.md) for the ownership gate.
