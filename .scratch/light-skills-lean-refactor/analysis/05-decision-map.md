# Decision Map — logic reconstruction

**Real job:** Plan large, multi-session, decision-heavy work as a persistent local markdown decision map and child tickets.

**Entry:** User explicitly invokes `$decision-map`.

**Core decision path:** If charting: name destination → breadth-first surface fog/frontier → create map.md + specifiable child tickets → wire blocking edges → stop. If working through existing map: load map → choose/claim frontier ticket → resolve via the right capability (`research`, `prototype`, `socratic`, `to-questionnaire`, task) → append answer and update map → stop after one ticket per session.

**Produces:** `.scratch/<effort>/map.md` + numbered ticket files; decisions, not deliverables.

**Completion/stop:** Map is done when open tickets are zero and fog is empty; then recommend `$project-spec` explicitly and stop.

**Every-invocation knowledge:** Tracker-native map/ticket shapes, one-ticket-per-session, composition by ticket type, handoff condition.

**Conditional knowledge:** Exact file shapes (MAP-CONTRACT) and full lifecycle (WORKFLOW/EXAMPLES) are loaded only when creating/updating a map.

**Duplicates:** Delegates to `socratic`, `research`, `prototype`, `to-questionnaire` rather than copying their methods.

**Negative constraints:** "Do not copy capabilities" is a composition guard; "do not auto-chain to project-spec" is a real user-invoked boundary.
