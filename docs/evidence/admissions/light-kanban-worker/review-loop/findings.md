# Finding Registry

## Finding F-001
- First recorded: round-01
- Status: resolved
- Severity: Low
- Related acceptance criterion: AC-11
- Canonical summary: the human-only review boundary checker matched each forbidden verb loosely and never pinned the full canonical sentence, so the shipped wording could drift undetected.
- Related finding: none
- Current evidence: round-01/critic-findings.md
- Resolution evidence: round-01/repair-evidence.md (worker_checks.py now asserts the canonical boundary sentence plus the per-verb gates; SKILL.md wording pinned by both)

## Finding F-002
- First recorded: round-01
- Status: resolved
- Severity: Low
- Related acceptance criterion: AC-11
- Canonical summary: two negative fixtures were textual mutations rather than self-consistent worker protocols that violate exactly one rule.
- Related finding: none
- Current evidence: round-01/critic-findings.md
- Resolution evidence: round-01/repair-evidence.md (all four fixtures rewritten as complete worker protocols violating exactly their target rule; the contract suite now asserts single-rule precision)

## Finding F-003
- First recorded: round-01
- Status: resolved
- Severity: Low
- Related acceptance criterion: AC-3
- Canonical summary: SKILL.md stated "never guessed" identity but did not enumerate the legal sources of the agent id.
- Related finding: none
- Current evidence: round-01/critic-findings.md
- Resolution evidence: round-01/repair-evidence.md (Configuration section now names the only legal id sources — current invocation/scheduled task or LIGHT_KANBAN_AGENT_ID — and forbids per-run invented ids)

## Finding F-004
- First recorded: round-01
- Status: rejected
- Severity: Low
- Related acceptance criterion: AC-10
- Canonical summary: references/api.md documents createdAt/updatedAt/status more broadly than SKILL.md's minimum read set.
- Related finding: none
- Current evidence: round-01/critic-findings.md
- Resolution evidence: the worker's ordering rules (SKILL.md "Review feedback first" / "Claiming new work", api.md "Ordering notes") actually read updatedAt/createdAt, so the reference documents fields the protocol uses; SKILL.md's read list is a stated minimum ("at least"), not an exhaustive set. Cosmetic and not a contract gap — rejected.
