---
name: project-tickets
description: Turn a formal SPEC into tracer-bullet vertical slices with blocking edges, then publish them as single-file-per-ticket issues on the local markdown tracker. Use only when the user explicitly invokes $project-tickets; it verifies the SPEC handoff, drafts a quiz-able breakdown, and hands execution to the frontier via implement.
disable-model-invocation: true
---

# Project Tickets

`project-tickets` is an **explicit, user-invoked planning stage**. Run it only
after an explicit `$project-tickets` request. It turns a formal SPEC (normally
from `project-spec` at `.scratch/<feature>/spec.md`) into agent-executable
tickets that a local tracker can serve as a task graph.

Read [WORKFLOW.md](references/WORKFLOW.md) before starting a run.
The ticket shape and Wayfinding compatibility are in
[TICKET-CONTRACT.md](references/TICKET-CONTRACT.md); examples are in
[EXAMPLES.md](references/EXAMPLES.md).

Reference baseline: Matt `to-tickets` per [ATTRIBUTION.md](ATTRIBUTION.md).
This package adapts that baseline to Light's `.scratch/<feature>/issues/`
tracker and vertical-slice graph (SPEC §7, §15 ADAPT).

## When to use

- A SPEC exists at `.scratch/<feature>/spec.md` (or at the path the user
  passes) and the user explicitly invokes `$project-tickets` against it.
- The SPEC covers Problem Statement, Solution, User Stories, Implementation
  and Testing/Verification Decisions, and its handoff path has been validated.

Do not start from a vague conversation without a SPEC — synthesis without a
SPEC belongs to `project-spec`, not this Skill.

## Core behavior

1. **Verify the SPEC handoff.** Read the SPEC at the supplied path and
   confirm it satisfies [TICKET-CONTRACT.md](references/TICKET-CONTRACT.md)'s
   readability bar; a missing or malformed SPEC is a handoff gap — stop and
   report it rather than fabricating tickets.
2. **Draft tracer-bullet vertical slices** from the SPEC per
   [WORKFLOW.md](references/WORKFLOW.md): each slice is a narrow but complete
   path through the relevant layers (schema/API/UI/tests for code; structure/
   template/render/verify for docs/Skills), demoable on its own and sized for
   a single fresh context window. Declare `Blocked by` edges, `ready work`,
   and `parallelizable` groups. See the wide-refactor exception in the
   workflow.
3. **Quiz the user** with the numbered breakdown (title, Blocked by, What it
   delivers). Ask whether granularity and blocking edges match expectations;
   iterate until approved.
4. **Publish one file per ticket** under `.scratch/<feature>/issues/` per
   [TICKET-CONTRACT.md](references/TICKET-CONTRACT.md) and
   [docs/agents/issue-tracker.md](../../docs/agents/issue-tracker.md)
   Wayfinding ops: numbered `NN-<slug>.md`
   from `01` in dependency order (blockers first), with the task-graph shape
   unchanged from the approved quiz. Do not rewrite as a single combined
   tickets file.

## Composition

- Do not duplicate the verification or execution logic that lives in
  `implement`, `tdd`, `agent-config`, or the review family. Tickets describe
  *what* must be built and what blocks it; referenced Skills own *how*.
- The publishing layout is tracker-native (see [TICKET-CONTRACT.md](references/TICKET-CONTRACT.md)
  and [docs/agents/issue-tracker.md](../../docs/agents/issue-tracker.md):21). It renders a visible **frontier**,
  supports **Claim** (`Status: claimed`) and **Resolve** (append `## Answer`,
  `Status: resolved`), and tracks **Blocked by** edges without requiring an
  external tracker.
- Upstream `to-tickets`' platform branching (local files vs native blocking
  links) is preserved in the workflow but Light's primary form is the local
  markdown file per ticket.

## Scope and stopping boundary

- Produces the numbered ticket files and validates their `Status` /
  `Blocked by` fields resolve for a frontier scan — it does not execute the
  tickets, perform implementation, or run review.
- Does not auto-invoke a user-invoked `implement` or `project-review`. After
  publishing, describe the frontier (`ready work` / first unblocked tickets)
  and recommend explicit `implement` on the chosen ticket, then stop.
- A SPEC that proves too foggy for ticketable slices is sent back via an
  explicit recommendation to `$project-clarify` / `$decision-map` rather than
  sliced speculatively.

## Verifiable handoff from project-spec

`project-spec` publishes `.scratch/<feature>/spec.md`; this Skill reads that
exact file as its input and returns the numbered `issues/NN-<slug>.md` set.
The chain `project-spec → project-tickets` is verifiable: the SPEC path used
is recorded, every supporting reference in both Skills resolves, and the
published tickets satisfy the explorer's frontier query — any unblocked,
unclaimed `ready-for-agent` ticket is ready work.

See [WORKFLOW.md](references/WORKFLOW.md) and
[TICKET-CONTRACT.md](references/TICKET-CONTRACT.md) for the authoritative
sequence, template, and compatibility contract.
