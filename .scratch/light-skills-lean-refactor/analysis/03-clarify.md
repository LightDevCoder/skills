# Clarify — logic reconstruction

**Real job:** Lightweight user-invoked standalone clarification for an ambiguous idea/requirement/plan/process when no formal project context or deliverable is required.

**Entry:** User explicitly invokes `$clarify`.

**Core loop:** Use `socratic` as the model-invoked engine to maintain decision-owned state; after each user answer, return current understanding, resolved decisions, unresolved decisions, dependencies/fact gaps, and the next frontier question; then stop.

**Produces:** Compact clarification state summary; never a formal SPEC, never files, never chained workflow.

**Completion/stop:** Each exchange ends after the summary is returned; the Skill is complete when the user stops invoking or a different user-invoked Skill is recommended.

**Every-invocation knowledge:** Invocation boundary, `clarify → socratic` composition, state-summary shape, stopping rule.

**Conditional knowledge:** Full turn mechanics and routing details live in `references/WORKFLOW.md`, `ROUTING.md`, `EXAMPLES.md`.

**Distinction from siblings:** `socratic` is the reusable engine; `project-clarify` is for an existing project with requirements; `decision-map` is for large multi-session fog. `clarify` is the standalone lightweight wrapper.

**Negative constraints:** The high-value ones (do not ask user to decide inspectable facts, do not auto-launch research/prototype, do not produce a formal SPEC) are genuine boundary guards and remain; generic "do not reimplement" phrasing was kept only where it names composition.
