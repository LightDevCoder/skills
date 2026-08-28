# Project-review workflow

Supporting detail for `project-review`. `SKILL.md` is the entry; this file
holds the full acceptance protocol.

## Public contract

Three modes, migrated from the mature `review-loop` final-acceptance protocol:

- `init`: resolve and freeze the acceptance baseline and Profile before review.
- `review`: run one bounded evidence, critique, validation, repair, and
  evaluation round (via `review-loop`).
- `resume`: continue the next unfinished recorded action without rewriting
  prior evidence.

If a manual request omits a mode, infer it only when `state.md` makes the next
action unambiguous; otherwise request the mode.

## Roles

- **Core (project-review):** freezes the baseline, selects the Profile,
  records state, validates candidates, enforces stop conditions, owns the
  verdict.
- **Producer:** supplies evidence and is the only role that modifies the
  target during an allowed repair.
- **Critic / reviewer:** read-only; returns candidate findings using the public
  `review-loop` reviewer contract or the full project-review registry schema.
- **Evaluator:** read-only and fresh from the Critic; judges the frozen
  baseline and admissible evidence.

Use the role-packet and independence rules in
[subagent-protocol.md](subagent-protocol.md). Do not call same-context
role-play independent review.

## Durable state

Store records in the target project's `.project-review/` directory. For
backwards compatibility the engine also accepts `.review-loop/` when no
`.project-review/` exists, but new projects must use `.project-review/`.
Create it only when the selected mode requires a durable record. Never
overwrite an existing Charter, finding, or round record.

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

`charter.md`, `state.md`, and `verdict.md` form one coherent durable review
transaction:
- `charter.md` defines what is being reviewed (Charter revision, Profile,
  Source baseline, Fixed point, and Implementation scope).
- `state.md` is authoritative for the current review lifecycle state (`Status`,
  `Charter revision`, `Profile`, `Round`, and next action).
- `verdict.md` is authoritative only for a coherent terminal State (`PASS`,
  `FAIL`, `BLOCKED`). When a review is active or reopened (`INIT`, `READY`,
  `CRITIC`, `REPAIR`, `EVALUATE`), old verdicts do not remain authoritative.
- For terminal acceptance, `state.md` and `verdict.md` must agree, and `Charter
  revision` and `Profile` across `charter.md`, `state.md`, and `verdict.md`
  must be mutually coherent.
- Canonical fields in `state.md` (`Status:`, `Charter revision:`, `Profile:`)
  are singleton fields; missing, ambiguous, or duplicate fields fail closed.
`findings.md` is the canonical finding registry. Round files preserve
observations and evidence. Keep facts in authoritative record and link rather
than duplicate.

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
   A `software`-Profile review additionally freezes the immutable code-review
   base (`- Fixed point:`, exactly one full commit SHA) and the reviewed
   software target (`- Implementation scope:`, repository-relative literal
   paths — never inferred from changed paths; if the complete target cannot be
   established reliably, return `BLOCKED`) in the Charter. Do not freeze the
   final implementation candidate at `init`; authorized repairs may move it,
   and the final verdict records it as `- Reviewed implementation revision:`
   ([profiles/software.md](profiles/software.md)). Use
   [acceptance-charter.md](acceptance-charter.md).
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
   [evidence-protocol.md](evidence-protocol.md).
2. **Invoke reviewers via `review-loop`.** Resolve the reviewer(s) for the
   bounded packet (`generic-review` for ordinary artifacts, `code-review`
   for software diff, domain reviewer when justified) and call them through
   `review-loop` (`resolve reviewer → invoke reviewer → receive findings`).
   A reviewer result is a candidate, not an instruction; its lightweight shape
   follows `review-loop`'s public reviewer contract.
3. **Validate every candidate.** Assign or reuse its stable Finding ID, then
   record one disposition: `confirmed`, `rejected`, `duplicate`, or
   `out-of-scope`. For the software Profile, ingest `code-review` Standards
   and Spec findings while preserving their source axis. Follow
   [finding-schema.md](finding-schema.md).
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
   [stopping-rules.md](stopping-rules.md).

### Software specialist boundary

When the selected Profile is `software`, `code-review` is invoked at the
frozen fixed point and approved Spec. It returns separate Standards and Spec
findings as `review` evidence. The Core validates those findings through the
same generic lifecycle, directs only bounded Producer repairs, and supplies the
fresh Evaluator with the original and repaired evidence. `code-review` is a
specialist and never issues the project's final `PASS`, `FAIL`, or `BLOCKED`;
`project-review` Core owns the final verdict and `review-loop` never runs the
repair loop on its own.

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
See [stopping-rules.md](stopping-rules.md) and [review-rubric.md](review-rubric.md)
for transitions, progress, and severity guidance.

For a `software` Profile, every durable `PASS`, `FAIL`, or `BLOCKED` binds the
immutable baseline to the implementation it actually evaluated by recording
`- Reviewed implementation revision: <full Git commit SHA>` in `verdict.md`.
A `PASS` may only be issued while the frozen `Implementation scope` holds no
uncommitted tracked, untracked, or ignored changes at evaluation time — Git
ignore rules hide files from `git status`, not from the reviewed component;
unrelated changes outside the scope do not block. Any later in-scope drift —
dirty, staged, committed, untracked, or ignored — stales that verdict for
consumers and requires a fresh review ([profiles/software.md](profiles/software.md)).
