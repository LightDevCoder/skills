# Agent Self-Evaluation Heuristics & Decision Matrix

When reaching the conclusion of a project workflow (after `project-review` or `release-workflow`), or at the end of a complex implementation milestone, the Agent evaluates whether to invoke `project-retro`.

---

## 1. Decision Principles

1. **Friction-Driven:** Retrospectives are triggered by evidenced execution friction, not by rote procedure.
2. **Value-Driven Invocation:** Run a retrospective only when meaningful, reusable systemic improvements can be extracted. If a session ran smoothly without systemic friction, skip cleanly to save tokens and avoid noise.
3. **Current-State Deduplication:** Every candidate finding must be verified against current repository `HEAD` before reporting, classifying findings into `CLOSED`, `PARTIAL`, or `OPEN`.
4. **Neutral Tone Discipline:** Present cold, audit-style findings directly from evidence without flattery, congratulations, or subjective commentary.
5. **Actionability:** Retrospective findings must propose concrete, bounded improvements (tests, scripts, references, linters, or steering cleanups).

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
- **Skip `project-retro`:** If zero High indicators and at most one Medium/Low indicator are present, and the primary work passed cleanly.

---

## 3. Tri-State Finding Classification Model

When analyzing candidate findings against current repository `HEAD`, assign one of three statuses:

```text
Finding
├── evidence (file, commit, command)
├── friction (observed failure or delay)
├── root_cause (why tooling/workflow missed it)
├── status
│   ├── [CLOSED]  -> Root cause already has persistent code, test, CI, doc, or process guardrail.
│   │                Document as closed experience; do NOT generate duplicate action items.
│   ├── [PARTIAL] -> Immediate symptom fixed, but durable guardrail, test, or reference has gaps.
│   │                Enter systemic findings.
│   └── [OPEN]    -> Problem remains unaddressed and can easily recur in future workflows.
│                    Enter systemic findings.
├── existing_guardrail
├── remaining_gap
├── durable_improvement
├── improvement_type
└── priority
```

---

## 4. Audit Invariants & Reporting Discipline

When compiling a retrospective report, strictly enforce these discipline rules:

1. **Neutral Tone:** Do not praise, thank, flatter, congratulate, or evaluate the reviewer or user. Start directly from verified facts, test status, and findings.
2. **Facts Before Conclusions:** Verify repository `HEAD`, test suite status, and commit/tag/release state before asserting claims.
3. **Recommendation Is Not Authorization:** Never label work "Approved" unless the user explicitly authorized execution in their message. Keep proposed actions labeled under `Suggested Actions — Pending Approval`.
4. **Deduplicate Against Current State:** Before creating a proposed TODO, verify whether the guard or test already exists at `HEAD`. Record already-closed historical remediations under `Already-Closed Guardrails [CLOSED]`, keeping them out of suggested actions.
5. **Preserve Conditional Evidence:** Do not collapse conditional environment data (e.g. "394 pass + 1 skip standalone / 395 pass with companion") into an unqualified aggregate.
6. **Explicit Structural Separation:** Clearly distinguish:
   - Observed incident / friction
   - Immediate repair
   - Permanent systemic guardrail
   - Proposed action
