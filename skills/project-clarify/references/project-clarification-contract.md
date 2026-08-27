# Project clarification contract

Use this reference to keep a `project-clarify` run inspectable and bounded.

## Evidence-first sequence

Before asking a user question, inspect the target root for the project
material that is applicable and readable:

- root instructions: `AGENTS.md`, `CLAUDE.md`
- brief/context: `README`, `CONTEXT.md` or `CONTEXT-MAP.md`
- decisions: `docs/adr/` (and `src/<context>/docs/adr/` for multi-context)
- source and tests: entry points relevant to the topic
- documents/specs: `docs/specs/`, existing specs
- task/tracker state: `.scratch/<effort>/`, issues, `map.md`
- prior handoff: a previous `Project clarification handoff` or readiness record
  when present

Record a path plus a stable location for every fact used (heading, symbol,
file, line). Mark an absent path, unreadable location, or outside-scope
material as an evidence gap rather than an unknown fact.

Separate the state into:

- confirmed project facts and their locations;
- user-owned decisions;
- fact or experiment dependencies; and
- an unblocked question frontier.

Only the frontier may be asked. Present the complete actionable frontier as a
round: number the questions (`Q1`, `Q2`, ...), add options and recommendations
when appropriate, and accept batch replies. An unresolved fact, an unavailable
capability, or an unstarted authorized call blocks its downstream decision.

## Capability-call ledger

`socratic` is the required model-invoked decision engine. `research` and
`prototype` are optional model-invoked fact-work capabilities, not stages to
start by default. `to-questionnaire` is the optional branch when the blocked
information is held by another person; because it is a user-invoked Skill,
record it as attempted/recommended rather than auto-running it.

For each invoked, attempted, or recommended call, record:

```text
Capability call: socratic | research | prototype | to-questionnaire
Question or experiment:
Blocked decision:
Authorization and input:
Call status: not-needed | not-authorized | unavailable | started | result-read | failed | recommended
Capability outcome: COMPLETE | NEED-INPUT | BOUNDARY | ANSWERED | UNKNOWN | BLOCKED | none
Result read: path or artifact identifier | none
Failure or limitation:
```

Valid outcomes preserve the invoked package's actual result vocabulary.
Never record `result-read` without a result path or artifact identifier that
was actually read. `not-authorized` and `unavailable` are valid no-write
outcomes; they leave the dependency visible and do not prompt the user to
decide the missing fact.

Do not claim a capability has started or completed unless it actually has.
If the decision is blocked by a missing capability, report `missing capability:
<name>` and keep the downstream decision out of the frontier.

## Handoff and write boundary

The returned `Project clarification handoff` is the default artifact:

```text
Project clarification handoff
- Target and inspected project facts:
- Evidence not found or not inspected:
- Current goal and constraints:
- Resolved user decisions:
- Open decisions and dependencies:
- Capability call records and results read:
- Current frontier or explicit blocker:
- Recommended next explicit invocation: project-spec | decision-map | none
- Status: ready-for-next-stage | waiting-for-user | blocked
```

It is not a formal SPEC or a ticket set, but its fields are sufficient for
`project-spec` to produce a SPEC without re-asking the inspection-answered
facts.

No project file is written merely to retain the handoff. A user may separately
name a destination and confirm that write; validate that it is inside the
target root and report the created path. The run always stops after the
handoff.

## Upgrade to decision-map

If the task is large, multi-session, or has many dependent decisions with fog
beyond the current frontier, recommend `$decision-map` rather than trying to
resolve all decisions in one `project-clarify` turn.

