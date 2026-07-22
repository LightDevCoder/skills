# Finding Registry

`findings.md` is the canonical registry for finding identity and lifecycle.
Round files preserve what a reviewer observed; they do not create a second
identity system.

## Stable identity rules

- The Finding ID is stable from its first recorded candidate through every later
  round, disposition, repair, and verdict.
- Allocate the next unused `F-###` when a candidate is first recorded. An ID
  must not be reused, even when the candidate is rejected or later resolved.
- Re-observe the same concern under its existing ID. Mark a genuinely duplicate
  candidate `duplicate` and link to the canonical ID.
- Keep the candidate evidence, disposition, and resolution evidence. Do not
  delete a rejected candidate or replace it with a differently numbered copy.

## Registry record

```markdown
# Finding Registry

## Finding F-001
- First recorded: round-01
- Status: pending | confirmed | rejected | duplicate | out-of-scope | resolved
- Severity: Critical | High | Medium | Low
- Related acceptance criterion: AC-<n> or <none with reason>
- Canonical summary: <one stable claim>
- Related finding: F-<n> or none
- Current evidence: <round evidence link>
- Resolution evidence: <required after disposition>
```

## Candidate record

Store each Critic candidate in `round-N/critic-findings.md` and reference its
registry ID:

```markdown
## Finding F-001
- Severity: Critical | High | Medium | Low
- Related acceptance criterion: AC-<n> or <none with reason>
- Evidence: <path, command output, or observation>
- Expected behavior: <Charter-backed result>
- Observed behavior: <actual result>
- Recommended minimal repair: <candidate, not an instruction>
- Disposition: pending | confirmed | rejected | duplicate | out-of-scope
- Resolution evidence: <verification or technical reason>
- Related finding: F-<n> or none
```

## Dispositions

- `confirmed`: evidence shows an in-scope gap against the frozen baseline; a
  bounded repair may be considered.
- `resolved`: after a bounded Producer repair, the fresh Evaluator no longer
  reproduces the same gap and links the repair and verification evidence. Keep
  the original candidate, disposition history, and stable ID.
- `rejected`: the claim is not reproduced, conflicts with stronger evidence, or
  rests on an incorrect assumption; state why and retain its evidence.
- `duplicate`: link to the canonical finding; do not make a second repair path.
- `out-of-scope`: the concern may be valid but cannot enter the current repair
  path. Preserve it and use a Change Proposal if it should alter the baseline.

Never confirm a candidate only because the Critic recommends it. Never close a
finding by changing its severity, deleting evidence, or silently assigning a new
ID.

After each bounded repair, the Evaluator rechecks the same Finding ID. It marks
the record `resolved` only when the original acceptance gap is absent and the
corresponding criterion is evidenced; otherwise it remains `confirmed` for the
next permitted round.
