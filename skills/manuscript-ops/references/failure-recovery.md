# Failure and recovery

## Dependency missing

Return `BLOCKED` with the missing dependency, required step, installation
instructions, preserved evidence, and exact resume invocation. Do not implement
a reduced private clone of `grill-me`, `wayfinder`, or `review-loop`.

## Snapshot stale

Re-run the read-only assessment when the snapshot exceeds the Profile freshness
limit or when scope, sources, outputs, tools, or project instructions changed.
Never resume from a stale route or capability claim.

## Same-day version collision

Run:

```text
python scripts/next_version.py --date YYYY.MM.DD --root <project-root>
```

Use the returned suffix consistently in bookmark, receipt, output, and archive
names.

## Review does not converge

Stop after three rounds, or after two rounds with no material progress. Preserve
all findings and dispositions, state the unresolved acceptance criteria, and
return `BLOCKED`. A user may approve a documented risk, revise the Brief, or
supply missing evidence; the agent may not lower the bar.

## No independent agent

Create a frozen review packet with hashes. Ask the user to open a fresh session
and provide the exact evaluator prompt. Continue with `resume` after importing
the verdict. Record independence as `fresh_session` or `degraded`.

## Render or visual QA unavailable

Preserve the generated artifact and structural checks. Mark layout
`not tested`, then return `DEGRADED` only if the approved acceptance policy
allows it; otherwise return `BLOCKED`. Never say that the format or layout
passed.

## Round-trip failure

Keep the original and failed round-trip output as separate hashed evidence.
Identify the lost invariants and choose one:

- repair the generator or adapter;
- designate a target application and lock its output;
- narrow the deliverable contract with user approval;
- return `BLOCKED`.

## Existing path mismatch

Update the Project Profile mapping after verifying the actual path. Do not move
or rename existing project content solely to satisfy the standard layout.

## Interrupted run

Read `.manuscript-ops/state.json` first, then the named snapshot, receipt, and
latest review report. Compare hashes before continuing. Append evidence; do not
restart or overwrite a completed batch or review round.

## Jujutsu mismatch

If version or command behavior differs from the tested baseline, probe help and
run the intended sequence in a disposable repository. Record the observed
capability. Do not auto-upgrade, auto-downgrade, add a remote, or use destructive
recovery.

