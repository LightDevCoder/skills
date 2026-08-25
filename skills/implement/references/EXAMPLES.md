# Implement examples

## Example 1 — Code ticket: one vertical slice with `tdd` and `code-review`

**Input:** `$implement .scratch/auth/spec.md` slice plus
`.scratch/auth/issues/02-session-middleware.md` (`Blocked by: 01`, now
`resolved`).

**Run:**

1. Read `02-session-middleware.md` (`What to build: add stateless session
   middleware at the API seam`) and its parent Spec section. Confirm
   `Blocked by: 01` is resolved and `Status: ready-for-agent`.
2. Inspect `CONTEXT.md` (vocabulary), `docs/adr/0007-session.md` if present,
   and the existing API seam. Record the seam as `POST /api/session → auth
   service → session store`.
3. The ticket is solo-owned (`middleware.ts` + its seam test file); skip
   `agent-config` and note `single-ticket solo` in the evidence.
4. Call `tdd` (model-invoked) at the API seam: one red test for "valid token
   returns session", then minimal middleware, then a boundary test for
   "expired token → 401", each with a focused single-file run. Typecheck after
   each cycle.
5. Run the full relevant suite once, capturing the passing boundary case as
   `review-loop` evidence.
6. Invoke `review-loop` (software Profile) with the frozen fixed point and
   approved Spec; it delegates Standards + Spec to `code-review` and collects
   behavioral evidence. `implement` stops after the handoff. It does not
   decide the final `PASS` and does not edit the ticket file.

## Example 2 — Document ticket: Skill + template without code

**Input:** `$implement .scratch/kb-init/issues/01-package-skeleton.md`
(`What to build: scaffold SKILL.md and supporting references from the
proposal template`).

**Run:**

1. Read the ticket and its parent Spec. Inspect the proposal template and
   existing Skill examples it names.
2. The artifact is an owned Skill skeleton; parallelism is not useful, so skip
   `agent-config`.
3. Produce `SKILL.md` (concise entry) and `references/WORKFLOW.md` (detailed
   procedure) within the bounded ticket scope. Do not add sibling tickets'
   chapters.
4. Verify by rendering each Markdown and spot-checking that internal
   references resolve.
5. Hand to `review-loop` (generic Profile, `generic-review` as reviewer) with
   the rendered observations. The loop's fresh Evaluator judges the frozen
   baseline; `implement` owns only the production and evidence.

## Example 3 — Configuration slice (non-code) with schema validation

**Input:** `$implement .scratch/infra/issues/04-ci-workflow.md` with a
`CI YAML` acceptance list.

1. Inspect the existing workflow and schema; record the evidence gap if the
   runner inventory is unknown.
2. Produce the bounded `ci.yml` for that single ticket; do not migrate every
   legacy job in the same diff.
3. Validate against the schema and dry-run the workflow where possible.
4. Hand to `review-loop` (generic Profile) with the validated artifact and
   limitations note.

## Example 4 — Research artifact slice

**Input:** `$implement .scratch/payments/issues/03-psp-research.md` (`What to
build: high-trust PSP comparison captured as Markdown` with a finding schema).

1. The ticket explicitly asks for a research artifact. Call `research`
   (model-invoked) with the directed question, or note `BLOCKED` if external
   fact work is not authorized in this invocation.
2. Capture findings as the required Markdown at the path the ticket names.
3. The artifact itself is `review-loop` `review` evidence for later
   verification; verify locally by reading the file and confirming sources
   before the generic review.

## Negative — vague scope without a ticket

**Input:** User says "clean up the codebase a bit" in a fresh session — no
ticket or Spec slice.

**Outcome:** `implement` does not invent scope. It reports the handoff gap
(`missing bounded Spec or ticket — route via $project-clarify or
$project-spec first`) and stops. Typechoice or review is not attempted.

