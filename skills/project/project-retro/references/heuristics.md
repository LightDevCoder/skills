# Agent Self-Evaluation Heuristics & Decision Matrix

When reaching the conclusion of a project workflow (after `project-review` or `release-workflow`), or at the end of a complex implementation milestone, the Agent evaluates whether to invoke `project-retro`.

---

## 1. Decision Principles

1. **Friction-Driven:** Retrospectives originate from evidenced execution friction rather than procedural routine.
2. **Value-Driven Invocation:** Run a retrospective when meaningful, reusable systemic improvements can be extracted. Routine sessions with no reusable systemic friction complete through the existing workflow without opening a retrospective.
3. **Current-State Deduplication:** Verify every candidate finding against current repository `HEAD` before reporting, classifying findings into `CLOSED`, `PARTIAL`, or `OPEN`.
4. **Neutral Tone:** Present audit findings directly from verified repository evidence, test results, and system state.
5. **Actionability:** Formulate concrete, bounded improvements (tests, scripts, references, linters, or steering cleanups) that transition to `AWAITING_SELECTION`.

---

## 2. Value-Judgment Trigger Matrix

Evaluate the session against the following indicators:

| Signal | Evidence Strength | Recurrence Likelihood | Mechanical Preventability | Future Impact | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Preventable failure** | High (failing test/crash) | High | High (lint/test/CI) | High | **Invoke** |
| **Reviewer / Standards gap** | High (review finding) | High | High (deterministic check) | Medium | **Invoke** |
| **Release / Provenance friction** | High (tag movement / audit) | High | High (preflight script) | High | **Invoke** |
| **Hidden dependency / Coupling** | High (standalone test failure) | High | High (hermetic boundary) | High | **Invoke** |
| **Information gap / Guessing** | Medium (extrapolated mappings) | Medium | Medium (provenance ref) | Medium | **Invoke** |
| **Steering bloat / Stale pointer** | Medium (stale path in steering) | Medium | Medium (wayfinding rule) | Low | **Invoke if combined** |
| **Tool economy churn** | Medium (zero-value queries) | Medium | High (query planning) | Medium | **Invoke if combined** |
| **Isolated minor typo / bug** | Low (single trivial fix) | Low | Low | Low | **Skip** |
| **Routine smooth delivery** | None (clean execution) | None | N/A | None | **Skip** |

### Evaluation Outcome

- **Trigger `project-retro`:** If any **High** impact indicator is present, or if two or more **Medium** indicators are detected.
- **Skip `project-retro`:** If zero High indicators and at most one Medium/Low indicator are present, and the primary work completed cleanly. Routine sessions with no reusable systemic friction complete through the existing workflow without opening a retrospective.

---

## 3. Tri-State Finding Classification Model

When analyzing candidate findings against current repository `HEAD`, assign one of three statuses:

```text
Finding
├── evidence (file, commit, command)
├── friction (observed failure or delay)
├── root_cause (why tooling/workflow missed it)
├── status
│   ├── [CLOSED]  -> CLOSED findings document durable lessons already protected by current
│   │                code, tests, CI, references, or workflow. They remain as evidence of
│   │                successful closure and stay outside Suggested Actions.
│   ├── [PARTIAL] -> Immediate symptom fixed, but durable guardrail, test, or reference has gaps.
│   │                Eligible for systemic findings.
│   └── [OPEN]    -> Problem remains unaddressed and can recur in future workflows.
│                    Eligible for systemic findings.
├── existing_guardrail
├── remaining_gap
├── durable_improvement
├── improvement_type
└── priority
```

---

## 4. Audit Invariants & Reporting Discipline

When compiling a retrospective report, guide the findings with these discipline rules:

1. **Neutral Tone:** Use a neutral engineering audit tone. Begin with verified repository evidence, current state, and test results. Frame findings around systems, workflows, information architecture, guardrails, and tool behavior.
2. **Facts Before Conclusions:** Ground all assertions in verified repository HEAD state, test suite outcomes, and peeled commit/tag/release records.
3. **Recommendation Is Not Authorization:** Transition completed retrospective findings to `AWAITING_SELECTION`. Maintain proposed changes under `Suggested Actions — Pending Approval`. When the human selects a recommendation, transition the selected item to `APPROVED_ACTION` for bounded execution.
4. **Deduplicate Against Current State:** Inspect repository HEAD to identify existing guardrails. Record verified historical solutions under `Already-Closed Guardrails [CLOSED]`, maintaining them outside suggested actions.
5. **Preserve Conditional Evidence:** Record conditional environment data with complete context (for example, distinguishing standalone offline test passes from companion-enabled integration passes).
6. **Explicit Structural Separation:** Trace each finding through its lifecycle stages:
   - Observed incident / friction
   - Immediate repair
   - Permanent systemic guardrail
   - Proposed action in `AWAITING_SELECTION` state
