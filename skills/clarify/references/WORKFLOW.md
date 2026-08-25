# Clarify workflow

Supporting detail for `clarify`. `SKILL.md` is the entry; this file holds the
full step description.

## Entry condition

- User explicitly invokes `$clarify` with an idea, requirement, brainstorm
  topic, plan, or vague request.
- No project context is required. The thread is standalone.

Do not start `clarify` from a general vague prompt — wait for the explicit
`$clarify` token.

## Steps

1. Collect the minimal context the user supplied (goal, constraints, initial
   vague request).
2. Call `socratic` (model-invoked) with that context. Let it separate known
   facts, user-owned open decisions, dependencies, and the current frontier.
3. Present only the frontier question(s) from `socratic`. Do not add a fixed
   questionnaire or re-ask settled decisions.
4. Return the compact state summary defined in `SKILL.md` and stop.

On a subsequent `$clarify` invocation with an answer, feed the answer back to
`socratic`, update the state, recompute the frontier, and present the next
frontier or the fact-finding gap that blocks it.

## Boundaries

- No formal SPEC or tickets are produced.
- No project files are written.
- No automatic chaining to another user-invoked Skill. If `project-clarify`,
  `research`, `prototype`, or `to-questionnaire` would be useful, recommend
  the explicit invocation and stop.
- Fact work is reported as a gap, not executed, unless the user separately
  authorizes it (see `ROUTING.md`).

## Handoff options

- If the clarified thread now has enough context to become a project stage,
  recommend `$project-clarify` and stop.
- If the user wants a questionnaire for another person, recommend
  `$to-questionnaire` and stop.
- Otherwise the user may simply continue `$clarify` turns until the frontier
  is empty or blocked.
