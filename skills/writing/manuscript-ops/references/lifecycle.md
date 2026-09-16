# Manuscript lifecycle

## Semantic layers

1. **Authoritative sources** — permitted evidence for factual claims.
2. **Reference-only material** — style, layout, or contextual inspiration.
3. **Incoming draft** — optional user draft; authority is not implied.
4. **Outline** — approved structure and content boundaries.
5. **Working draft** — body under active main-thread editing.
6. **Frozen review draft** — immutable review input with hashes.
7. **Candidate** — cumulative manuscript after confirmed findings are repaired.
8. **Locked source** — user-approved source for translation or derivation.
9. **Translation/derived edition** — generated only from the locked source.
10. **Final** — format-complete, independently accepted deliverable.
11. **Archive** — receipts, evidence, reproducible inputs, and retained outputs.

Never collapse a user gate by renaming an earlier layer.

## Fixed human gates

| Gate | Required evidence | Permission granted |
|---|---|---|
| Brief | `brief-approved-*` receipt for scope, sources, outputs, acceptance | initialize the project |
| Initialization | `baseline-*` receipt with immutable full Profile snapshot for paths and VCS | begin outline work |
| Outline | `framework-approved-*` receipt and fresh Evaluator `PASS` over the mapped outline | write the full body |
| Source lock | `source-locked-*` receipt and fresh Evaluator `PASS` over the register and locked manuscript | create translations/derivatives |
| Final | `final-approved-*` receipt, format QA, fresh Evaluator `PASS` | present final deliverables |
| Publish | `publish-approved-*` receipt for the final snapshot and target | create remote, push, release, deploy, or install |

Approval applies only to the named snapshot. Record the user's exact statement
and date in the receipt. The confirmation must follow the evidence it approves;
it cannot pre-authorize a later review, capability probe, or format-QA run.

## Batches

Partition by:

- semantic cohesion;
- prerequisite order;
- source and terminology dependencies;
- factual, privacy, or safety risk;
- format/layout coupling;
- volume a reviewer can evaluate without losing context.

Each batch names its kind, incremental or cumulative cadence, explicit
regression surface, hash-capable intended outputs, state, specialist report,
and human-gate policy. A normal
batch may receive incremental review; outline, candidate, and final always
receive cumulative review. Freeze and hash the input before a batch becomes
active, keep at most one active/review batch, and make LifecycleState point to
that exact batch.

Do not activate, review, or accept a successor until every prerequisite is
accepted. Review/accepted outputs are real hash-bound files. `accepted`
requires a matching `PASS` ReviewReport whose frozen snapshot contains those
outputs; a required user gate is timestamped after that review.

Source dependencies are typed. Each entry names a registered `source_id`, its
intended `use` (`factual`, `context`, `style`, or `incoming`), and a bounded
purpose. Reference-only or incoming-draft material cannot silently become
factual authority. Every Source Register row states non-empty permitted use and
exclusions.
Both fields use the same controlled use IDs. `permitted_use` is a
comma-separated subset of `factual`, `context`, `style`, and `incoming`;
`exclusions` is `none` or a disjoint comma-separated subset.

## Writer and reviewer boundaries

The main thread is the only body writer. Reviewers remain read-only and return
findings against a frozen snapshot. The main thread validates findings, repairs
confirmed issues, regenerates outputs, and freezes a successor snapshot.

## Reproducible generation

Prefer readable source plus deterministic generators for binary outputs. Record
tool versions, configuration, source hashes, commands, and output hashes.
Each READY format-QA record carries this generation lineage, and every final
record includes the active locked manuscript among its inputs. Semantic QA
compares against that exact hash-bound source.
Manual edits to a binary candidate must be either:

- promoted into the readable source/generator;
- preserved as an explicitly user-approved locked input; or
- reported as non-reproducible and therefore degraded.

Never overwrite a prior user-visible milestone. Generate a new stable filename
or date version.
