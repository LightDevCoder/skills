# Socratic workflow

Detailed turn procedure for the `socratic` engine. `SKILL.md` is the entry
point; this file is the supporting reference.

## Decision ownership

- **User-owned**: outcomes, priorities, tradeoffs, acceptable risk, scope
  choices that require judgment.
- **Agent-owned facts**: inspectable project facts, external docs/APIs/specs,
  source code behavior, experiment results.

Never phrase an inspectable or researchable fact as a user decision. If a
fact is needed, record it as a dependency and note the appropriate
capability (`research` for external facts, `prototype` for experiments,
`to-questionnaire` when held by another person, local inspection otherwise).

Do not claim inspection, research, or a prototype has started or completed
unless that work actually occurred. If the capability is not callable in the
current context, retain the fact as unresolved and report the exact missing
capability.

## State fields

At each turn, maintain and return:

- **current understanding** — goals, constraints, confirmed facts with source
  or explicit `UNKNOWN` marker.
- **open decisions** — user-owned choices not yet settled.
- **dependencies** — facts/experiments/prior choices that block a decision.
- **frontier** — open decisions whose dependencies are satisfied and that may
  be asked now.
- **newly resolved decisions** — choices settled by the latest user answer.

Do not repeat resolved facts/decisions. Treat each user answer as evidence:
update current understanding, mark every decision it settles as newly
resolved, identify affected dependencies, then recompute the frontier.

## Conversation turn

1. Separate the supplied information into known facts, user decisions, and
   fact-finding dependencies (see `ROUTING.md`).
2. Ask only the current frontier. Keep each question tied to the decision it
   would settle and state the meaningful options or tradeoff when context
   provides them. Do not manufacture a fixed set or count of questions.
3. On an answer, dynamically adjust the next frontier rather than following a
   prewritten order. An answer often settles multiple decisions or surfaces
   new ones.
4. Return the updated state and any clear, unstarted fact-finding next step.
   Stop for the user's decision or for separately authorized fact work.

## Stopping

- If frontier is empty and no dependencies remain: `done`.
- If frontier is empty but dependencies are blocked on facts: report the
  fact gap and capability needed; `wait for decision` is not applicable.
- If a dependency is blocked by missing capability: report the gap, keep the
  downstream decision out of the frontier.

The engine never auto-invokes another user-invoked Skill, launches research
or a prototype, modifies project files, or advances into a formal SPEC.
