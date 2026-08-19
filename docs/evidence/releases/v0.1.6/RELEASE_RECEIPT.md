# LightDevCoder/skills v0.1.6 Release Receipt

[中文收据](RELEASE_RECEIPT.zh-CN.md)

Status: `RELEASED` — tag published, post-release verification recorded on main.

## Identity

| Field | Value |
| --- | --- |
| Repository | `LightDevCoder/skills` (public) |
| Release | `v0.1.6` |
| Release commit | `<release-commit>` |
| Release tag | `v0.1.6` |
| Release URL | https://github.com/LightDevCoder/skills/releases/tag/v0.1.6 |
| Scope | Publish `kb-init` v1.0.0 as the ninth admitted first-party Skill; user-invoked only; docs/tests/evidence synchronized for the nine-package collection |

## What changed

- `kb-init` v1.0.0 replaces the earlier unreleased draft with the formal
  package: expanded core principles, decision provenance, open-decision
  surfacing, depth-before-settlement, readiness check, human navigation,
  research contract, connection setup/validation, and backup/recovery
  semantics.
- `kb-init` remains user-invoked only: `disable-model-invocation: true` and
  `allow_implicit_invocation: false`.
- README, catalog, installation guide, maintenance baseline, changelog, and
  bilingual guides now describe the v0.1.6 nine-package release.

## Pre-release gate

| Gate | Status |
| --- | --- |
| `kb-init` contract tests | PASS |
| Collection tests | PASS |
| Full collection discovery/contract suite | PASS |
| Independent `review-loop agent-skill` acceptance (v1.0.0) | PASS |
| Docs synchronized | PASS |
| Changelog prepared | PASS |

## Post-release verification

| Check | Record |
| --- | --- |
| Published tag identity and release commit | `v0.1.6` → `<release-commit>` |
| Fresh install from `LightDevCoder/skills#v0.1.6` | PASS — [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md) |
| Host discovery | PASS — [DISCOVERY_VERIFICATION.md](DISCOVERY_VERIFICATION.md) |
| Release CI (`collection-quality`) | PASS |
| GitHub Release | https://github.com/LightDevCoder/skills/releases/tag/v0.1.6 |
