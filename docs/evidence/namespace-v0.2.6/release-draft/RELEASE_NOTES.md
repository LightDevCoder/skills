# v0.2.6 — Skill Names and Migration

[中文发布说明](RELEASE_NOTES.zh-CN.md) · [Release Manifest](RELEASE_MANIFEST.md)

**Candidate status: BLOCKED.** The local namespace candidate is unpublished. Remote v0.2.6 is occupied by a travel-handbook release; v0.2.5 is this checkout’s verified release baseline. This title is the requested draft title, not a description of that published Release. D7 prohibits overwriting the tag or selecting a new version; see the [publication blocker](../publication-blocker.md).

This candidate adds `light-` names to twelve Skills so their source is clear in global installations. Internal references, `ask-light` routes, and UI labels use the new names. The collection remains at 36 Skills.

## What changed

| Previous Light name | New name |
| --- | --- |
| `implement` | `light-implement` |
| `code-review` | `light-code-review` |
| `research` | `light-research` |
| `prototype` | `light-prototype` |
| `tdd` | `light-tdd` |
| `diagnosing-bugs` | `light-diagnosing-bugs` |
| `wizard` | `light-wizard` |
| `handoff` | `light-handoff` |
| `teach` | `light-teach` |
| `to-questionnaire` | `light-to-questionnaire` |
| `wait-what` | `light-wait-what` |
| `writing-for-agents` | `light-writing-for-agents` |

The other 24 names, package categories, responsibilities, and invocation permissions stay unchanged. `ask-light` and `light-travelpage` keep their names. Software work uses `light-implement` and, when appropriate, `light-tdd`; `review-loop` composes `light-code-review`. `project-review` still owns final acceptance. Missing Light dependencies remain explicit gaps.

## Upgrade notes

Update old Light `--skill` arguments and explicit invocations, such as `$implement` to `$light-implement`. Check project prompts, capability declarations, automations, and source symlinks. Confirm the actual source or link target before handling an old-name package, and save its contents or link target. Reinstalling does not prove the old names were removed. No old-name aliases are shipped, and real global installations are not migrated automatically.

For recovery, restore the saved Light copies or symlink targets, restore related references, and reinstall `#v0.2.5` if needed; first check that an old-name restoration will not overwrite another source. See the [complete migration guide](../../../MIGRATION-v0.2.6.md).

## Other changes

Changes already included since the v0.2.5 tag are part of this candidate:

- `light-travelpage` builds authenticated first-page PNG previews for PDF tickets and shows them in the shared dialog with zoom and an original-PDF link. Google and Apple navigation prefer readable local names and addresses over coordinate-only searches. Mobile interaction, map fallback, and generated PDF build fixtures have additional coverage.
- Stable-release checks derive their expected release from the catalog, keeping them aligned with the declared stable version.
- v0.2.5 publication attestation and bilingual documentation were completed after its tag. Its English release page and separate Chinese page have reciprocal links; historical tag snapshots remain unchanged.

## Installation

**BLOCKED templates; do not execute.** The existing `#v0.2.6` selects the travel-handbook snapshot, which does not contain these new names. These commands cannot install the namespace candidate.

```bash
# BLOCKED — do not execute: npx skills add LightDevCoder/skills#v0.2.6
# BLOCKED — do not execute: npx skills add LightDevCoder/skills#v0.2.6 --skill light-implement
# BLOCKED — do not execute: npx skills add LightDevCoder/skills#v0.2.6 --global --agent codex
```

The unqualified command follows actual `main`, including admitted changes on that branch; it does not automatically select a stable release:

```bash
npx skills add LightDevCoder/skills
```

## Verification

The local implementation passes 521 pytest tests, 158 unittest tests, compilation and public documentation checks. Two independent review axes converged without outstanding findings. Fresh local CLI installations retain 36 complete Light packages across both installation orders and modes. These are local test, review and installation observations.

Actual Codex discovery and invocation remain unverified because the runtime failed before Skill reads. Candidate acceptance and publication are blocked. No exact-candidate remote CI or fixed-version namespace installation is claimed; existing v0.2.6 is a different release. See the [candidate evidence](../producer-evidence.md) and [review convergence](../review-summary.md).
