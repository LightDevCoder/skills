---
name: ask-light
description: Inspect the Skills available to the active Agent host and recommend the single most appropriate next Skill from the current goal, artifacts, blockers, project type, task kind, availability, and invocation control. Use only when the user explicitly invokes $ask-light; it reports a recommendation and never executes or orchestrates it.
---

# Ask Light

`ask-light` is a user-invoked, read-only router. It answers "which installed
Skill is the best next fit?" from the active host and project state. It does not
replace project discovery, specification, implementation, or final acceptance.
The recommendation is an output for the user to invoke separately.

## Invocation and safety boundary

Run only after an explicit `$ask-light` request. Do not run a recommended Skill,
call a Skill, launch a sub-agent, install a package, edit a project, or create
workflow state. Do not silently chain another user-invoked Skill. If a next
step is needed, print the host-appropriate invocation and stop.

The deterministic scanner in [ask-light.ps1](scripts/ask-light.ps1) is an
optional read-only aid for hosts that can run PowerShell. It scans metadata and
prints a recommendation; it does not execute the recommendation. On hosts that
cannot run the script, follow this same contract manually.

## Required input context

Collect what is known; do not invent missing facts. Use the fields in
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
6. **Return one result.** Recommend one best candidate with source, reason,
   confidence, and a host-appropriate invocation. Show one alternative only
   when two distinct candidates remain materially tied after the narrow read
   and represent materially different next actions; equivalent duplicate
   packages do not justify an alternative;
   otherwise omit `Alternative` entirely. Include skipped candidates and
   metadata/readability gaps when they affect confidence.

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

The result must not claim runtime behavior from metadata alone. State when a
candidate's body/reference was not readable or when host availability could not
be verified.

## Verification

Run the package contract and behavior tests. They exercise fresh disposable
catalogs, all supported source categories, duplicate names, large catalogs with
shortlist-bounded body reads, unavailable metadata, context-based ranking,
genuine ambiguity, installation guidance, and the no-execution boundary. These
are protocol tests rather than proof that a particular external host exposes a
given installation path.
