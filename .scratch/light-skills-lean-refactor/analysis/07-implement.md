# Implement — logic reconstruction

**Real job:** Execute one bounded, already-decided work item (code, doc, config, research artifact, Skill, generic task) and hand the result to review.

**Entry:** User explicitly invokes `$implement` against a ready ticket, Spec section, or explicit scope.

**Core loop:** Pin one item → inspect relevant context → route to `agent-config`/`tdd` only when useful → execute bounded slice → verify (typecheck/tests/render/schema) → collect evidence → hand to `review-loop` with appropriate reviewer.

**Produces:** One verified diff/artifact plus evidence packet.

**Completion/stop:** After producing evidence and recommending explicit next invocation; does not auto-chain another user-invoked Skill, does not claim PASS, does not publish.

**Every-invocation knowledge:** One-item boundary, explicit-invocation boundary, inspect-then-execute, handoff to review-loop, where workflow detail lives.

**Conditional knowledge:** Per-artifact branching, tickets consumption, and review handoff details in `references/WORKFLOW.md` and `EXAMPLES.md`.

**Duplicates:** Delegates execution mechanics to `tdd`, planner routing to `agent-config`, review to `review-loop`; does not restate them.

**Negative constraints:** No auto-invoking user-invoked Skills and no expanding scope are high-risk boundaries and remain.
