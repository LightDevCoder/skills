# First-Party Review Policy

[中文审查策略](REVIEW_POLICY.zh-CN.md)

This policy assigns review responsibilities and evidence requirements for
first-party Skill work. It does not make a static check, a specialist finding,
or a producer's self-report into final acceptance evidence.

## Review triggers

Use this policy for:

- a new Skill admission;
- a change to a Skill's behavior, trigger, invocation type, boundary,
  dependency, resource, or attribution;
- any runtime executable script, shared test infrastructure, or installer
  behavior change;
- a rename, deprecation, or removal that changes discovery, installation, or
  migration behavior; and
- a release candidate containing any of the above.

Documentation-only governance changes still require link, scope, and
cross-reference inspection. They do not substitute for the future package-level
`review-loop agent-skill` acceptance that an admitted Skill requires.

## Profile selection and specialist review

| Change | Required final review | Additional specialist evidence |
| --- | --- | --- |
| Eligible low-risk prompt-only Skill | One fresh independent Evaluator using the fast track in [admission](SKILL_ADMISSION.md) | Structure/metadata, isolated copy/discovery, deterministic positive/negative contract tests, explicit-use/non-trigger observations, and synchronized docs. No separate Critic or `code-review`. |
| New or materially changed first-party Skill | `review-loop` using the `agent-skill` Profile | Structural, fresh-install, behavioral, invocation, and attribution evidence. |
| Skill with executable scripts | `review-loop` using the `agent-skill` Profile | Focused automated and negative tests, adversarial or mutation fixtures where appropriate, and `code-review`. |
| Software artifact inside a Skill | `review-loop` owns the final verdict; use the applicable profile | `code-review` supplies software standards and Spec findings. |
| Manuscript or specification artifact produced by a Skill | `review-loop` selects the manuscript or specification Profile as applicable | Artifact-specific evidence and specialist findings. |
| Release candidate | The applicable package-level reviews plus the required Program-level acceptance gate | Verified release installation and synchronized documentation evidence. |

`code-review` remains a specialist reviewer. It does not own the Program or
package final acceptance verdict.

Self-contained validation tests for an eligible prompt-only Skill do not by
themselves trigger the executable-script row. If a test exercises product
code, shared helpers, installers, hooks, subprocesses, network access, or other
runtime behavior, the fast track is unavailable and specialist review applies.

## Evidence and independence

Producer evidence must identify exact commands, environment, inputs, outputs,
revisions, scope, and limitations. The reviewer checks that each evidence item
is correctly labeled as structural, installation, behavioral, invocation,
script, or review evidence.

The Producer performs repairs. Critics, when required, and Evaluators remain
read-only. Every final evaluation uses a fresh, independent Evaluator with the
frozen acceptance source and admissible evidence, rather than an intended
conclusion. The fast track omits the separate Critic stage.

## Bounded repair and verdicts

`review-loop` may direct the current Producer to repair only a confirmed,
in-scope finding with a bounded correction that can converge within the
configured repair limit. It must stop with `FAIL` or `BLOCKED` when repair
would require changed requirements, a new architecture decision, multiple new
implementation tickets, missing authority, missing environment access, or an
unavailable independent review.

The final verdict is owned by `review-loop`:

- **PASS:** All frozen acceptance conditions and evidence requirements are met.
- **FAIL:** A confirmed in-scope condition is unmet and is not resolved within
  the allowed repair path.
- **BLOCKED:** Required authority, environment, evidence, or independent
  review is unavailable.

A candidate with only structural validation, keyword matches, simulated
fixtures, or a no-op test run cannot receive a behavior or runtime claim.

## Review record and release boundary

Preserve the frozen acceptance source, findings, repairs, evidence across
rounds, final Evaluator result, and exact verdict. For a Skill, link this
record from its admission evidence; for a release, link the affected package
records and the verified installation evidence.

No release, catalog entry, or installation command may imply final acceptance
before the required verdict and release checks exist. See
[admission](SKILL_ADMISSION.md) and [maintenance](MAINTENANCE.md).
