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

- the fixed-point identity and non-empty diff reviewed by `code-review`;
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

### Durable fixed-point record

A software verdict binds to two frozen baselines, and both must be durably
recorded in the Charter at `init` time:

- the approved source, through the normal `Source:` and
  `Source revision or identity:` fields; and
- the reviewed implementation, through a `- Fixed point:` field resolving to
  local Git commits. Two values (`<base> <candidate>`) delimit the reviewed
  implementation window directly; one value identifies a candidate commit whose
  parent delimits its own change set. A repository-first commit may never be
  the sole value, because no window can be delimited from it.

A consumer may rely on a software verdict only while the current tree still
matches that fixed point on exactly the paths the recorded window touched;
anything else requires a fresh review. A missing, unresolvable, or
undelimitable `Fixed point:` fails the record closed rather than relaxing
acceptance.

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
  the reviewed target;
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

- the fixed point, approved Spec, or required `code-review` axis is missing;
- the diff is empty, the code-review report is a repository-wide redesign, or
  the report cannot identify the changed software scope;
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
