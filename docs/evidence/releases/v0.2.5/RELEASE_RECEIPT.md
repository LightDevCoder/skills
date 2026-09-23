# LightDevCoder/skills v0.2.5 Release Receipt

[中文收据](RELEASE_RECEIPT.zh-CN.md) · [Release Manifest](RELEASE_MANIFEST.md) · [Release Notes](RELEASE_NOTES.md)

Status: `VERIFIED` — Published with exact-commit CI, an annotated tag, two fresh whole-collection installs, and a public GitHub Release.

## Identity

| Field | Value |
| --- | --- |
| **Repository** | `LightDevCoder/skills` (public) |
| **Release** | `v0.2.5` |
| **Release Tag** | `v0.2.5` |
| **Annotated Tag Object** | `576e3bbdf2002b10390f48646184305050ed951e` |
| **Tag Target Commit** | `ecafc2f3da3ab25a62e7a31285658fac5a50b47f` |
| **Release URL** | https://github.com/LightDevCoder/skills/releases/tag/v0.2.5 |
| **Publication Timestamp** | `2026-09-23T17:51:28Z` |
| **Scope** | Reliable Host/Profile and workflow routing; shared ticket numbering; manuscript bootstrap and dependency contracts; review findings; travel todo validation; complete CI and remote release gates. |
| **Collection Package Count** | 36 admitted packages |
| **Policy Status** | `PROVISIONAL` |
| **Tag Immutability** | Protected annotated tag; no update or deletion bypass |

## Verification Checklist

| Gate | Status | Evidence |
| --- | --- | --- |
| **Local Test Suite** | `PASS` | 515 pytest tests, 156 unittest tests, 35 Node tests, generated-trip validation/build, sibling MCP contract integration, documentation check |
| **GitHub Actions CI (`collection-quality`)** | `PASS` | [Run 35858468222](https://github.com/LightDevCoder/skills/actions/runs/35858468222) succeeded on exact candidate commit `ecafc2f3da3ab25a62e7a31285658fac5a50b47f` |
| **Tag Object & Resolution** | `PASS` | Remote annotated object `576e3bbdf2002b10390f48646184305050ed951e` peels to the exact candidate commit |
| **Pinned Fresh Install** | `PASS` | `npx --yes skills add LightDevCoder/skills#v0.2.5 --yes --copy --agent '*'` in a disposable directory: 36/36 packages, 367/367 package files byte-identical to the tag |
| **Generic Latest Fresh Install** | `PASS` | `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'` in a separate disposable directory: 36/36 packages, 367/367 package files byte-identical to the candidate commit |
| **Discovery Verification** | `PASS` | Skills CLI 1.7.0 found 36 Skills with `npx --yes skills list --agent codex`; installation targeted all 79 CLI-supported agents |
| **GitHub Release Publication** | `PASS` | [v0.2.5 GitHub Release](https://github.com/LightDevCoder/skills/releases/tag/v0.2.5) is published, neither draft nor prerelease |

The byte comparison covers every tracked file inside the 36 package directories. Repository-level assets outside packages are not installed by Skills CLI. The generic command follows the default branch and is reproducible only while `main` still resolves to this candidate; use the pinned tag for a stable snapshot. The sibling `../agent-config` MCP was used for contract validation and is not included in this release.
