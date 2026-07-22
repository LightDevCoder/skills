---
name: review-loop
description: Run a generic final-acceptance and bounded-repair loop when an artifact's target and approved acceptance source are already defined. Use to freeze the baseline, collect Producer evidence, validate reviewer findings, direct only in-scope repairs, preserve durable state, and issue PASS, FAIL, or BLOCKED.
---

# Review Loop

## Purpose and boundary

Use this Skill after direction and the acceptance source are already clear. It
is model-invoked and may also be manually invoked. It is a final-acceptance
capability, not a discovery, planning, implementation, release, or publication
workflow.

Do not use it to invent a target, settle unresolved product or architecture
decisions, weaken an acceptance source to fit an implementation, or make a
reviewer repair the artifact.

## Public contract

The public protocol has three modes:

- `init`: resolve and freeze the acceptance baseline and Profile before review.
- `review`: run one bounded evidence, critique, validation, repair, and
  evaluation round.
- `resume`: continue the next unfinished recorded action without rewriting
  prior evidence.

If a manual request omits a mode, infer it only when `state.md` makes the next
action unambiguous; otherwise request the mode. The Core may select the
`generic` Profile when no accepted narrower Profile is named. For executable
software, select the accepted `software` Profile and read
[software.md](references/profiles/software.md). For manuscripts, documents,
editions, semantic batches, source locks, or final document deliverables,
select the accepted `manuscript` Profile and read
[manuscript.md](references/profiles/manuscript.md). Read
[agent-skill.md](references/profiles/agent-skill.md) when the target is an
installable Agent Skill package whose installation, discovery, invocation, or
interaction boundaries must be accepted. Read
[specification.md](references/profiles/specification.md) when the target is a
Spec, brief, ticket, or equivalent acceptance contract whose requirements must
be checked against an authoritative source. Read
[generic.md](references/profiles/generic.md) for the deliberately empty
artifact-specific additions of the generic Profile.

## Roles

- **Core:** freezes the baseline, selects the Profile, records state, validates
  candidates, enforces stop conditions, and owns the verdict.
- **Producer:** supplies evidence and is the only role that modifies the target
  during an allowed repair.
- **Critic:** read-only; returns candidate findings using the finding schema.
- **Evaluator:** read-only and fresh from the Critic; judges the frozen baseline
  and admissible evidence rather than accepting a Producer conclusion.

Use the role-packet and independence rules in
[subagent-protocol.md](references/subagent-protocol.md). Do not call same-context
role-play independent review.

## Durable state

Store records in the target project's `.review-loop/` directory. Create it only
when the selected mode requires a durable record. Never overwrite an existing
Charter, finding, or round record.

```text
.review-loop/
|-- charter.md
|-- state.md
|-- findings.md
|-- verdict.md
|-- changes.md
`-- rounds/
    `-- round-01/
        |-- producer-evidence.md
        |-- critic-findings.md
        |-- finding-disposition.md
        |-- repair-plan.md
        |-- repair-evidence.md
        `-- evaluator-verdict.md
```

`charter.md` is the frozen acceptance baseline. `findings.md` is the canonical
finding registry. `state.md` is the current status, round, blocker, and next
action. Round files preserve observations and evidence; `verdict.md` is the
latest conclusion that links to them. Keep facts in their authoritative record
and link rather than duplicate them.

## `init` workflow

1. Inspect the existing state, the proposed acceptance source, and any existing
   Charter. Do not infer a baseline from a Producer summary, a passing check, or
   an external review conclusion.
2. For a missing acceptance source, return `BLOCKED`, record the exact missing
   source and smallest unblock action in `state.md`, and do not start a round.
3. Resolve the Profile. Honor an accepted named Profile; otherwise select the
   applicable Profile (`software` for executable software, `generic` when no
   narrower Profile applies) and record the reason in the Charter.
4. Freeze the baseline with the source location, revision or immutable identity,
   scope, exclusions, criteria, required evidence, approval state, and Profile.
   Use [acceptance-charter.md](references/acceptance-charter.md).
5. Preserve an already approved Charter. A material requirement change needs a
   recorded Change Proposal and new approved revision; it never silently edits
   the current baseline.
6. Set `state.md` to `READY` with the Charter revision, selected Profile,
   configured maximum rounds, independence requirement, and next action.

## `review` workflow

Read `state.md` first. Confirm an approved Charter, a selected Profile, an
available round, and a writable new round directory before progressing.

1. **Collect Producer evidence.** Record scope, commands or observations,
   inputs, outputs, limitations, and an accurate evidence label using
   [evidence-protocol.md](references/evidence-protocol.md). Evidence retains its
   original label across later rounds.
2. **Request a read-only Critic.** Give it only the frozen baseline, bounded
   artifact view, permitted evidence, Profile requirements, and finding schema.
   A Critic result is a candidate, not an instruction.
3. **Validate every candidate.** Assign or reuse its stable Finding ID, then
   record one disposition: `confirmed`, `rejected`, `duplicate`, or
   `out-of-scope`. For the software Profile, ingest `code-review` Standards
   and Spec findings as candidates while preserving their source axis and
   specialist evidence. Preserve the candidate and resolution evidence. Follow
   [finding-schema.md](references/finding-schema.md).
4. **Repair only within the frozen baseline.** Direct only a confirmed,
   in-scope, bounded repair to the Producer. The Producer records repair
   evidence without replacing the original finding or earlier evidence.
5. **Stop scope expansion.** If a repair needs changed requirements, a new
   architecture decision, multiple new implementation tickets, missing access,
   or new user authority, do not repair it. Return `FAIL` when the current
   baseline is demonstrably unmet with no permitted repair; return `BLOCKED`
   when authority, source, access, or an independent context is required to
   determine or perform the next action.
6. **Request a fresh read-only Evaluator.** It reassesses the original baseline,
   Profile, findings, dispositions, repairs, and evidence. An unavailable
   required independent context is `BLOCKED`, not degraded acceptance.
7. **Close the round.** Record the Evaluator judgment, update state and the
   canonical finding registry, then apply the verdict and stopping rules in
   [stopping-rules.md](references/stopping-rules.md).

### Software specialist boundary

When the selected Profile is `software`, invoke the upstream `code-review`
capability at the frozen fixed point and approved Spec. It returns separate
Standards and Spec findings as `review` evidence. The Core validates those
findings through the same generic lifecycle, directs only bounded Producer
repairs, and supplies the fresh Evaluator with the original and repaired
evidence. `code-review` is a specialist and never issues the Program's final
`PASS`, `FAIL`, or `BLOCKED`; review-loop Core owns that verdict.

## `resume` workflow

1. Read `state.md`, the named Charter revision, the finding registry, and the
   latest round evidence before taking action.
2. Confirm that the records agree on the active round and next action. Record a
   mismatch as `BLOCKED` until it is resolved.
3. Re-run only stale or missing evidence, then continue the same permitted
   action or the next round. Append rather than rewrite evidence, findings, or
   verdict history.

Never recreate a completed round or fabricate a Producer, Critic, or Evaluator
record to make the state appear complete.

## Verdicts and limits

The Core owns the final verdict:

- `PASS`: every frozen criterion and Profile requirement has appropriately
  labeled evidence; no blocking confirmed finding remains; the fresh Evaluator
  accepts the baseline.
- `FAIL`: a frozen condition is unmet and cannot be resolved through a
  confirmed, in-scope, bounded repair.
- `BLOCKED`: required baseline, authority, environment, evidence, access, or
  independent context is unavailable; records conflict; or the repair limit
  stops safe convergence.

The default maximum is three rounds. A round may continue only with a concrete,
bounded repair path. At the configured maximum, return `BLOCKED` if acceptance
is not reached. Do not run another round solely to obtain a favorable result.

## References

- [generic.md](references/profiles/generic.md): Profile with no
  artifact-specific rules.
- [software.md](references/profiles/software.md): software axes, evidence,
  `code-review` specialist boundary, severity guidance, acceptance conditions,
  and software-specific failure cases.
- [manuscript.md](references/profiles/manuscript.md): manuscript axes,
  source/provenance and lifecycle evidence, format/render/visual QA seams,
  severity guidance, acceptance conditions, and manuscript-specific failure
  cases.
- [agent-skill.md](references/profiles/agent-skill.md): Agent-Skill package
  structure, installation/discovery, invocation, behavior, composition seams,
  executable evidence, severity guidance, acceptance conditions, and failure
  cases.
- [specification.md](references/profiles/specification.md): specification
  authority, scope and criterion traceability, ambiguity and contradiction
  control, testability, change/handoff evidence, severity guidance, acceptance
  conditions, and specification-specific failure cases.
- [acceptance-charter.md](references/acceptance-charter.md): frozen baseline,
  Profile, and revision fields.
- [evidence-protocol.md](references/evidence-protocol.md): Producer and repair
  evidence labels and records.
- [finding-schema.md](references/finding-schema.md): stable identities,
  dispositions, and registry format.
- [review-rubric.md](references/review-rubric.md): generic Core checks and
  Profile-supplied review dimensions.
- [subagent-protocol.md](references/subagent-protocol.md): read-only Critic and
  Evaluator packets and independence declaration.
- [stopping-rules.md](references/stopping-rules.md): state transitions, repair
  limit, scope-expansion stop, and verdict rules.
- [mission-center-compatibility.md](references/mission-center-compatibility.md):
  optional pointer integration with a separate task system.
- [attribution.md](references/attribution.md): source attribution.

For structural contract coverage, run:

```powershell
& .\review-loop\tests\generic-profile-contract-tests.ps1
```

This test validates the documented public protocol. It is not host-runtime or
independent-acceptance proof.

For software-profile integration coverage, run:

```powershell
& .\review-loop\tests\software-profile-contract-tests.ps1
& .\review-loop\tests\software-profile-behavior-tests.ps1
```

These tests exercise the software Profile's `code-review` candidate handoff,
bounded repair and scope stop, and the Core-owned final verdict in disposable
fixtures. They are protocol evidence, not a substitute for independent review
of a live software target.

For manuscript-profile integration coverage, run:

```powershell
& .\review-loop\tests\manuscript-profile-contract-tests.ps1
& .\review-loop\tests\manuscript-profile-behavior-tests.ps1
```

These tests exercise manuscript evidence and applicability through the generic
finding, repair, and Evaluator lifecycle in fresh disposable fixtures. They are
protocol evidence, not a substitute for independent review of a live manuscript.

For Agent-Skill Profile integration coverage, run:

```powershell
& .\review-loop\tests\agent-skill-profile-contract-tests.ps1
& .\review-loop\tests\agent-skill-profile-behavior-tests.ps1
```

These tests exercise package installation/discovery, invocation boundaries,
success/boundary/failure evidence, executable-script evidence, and interaction
handoffs through the generic finding, repair, and Evaluator lifecycle in fresh
disposable fixtures. They are protocol evidence, not a substitute for a fresh
host review of a published Skill.

For Specification Profile integration coverage, run:

```powershell
& .\review-loop\tests\specification-profile-contract-tests.ps1
& .\review-loop\tests\specification-profile-behavior-tests.ps1
```

These tests exercise authority and traceability evidence, ambiguity and
contradiction boundaries, stable findings, bounded repair, and Core-owned
PASS/FAIL/BLOCKED outcomes in fresh disposable fixtures. They are protocol
evidence, not a substitute for independent review of a live specification.
