# LightDevCoder/skills v0.1.6 Release Receipt

[中文收据](RELEASE_RECEIPT.zh-CN.md)

Status: `RELEASED` — tag published, post-release verification recorded on main.

## Identity

| Field | Value |
| --- | --- |
| Repository | `LightDevCoder/skills` (public) |
| Release | `v0.1.6` |
| Release commit | `41b6e7169a1c68bb017f9ff6c464b220185b02ff` |
| Release tag | `v0.1.6` |
| Release URL | https://github.com/LightDevCoder/skills/releases/tag/v0.1.6 |
| Scope | Add `kb-init` as the ninth admitted first-party Skill and rename `light-kanban-worker` → `kanban-worker`; docs/tests/evidence synchronized for the nine-package collection |

## What changed

- `kb-init` (the formal knowledge-base initialization package) replaces the
  earlier unreleased draft: expanded core principles, decision provenance, open-decision
  surfacing, depth-before-settlement, readiness check, human navigation,
  research contract, connection setup/validation, and backup/recovery
  semantics.
- `kb-init` remains user-invoked only: `disable-model-invocation: true` and
  `allow_implicit_invocation: false`.
- `light-kanban-worker` was renamed to `kanban-worker`; package, metadata,
  tests, guides, catalog, README, and installation surfaces use the new name.
- README, catalog, installation guide, maintenance baseline, changelog, and
  bilingual guides now describe the v0.1.6 nine-package release.

## Pre-release gate

| Gate | Status |
| --- | --- |
| `kb-init` contract tests | PASS |
| Collection tests | PASS |
| Full collection discovery/contract suite | PASS |
| Independent `review-loop agent-skill` acceptance | PASS |
| Docs synchronized | PASS |
| Changelog prepared | PASS |

## Post-release verification

| Check | Record |
| --- | --- |
| Published tag identity and release commit | `v0.1.6` → `41b6e7169a1c68bb017f9ff6c464b220185b02ff` |
| Fresh install from `LightDevCoder/skills#v0.1.6` | PASS — [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md) |
| Host discovery | PASS — [DISCOVERY_VERIFICATION.md](DISCOVERY_VERIFICATION.md) |
| Release CI (`collection-quality`) | PASS — run `32230990952` on commit `41b6e71` |
| GitHub Release | https://github.com/LightDevCoder/skills/releases/tag/v0.1.6 |
