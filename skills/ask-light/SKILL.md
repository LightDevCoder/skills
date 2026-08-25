---
name: ask-light
description: Inspect the Skills available to the active Agent host and recommend either one appropriate next Skill or one bounded workflow recipe from the current goal, artifacts, blockers, project type, task kind, availability, and invocation control. Use only when the user explicitly invokes $ask-light; it reports a recommendation and never executes, installs, or orchestrates it.
disable-model-invocation: true
---

# Ask Light

`ask-light` is the **Light Workflow Router** — a user-invoked, read-only router
built last, after the full Skill map exists ("先把路修好，再画地图"). It answers
"which installed Skill is the best next fit?" from the active host and project
state across the 33 first-party Skills. It does not replace project discovery,
specification, implementation, or final acceptance. The recommendation is an
output for the user to invoke separately. It never reimplements the capabilities
it routes to.

## Invocation and safety boundary

Run only after an explicit `$ask-light` request. Do not run a recommended Skill,
call a Skill, launch a sub-agent, install a package, edit a project, or create
workflow state. Do not silently chain another user-invoked Skill. If a next
step is needed, print the host-appropriate invocation and stop.

The deterministic scanner in [ask-light.ps1](scripts/ask-light.ps1) is an
optional read-only aid for hosts that can run PowerShell. Use `$ask-light next`
for one next Skill, or `$ask-light workflow` for one bounded recipe. It scans
metadata and availability and prints a recommendation; it does not execute the
recommendation. On hosts that cannot run the script, follow this same contract
manually.

## Required input context

`ask-light` must understand current intent, project context, existing
artifacts, available first-party Skills, current project stage, specialized
workflow, and host capabilities before routing. Collect what is known; do not
invent missing facts. Use the fields in
[discovery-contract.md](references/discovery-contract.md):

- **Goal** - the user-visible outcome or question;
- **Artifacts** - relevant paths, extensions, manifests, notes, images,
  presentations, data, or review records;
- **Blockers** - errors, missing evidence, unavailable access, or a waiting
  decision;
- **Project type** - software, manuscript, Skill-development, research,
  knowledge-base, data-analysis, or generic;
- **Task kind** - discovery, specification, implementation, debugging, review,
  ingestion, initialization, research, or another explicit kind;
- **Availability** - host, readable paths, installed package revisions, and
  capabilities that are actually visible now;
- **Invocation control** - whether the user requires explicit-only, permits a
  model-callable Skill, or accepts either. Preserve the Skill's declared
  `allow_implicit_invocation` policy.

If Goal or task kind is genuinely unknown, ask one concise question and return
`NEED-INPUT`; do not guess from a Skill name. If no usable Skill remains,
return `BLOCKED` with installation or readability guidance.

## Discovery protocol

1. **Enumerate source roots.** Inspect the active project-level Skills, global
   host Skills, first-party collection packages, direct upstream packages,
   modified third-party packages, and every other readable installed Skill root
   exposed by the host. Keep the source category and resolved path on every
   record.
2. **Read metadata first.** For each candidate, read only the `SKILL.md`
   frontmatter and, when present, `agents/openai.yaml`. Capture name,
   description, display name, short description, default prompt,
   `allow_implicit_invocation`, readability, and any declared installation
   source. Do not load Skill bodies or references during this pass.
3. **Keep duplicate identities.** A name is not an identity. Preserve every
   candidate as `source-category + resolved package path + normalized name` and
   group same-name candidates for comparison. Mark malformed, missing, or
   unreadable metadata as a capability gap rather than treating it as a valid
   recommendation.
4. **Score and shortlist.** Rank only readable candidates with complete
   metadata against all supplied context fields. Relevance comes from the
   goal, artifacts, blockers, project type, and task kind; then apply
   availability and invocation-control compatibility. Filter candidates that
   the active host cannot read or invoke; never recommend an unavailable host
   package. Use source category and
   stable path only as deterministic tie-breakers. Shortlist the best few
   candidates; the default limit is three.
5. **Read narrowly.** Load Skill bodies and linked references only for the
   shortlist (or for a tied pair). Record the body/reference reads. Never read
   every Skill body merely because the catalog is large. If a shortlisted body
   or linked reference cannot be read, mark that candidate ineligible, report
   the exact recovery gap, and continue only with a successfully read
   candidate; if none remains, return `BLOCKED`.
6. **Return one result.** In `next` mode, recommend one best candidate with source, reason,
   confidence, and a host-appropriate invocation. Show one alternative only
   when two distinct candidates remain materially tied after the narrow read
   and represent materially different next actions; equivalent duplicate
   packages do not justify an alternative;
   otherwise omit `Alternative` entirely. Include skipped candidates and
   metadata/readability gaps when they affect confidence.

## Typical routing (Light workflow)

`ask-light` routes; it does not reimplement. After the metadata-first discovery
and availability checks, apply this typical map and the project's actual stage:

```text
vague idea                                    → clarify
existing project + unclear requirements       → project-clarify
large / foggy / multi-session project         → decision-map
missing external fact                         → research
need experiment to decide                     → prototype
information held by another person            → to-questionnaire
SPEC exists (needs slicing)                   → project-tickets
ticket is ready (and unblocked)               → implement
hard bug / regression / performance issue     → diagnosing-bugs
implementation complete (needs acceptance)    → project-review (via review-loop)
ready to publish / release                    → release-workflow
previous explanation did not land             → wait-what
```

Specialized workflows (`manuscript-ops`, `kb-init`, `learn-anything`,
`kanban-worker`) and reusable capabilities (`socratic`, `agent-config`,
`generic-review`, `code-review`, `tdd`, `handoff`, `wizard`, `teach`,
`writing-for-agents`, `resolving-merge-conflicts`) remain independent. Route to
them when their entry condition is the best fit; do not force them through
`project-init → project-clarify → ...`.

## Explicit workflow mode

`$ask-light workflow` is a recipe recommendation, not an orchestration engine.
It selects one documented recipe only when `goal`, `projectType`, `taskKind`,
artifacts, blockers, availability, and invocation control provide a reliable
match. It returns each step's Skill, source category/path, actual invocation
type, expected input/output, handoff artifact, stop condition, optional flag,
and missing dependency. It never invokes, installs, edits, creates a permanent
state machine, or silently chains user-invoked Skills.

The validated recipe set covers software feature, bug diagnosis, manuscript
project, source-to-Skill, new project initialization, final review, and private
third-party dependency gaps. When no reliable recipe exists, return
`NEED-INPUT`; when a required Skill is not visible/readable, return `BLOCKED`
with an accurate availability gap. A private `skills-3rdParty` package must not
be described as available when its root is absent.

## Source and host rules

Use the host's actual Skill roots and invocation syntax. For Codex, an explicit
invocation is normally `$<name>`; if the host does not advertise that syntax,
say "select `<name>` in the host Skill picker" and include the declared default
prompt as text. Never invent an installer command. For a missing or unreadable
candidate, cite its declared upstream/repository source when available and
give a manual-install fallback: restore a readable package containing
`SKILL.md`, refresh the host, and re-run `$ask-light`.

Source category is evidence, not a license to prefer a poor fit. Project-local
and global packages may win a final tie because they are host-specific;
first-party, modified third-party, direct upstream, and other readable
packages remain eligible and visible. A duplicate name never causes a second
invocation or an automatic merge.

## Result contract

Return a compact record with these fields:

```text
Mode: next | workflow
Status: RECOMMEND | NEED-INPUT | BLOCKED
Skill: <one name, or none>
Source: <category and resolved package path>
Reason: <context-specific evidence, not a generic description>
Invocation: <host-specific command or picker action>
Confidence: high | medium | low
Alternative: <at most one, only for a material tie>
Gaps: <missing/unreadable metadata and actionable guidance>
Reads: metadata=<count>; bodies=<count>; references=<count>
Execution: recommendation only; nothing was invoked or installed
```

Workflow mode additionally returns `workflow`, `entryCondition`, `steps`,
`stoppingBoundary`, and `finalAuthority`. The final verdict for a recipe that
reaches acceptance remains owned by `review-loop`; `ask-light` only reports the
recipe and stops. Each returned step declares `expectedInput`,
`expectedOutput`, `handoffArtifact`, `stopCondition`, and
`missingDependency` so the handoff remains inspectable. The scanner is a
recommendation-only aid: nothing was invoked, installed, or orchestrated.

The result must not claim runtime behavior from metadata alone. State when a
candidate's body/reference was not readable or when host availability could not
be verified.

## Verification

Run the package contract and behavior tests. They exercise fresh disposable
catalogs, all supported source categories, duplicate names, large catalogs with
shortlist-bounded body reads, unavailable metadata, context-based ranking,
workflow recipes, missing third-party dependencies, explicit-only
`learn-anything`, genuine ambiguity, installation guidance, and the
no-execution boundary. These are protocol tests rather than proof that a
particular external host exposes a given installation path.
