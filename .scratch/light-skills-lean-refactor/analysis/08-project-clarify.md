# Project Clarify — logic reconstruction

**Real job:** Clarify an existing project's requirements into a bounded clarification handoff, using inspected facts before user decisions.

**Entry:** User explicitly invokes `$project-clarify` for an existing project with unclear requirements.

**Core loop:** Inspect project facts/manifests → use `socratic` to track user-owned decisions → distinguish facts from decisions → record evidence and gaps → produce a formal clarification handoff for `project-spec`.

**Produces:** Project clarification handoff (target, inspected facts, evidence not found, goal/constraints, resolved/open decisions, capability call records, frontier/blocker).

**Completion/stop:** Handoff is complete when blocking user decisions are resolved and the way is ready for `project-spec`; recommend explicit `$project-spec` and stop.

**Every-invocation knowledge:** Inspect-before-ask, `project-clarify → socratic`, handoff shape, difference from `clarify`.

**Conditional knowledge:** Full workflow, contract, examples live in references.

**Duplicates:** Does not re-document `socratic`, `research`, `prototype`, `to-questionnaire`; records when they were called.

**Negative constraints:** Do not treat fact-finding as user decision and do not auto-chain are central boundaries.
