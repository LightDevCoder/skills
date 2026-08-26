# Socratic — logic reconstruction

**Real job:** Model-invoked Clarification Engine that maintains a decision-owned state and asks only the currently unblocked user decisions.

**Entry:** Invoked by a clarification wrapper (`clarify`, `project-clarify`, `decision-map`) when user-owned choices need tracking.

**Core loop:** Receive answer → update current understanding → mark newly resolved decisions → recompute dependencies/frontier → ask only unblocked frontier decisions → return compact state update.

**Produces:** Compact state update; never a fixed questionnaire, research, prototype, or formal SPEC.

**Completion/stop:** Each turn stops after the state update and question; empty frontier means state whether blocker is fact/capability/no remaining decision, not invent conclusion.

**Every-invocation knowledge:** Dynamic follow-up, fact-vs-decision rule, state fields, unknown routing.

**Conditional knowledge:** Full turn procedure and examples in references; routing contract in `ROUTING.md`.

**Duplicates:** Delegates unknown fact/experiment/human-held work to `research`, `prototype`, `to-questionnaire`.

**Negative constraints:** Do not phrase facts as user decisions and do not auto-launch fact work are core engine boundaries.
