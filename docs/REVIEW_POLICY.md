# First-Party Review Policy

[中文审查策略](REVIEW_POLICY.zh-CN.md)

This policy assigns review responsibilities and evidence requirements for first-party Skill work. It does not make a static check, a specialist finding, or a producer's self-report into final acceptance evidence.

## Reviewer vs review-loop vs project-review

| Role | What it is | What it does | What it never does |
| --- | --- | --- | --- |
| **Reviewer** (`generic-review` · `code-review` · domain) | Read-only specialist; see [Reviewer contract](REVIEWER_CONTRACT.md) | Inspects a bounded target + requirements and returns normalized, evidence-backed `Findings: []` | Repairs the target, directs the Producer, changes requirements, or issues a final verdict |
| **`review-loop`** | Lightweight convergence engine | Resolves the reviewer, invokes it, receives findings, returns them to the Producer, re-runs the reviewer, stops when clean or at the bounded repair limit | Owns the frozen acceptance baseline or the project final `PASS`/`FAIL`/`BLOCKED` (that belongs to `project-review`) |
| **`project-review`** | Project-level final acceptance owner | Freezes the Charter/baseline, composes the right reviewers (`generic-review` / `code-review` / domain), drives them through `review-loop`, validates dispositions, and issues the final `PASS` / `FAIL` / `BLOCKED` | Replaces reviewers' methods or invents missing acceptance criteria |

Do not put final project acceptance back into `review-loop`. A reviewer finding never becomes a project verdict without the acceptance owner's judgment.

## Review triggers

Use this policy for:

- a new Skill admission;
- a change to a Skill's behavior, trigger, invocation type, boundary, dependency, resource, or attribution;
- any runtime executable script, shared test infrastructure, or installer behavior change;
- a rename, deprecation, or removal that changes discovery, installation, or migration behavior; and
- a release candidate containing any of the above.

Documentation-only governance changes still require link, scope, and cross-reference inspection. They do not substitute for the future package-level `project-review` or `review-loop agent-skill` acceptance that an admitted Skill requires.

## Profile selection and specialist review

| Change | Required final acceptance | Additional specialist evidence |
| --- | --- | --- |
| Eligible low-risk prompt-only Skill | One fresh independent Evaluator using the fast track in [admission](SKILL_ADMISSION.md) | Structure/metadata, isolated copy/discovery, deterministic positive/negative contract tests, explicit-use/non-trigger observations, synchronized docs. No separate Critic or `code-review`. |
| New or materially changed first-party Skill | `project-review` or `review-loop` with the `agent-skill` Profile (project-level vs package-level) | Structural, fresh-install, behavioral, invocation, and attribution evidence. |
| Skill with executable scripts | `project-review` or `review-loop` with `agent-skill` Profile | Focused automated + negative tests, adversarial/mutation fixtures where appropriate, and `code-review` findings. |
| Software artifact inside a Skill | `project-review` owns the verdict; `review-loop` is its engine | `code-review` supplies Standards/Spec findings. |
| Manuscript or specification artifact | `project-review` selects `manuscript` or `specification` Profile; `review-loop` drives convergence | Artifact-specific evidence and specialist findings. |
| Release candidate | Package-level acceptance plus the Program-level gate | Verified release installation and synchronized documentation evidence. |

`generic-review` is the default reviewer when no specialist is more appropriate. `code-review` is the specialist for bounded `git diff` (Standards + Spec) — read-only.

Self-contained validation tests for an eligible prompt-only Skill do not by themselves trigger the executable-script row. If a test exercises product code, shared helpers, installers, hooks, subprocesses, network access, or other runtime behavior, the fast track is unavailable and specialist review applies.

## Evidence and independence

Producer evidence must identify exact commands, environment, inputs, outputs, revisions, scope, and limitations. The reviewer checks that each evidence item is correctly labeled as structural, installation, behavioral, invocation, script, or review evidence.

The Producer performs repairs. Critics, when required, and Evaluators remain read-only. Every final evaluation uses a fresh, independent Evaluator with the frozen acceptance source and admissible evidence. Reviewers ([REVIEWER_CONTRACT.md](REVIEWER_CONTRACT.md)) follow the normalized input packet (`Target` · `Requirements` · `Relevant context` · `Previous findings`) and return `id`/`severity`/`location`/`problem`/`reason` (+ optional `suggestion`) — never `PASS`/`FAIL`/`BLOCKED`. The fast track omits the separate Critic stage.

## Bounded repair and verdicts

`review-loop` may direct the current Producer to repair only a confirmed, in-scope finding with a bounded correction that can converge within the configured limit. It must stop with `FAIL` or `BLOCKED` when repair would require changed requirements, a new architecture decision, multiple new tickets, missing authority, missing environment access, or unavailable independent review.

The final verdict is owned by **`project-review`** (for projects/releases) or by the designated package acceptance owner (`review-loop` with `agent-skill` Profile for package admission where no separate project acceptance exists) — never by a reviewer:

- **PASS:** All frozen acceptance conditions and evidence requirements are met.
- **FAIL:** A confirmed in-scope condition is unmet and not resolved within the allowed repair path.
- **BLOCKED:** Required authority, environment, evidence, or independent review is unavailable.

A candidate with only structural validation, keyword matches, simulated fixtures, or a no-op test run cannot receive a behavior or runtime claim.

## Review record and release boundary

Preserve the frozen acceptance source, reviewer findings, repairs, evidence across rounds, final Evaluator result, and exact verdict. For a Skill, link this record from its admission evidence; for a release or project, link the affected package records and the verified installation evidence. Reviewers produce `Findings: []`; the acceptance owner produces the verdict.

No release, catalog entry, or installation command may imply final acceptance before the required verdict and release checks exist. See [admission](SKILL_ADMISSION.md) and [maintenance](MAINTENANCE.md).

Historical note: the final-acceptance capabilities (`frozen baseline`, `final verdict`, `PASS/FAIL/BLOCKED`, `scope-change boundary`) formerly embedded in `review-loop` were migrated to `project-review` (§25 Phase 7). `review-loop` is now intentionally lightweight.
