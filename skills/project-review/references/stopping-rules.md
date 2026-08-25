# Stopping Rules

## State values

Use one current status in `.review-loop/state.md`:

`INIT`, `READY`, `CRITIC`, `REPAIR`, `EVALUATE`, `PASS`, `FAIL`, or `BLOCKED`.

Record the Charter revision, selected Profile, round number, configured maximum,
independence declaration, last completed action, next action, blocker, and
links to evidence and the finding registry.

## Normal transitions

```text
INIT -> READY -> CRITIC -> REPAIR -> EVALUATE -> PASS
                         |                     |
                         +---------------------+-> FAIL
                                               |
                         bounded repair path  +-> CRITIC (next round)
any state -> BLOCKED
```

Enter `REPAIR` only for at least one confirmed, in-scope, bounded finding. When
there is no such finding, proceed from `CRITIC` to `EVALUATE` with the original
Producer evidence.

## Final verdicts

- `PASS`: every frozen criterion and Profile requirement has accurately labeled
  evidence, no blocking confirmed finding remains, and the required fresh
  Evaluator accepts the baseline.
- `FAIL`: a frozen criterion is unmet and no permitted bounded repair can
  resolve it. Include the unmet criterion and why the repair path is not
  allowed or cannot converge.
- `BLOCKED`: required acceptance source, authority, access, environment,
  evidence, or independent context is unavailable; state and evidence disagree;
  or the configured repair limit prevents safe convergence.

## Required stops

- For a missing acceptance source, return `BLOCKED`; do not synthesize or infer
  a replacement baseline.
- For unavailable required independent context, return `BLOCKED`; no
  same-context role-play can substitute for it.
- For a repair that expands the frozen scope, return `FAIL` when the current
  baseline is known to be unmet without that repair, or `BLOCKED` when new
  authority, source, access, or a decision is needed to determine the path.
- For contradictory records, return `BLOCKED` until the contradiction is
  resolved without rewriting prior evidence.

## Repair limit and progress

- Configure the maximum before the first review; use three rounds by default.
- Start at round 1. Open another round only with a concrete, bounded repair
  path and preserved evidence from the previous round.
- When evaluation records an unmet criterion but a permitted bounded repair
  remains, preserve that round's `FAIL` result and resume at `CRITIC` for the
  next round. `FAIL` is terminal only when no permitted repair path remains.
- If two consecutive rounds make no material progress, return `BLOCKED`.
- At the maximum round, return `BLOCKED` when acceptance has not been reached.
- Never run another round merely to obtain a more favorable conclusion.

## Blocker record

Every `BLOCKED` state names the exact blocker, attempted resolution, owner of
the unblock, and smallest safe next action. Do not use `BLOCKED` merely because
work is difficult when an in-scope action remains.

## PASS prohibition

Never return `PASS` because evidence appears persuasive, a reviewer timed out,
an external service failed, a required scenario was skipped, or the baseline was
quietly weakened. Preserve the limitation and return `FAIL` or `BLOCKED` under
the rules above.
