---
name: project-retro
description: >
  Review a completed project or complex working session, trace meaningful
  execution friction to its root causes, verify which issues are already
  permanently guarded, and surface durable improvements to workflow,
  navigation, automated checks, steering, information access, test
  architecture, and tool economy.
---

# Project Retro

`project-retro` is a workflow-aware retrospective skill. Following a complex
project, implementation session, review, or release, it traces evidenced
friction to root causes, verifies which issues are already permanently
guarded at current HEAD, and extracts durable improvements across the agent's
environment, workflow, and guardrails.

## When to use

- **Workflow completion:** After `project-review` issues a verdict,
  `release-workflow` prepares/completes a release, or a complex implementation
  effort finishes.
- **Friction-heavy session:** When an agent encounters repeated rework,
  reviewer-caught mechanical defects, unverified assumptions, unfindable
  contracts, expensive tool churn, or cross-repo friction.
- **User-invoked:** On direct human request (`project-retro`, `retrospective`,
  `$project-retro`).

## Agent self-evaluation trigger (Workflow final step)

At the final step of a project or task, evaluate whether a retrospective is
warranted using the value-judgment matrix in [heuristics.md](references/heuristics.md):

| Friction signal | Recurrence | Preventable | Impact | Decision |
| :--- | :--- | :--- | :--- | :--- |
| **Preventable failure** | High | High (lint/test/CI) | High | **Invoke** |
| **Reviewer / Standards gap** | High | High (mechanical check) | Medium | **Invoke** |
| **Hidden dependency / Test coupling** | High | High (hermetic boundary) | High | **Invoke** |
| **Release / Workflow friction** | High | High (preflight guard) | High | **Invoke** |
| **Information gap / Extrapolation** | Medium | Medium (provenance ref) | Medium | **Invoke** |
| **Navigation / Steering bloat** | Medium | Medium (index / cleanup) | Low | **Invoke if >1** |
| **Tool economy churn** | Medium | High (query planning) | Medium | **Invoke if >1** |
| **Routine smooth delivery** | Low | N/A | None | **Skip** |

- **If meaningful, reusable friction is observed:** Invoke `project-retro` to
  extract durable systemic improvements.
- **Routine smooth delivery:** Routine sessions with no reusable systemic
  friction complete through the existing workflow without opening a
  retrospective.

## Retrospective Workflow

1. **Establish Scope:** Identify target scope (`current session`,
   `implementation effort`, `workflow run`, `release cycle`, or user range).
2. **Gather Primary Evidence:** Inspect primary sources: git history and diff,
   test and CI outputs, review findings, release evidence, relevant steering,
   and primary-source references involved in the friction.
3. **Extract Friction Signals:** Scan candidate friction across core categories:
   - **Navigation:** Are file pointers, indices, or contract locations missing?
   - **Automated checks:** Could a deterministic check (lint, typecheck, hook,
     script, preflight) replace manual vigilance or guesswork?
   - **Coding standards:** Should mechanical reviewer rules move to linters,
     leaving judgment calls to standards?
   - **Steering economy:** Can instructions in `AGENTS.md` or `CLAUDE.md` be
     slimmed, uncoupled from stale paths, or moved to progressive references?
   - **Tool economy:** Did the agent make redundant reads or queries without
     an active consumer?
   - **Information access:** Were upstream schemas, provenance, or runtime
     logs unavailable locally?
   - **Test architecture:** Are tests coupled to external sibling repos,
     missing hermetic snapshots, or lacking drift detection?
   - **Workflow / Release mechanics:** Were tag immutability, receipt
     invariants, or state transitions unprotected?
4. **Verify Current State (Deduplication):** Inspect repository `HEAD` for
   each candidate finding before reporting:
   - **`[CLOSED]`:** CLOSED findings document durable lessons already protected
     by current code, tests, CI, references, or workflow. They remain in the
     retrospective as evidence of successful closure and stay outside Suggested
     Actions.
   - **`[PARTIAL]`:** Immediate symptom repaired, but long-term automated
     guardrail, test coverage, or reference remains missing.
   - **`[OPEN]`:** Systemic gap remains unguarded and can recur.
5. **Separate Immediate Fix from Permanent Improvement:** Distinguish
   `Observed incident` $\to$ `Immediate repair` $\to$ `Permanent guardrail`.
   The retrospective focuses strictly on permanent systemic guardrails.
6. **Classify Improvement Type & Nature:** Label each finding's category and
   nature (`Mechanical` $\to$ test/script/CI; `Judgment-based` $\to$ standards/review;
   `Hybrid`).
7. **Rank by Leverage:** Order remaining findings by:
   `Severity × recurrence probability × generalizability ÷ maintenance cost`.
8. **Present Findings:** Use the neutral, facts-first template in
   [template.md](references/template.md), separating `Already-Closed Guardrails`
   from `Remaining Systemic Findings`.
9. **Formulate Suggested Actions:** Propose bounded, actionable steps
   (default top 3) under `Suggested Actions — Pending Approval`.
10. **Transition State & Await Selection:** Transition the retrospective to
    `AWAITING_SELECTION`. Await explicit human selection before moving any
    recommendation to `APPROVED_ACTION`.

## Audit Communication

Use a neutral engineering audit tone.

Begin with verified repository evidence, current state, and test results.

Frame findings around systems, workflows, information architecture,
guardrails, and tool behavior.

Describe recommendations through evidence, expected leverage, and the
corresponding durable improvement.

Keep the report concise enough for human selection and follow-up.

## Handoff

After presenting findings, transition the retrospective to:

AWAITING_SELECTION

The report provides ranked recommendations and sufficient evidence for the
human to choose the next action.

When the human selects a recommendation, transition the selected item to:

APPROVED_ACTION

The selected action can then enter its normal bounded implementation and
verification workflow.

## References

- [categories.md](references/categories.md) — Detailed inspection criteria,
  signals, and typical durable improvements across all categories.
- [heuristics.md](references/heuristics.md) — Decision matrix, tri-state status
  classification (`CLOSED`/`PARTIAL`/`OPEN`), and reporting discipline.
- [template.md](references/template.md) — Standard markdown retrospective
  report template.
