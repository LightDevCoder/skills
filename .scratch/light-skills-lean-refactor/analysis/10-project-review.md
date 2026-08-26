# Project Review — logic reconstruction

**Real job:** Own project/package/release final acceptance and issue the final `PASS`/`FAIL`/`BLOCKED`, composing reviewers through `review-loop`.

**Entry:** User-invoked for final acceptance when a bounded artifact/plan and acceptance source exist; also the final-acceptance owner referenced by implementation and admission flows.

**Core loop:** Freeze acceptance baseline/charter → select profile → drive `review-loop` as the convergence engine with specialist reviewers (`generic-review`, `code-review`, domain) → validate core dispositions and evidence → bounded repair through Producer → issue final verdict.

**Produces:** Durable verdict record and review state.

**Completion/stop:** At a durable `PASS`/`FAIL`/`BLOCKED`; never lets reviewers or `review-loop` issue the verdict.

**Every-invocation knowledge:** Verdict ownership, profile selection, review-loop composition, stopping rules.

**Conditional knowledge:** Profile-specific behavior, evidence protocol, acceptance charter, reviewer contract live in references.

**Duplicates:** Does not re-document `generic-review`, `code-review`, or `review-loop` internal runbooks; it owns acceptance only.
