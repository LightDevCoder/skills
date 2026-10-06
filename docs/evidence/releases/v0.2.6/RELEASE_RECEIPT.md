# LightDevCoder/skills v0.2.6 Release Receipt

[中文收据](RELEASE_RECEIPT.zh-CN.md) · [Release Manifest](RELEASE_MANIFEST.md) · [Release Notes](RELEASE_NOTES.md)

Status: `VERIFIED` — Published with exact-commit CI, an annotated tag, two fresh whole-collection installs, and a public GitHub Release.

## Identity

| Field | Value |
| --- | --- |
| **Repository** | `LightDevCoder/skills` (public) |
| **Release** | `v0.2.6` |
| **Release Tag** | `v0.2.6` |
| **Annotated Tag Object** | `33dfd1acbce07f2908c1662c5c527fcc6fc6f0d1` |
| **Tag Target Commit** | `38015048f69f988eb2fc57dca66e65c252c2b4e4` |
| **Release URL** | https://github.com/LightDevCoder/skills/releases/tag/v0.2.6 |
| **Publication Timestamp** | `2026-10-05T11:01:46Z` |
| **Scope** | Travel handbook UI; visible daily routes and group selection; undated initialization; consistent sign-in and secondary surfaces; optional server-side AI; mouse date-strip interaction; credential, draft and retry guards. |
| **Collection Package Count** | 36 admitted packages |
| **Policy Status** | `PROVISIONAL` |
| **Tag Immutability** | Protected annotated tag; no update or deletion bypass |

## Verification Checklist

| Gate | Status | Evidence |
| --- | --- | --- |
| **Independent Source Acceptance** | `PASS` | Separate Standards/Spec and a fresh whole-package Evaluator; Core PASS on `d0a4b0700cc645aa9ca45bff0106a2c7badb52de`, `agent-skill`, owner-authorized round 4/4, `FULL` independence, no exception or open blocker. The candidate adds documentation only; the frozen implementation is byte-identical. |
| **Local Test Suite** | `PASS` | 528 pytest tests, 156 unittest tests, 80 template tests, 4 generator tests, off/on/undated builds, compilation and documentation checks |
| **GitHub Actions CI (`collection-quality`)** | `PASS` | [Run 37299427425](https://github.com/LightDevCoder/skills/actions/runs/37299427425) succeeded on exact candidate commit `38015048f69f988eb2fc57dca66e65c252c2b4e4` |
| **Tag Object & Resolution** | `PASS` | Remote annotated object `33dfd1acbce07f2908c1662c5c527fcc6fc6f0d1` peels to the exact candidate commit |
| **Pinned Fresh Install** | `PASS` | `npx --yes skills add LightDevCoder/skills#v0.2.6 --yes --copy --agent '*'` in a disposable directory: 36/36 packages, 385/385 package files byte-identical to the tag |
| **Generic Latest Fresh Install** | `PASS` | `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'` in a separate disposable directory: 36/36 packages, 385/385 package files byte-identical to the candidate commit |
| **Single-Skill Installation** | `PASS` | Separate fresh project directories select `--skill light-travelpage` and `--skill project-retro` from `#v0.2.6`, using `--yes --copy --agent '*'`: 75/75 and 8/8 files respectively match the tag byte for byte. |
| **Discovery Verification** | `PASS` | Skills CLI 1.7.0 found 36 Skills with `npx --yes skills list --agent codex`; installation targeted all 79 CLI-supported agents |
| **GitHub Release Publication** | `PASS` | [v0.2.6 GitHub Release](https://github.com/LightDevCoder/skills/releases/tag/v0.2.6) is published, neither draft nor prerelease |

The byte comparison covers every tracked file inside the 36 package directories. Repository-level assets outside packages are not installed by Skills CLI. The generic command follows the default branch and is reproducible only while `main` still resolves to this candidate; use the pinned tag for a stable snapshot. The sibling `../agent-config` MCP was used for contract validation and is not included in this release.

The English GitHub Release links to the independent Chinese notes at the immutable tag. The Chinese page links back to the English Release and notes. Runtime browser evidence is responsive desktop/390px testing; AI uses a synthetic local upstream. No hosted-provider, physical-device, native-map-app or live Host reload claim is made.
