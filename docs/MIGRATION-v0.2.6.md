# Light Skills v0.2.6 name migration

[简体中文](MIGRATION-v0.2.6.zh-CN.md) · [Candidate notes](evidence/namespace-v0.2.6/release-draft/RELEASE_NOTES.md)

**Status:** The local namespace candidate is unpublished; remote v0.2.6 is occupied by a travel-handbook release. v0.2.5 is this checkout’s verified release baseline, not the latest remote stable release. New-name templates are **BLOCKED; do not execute**. D7 prohibits overwriting the tag or selecting a new version. See the [publication blocker](evidence/namespace-v0.2.6/publication-blocker.md).

Twelve Light packages gain `light-` names. The other 24 names, seven categories, 36-package total, responsibilities, and invocation permissions remain unchanged. There are no installable aliases or wrappers for old names. `ask-light` and `light-travelpage` keep their names. Installed paths become `<skills-root>/<new-name>/`; source paths remain `skills/<category>/<new-name>/`.

| Previous Light name | New name | Category | Invocation |
| --- | --- | --- | --- |
| `implement` | `light-implement` | project | user-invoked |
| `code-review` | `light-code-review` | review | model-invoked |
| `research` | `light-research` | thinking | model-invoked |
| `prototype` | `light-prototype` | engineering | model-invoked |
| `tdd` | `light-tdd` | engineering | model-invoked |
| `diagnosing-bugs` | `light-diagnosing-bugs` | engineering | model-invoked |
| `wizard` | `light-wizard` | productivity | model-invoked |
| `handoff` | `light-handoff` | productivity | user-invoked |
| `teach` | `light-teach` | knowledge | user-invoked |
| `to-questionnaire` | `light-to-questionnaire` | thinking | user-invoked |
| `wait-what` | `light-wait-what` | productivity | user-invoked |
| `writing-for-agents` | `light-writing-for-agents` | writing | model-invoked |

## Before upgrading

Record the target Host and its recognized Skill root. For each old-name package, record its source repository/revision, actual path, and installation mode. For a symlink, inspect its link target and the target's content; for a copy, inspect `SKILL.md`, `ATTRIBUTION.md`, and installer source metadata. Compare those facts with the installed source. A directory name alone does not establish ownership. Back up confirmed Light copies or record symlink targets before removing anything.

Inventory old names in project prompts, `AGENTS.md`, availability declarations, scripts, scheduled automations, and installer `--skill` arguments. Update capability references only. Business fields such as project type `research`, ticket type `research` or `prototype`, research output paths, and ordinary handoff text retain their meanings. Existing project state is not rewritten automatically.

## Upgrade steps

1. After the decision owner resolves the version conflict and the namespace release passes its gates, install its confirmed fixed tag into the intended Host scope. Choose the Skills and Host you actually use; the commands below do not force copies or populate every Host.
2. Remove or archive an old-name installation only after confirming it belongs to Light and saving its contents or link target. Reinstallation may leave the old directory present. Leave packages from another source intact.
3. Update old Light `--skill` arguments and explicit invocations using the complete table. For example, `$implement` becomes `$light-implement`. Update project availability declarations, prompts, automations, and source links deliberately; each write requires the authority for that destination.
4. For symlinks, verify the canonical source was upgraded and links resolve to the new directories. For copies, verify each Host's complete package content. Refresh discovery according to the Host's own interface.
5. Inspect the Host selector or discovery listing. Record all 36 Light package identities when installing the whole collection, the 12 new labels (`Light · …`), their resolved paths/source, and the selected invocation. `ask-light` must recommend `light-implement` for a ready ticket and resolve software review through `light-code-review`; a missing Light dependency must remain unavailable rather than resolve to an old same-name capability.

```bash
# BLOCKED — do not execute: npx skills add LightDevCoder/skills#v0.2.6
# BLOCKED — do not execute: npx skills add LightDevCoder/skills#v0.2.6 --skill light-implement
# BLOCKED — do not execute: npx skills add LightDevCoder/skills#v0.2.6 --global --agent codex
```

An unqualified `npx skills add LightDevCoder/skills` follows actual default branch `main`; it does not automatically follow the latest stable tag. Candidate names are unavailable from v0.2.5. A static file scan verifies structure; it does not establish Host invocation behavior. Discovery and explicit source selection do not lock all model-invoked calls to one workflow.

## Recovery

If migration fails, preserve the diagnostic and stop using the new entry until its dependency is resolved. Restore the saved Light package copies or symlink targets, restore the related project/automation references, and reinstall the fixed `#v0.2.5` snapshot if needed. Before restoring any old-name directory, confirm it will not replace a package from another source. Refresh the Host and verify the restored source and entry. Keep historical tags and evidence unchanged.

This repository task prepares the candidate and isolated evidence only. It does not modify the real user's global Skills, Host configuration, other projects, or automations. Those writes require a separately authorized migration step. Record actual discovery, installation mode, source, and recovery result for that step; do not infer it from a repository rename.
