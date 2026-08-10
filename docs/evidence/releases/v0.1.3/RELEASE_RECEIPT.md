# LightDevCoder/skills v0.1.3 Release Receipt

Status: `RELEASED` — tag, GitHub release, merged CI, and local cross-platform
verification. Toolchain migration release: PowerShell test suites ported to
Python; CI moved to ubuntu-latest; no governance wording changes.

## Identity

| Field | Value |
| --- | --- |
| Repository | `LightDevCoder/skills` (public) |
| Release | `v0.1.3` |
| Release commit | current main after this receipt |
| Release URL | https://github.com/LightDevCoder/skills/releases/tag/v0.1.3 |
| Scope | Test toolchain migration only: 21 PowerShell test files replaced by 18 Python suites (collection, header assets, quick start, ask-light, project-init, recap, language-learning, review-loop ×5 profiles) |

## What changed

- PowerShell test files (`tests/*.ps1`, `skills/<name>/tests/*.ps1`,
  `review-loop` protocol helpers) removed.
- Python ports preserve the assertion sets (collection discovery 1064+
  assertions incl. composed recap/language-learning suites; per-profile
  review-loop contract and behavior scenarios).
- `ask-light` scanner behavior suite still executes the real
  `scripts/ask-light.ps1` via `pwsh` and skips gracefully when pwsh is
  absent (CI ships pwsh and runs it).
- CI: `ubuntu-latest`, bash + python; retired-boundary and no-ps1-test
  checks included.
- Docs: only file-name and manual-fallback references updated; governance
  wording unchanged.

## Evidence

- [Test summary](TEST_SUMMARY.md)
- Historical releases remain at v0.1.1/v0.1.2 with their original evidence.
