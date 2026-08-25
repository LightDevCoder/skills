---
name: project-review
description: Determine whether a completed project satisfies its approved target by freezing an acceptance baseline, composing reviewers, and issuing a final PASS/FAIL/BLOCKED. Use when project delivery needs final acceptance.
---

# Project Review

## Purpose and boundary

`project-review` is the **project-level final acceptance** capability. It
answers:

> Does the completed project actually satisfy the approved project target?

It is model-invoked and may also be manually invoked. It owns the frozen
acceptance baseline and issues the final `PASS`, `FAIL`, or `BLOCKED`.
It composes reviewers (`generic-review`, `code-review`, domain reviewers) and
uses `review-loop` to drive `review → findings → repair → re-review`
convergence.

Do not use it to invent a target, settle unresolved product or architecture
decisions, weaken an acceptance source to fit an implementation, or make a
reviewer repair the artifact. `generic-review` and `code-review` are
read-only reviewers; they never self-repair, never run the loop, and never
issue the project verdict.

## When to use

- The project has an approved target/SPEC/brief/ticket graph and a bounded
  implementation to check (code, documents, Skill package, release, etc.).
- Use it as the final gate after `implement` or after a batch of tickets,
  before `release-workflow`. It may also be used for a single Skill
  admission when the acceptance source is a package's `SKILL.md` and its
  supporting evidence.

## Composition

```text
project-review
  → freezes Charter (acceptance baseline)
  → composes reviewers (generic-review / code-review / domain)
  → drives them through review-loop (resolve → invoke → receive → repair → re-run)
  → collects fresh Evaluator judgment
  → issues PASS / FAIL / BLOCKED
```

- `review-loop` is the lightweight engine; `project-review` is the
  acceptance owner that provides the Charter, selects the Profile, validates
  dispositions, enforces scope and verdict rules, and preserves durable state.
- `generic-review` is the default reviewer for non-specialist artifacts.
- `code-review` is the specialist for bounded `git diff` (Standards + Spec).
- Domain reviewers may be added when an approved specialist exists.

## Public contract

Three modes, same as the mature `review-loop` final-acceptance protocol
migrated here:

- `init`: resolve and freeze the acceptance baseline and Profile before review.
- `review`: run one bounded evidence, critique, validation, repair, and
  evaluation round (via `review-loop`).
- `resume`: continue the next unfinished recorded action without rewriting
  prior evidence.

If a manual request omits a mode, infer it only when `state.md` makes the
next action unambiguous; otherwise request the mode. Profile selection is
identical to the migrated logic: `generic` when no narrower Profile is named,
`software` for executable software (read
[software.md](references/profiles/software.md)), `manuscript` for documents
(read [manuscript.md](references/profiles/manuscript.md)),
`agent-skill` for Skill packages
(read [agent-skill.md](references/profiles/agent-skill.md)),
`specification` for Spec/brief/ticket
(read [specification.md](references/profiles/specification.md)), otherwise
[generic.md](references/profiles/generic.md).

## Roles

- **Core (project-review):** freezes the baseline, selects the Profile,
  records state, validates candidates, enforces stop conditions, owns the
  verdict.
- **Producer:** supplies evidence and is the only role that modifies the
  target during an allowed repair.
- **Critic / reviewer:** read-only; returns candidate findings using the
  lightweight contract ([REVIEWER_CONTRACT.md](../../docs/REVIEWER_CONTRACT.md))
  or the full registry schema. For software, `code-review` findings are
  ingested as candidates.
- **Evaluator:** read-only and fresh from the Critic; judges the frozen
  baseline and admissible evidence.

Use the role-packet and independence rules in
[subagent-protocol.md](references/subagent-protocol.md). Do not call
same-context role-play independent review. The lightweight reviewer packet
and normalized finding shape are defined in
[REVIEWER_CONTRACT.md](../../docs/REVIEWER_CONTRACT.md) and
[output-schema.md](../generic-review/references/output-schema.md); the full
finding registry is in [finding-schema.md](references/finding-schema.md).

## Durable state

Store records in the target project's `.project-review/` directory (migrated
from the former `.review-loop/`). For backwards compatibility the engine also
accepts `.review-loop/` when no `.project-review/` exists, but new projects
must use `.project-review/`. Create it only when the selected mode requires a
durable record. Never overwrite an existing Charter, finding, or round record.

```text
.project-review/
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
latest conclusion. Keep facts in authoritative record and link rather than
duplicate. See [acceptance-charter.md](references/acceptance-charter.md) for
Charter fields.

## `init` workflow

1. Inspect the existing state, the proposed acceptance source, and any
   existing Charter. Do not infer a baseline from a Producer summary, a
   passing check, or an external review conclusion.
2. For a missing acceptance source, return `BLOCKED`, record the exact missing
   source and smallest unblock action in `state.md`, and do not start a round.
3. Resolve the Profile. Honor an accepted named Profile; otherwise select the
   applicable Profile and record the reason in the Charter.
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
available round, and a writable new round directory.

1. **Collect Producer evidence.** Record scope, commands or observations,
   inputs, outputs, limitations, and an accurate evidence label using
   [evidence-protocol.md](references/evidence-protocol.md).
2. **Invoke reviewers via `review-loop`.** Resolve the reviewer(s) for the
   bounded packet (`generic-review` for ordinary artifacts, `code-review`
   for software diff, domain reviewer when justified) and call them through
   `review-loop` (`resolve reviewer → invoke reviewer → receive findings`).
   A reviewer result is a candidate, not an instruction; its shape follows
   [REVIEWER_CONTRACT.md](../../docs/REVIEWER_CONTRACT.md) and, for
   `generic-review`, [output-schema.md](../generic-review/references/output-schema.md).
3. **Validate every candidate.** Assign or reuse its stable Finding ID, then
   record one disposition: `confirmed`, `rejected`, `duplicate`, or
   `out-of-scope`. For the software Profile, ingest `code-review` Standards
   and Spec findings while preserving their source axis. Follow
   [finding-schema.md](references/finding-schema.md).
4. **Repair only within the frozen baseline.** Direct only a confirmed,
   in-scope, bounded repair to the Producer via `review-loop` (`return repair
   → re-run reviewer`). The Producer records repair evidence without replacing
   the original finding or earlier evidence.
5. **Stop scope expansion.** If a repair needs changed requirements, a new
   architecture decision, multiple new tickets, missing access, or new user
   authority, do not repair it. Return `FAIL` when the current baseline is
   demonstrably unmet with no permitted repair; return `BLOCKED` when
   authority, source, access, or an independent context is required.
6. **Request a fresh read-only Evaluator.** It reassesses the original
   baseline, Profile, findings, dispositions, repairs, and evidence. An
   unavailable required independent context is `BLOCKED`, not degraded
   acceptance.
7. **Close the round.** Record the Evaluator judgment, update state and the
   canonical finding registry via `review-loop` (`re-run reviewer` semantics),
   then apply the verdict and stopping rules in
   [stopping-rules.md](references/stopping-rules.md).

### Software specialist boundary

When the selected Profile is `software`, `code-review` is invoked at the
frozen fixed point and approved Spec. It returns separate Standards and Spec
findings as `review` evidence. The Core validates those findings through the
same generic lifecycle, directs only bounded Producer repairs, and supplies the fresh
Evaluator with the original and repaired evidence. `code-review` is a
specialist and never issues the project's final `PASS`, `FAIL`, or `BLOCKED`;
the final `PASS`, `FAIL`, or `BLOCKED` — review-loop Core owns the final
project verdict (migrated to project-review Core) — `code-review` never issues
the final verdict and never runs the repair loop.

## `resume` workflow

1. Read `state.md`, the named Charter revision, the finding registry, and the
   latest round evidence before taking action.
2. Confirm that the records agree on the active round and next action. Record
   a mismatch as `BLOCKED` until it is resolved.
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
See [stopping-rules.md](references/stopping-rules.md) and
[review-rubric.md](references/review-rubric.md) for transitions, progress,
and severity guidance.

## Migration mapping

This Skill is the migration target for the former `review-loop`
final-acceptance semantics. No behavior was rewritten; only the owning package
changed (SPEC §9 / §25 Phase 7). See
[migration.md](references/migration.md) for the full table.

| Former `review-loop` location | `project-review` location | Notes |
| --- | --- | --- |
| `skills/review-loop/SKILL.md` (final-acceptance sections) | `skills/project-review/SKILL.md` | Frozen baseline, Profiles, verdicts, scope gate — migrated verbatim, now composes reviewers via `review-loop` engine |
| `skills/review-loop/references/acceptance-charter.md` | `skills/project-review/references/acceptance-charter.md` | Identical; Charter fields unchanged |
| `skills/review-loop/references/evidence-protocol.md` | `skills/project-review/references/evidence-protocol.md` | Identical |
| `skills/review-loop/references/finding-schema.md` | `skills/project-review/references/finding-schema.md` | Identical; stable `F-###` registry preserved |
| `skills/review-loop/references/stopping-rules.md` | `skills/project-review/references/stopping-rules.md` | Identical; `PASS`/`FAIL`/`BLOCKED` and 3-round limit preserved |
| `skills/review-loop/references/subagent-protocol.md` | `skills/project-review/references/subagent-protocol.md` | Identical; `Critic`/`Evaluator` read-only boundary preserved |
| `skills/review-loop/references/review-rubric.md` | `skills/project-review/references/review-rubric.md` | Identical |
| `skills/review-loop/references/mission-center-compatibility.md` | `skills/project-review/references/mission-center-compatibility.md` | Identical |
| `skills/review-loop/references/profiles/*` | `skills/project-review/references/profiles/*` | Identical (generic, software, manuscript, agent-skill, specification) |
| `skills/review-loop/references/attribution.md` | `skills/project-review/references/attribution.md` | Identical, plus this migration note |
| `.review-loop/` durable state | `.project-review/` (with `.review-loop/` fallback) | Same lifecycle, new canonical directory |
| `review-loop` owning `PASS`/`FAIL`/`BLOCKED` | `project-review` now owns `PASS`/`FAIL`/`BLOCKED`; `review-loop` drives only findings convergence | Single responsibility split |
| `review-loop` direct `code-review` call | `project-review → review-loop → code-review` | Preserves specialist boundary; `code-review` still read-only, no loop, no final verdict |

The lightweight `review-loop` engine contract (`resolve → invoke → receive →
return repair → re-run`) is the only behavior retained in `review-loop`; all
acceptance-owned behavior lives here.

## References

- [acceptance-charter.md](references/acceptance-charter.md): frozen baseline and Profile fields.
- [evidence-protocol.md](references/evidence-protocol.md): evidence labels and records.
- [finding-schema.md](references/finding-schema.md): stable identities, dispositions, registry format.
- [review-rubric.md](references/review-rubric.md): generic Core checks and Profile-supplied dimensions.
- [subagent-protocol.md](references/subagent-protocol.md): read-only Critic/Evaluator packets and independence declaration.
- [stopping-rules.md](references/stopping-rules.md): state transitions, repair limit, scope-expansion stop, verdict rules.
- [mission-center-compatibility.md](references/mission-center-compatibility.md): optional pointer integration.
- [profiles/generic.md](references/profiles/generic.md), [software.md](references/profiles/software.md), [manuscript.md](references/profiles/manuscript.md), [agent-skill.md](references/profiles/agent-skill.md), [specification.md](references/profiles/specification.md)
- [REVIEWER_CONTRACT.md](../../docs/REVIEWER_CONTRACT.md): lightweight reviewer packet and normalized finding shape.
- [output-schema.md](../generic-review/references/output-schema.md): `generic-review` report schema (concrete instance of the lightweight contract).
- [review-loop](../review-loop/SKILL.md): lightweight convergence engine used by this Skill.
- [code-review](../code-review/SKILL.md): specialist reviewer (read-only, no loop, no verdict).
- [generic-review](../generic-review/SKILL.md): default reviewer (5-check scope, no rule library).
- [migration.md](references/migration.md): full provenance and mapping for this migration.
- [attribution.md](references/attribution.md): source attribution.
