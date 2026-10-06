# v0.2.7 — Skill Names and Migration

[中文发布说明](RELEASE_NOTES.zh-CN.md) · [Release Manifest](RELEASE_MANIFEST.md)

Twelve Skills now use `light-` names so their source is clear in global installations. Internal references, `ask-light` routes, and UI labels use the new names. The collection remains at 36 Skills.

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

The other 24 names, package categories, responsibilities, and invocation permissions stay unchanged. `ask-light` and `light-travelpage` keep their names. Software work uses `light-implement` and, when appropriate, `light-tdd`; `review-loop` composes `light-code-review`. `project-review` still owns final acceptance. Missing Light dependencies remain explicit gaps. Changes relative to v0.2.6 are the name migration and its supporting references, routing, documentation, attribution, and checks. The released travel handbook and optional AI remain intact.

## Upgrade notes

Update old Light `--skill` arguments and explicit invocations, such as `$implement` to `$light-implement`. Check project prompts, capability declarations, automations, and source symlinks. Confirm the actual source or link target before handling an old-name package, and save its contents or link target. Reinstalling does not prove the old names were removed. No old-name aliases are shipped, and real global installations are not migrated automatically.

For recovery, restore the saved Light copies or symlink targets, restore related references, and reinstall `#v0.2.6` if needed; first check that an old-name restoration will not overwrite another source. See the [complete migration guide](https://github.com/LightDevCoder/skills/blob/main/docs/MIGRATION-v0.2.7.md).

## Installation

Installation from the actual v0.2.7 source passed in fresh environments. Select the fixed tag for a reproducible install:

```bash
npx skills add LightDevCoder/skills#v0.2.7
npx skills add LightDevCoder/skills#v0.2.7 --skill light-implement
npx skills add LightDevCoder/skills#v0.2.7 --global --agent codex
```

The unqualified command follows actual `main`, including admitted changes on that branch; it does not automatically select a stable release:

```bash
npx skills add LightDevCoder/skills
```

## Verification

The candidate source passes 543 pytest tests, 167 unittest tests, compilation and documentation checks. Local installation tests cover both source orders and modes, with all intended package files preserved. Actual Codex 0.160.1 shows all twelve Light source labels and resolves the explicit Light entry and its dependencies during a successful bounded task. The native selector uses a disclosed temporary transport adapter that preserves the Host Skill responses.

Independent source acceptance passed. Exact-candidate CI and the protected annotated tag identity are verified. Actual released-source installation passed in a fresh hosted Linux user: Codex and Claude Code pinned/default whole targets each preserve 36 packages and 386 files against their exact source revisions. Native Codex global installation and single installs of `light-implement`, `light-tdd` and `light-research` also passed, without overriding HOME/CODEX_HOME. The first verifier run checked the wrong global directory; the corrected rerun passed with the tag and package payload unchanged.

The manifest preserves the pre-publication tag snapshot; publication facts are attested in the post-release receipt on main. See the [source and runtime evidence](https://github.com/LightDevCoder/skills/blob/main/docs/evidence/namespace-v0.2.7/producer-evidence.md).
