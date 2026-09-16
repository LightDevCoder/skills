# Authorization and completion boundary maintenance — 2026-09-16

## Approved scope

User-approved maintenance of `tdd`, `clarify`, `implement`, `review-loop`, and
`manuscript-ops`: reuse existing explicit authorization within its scope;
distinguish optional routing failure from missing task authority; return
stage-local completion to the caller; accept unambiguous same-session resume
requests where the host permits. No package addition or invocation-type change.

Preserve new-seam approval, configuration preview approval, separately
authorized fact work, user-invoked handoffs, one-item execution, review limits,
independent acceptance, manuscript gates, and release candidate approval.
Optional-route fallback needs affirmative evidence for scope, current-session
capability and authority, preserved constraints, and absence of a required route.

## Evidence classification

- Structural/contract: full pytest suite, Markdown link/discovery checks,
  and diff whitespace validation.
- Simulated behavior: the existing implement decision model covers positive
  optional fallback and negative cases for each required condition, unknown
  readiness, and ticket decomposition. It is test-local, not a runtime executor.
- Clarify lifecycle: policy metadata reflects explicit authorization reuse;
  shared-understanding confirmation and user-invoked chaining remain unchanged.
- Static scenario review: independent review checks prompts and linked workflow
  consistency against the approved scope. This is not host runtime proof.
- Installation: affected installed package files will be byte-compared to the
  reviewed source. No fresh published installation or host reload claim.

## Validation status

Candidate review pending. Initial suite: 303 passed; one discovery check failed
because this evidence link had been added before its target existed. The link
is now present; final checks and independent review will be recorded below.
No release tag or GitHub Release is requested or produced.
