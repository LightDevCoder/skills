# Implement workflow

Supporting detail for `implement`. `SKILL.md` is the entry;
this file holds the full step description.

## Entry condition

- User explicitly invokes `$implement` with a bounded work item: a path to
  `.scratch/<feature>/issues/NN-<slug>.md`, a path to
  `.scratch/<feature>/spec.md` (or a narrow section of it), or a small
  explicit conversation slice.
- Do not synthesize a scope from a vague thread without a Spec or ticket.
  That case belongs to `project-clarify` / `project-spec` first.
- One run covers **one** work item inside **one** fresh context window. Do not
  batch many tickets in one run and do not pre-load several tickets to execute
  in sequence.

## Inputs and ticket consumption

`project-tickets` produces one file per ticket under the tracker convention
used by the active repository (`.scratch/<feature>/issues/`). Wayfinding
operations:

```text
.scratch/<feature>/issues/NN-<slug>.md    # from 01 in dependency order
```

Each file carries near the top:

```text
**Blocked by:** 01, 03
**Status:** ready-for-agent | claimed | resolved
```

and a body starting `## What to build` with acceptance criteria.

When `$implement` is passed a ticket path:

1. Read the file body and its header lines. Record the title, `Blocked by` set,
   `Status`, and parent Spec pointer (the ticket body normally cites the Spec
   path). If the caller used `#NN` rather than a full path, confirm the title
   back against the file on disk before proceeding (mirrors the Matt upstream
   guidance on ticket-number resolution).
2. Verify the ticket is `ready-for-agent` (treat `open` as its alias when the
   caller scanned an unblocked frontier) and that every blocker listed in
   `Blocked by` is `resolved`. If not ready or blocked, report `BLOCKED` and
   stop — do not jump to a different ticket.
3. Treat the ticket body as the bounded Spec for this run. Do not re-slice it,
   merge other tickets, or broaden its acceptance.
4. The run works in a single independent context and produces one bounded diff
   (or one non-code artifact) attributable to that ticket only. Traceable issue
   state (`Status: claimed / resolved`, appending `## Answer`) is not this
   Skill's side-effect; the caller or tracker workflow updates the file after
   `project-review` reaches a verdict. Early `Claim` before work is a recommended
   external step for concurrent sessions but not a required side-effect of this
   Skill.

For a small Spec slice or conversation slice, record the scope string and
limit the diff to that slice. Any gap that makes the scope ambiguous is a
handoff gap — report it rather than inventing a broader scope.

## Steps

### 1. Pin the work item and the fixed point

- Resolve the exact item path and read its full body plus comments. For a
  ticket, load its parent Spec at `.scratch/<feature>/spec.md` for provenance;
  the ticket body remains the bounded authority.
- For code work, note the fixed point for later `code-review`: the branch
  point or the reference the user passed (default to the fork-point of the
  current branch). Do not start changing files if the fixed point cannot be
  resolved.

### 2. Inspect relevant context

- Skim the domain glossary (`CONTEXT.md` / `CONTEXT-MAP.md`), ADRs, and only
  the source or templates the item touches. Locate the seams (public
  boundaries) that the work will be verified at; prefer existing seams.
- Record each usable fact with a bounded locator (file + heading/symbol/line).
  A seam or contract that the item assumes but the inspection cannot find is
  an evidence gap — note the `BLOCKED` location rather than assuming it.
- Keep this inspection bounded; it exists to avoid proposing a seam the repo
  cannot host.

### 3. Route execution when useful (optional)

Call the model-invoked `agent-config` only when the task benefits from
explicit routing:

- the work benefits from parallel disjoint ownership units,
- independent review isolation matters (a fresh reviewer context is required),
- ownership, concurrency cap, or worktree isolation must be declared.

Inputs to `agent-config` are exactly the bounded item, its acceptance source,
declared change units with exact file ownership, current Host evidence as
`agent-config` defines, and any non-negotiable review/worktree constraints.

- If Host evidence shows a single-model single-agent Host, `agent-config`
  returns a serial plan with a self-check gate rather than a purported
  independent reviewer. Treat that as the routing; do not invent parallelism.
- For a bounded solo task whose structure is already settled, skip
  `agent-config` entirely (SPEC §8: "when useful" rather than mandatory
  orchestration).

Never guess model names or infer capabilities from memory. Do not start work
that requires an `agent-config` gate before the plan is accepted.

### 4. Execute the bounded slice

Branch by artifact type. One item produces one slice through every relevant
layer (tracer-bullet), sized for the single context window.

**Code artifact** (default branch when the item touches `src/`, tests, or a
software Profile):

1. Agree the seams. Read the Spec/slice for declared seams; if none are
   declared, sketch one seam candidate and confirm briefly with the user
   before writing tests.
2. Drive `tdd` (model-invoked) at those seams. One red→green cycle at a time:
   a named seam, a failing test in the correct harness location, then the
   minimal implementation that makes that test pass. Do not write tests bulk
   ahead of implementation. Follow `tdd`'s seams, anti-patterns, and loop
   rules — do not duplicate them here.
3. The run's editorial position is **tracer-bullet vertical**: each cycle is a
   narrow but complete path through the relevant layers, demoable on its own.

**Document / configuration / research artifact / Skill / generic task**
(branch when the item's deliverable is not executable code):

1. Resolve the artifact's template or contract (e.g., `SKILL.md` shape,
   proposal template, configuration schema, research Markdown). Prefer the
   template the Spec names; when none is named, use the item body's stated
   structure.
2. Produce the artifact once. Keep it bounded to the item — do not pull in
   sibling tickets or the broader Spec.
3. The item's body is the contract; do not broaden it to "finish the whole
   feature".

### 5. Verify locally

**Code:** typecheck often and run single test files often during the loop;
run the full relevant test suite once at the end, including focused boundary
and failure cases relevant to the changed behavior. Report any environment or
dependency gap as a limitation. Code that cannot be exercised by focused tests
adds a representative runtime or integration observation.

**Non-code:** run the verification the item's contract implies: render the
document in its target format and spot-check a real output, validate the
configuration or schema, or perform the domain check the Spec names. Record
the observation path rather than asserting correctness abstractly.

A verify step that surfaces a missing requirement (new ticket, Spec revision,
ADR) is a stop — report the gap rather than repairing by broadening scope.

### 6. Hand to `review-loop` when appropriate

Package the evidence for `review-loop`:

- frozen item path and acceptance source with revision,
- fixed-point identity and bounded diff or artifact observation,
- verification outputs (test commands and results, render/schema observation),
- limitations (unavailable dependencies, environments, generated outputs, or
  untestable paths).

Select the reviewer implied by the artifact and call it through `review-loop`:

- **Code** → `code-review` (Standards + Spec) as the specialist reviewer. It
  returns candidate findings; `review-loop` drives convergence and
  `project-review` owns any final verdict.
- **Non-code** → `generic-review` (or an available domain reviewer). Do not
  call `code-review` on a non-code diff.

Do not copy the reviewer's rubric or the acceptance/state machine into this
file; call those Skills via their public protocols.

## Boundaries

- One item per run. A new ticket needs a fresh `$implement` invocation in a
  fresh context. Do not merge sibling tickets to "save a round trip".
- Inspect only what the item names; do not run a whole-repo redesign inside an
  item.
- `agent-config`, `tdd`, `review-loop`, `code-review`, and `generic-review`
  are composition targets, not text to duplicate. Call them per their
  instructions.
- This Skill commits its bounded change to the current branch (mirroring the
  Matt baseline) but does not push, publish, or claim the ticket resolved.
  Upstream ticket-closure semantics belong to the tracker/workflow caller.

## Handoff options

- On a verified diff/artifact, invoke `review-loop` and stop. The caller
  decides the next frontier ticket via `$implement` on the next ready item.
- On a `BLOCKED` gap (missing Spec/ticket/authority/Spec-fidelity decision),
  report the gap with the smallest unblock and stop without branching into
  clarification or reticketing.
- If a focused question is needed for a human decision, recommend
  `$ask-light` or `$clarify` and stop; the recommendation is not an automatic
  invocation.

