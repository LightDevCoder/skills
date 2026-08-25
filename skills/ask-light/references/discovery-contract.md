# Ask-light discovery contract

This reference defines the observable read-only protocol used by `ask-light`
(Light Workflow Router). Light's first-party collection now contains 33 Skills
across Project Workflow, Clarification & Research, Execution, Review, Reusable
Capabilities, Specialized Workflows, and Router. This contract covers how the
router discovers and ranks those Skills without reimplementing them.

## Context record

The caller supplies a JSON-like record. Empty fields remain unknown rather than
being inferred from a package name.

| Field | Meaning | Examples |
| --- | --- | --- |
| `goal` | User-visible outcome or question | "fix the failing parser" |
| `artifacts` | Relevant artifact paths/types | `src/*.ts`, `README.md`, `figure.png` |
| `blockers` | Current errors, missing evidence, access, or decisions | "no independent review" |
| `projectType` | Dominant project domain | `software`, `manuscript`, `research` |
| `taskKind` | Current operation, not the whole project | `debugging`, `implementation`, `review` |
| `availability` | Host, readable roots, revisions, and visible capabilities | `codex`, `global Skills readable` |
| `invocationControl` | User's permitted invocation mode | `explicit-only`, `model-callable`, `either` |

`goal` or `taskKind` may be absent only when the result is `NEED-INPUT`.

The caller selects an explicit mode: `next` returns one next Skill, while
`workflow` returns one bounded recipe recommendation. The mode never changes
the no-execution boundary.

## Candidate record and metadata pass

Each source root is declared as `{ category, path }`. Supported categories are
`project`, `global`, `first-party`, `upstream`, `modified-third-party`, and
`other`. The scanner may accept host-specific aliases but preserves the
canonical category in output.

For every package directory, the metadata pass reads only:

1. the YAML frontmatter in `SKILL.md` up to its closing `---`;
2. `agents/openai.yaml` when it exists;
3. file readability and resolved package path.

The pass records `name`, `description`, `displayName`, `shortDescription`,
`defaultPrompt`, and `allowImplicitInvocation`. A missing, malformed, or
unreadable field, including any missing display/default-prompt metadata, sets
`metadataStatus: unavailable` and records a gap. Such a candidate remains
visible with `metadataReadable: false`, its source, package path, and
readability details for remediation
but is not eligible for a normal recommendation. Bodies and references are not
read in this pass.

The stable identity is:

```text
normalized-name + source-category + resolved-package-path
```

Same-name records are grouped, never overwritten. A source-specific package
may therefore win a tie without hiding another installation of that name.

## Ranking and narrow reads

Compute a fit score from independent evidence: goal, artifact, blocker,
project-type, and task-kind matches. Add compatibility for host availability and
the requested invocation control. A candidate with incomplete metadata,
unreadable files, or an unavailable host is ineligible. Source precedence is a
final tie-break only:

```text
project -> global -> first-party -> modified-third-party -> upstream -> other
```

The scanner sorts by score, compatibility, source precedence, then normalized
path. It reads bodies and relative references only for the top `N` candidates
(`N=3` by default) or for a tied pair. It must expose body/reference read counts
so a large catalog cannot masquerade as a full-body scan.

Availability is an eligibility gate, not a display hint. If the active context
declares a host, available/unavailable Skill names, readable paths, or a
candidate's declared `hosts` list (inline or YAML block-list form), filter
incompatible candidates before shortlisting and record the exact gap. A
compatible candidate receives an availability score contribution; an
unavailable candidate is never recommended.

After shortlisting, a failed `SKILL.md` or linked-reference read sets the
candidate's `readStatus` to `unavailable`, preserves the read error, and removes
it from the final recommendation set. If every shortlisted candidate fails a
body/reference read, return `BLOCKED` with the smallest restore/readability
remedy rather than accepting metadata-only evidence.

Two candidates are **genuinely ambiguous** only when both are eligible, their
scores remain within one point after body/reference checks, and their matched
task evidence represents materially different next actions. Equivalent
duplicate packages with the same action fingerprint are not ambiguous. Return one best
candidate and at most one `Alternative`; suppress alternatives for ordinary
ranking differences.

## Workflow recommendation

Workflow mode uses a small validated recipe catalog rather than a permanent
state machine. A recipe has an entry condition, participating Skills, source
category, invocation type, expected input (`expectedInput`), expected output
(`expectedOutput`), handoff artifact, per-step stop condition
(`stopCondition`), optional flag, missing dependency, and final authority. The
supported recipes cover software feature, bug diagnosis, manuscript project,
source-to-Skill, new project initialization, final review, and private
third-party dependency availability gaps.

Only candidates visible in the declared roots and passing metadata/availability
checks are reported as available. Missing upstream or private third-party
steps stay in the output with `missingDependency`; a required gap makes the
workflow `BLOCKED`. An uncertain or tied recipe returns `NEED-INPUT`. In
`explicit-only` mode, a user-invoked `learn-anything` remains eligible and its
invocation type is reported; explicit-only does not silently exclude it.

## Output and non-execution

`RECOMMEND` contains exactly one best Skill, a context-specific reason, source,
confidence, and host-appropriate invocation. `NEED-INPUT` asks one question.
`BLOCKED` lists the missing/unreadable capability and the smallest actionable
installation/readability remedy. Every result includes metadata/body/reference
read counts and the statement that no recommendation was invoked or installed.

`ask-light` may inspect files and metadata, but it never executes, orchestrates,
installs, edits, commits, or delegates the recommended Skill or workflow step:
nothing was invoked, installed, or orchestrated.
The user must invoke the printed command or choose each recipe step in a later
action. `review-loop` owns any final acceptance verdict; recipe output is not a
verdict.
