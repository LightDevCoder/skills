# Software Profile

Select this Profile when the frozen target is executable software, a software
component, or a repository change whose acceptance depends on code behavior.
The Profile adds software-specific review inputs to the generic Core; it does
not replace the Core's finding registry, state machine, repair limit,
independence requirement, or final-verdict rules.

## Review axes

Review each applicable axis independently and retain the axis on every
specialist finding:

1. **Standards** — conformance to the target repository's documented coding,
   security, dependency, and maintainability standards. The upstream
   `code-review` Skill supplies this axis's findings.
2. **Spec fidelity** — behavior and interfaces match the approved Spec, ticket,
   or acceptance Charter, including explicit exclusions. The upstream
   `code-review` Skill supplies this axis's findings.
3. **Behavioral correctness** — focused success, boundary, failure, and
   regression scenarios exercise the changed behavior rather than only its
   file shape.
4. **Operational safety** — error handling, validation, compatibility,
   security-sensitive behavior, and data/resource safety are adequate for the
   frozen scope.

An axis may be marked `Not applicable` only with a reason in the Producer
evidence and Charter-linked acceptance record. The Core still applies all
generic lifecycle and stopping rules.

## Evidence requirements

The software review packet must include the following, with labels from the
generic [Evidence Protocol](../evidence-protocol.md):

- the frozen `Fixed point` / `Implementation scope` identities and the
  non-empty in-scope diff reviewed by `code-review`;
- the approved Spec or equivalent acceptance source and its immutable revision;
- separate `code-review` reports for **Standards** and **Spec** findings;
- focused automated tests covering changed success, boundary, and failure
  behavior, including a negative or adversarial case where relevant;
- a representative runtime or integration observation when the software's
  behavior cannot be established by focused tests alone;
- limitations such as unavailable dependencies, environments, generated
  outputs, or untestable paths.

`code-review` findings are `review` evidence and candidates only. The Core
copies each candidate into the generic finding schema, preserving its source
axis, source finding reference, evidence, severity, and stable `F-###` ID.
The specialist's own `PASS`/`FAIL` summary is evidence about its axes; it is
never the Program's acceptance verdict.

### Durable software baseline record

A software verdict binds to a three-part produced identity. Two parts freeze
in the Charter at `init`; the third is recorded on the final verdict because
authorized bounded repairs may legitimately move the evaluated candidate
during the review lifecycle. Each field is a singleton field: it must appear
exactly once in its record. A missing, duplicated (even identically), or
ambiguous occurrence is invalid durable review state, and consumers fail
closed instead of selecting a value.

1. **`Fixed point`** — `- Fixed point: <full Git commit SHA>` in the Charter.
   Exactly one full 40-character commit SHA: the immutable base from which
   `code-review` reviews the software change. This is the *review base*, not
   the final accepted implementation. When the caller names a branch or tag,
   freeze the actual effective commit that delimits the review, never the
   mutable ref name. No prose, no second endpoint, no short SHA.
2. **`Implementation scope`** — `- Implementation scope: <repo-relative literal
   path>; <repo-relative literal path>; ...` in the Charter: the
   machine-readable projection of this Charter's approved software
   `In scope`, i.e. the complete component whose state must remain equal to
   the accepted implementation. Freeze stable component roots (`src/`,
   `src/; tests/; pyproject.toml`), or `.` only when the whole repository
   intentionally is the reviewed target — not merely the files the current
   diff happens to touch. Never derive the scope from changed paths, from a
   common directory of those paths, or from file extensions. Establish it
   from the approved acceptance target, explicit SPEC/Charter paths, project
   or ticket scope, repository/component boundaries, or an explicit
   user-approved target; if the complete software target cannot be
   established reliably, return `BLOCKED` instead of guessing a narrow scope
   just to continue. Every entry must be a repository-relative POSIX literal
   path: an absolute path, `..` traversal, Git pathspec magic, wildcard/glob
   characters, quoting wrappers, or one malformed entry inside an otherwise
   valid list rejects the WHOLE field — valid entries are never partially
   salvaged. There are no implicit documentation exceptions: with scope `.`
   a README change counts; with scope `src/` a root README stays outside
   acceptance. The scope decides, never a hard-coded filename rule.
3. **`Reviewed implementation revision`** — `- Reviewed implementation
   revision: <full Git commit SHA>` on `.project-review/verdict.md`: the
   exact committed implementation the final fresh Evaluator judged. It lives
   on the verdict rather than in the immutable Charter precisely because
   `review → confirmed finding → bounded repair → re-review → fresh
   Evaluator → PASS` may move the candidate from C1 to C2; the verdict then
   binds the immutable Charter requirements to C2 without mutating the
   Charter.

### Baseline lifecycle rules

- Each review round evaluates the current implementation delimited by the
  frozen `Fixed point`. The window from `Fixed point` to the reviewed
  candidate must contain non-empty change inside `Implementation scope`;
  a diff that only touches out-of-scope files is not software evidence, and
  the scope is never broadened to manufacture one.
- An authorized repair stays inside the frozen scope. Before C2 can become
  the durable reviewed implementation, the in-scope repair is committed, the
  required focused evidence and specialist review are refreshed, a fresh
  Evaluator judges C2, and the verdict records C2 — never C1. Do not mutate
  the Charter's `Fixed point` to make a repair fit.
- A durable `PASS`, `FAIL`, or `BLOCKED` always names the implementation
  revision it evaluated. At final evaluation time the frozen scope must hold
  no uncommitted tracked, untracked, or ignored changes: Git ignore rules
  hide files from `git status`, not from the reviewed component, so an
  ignored file inside the scope is drift exactly like any other addition. A
  `PASS` never binds while additional in-scope implementation work exists.
  Unrelated dirty files outside the scope do not block acceptance.
- Files that pre-existed inside the scope but were untouched by the review
  diff, and files created inside the scope afterwards (tracked, untracked,
  or ignored), still belong to the accepted component; drifting them
  invalidates the verdict whatever the review window once said.
- Keep project-review's own mutable records out of the frozen target.
  `.project-review/`, `.review-loop/`, and `.scratch/` acceptance/spec/ticket
  state are review metadata, not implementation — unless they genuinely are
  the software artifact under review. In particular, a whole-repo scope `.`
  includes them: the closeout writes that record the verdict would then be
  in-scope drift and stale the PASS the moment it is issued. Freeze the real
  component scope instead.

## Specialist reviewer: `code-review`

Invoke the upstream `code-review` capability with the frozen fixed point and
approved Spec. Request the two normal axes separately:

```text
code-review (Standards) + code-review (Spec)
  -> specialist findings and evidence
  -> Core candidate validation and generic finding lifecycle
```

The Critic/Core validates every candidate as `confirmed`, `rejected`,
`duplicate`, or `out-of-scope` using the generic [Finding Schema](../finding-schema.md).
Do not treat a specialist recommendation as proof, and do not ask
`code-review` to edit the target. Only the Producer performs an authorized
bounded repair; a fresh Evaluator rechecks the original finding ID afterward.

## Severity guidance

Use impact against the frozen software baseline, not estimated repair effort:

- **Critical** — exploitable security issue, data loss/corruption, unsafe
  execution, or a failure that makes the software unusable for the accepted
  goal.
- **High** — a required Spec behavior or public interface is absent/broken, a
  regression blocks a required scenario, or a mandatory repository standard is
  violated.
- **Medium** — a material in-scope defect, compatibility risk, or missing
  boundary/error handling that must be resolved before `PASS` unless the
  Charter records an approved exception.
- **Low** — limited-impact maintainability, diagnostic, or test-quality gap
  that does not block `PASS` unless the Charter says otherwise.

When Standards and Spec disagree about impact, record both axis judgments and
let the Core validate the resulting candidate; severity does not authorize a
scope change.

## Acceptance conditions

The Core may ask its fresh Evaluator to consider `PASS` only when:

- the fixed point, approved Spec, and software Profile are frozen and match
  the reviewed target, and the verdict records the exact implementation
  revision (`Reviewed implementation revision`) the fresh Evaluator judged;
- every applicable axis has correctly labeled evidence, including both
  `code-review` axes and required behavioral/operational scenarios;
- each specialist candidate has a generic disposition and every confirmed
  blocking finding is resolved with fresh evidence under the same stable ID;
- tests are real, assertion-bearing, and relevant to the changed behavior;
- no repair changed requirements, architecture, interfaces, or other frozen
  scope; and
- the independent Evaluator records the criterion-by-criterion judgment.

The final `PASS`, `FAIL`, or `BLOCKED` is issued and recorded by **project-review
Core** under the generic stopping rules. A `code-review` report can never close
the loop by itself.

## Artifact-specific failure cases

Return the generic `FAIL` or `BLOCKED` outcome as applicable when:

- the fixed point, implementation scope, approved Spec, or required
  `code-review` axis is missing, malformed, or cannot be verified;
- the in-scope diff is empty (out-of-scope-only change), the code-review report is a
  repository-wide redesign, or the report cannot identify the changed software scope;
- tests are absent where required, pass without assertions, or cannot exercise
  a required success/boundary/failure scenario;
- a candidate is accepted solely because `code-review` recommended it, or a
  specialist summary is presented as the final Program verdict;
- a proposed repair needs a new requirement, Spec revision, architecture
  decision, access/authority, or multiple new implementation tickets; or
- required runtime/dependency evidence or independent Critic/Evaluator context
  is unavailable or contradicts the durable records.

Preserve the specialist report and candidate evidence even when a candidate is
rejected, duplicated, out of scope, or the review is blocked. Use a Change
Proposal for any material baseline change; do not weaken this Profile to make
the current implementation pass.
