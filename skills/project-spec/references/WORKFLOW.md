# Project-spec workflow

Supporting detail for `project-spec`. `SKILL.md` is the entry; this file
holds the full step description.

## Entry condition

- User explicitly invokes `$project-spec`.
- At least one of these exists:
  - a `project-clarify` handoff (the `Project clarification handoff` record),
  - a `decision-map` map (`.scratch/<effort>/map.md`) with its `Decisions so
    far` and resolved child ticket `## Answer` records,
  - or a focused current conversation already carrying settled decisions.
- Optional argument: a feature slug, an existing handoff path, or a map path.
  When the user passes a reference, fetch it and read its full body and
  comments before proceeding.

Do not start from a general vague prompt and do not auto-chain from a prior
clarification stage — wait for the explicit `$project-spec` token.

## Steps

### 1. Gather already-clarified material

Collect, without re-asking:

- from `project-clarify`: `Target and inspected project facts` (with paths and
  stable locations), `Evidence not found`, `Current goal and constraints`,
  `Resolved user decisions`, `Open decisions and dependencies`, `Capability call
  records`, `Current frontier or explicit blocker`, `Recommended next
  invocation`, `Status`;
- from `decision-map`: the map's `Destination`, `Notes`, `Decisions so far`
  (gist + ticket link per closed ticket), `Not yet specified` fog, `Out of
  scope`, plus every resolved ticket's `## Answer`;
- from the conversation: the thread's current goal, constraints, and any
  inline decision the user just gave.

Treat inspected facts as authoritative and record their locator (heading,
symbol, file, line). Absent material remains an evidence gap; do not invent a
fact and do not phrase a fact as a user question.

### 2. Light inspection to ground the SPEC

Skim the repo to ground the Implementation and Testing decisions that the SPEC
will make:

- domain glossary (`docs/agents/domain.md`, `CONTEXT.md`/`CONTEXT-MAP.md`,
  existing glossary terms);
- ADRs (`docs/adr/`, `src/<context>/docs/adr/`);
- existing seams and entry points relevant to the feature (prefer existing
  seams; see step 3).

Do not repeat the full `project-clarify` inspection. This pass exists only to
avoid proposing modules, interfaces, or test seams that the codebase cannot
host.

### 3. Seam sketch and check

Sketch the seam(s) at which the feature will be verified:

- prefer existing seams over new ones;
- prefer the highest seam that still isolates the feature;
- propose the fewest seams that can cover the user stories — one is ideal;
- when a new seam is needed, place it as high as practical.

If the sketch affects scope or implies a module/interface trade-off, confirm
with the user that the seams match expectations before writing the SPEC.
For a non-code deliverable (document, Skill, configuration), the "seam" is the
bounded verification boundary (template, script, manifest, review packet).

### 4. Blocking-decision gate

Before writing, test whether a truly blocking, user-owned decision remains:

- A blocking decision is one without which the SPEC would have to speculate
  about an outcome, priority, trade-off, or risk — and for which no
  clarification material settles the choice nor can inspection settle it.
- If such a decision exists: do **not** write the SPEC. Return to
  `project-clarify` (or to the map when the effort is still foggy) with the
  exact blocker, its dependencies, and a context pointer. Recommend explicit
  `$project-clarify` or `$decision-map` and stop.
- If only fact gaps remain that do not force speculation, note them in the
  SPEC's `Further Notes` / `Out of Scope` and proceed.

### 5. Write the SPEC

Use [OUTPUT-FORMAT.md](OUTPUT-FORMAT.md) for the template and vocabulary
rules. Keep prose bounded: describe modules/interfaces, architectural choices,
schema/API contracts, and verification boundaries — not file paths or code
snippets, unless a prototype snippet encodes a decision more precisely than
prose (trim to the decision-rich fragment and note its prototype origin).

### 6. Publish to the local tracker

Read `docs/agents/light-project.md` when present and write the approved SPEC
under its working area according to `docs/agents/issue-tracker.md`:

```text
.scratch/<feature>/spec.md
```

`<feature>` is the supplied slug, the map's `<effort>`, or a slug derived
from the goal — confirmed with the user. Create the directory if needed. Do
not publish to a single combined tickets file and do not co-opt the
`docs/agents/domain.md` glossary as a spec store.

Apply no extra triage label here; the SPEC file itself is the artifact that
`project-tickets` will consume. Record the exact path in the run result.

### 7. Recommend the next explicit invocation and stop

On success, report the published SPEC path and recommend:

```text
project-spec → project-tickets
```

Do not auto-invoke `project-tickets` or any other user-invoked Skill. The
handoff is verifiable: the SPEC file exists at the stated path and satisfies
[OUTPUT-FORMAT.md](OUTPUT-FORMAT.md) without reintroducing settled questions.

## Boundaries

- No tickets, implementation, research, prototype, questionnaire, or review
  loop is started by this Skill. When a return to `project-clarify` is
  required, that stage owns the next capability-call ledger.
- No project file is mutated except the single SPEC publish validated above.
- A missing or unreadable handoff is reported as an evidence gap; the run
  stops and asks the user to supply or confirm the handoff before retrying.
