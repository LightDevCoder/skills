# Retrospective Report Template

Use this format when presenting retrospective findings:

```markdown
# Session Retrospective

## Trigger & Scope

- **Scope:** [Current session, specific effort, workflow, release cycle, or user-specified range]
- **Friction trigger:** [Why retrospective was invoked, e.g. preventable failure, reviewer gap, test coupling]
- **Evidence reviewed:** [Exact commit SHA, changed files, test output, review findings, steering files]

## Already-Closed Guardrails

### [CLOSED] [Finding Title]
- **Original friction:** [Observed issue during implementation/review]
- **Current guardrail:** [Implemented code, test, CI, or doc mechanism at HEAD]
- **Verification:** [Exact test names or commands proving closure at HEAD]

## Remaining Systemic Findings

### 1. [OPEN/PARTIAL] [Category] — [Concise Title]
**Severity:** High / Medium / Low

- **Evidence:** [Exact file, commit, log, or command reference]
- **Observed friction:** [What failed or caused execution friction]
- **Root cause:** [Why existing workflow/tooling did not prevent it earlier]
- **Current state:** [What immediate repair was made vs what systemic gap remains]
- **Durable improvement:** [Concrete permanent guardrail, script, test, or reference]
- **Improvement type:** [Automated Guardrail / Navigation / Reference & Provenance / Test Architecture / Steering / Tooling / Workflow / Human Judgment]
- **Mechanical vs Judgment:** [Mechanical / Judgment-based / Hybrid]

### 2. [OPEN/PARTIAL] [Category] — [Concise Title]
...

## Suggested Actions — Pending Approval

1. [Specific bounded change, e.g. wire preflight script into CI]
2. [Specific reference update or contract test]
3. [Specific steering cleanup or navigation pointer]
```
