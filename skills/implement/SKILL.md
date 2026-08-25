---
name: implement
description: Execute one bounded, already-decided work item — code, document, configuration, research artifact, Skill, or generic project task — by inspecting relevant context, routing execution when useful, verifying locally, and handing the result to review-loop with the appropriate specialist reviewer.
disable-model-invocation: true
---

# Implement

`implement` is a **user-invoked bounded executor**. Run it only after an
explicit `$implement` request. It turns one clear work item that upstream
planning already decided into a verified artifact inside a single fresh context
window. It never reopens the plan, invents scope, or auto-invokes another
user-invoked Skill.

Read [WORKFLOW.md](references/WORKFLOW.md) before starting a run. Examples are
in [EXAMPLES.md](references/EXAMPLES.md).

Reference baseline: Matt `implement` per [ATTRIBUTION.md](ATTRIBUTION.md).
Light adapts it to a general-purpose executor (SPEC §8, §15 ADAPT).

## When to use

- A single ticket file at `.scratch/<feature>/issues/NN-<slug>.md` produced by
  `project-tickets` is ready (`Status: ready-for-agent` and every `Blocked by`
  entry is `resolved`), and the user explicitly invokes `$implement` against
  that path. See [WORKFLOW.md](references/WORKFLOW.md) for single-ticket
  consumption.
- Or a small, already-decided Spec section, source-backed scope, or
  conversation slice exists and the user explicitly invokes `$implement`
  directly against that path or description.

Do not start from a vague conversation without a bounded Spec or ticket — that
belongs to `project-clarify` / `project-spec` first.

## Core behavior

1. **Pin one work item.** Resolve exactly one bounded item — one ticket file,
   one Spec section, or one explicit conversation slice — and record it as the
   run's target. For a ticket, read its `What to build`, `Blocked by`,
   `Status`, and parent Spec pointer; verify the fixed point (`git diff` base)
   and that blockers are resolved. One run covers one item within one context
   window (see [WORKFLOW.md](references/WORKFLOW.md)).

2. **Inspect relevant context.** Skim only the code, docs, templates, glossary
   (`CONTEXT.md` / `CONTEXT-MAP.md`), and ADRs the item touches. Record source
   locations. Do not claim inspection that did not run.

3. **Route execution when useful.** Call the model-invoked `agent-config` only
   when the work benefits from explicit role splitting, parallelism, or an
   independent review context. For a bounded solo task, skip it. Use only
   evidenced Host models and capabilities from current Host evidence; never
   guess a model name or lane.

4. **Execute the bounded slice, then verify.** Branch by artifact type per
   [WORKFLOW.md](references/WORKFLOW.md):
   - **Code** → confirm seams → `tdd` when appropriate (seam-scoped
     red→green) → code changes → typecheck often, single test files often,
     full suite once at the end.
   - **Document / configuration / research artifact / Skill / generic task**
     → produce the artifact per its template or contract, then validate (render,
     schema, script, or domain check).

5. **Hand to `review-loop` when appropriate.** Package implementation evidence
   (scope, diff or artifact observation, test/render results, limitations) and
   invoke `review-loop` with the matching Profile: software / `code-review`
   for code, `generic-review` or a domain reviewer for non-code (see
   [WORKFLOW.md](references/WORKFLOW.md)). Do not copy those Skills'
   instructions here; call them.

## Composition

```text
implement → agent-config when useful
implement → tdd when appropriate
implement → review-loop → code-review (code) / generic-review (non-code)
```

Do not reimplement `agent-config`, `tdd`, `review-loop`, `code-review`, or
`generic-review`. Tickets describe *what* must be built; those Skills own
*how*. One ticket per run; one verification pass per run.

## Scope and stopping boundary

- Produces one verified diff or artifact and its evidence; it does not retriage
  tickets, close the tracker item, claim the `PASS`, or publish/release.
- Does not auto-invoke another user-invoked Skill. After the hand-off, report
  the produced evidence and recommend the explicit next invocation (normally
  review or the next frontier ticket), then stop.
- A missing or blocked Spec/ticket, a needed new ticket, a Spec change, or a
  required human decision is a stop — report the `BLOCKED` gap and the
  smallest unblock rather than expanding scope.

