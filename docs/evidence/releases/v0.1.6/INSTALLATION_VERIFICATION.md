# v0.1.6 installation verification

[中文记录](INSTALLATION_VERIFICATION.zh-CN.md)

## Status

`PASS` for the tagged public repository using Skills CLI, verified against
fresh destinations for both the generic `latest` form and the pinned
`#v0.1.6` form. Host refresh is host-specific and was not claimed; CLI
discovery was run from each fresh destination without a source checkout.

| Field | Whole collection | Per-Skill (`kb-init`) |
| --- | --- | --- |
| Command | `npx skills add LightDevCoder/skills --yes --copy --agent '*'` (latest) and `npx skills add LightDevCoder/skills#v0.1.6 --yes --copy --agent '*'` (tag) | `npx skills add LightDevCoder/skills --skill kb-init --yes --copy --agent '*'` (latest) and `npx skills add LightDevCoder/skills#v0.1.6 --skill kb-init --yes --copy --agent '*'` (tag) |
| CLI version | `<cli-version>` | `<cli-version>` |
| Released commit | `<release-commit>` (`v0.1.6` tag) | same |
| Fresh destination | New empty temporary directory; found/installed 9 skills | New empty temporary directory; exactly 1 package (`kb-init`) |
| Install result | PASS | PASS |
| Discovery without source checkout | `npx --yes skills list` exit 0; `kb-init` listed; source checkout absent | `npx --yes skills list` exit 0; exactly `kb-init` listed; source checkout absent |
| Installed-package smoke | — | Installed `kb-init` files byte-identical to the tagged source and contract test OK |
| Repeat-install behavior | Same command exit 0; no-op overwrite | Same command exit 0; no-op overwrite |

Procedure and limitation details are recorded in the finalized receipt.
