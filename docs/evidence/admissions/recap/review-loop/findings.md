# Finding Registry

## Finding F-001
- First recorded: round-01 Evaluator
- Status: superseded for admission; not applicable to the prompt-only fast track
- Severity: High
- Related acceptance criterion: AC-7
- Canonical summary: Executable PowerShell package tests lack the separate Standards and Spec `code-review` evidence required by the Agent-Skill Profile and repository review policy.
- Related finding: none
- Current evidence: [round-01/evaluator-verdict.md](rounds/round-01/evaluator-verdict.md)
- Resolution evidence: the user-approved fast track does not require Standards/Spec review for self-contained static contract tests; final fast-track verdict confirms no behavior-risk escalation

## Finding F-002
- First recorded: round-01 Evaluator
- Status: confirmed
- Severity: Medium
- Related acceptance criterion: AC-6
- Canonical summary: Catalog and current-branch documentation claim `recap` is admitted while the authoritative admission record is still in progress.
- Related finding: none
- Current evidence: [round-01/evaluator-verdict.md](rounds/round-01/evaluator-verdict.md)
- Resolution evidence: pre-admission wording was synchronized before evaluation and final closeout now records fast-track PASS

## Finding F-003
- First recorded: round-01 Standards specialist
- Status: confirmed
- Severity: High
- Related acceptance criterion: AC-7
- Canonical summary: A deterministic canned-string predicate is named and reported as a behavior test, which can be mistaken for Agent/runtime evidence.
- Related finding: F-007
- Current evidence: [round-01/code-review-standards.md](rounds/round-01/code-review-standards.md)
- Resolution evidence: deterministic suite renamed to `recap-output-contract-tests.ps1`; final Evaluator confirmed all current labels are accurate

## Finding F-004
- First recorded: round-01 Standards specialist
- Status: confirmed
- Severity: High
- Related acceptance criterion: AC-7
- Canonical summary: Both new PowerShell suites can report PASS after every assertion call is removed because they lack a zero-assertion guard.
- Related finding: none
- Current evidence: [round-01/code-review-standards.md](rounds/round-01/code-review-standards.md)
- Resolution evidence: both package suites fail when assertion count is zero; independently rerun at 12 + 8 assertions

## Finding F-005
- First recorded: round-01 Standards specialist
- Status: confirmed
- Severity: Medium
- Related acceptance criterion: AC-7
- Canonical summary: Contract checks for compaction and review-loop boundaries use weak keyword presence and do not reject opposite-polarity mutations.
- Related finding: none
- Current evidence: [round-01/code-review-standards.md](rounds/round-01/code-review-standards.md)
- Resolution evidence: prohibition-aware compaction/handoff checks and an unsafe opposite-polarity mutation fixture pass final verification

## Finding F-006
- First recorded: round-01 Standards specialist
- Status: rejected
- Severity: Low
- Related acceptance criterion: AC-7
- Canonical summary: The two small PowerShell suites duplicate assertion helper and reporting scaffolding.
- Related finding: none
- Current evidence: [round-01/code-review-standards.md](rounds/round-01/code-review-standards.md)
- Resolution evidence: rejected because keeping the suites self-contained prevents a shared helper from becoming an additional runtime/test dependency; the duplicated scaffold is bounded and not a documented violation

## Finding F-007
- First recorded: round-01 Spec specialist
- Status: rejected
- Severity: High
- Related acceptance criterion: AC-3, AC-4
- Canonical summary: The PowerShell fixtures do not execute an Agent, so VS-1 through VS-3 allegedly lack executable behavioral evidence.
- Related finding: F-003
- Current evidence: [round-01/code-review-spec.md](rounds/round-01/code-review-spec.md)
- Resolution evidence: rejected because the Charter and Profile accept fresh Agent observations; E-005, E-006, and E-007 separately supply behavioral/invocation evidence, while the scripts are accurately limited to structural output-contract checks after F-003 repair

## Finding F-008
- First recorded: round-01 Spec specialist
- Status: confirmed
- Severity: Medium
- Related acceptance criterion: AC-3, AC-7
- Canonical summary: Output validation rejects only a few labels and permits obvious alternatives such as Status, Result, or bold Recap labels.
- Related finding: none
- Current evidence: [round-01/code-review-spec.md](rounds/round-01/code-review-spec.md)
- Resolution evidence: generalized leading-label rejection covers Recap, Status, Result, and bold-label fixtures and passes final verification

## Finding F-009
- First recorded: round-01 Spec specialist
- Status: confirmed
- Severity: Low
- Related acceptance criterion: AC-6
- Canonical summary: Collection tests assert the six-package candidate tree but do not explicitly assert that stable v0.1.1 remains a five-package release.
- Related finding: none
- Current evidence: [round-01/code-review-spec.md](rounds/round-01/code-review-spec.md)
- Resolution evidence: both PowerShell and Python collection suites explicitly assert the stable v0.1.1 five-package boundary and pass final verification

## Finding F-010
- First recorded: round-02 Evaluator
- Status: superseded for admission; not applicable to the prompt-only fast track
- Severity: High
- Related acceptance criterion: AC-8
- Canonical summary: The full Agent-Skill Profile asks for a behavioral failure or missing-dependency path, while the evidence contains success, empty-session boundary, and non-trigger observations only.
- Related finding: none
- Current evidence: [round-02/evaluator-verdict.md](rounds/round-02/evaluator-verdict.md)
- Resolution evidence: final fast-track Evaluator confirmed explicit-use and non-trigger observations are sufficient because the eligible package prohibits dependencies and runtime failure modes
