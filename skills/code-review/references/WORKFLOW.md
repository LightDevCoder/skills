# Code-review workflow

Supporting detail for `code-review`. `SKILL.md` is the entry;
this file holds the full step description. `SMELL-BASELINE.md` is the fixed
Fowler baseline the Standards axis carries underneath repo standards.

## Entry condition

- User explicitly invokes `$code-review` with a fixed point (commit SHA,
  branch name, tag, `main`, `HEAD~N`), or `review-loop` / `project-review`
  (software Profile via `project-review`) invokes this Skill with a frozen
  fixed point and approved Spec. Do not guess a fixed point from recent
  commits.
- Do not run `code-review` to justify already-written code inside the same
  authoring context that produced it — prefer a fresh context for an honest
  read.

## Steps

### 1. Pin the fixed point and capture the diff once

1. Resolve the ref: `git rev-parse <fixed-point>`. If it fails, report the
   bad ref and stop before spawning sub-agents.
2. Capture the diff once: `git diff <fixed-point>...HEAD` (three-dot, against
   the merge-base). Also note `git log <fixed-point>..HEAD --oneline`.
3. If the diff is empty, report that and stop — an empty diff is a finding
   about the fixed point, not an invitation to broaden the window.

Only a non-empty diff proceeds to review.

### 2. Identify the Spec source

Search in this order; the first success is the Spec axis source:

1. Issue references in the captured commit messages (`#123`, `Closes #45`,
   GitLab `!67`) — resolve them through the active repository's tracker
   convention.
2. A path the user passed in the invocation argument.
3. A Spec file under `docs/`, `specs/`, or `.scratch/<feature>/` matching the
   branch or feature name (prefer `.scratch/<feature>/spec.md`).
4. If nothing is found, note "no spec available" for the Spec axis rather
   than inventing requirements or reading the code as its own Spec.

When `review-loop` or `project-review` is the caller, its frozen `charter.md`
and approved Spec revision are the source; treat that as authoritative. The
`software` Profile is owned by `project-review`; this package does not need to
resolve that file.

### 3. Identify the standards sources

1. List every file in the repo that documents how code should be written:
   `CODING_STANDARDS.md`, `CONTRIBUTING.md`, `AGENTS.md` style sections,
   security or ADR notes that bind style. Record the file and rule being
   cited per finding.
2. On top of whatever the repo documents, the Standards axis always carries the
   fixed twelve-smell baseline in [SMELL-BASELINE.md](SMELL-BASELINE.md).
   Two rules bind it:
   - **The repo overrides.** Where a documented repo standard endorses
     something the baseline would flag, suppress the smell.
   - **Always a judgement call.** Each smell is a labelled heuristic
     ("possible Feature Envy"), never a hard violation — and, like any
     standard here, skip anything tooling already enforces (formatter, linter).

The baseline is intentionally small and portable; it is what lets a repo with
no documented standards still get a Standards-axis read.

### 4. Spawn both sub-agents in parallel

Sub-agents share no context. Both briefs include the fixed diff command and
the commit list. Neither brief permits a further delegation:

> `Do not invoke /code-review or spawn additional agents — perform this review
> directly.`

#### Standards sub-agent prompt — include:

- The recorded diff command and commit list.
- The list of standards-source files discovered in Step 3, **plus the full
  smell baseline from SMELL-BASELINE.md pasted in full** — the sub-agent has
  no other access to it.
- The brief (under ~400 words output):

  > Report — per file/hunk where relevant — (a) every place the diff
  > violates a documented standard: cite the standard (file + the rule);
  > and (b) any baseline smell you spot: name it and quote the hunk.
  > Distinguish hard violations from judgement calls — documented-standard
  > breaches can be hard, but baseline smells are always judgement calls,
  > and a documented repo standard overrides the baseline. Skip anything
  > tooling enforces. Under 400 words.

#### Spec sub-agent prompt — include:

- The diff command and commit list.
- The fetched Spec path or its body.
- The brief (under ~400 words output):

  > Report: (a) requirements the Spec asked for that are missing or partial;
  > (b) behaviour in the diff that was not asked for (scope creep);
  > (c) requirements that look implemented but where the implementation
  > looks wrong. Quote the Spec line for each finding. Under 400 words.

When the Spec is missing, skip the Spec sub-agent instantiation and record
`Spec: no spec available` in the final report.

### 5. Aggregate

Present the two reports under `## Standards` and `## Spec` headings, verbatim
or lightly cleaned. Do **not** merge or rerank findings — the two axes are
deliberately separate (see _Why two axes_ in [EXAMPLES.md](EXAMPLES.md)).

End with a one-line per-axis summary: total findings on that axis and the
worst issue **within** that axis (if any). Do not pick a single winner across
axes — the separation exists to prevent one axis from masking the other.

Example aggregate shape is shown in [EXAMPLES.md](EXAMPLES.md).

## Composition

- Do not merge findings or propose repairs. Findings are candidates for
  `project-review` (via `review-loop` engine) to validate as `confirmed`,
  `rejected`, `duplicate`, or `out-of-scope`; `project-review` Core is the
  only writer that directs a bounded in-scope repair and supplies a fresh
  Evaluator. The final `PASS`, `FAIL`, or `BLOCKED` belongs to
  `project-review` under the `software` Profile.
- Do not run a second review pass; convergence is the `review-loop` engine's
  responsibility, final acceptance is `project-review`'s.

## Stopping boundary

- Every Standards finding cites either a file+rule or `possible <Smell Name>`
  plus the quoted hunk; every Spec finding quotes a Spec line. Do not fabricate
  a citation.
- A change can pass one axis and fail the other. Report that faithfully;
  do not soften the failing axis.

