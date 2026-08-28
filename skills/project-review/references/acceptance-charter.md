# Acceptance Charter

Use this template for `.project-review/charter.md`. The Charter freezes what the
current review may accept. Keep the source identity and criteria here; do not
copy them into state, round, or verdict records.

```markdown
# Acceptance Charter

## Revision
- Charter revision: 1
- Supersedes: none
- Created at: <timestamp>

## Acceptance baseline
- Source: <approved source path or immutable identifier>
- Source revision or identity: <commit, version, timestamp, or equivalent>
- Fixed point: <software Profile only - exactly one full Git commit SHA: the immutable code-review base>
- Implementation scope: <software Profile only - reviewed software target as ';'-separated repository-relative literal paths>
- Approval state: approved | pending user confirmation
- Approval evidence: <source section or confirmation>

## Review Profile
- Profile: generic | <accepted named Profile>
- Selection reason: <why this Profile applies>

## Original goal
<preserve the requested outcome in meaning>

## User-visible outcome
<observable result when the goal is met>

## In scope
- <bounded capability, artifact, or interaction>

## Out of scope
- <explicit exclusions>

## Acceptance criteria
- AC-1: <observable criterion and required evidence>

## Required evidence
- <evidence item and its allowed label>

## Required validation scenarios
- VS-1: <setup, action, expected observable result, and cleanup>

## Constraints, assumptions, and risks
- <constraint, checkable assumption, or risk and mitigation>

## Approved exceptions
- None
```

Use `Not applicable - <reason>` rather than silently omitting a necessary
section. A source explicitly approved by the user or program record may create
an approved Charter. A synthesized baseline starts `pending user confirmation`;
do not review it until confirmation is recorded.

Canonical durable fields are singleton fields: `- Charter revision:`,
`- Source:`, `- Source revision or identity:`, and `- Profile:` (plus the
software-only `- Fixed point:` and `- Implementation scope:`) in `charter.md`,
`- Status:`, `- Charter revision:`, `- Profile:`, and `- Round:` (with Round >= 1) in `state.md`,
and `- Verdict:` (strictly `PASS | FAIL | BLOCKED`, no aliases such as Result/Outcome/Acceptance/Status/State),
`- Charter revision:`, `- Profile:`, and `- Round:` (with Round >= 1, plus
software `- Reviewed implementation revision:`) in `verdict.md` must each appear
exactly once and remain mutually coherent across the entire transaction. A missing,
duplicated (even identically), or ambiguous canonical field is invalid durable
review state — consumers fail closed rather than choosing a value. A reviewed
directory `Source:` is a complete baseline: files that appear inside it after
the recorded revision count against freshness even when Git ignore rules hide
them from `git status` — ignore configuration controls status presentation,
not baseline membership.

For a software Profile, `Fixed point` and `Implementation scope` are immutable
Charter fields frozen at `init` ([profiles/software.md](profiles/software.md)).
The final implementation candidate is deliberately NOT frozen here: an
authorized bounded repair moves the candidate during review, so it is recorded
as `- Reviewed implementation revision:` on the final verdict instead. Never
edit an approved Charter to chase the current candidate.

## Immutability and change proposals

Never edit an approved Charter to make the current artifact pass. Preserve the
old revision and append a Change Proposal to `.project-review/changes.md` when a
material change is requested:

```markdown
## CP-001 - <short title>
- Proposed at: <timestamp>
- Requested by: <person or source>
- Reason: <why the baseline would change>
- Old Charter revision: <n>
- Proposed revision: <n+1>
- Scope and evidence impact: <affected work and records>
- Decision: pending | approved | rejected
- Decision evidence: <user confirmation or approved source>
```

Do not apply a new revision until it is approved. A rejected proposal remains
evidence; it does not erase the earlier Charter or findings.
