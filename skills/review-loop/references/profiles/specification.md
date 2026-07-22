# Specification Profile

Select this Profile when the frozen target is a Spec, brief, ticket,
acceptance contract, or equivalent requirements artifact whose claims must be
checked against an authoritative source. It adds specification-specific review
inputs to the generic Core; it does not replace the Core's finding identity and
disposition lifecycle, repair boundary, state machine, independence
requirement, round limit, or final verdict.

## Review axes

Review each applicable axis independently and retain the axis on every finding:

1. **Authority and baseline integrity** — the authoritative source, revision,
   approval state, decision owner, and frozen artifact identity are explicit;
   source precedence is recorded when more than one authority exists.
2. **Scope and target traceability** — the target, in-scope outcomes,
   exclusions, assumptions, dependencies, and change boundaries are explicit
   and traceable to the authoritative source rather than inferred from a
   Producer summary.
3. **Criteria and acceptance traceability** — each requirement, acceptance
   criterion, ticket condition, and required evidence has a stable identifier,
   source link, observable outcome, and an owner or validation seam.
4. **Terminology and ambiguity control** — domain terms, quantities,
   qualifiers, audience, and preconditions are defined; unknown, vague, or
   multiply interpretable language is recorded as an ambiguity, not silently
   resolved by the reviewer.
5. **Contradiction and decision coherence** — conflicting requirements,
   authority sources, dependencies, priorities, and acceptance outcomes are
   surfaced with the governing decision or a precise unblock action.
6. **Testability and evidence design** — criteria are measurable or otherwise
   observable, required evidence classes are appropriate, negative/boundary
   cases are named, and a future Producer can demonstrate each condition.
7. **Version, change, and hand-off integrity** — revision identity, change
   history, assumptions, open questions, dependency owners, gates, and
   downstream hand-offs are resumable without changing the frozen baseline.

An axis may be marked `Not applicable` only with a reason in Producer evidence
and a Charter-linked acceptance record. The Core still applies all generic
lifecycle and stopping rules.

## Evidence requirements

The specification review packet must include the following, each with exactly
one primary label from the generic [Evidence Protocol](../evidence-protocol.md):

- the immutable authoritative source identity and revision, approval state,
  source precedence, frozen target, Profile, and acceptance Charter;
- a scope/target/exclusion map that links every in-scope outcome and explicit
  non-goal to its source location or records why it is absent;
- an acceptance matrix linking every stable criterion or requirement ID to its
  source, observable outcome, owner/validation seam, and required evidence;
- a terminology and ambiguity register covering undefined terms, units,
  qualifiers, audience assumptions, and the smallest clarification needed to
  unblock review;
- a contradiction and dependency record showing competing authorities,
  unresolved conflicts, decision owner, priority, and stop condition;
- focused examples or executable checks where the contract claims behavior,
  including at least one success, boundary, and failure/missing-source case;
- version/change and hand-off evidence that preserves assumptions, open
  questions, gates, and downstream ownership across repair rounds;
- fresh independent Evaluator evidence with criterion-by-criterion links and
  outcomes. A missing source, unresolved ambiguity, or unresolved contradiction
  is a blocker, not a favorable inference.

Use only the protocol's labels (`source`, `structural`, `behavioral`,
`installation`, `invocation`, `runtime`, `manual`, or `review`). A specialist
observation is `review` evidence and remains a candidate for the generic
finding schema.

## Specialist reviewers

Use read-only specification or domain reviewers as applicable to inspect
authority, traceability, terminology, contradictions, and testability. They
return candidate findings with the axis, source reference, severity, and
evidence label preserved in the generic finding schema with a stable finding
ID. The generic Core validates every candidate as
`confirmed`, `rejected`, `duplicate`, or `out-of-scope`, directs only a bounded
Producer repair, and owns the final `PASS`, `FAIL`, or `BLOCKED` verdict.
Specialists never edit the contract and never issue the Program verdict.

## Severity guidance

Use impact against the frozen specification baseline, not estimated repair
effort:

- **Critical** — an unsafe, unauthorized, or impossible requirement, or a
  contradiction that could cause material harm if implemented as written;
- **High** — missing authority, materially untraceable scope/criterion,
  unresolved contradiction, or ambiguity that prevents a reliable acceptance
  decision;
- **Medium** — a significant owner, evidence, definition, dependency, or
  change-control gap that must be repaired before `PASS` unless an explicit
  risk acceptance is recorded;
- **Low** — a limited-impact wording, cross-reference, or maintainability gap
  that does not block `PASS` unless the Charter says otherwise.

Severity does not authorize a new requirement, product decision, source,
architecture, or ticket. Those are baseline changes or blockers under the Core.

## Acceptance conditions

The Core may ask its fresh Evaluator to consider `PASS` only when:

- the exact specification revision, authoritative source, Profile, approval
  state, target, scope, exclusions, and source precedence are frozen and agree;
- every in-scope requirement and acceptance criterion is stable, source-linked,
  observable, and mapped to an owner/validation seam and evidence class;
- definitions, units, qualifiers, assumptions, and audience are adequate for
  a single interpretation, with no unrecorded ambiguity;
- contradictions and dependency conflicts are resolved by the recorded
  authority or have a precise authority-owned unblock action;
- change history, open questions, gates, hand-offs, and non-goals are
  resumable without silently revising the Charter;
- success, boundary, failure, and missing-source checks have accurate evidence
  labels and expected versus observed outcomes;
- every confirmed blocking finding is resolved under its stable ID with fresh
  per-ID repair evidence, and any accepted Medium/Low risk has the user's exact
  post-review statement, actor, and timestamp; and
- a genuinely fresh Evaluator records criterion-by-criterion judgment. The
  generic Core records the final verdict.

## Artifact-specific failure cases

Preserve specialist observations and apply the Core's generic `FAIL` or
`BLOCKED` stopping rule when:

- the authoritative source, approval, revision, target, or acceptance scope is
  missing, stale, inaccessible, or contradictory;
- a requirement, criterion, exclusion, or dependency cannot be traced to its
  source, has no stable identifier, or is inferred from a Producer summary;
- terms, units, qualifiers, audience, preconditions, or expected outcomes are
  undefined or admit multiple materially different interpretations;
- two authorities or criteria conflict without a recorded precedence decision,
  owner, and smallest safe unblock action;
- a condition is not observable, lacks required evidence or negative/boundary
  coverage, or would force implementation to invent behavior;
- a proposed repair changes requirements, scope, authority, architecture,
  dependency, or ticket count, or requires new user authority; or
- independent Evaluator context, source access, or a required decision owner is
  unavailable. Do not weaken this Profile to make an incomplete contract pass.

The generic Core, not this Profile or a specification specialist, owns finding
identity, dispositions, repair rounds, state transitions, independence stops,
and final `PASS`, `FAIL`, or `BLOCKED`.

## Selection record

Record `Profile: specification` in the Acceptance Charter and identify the
specification revision, authoritative source, target artifact, approval state,
and reason this Profile applies. A later change to requirements, authority,
scope, or acceptance criteria is a baseline change requiring the Core's
approved change process.
