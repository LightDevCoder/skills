# Code Review - Standards Axis

- Reviewer: fresh independent read-only agent `recap_code_standards`
- Fixed point: `origin/main` at `178b2970140b6cd3dc1264d2072ca1ee20ee58f0`
- Candidate commit: `7cd3a60 add manual session recap skill`
- Diff: `git diff origin/main...HEAD`
- Target mutation: none

## Candidates

1. High, hard violation: the canned-string predicate is reported as `RECAP_BEHAVIOR=PASS` without Agent/session execution, conflicting with accurate evidence-label rules.
2. High, hard violation: both suites can pass with zero assertions because no zero-assertion guard exists.
3. Medium, hard violation: bare `compact` and `review-loop` keyword checks accept opposite-polarity mutations.
4. Low, judgment call: duplicated test helper/reporting scaffold across two small suites.

`STANDARDS_FINDINGS=4; WORST_SEVERITY=HIGH`

The Core dispositions are F-003 confirmed, F-004 confirmed, F-005 confirmed,
and F-006 rejected with a dependency-isolation rationale.
