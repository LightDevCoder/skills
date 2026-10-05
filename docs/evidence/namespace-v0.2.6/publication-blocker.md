# Namespace candidate publication blocker

**Status:** BLOCKED under namespace SPEC Revision 2 D7. This is an observation record for the local name-migration candidate, not a release receipt.

The existing remote `v0.2.6` is a different published snapshot. Its title is **A clearer travel handbook, with optional AI**. It retains the previous `implement` name. It is not the Light Skill Names and Migration draft in this directory.

| Remote fact | Observed value |
| --- | --- |
| Repository | `LightDevCoder/skills` |
| Tag | `v0.2.6` (annotated) |
| Tag object SHA | `33dfd1acbce07f2908c1662c5c527fcc6fc6f0d1` |
| Peeled commit SHA | `38015048f69f988eb2fc57dca66e65c252c2b4e4` |
| Observed `origin/main` | `97adf5f319b8800b6635057434dcb4aeda2ddecd` |
| GitHub Release | [Existing v0.2.6 release](https://github.com/LightDevCoder/skills/releases/tag/v0.2.6) |
| `published_at` | `2026-10-05T11:01:46Z` (2026-10-05 19:01:46 Asia/Taipei) |
| Local implementation baseline | `7a98ed9574e6ffb69f533cdcbdf16a22633ef0e6` |
| Local verified release baseline | `v0.2.5` at `ecafc2f3da3ab25a62e7a31285658fac5a50b47f` |

These remote identities were supplied by the controller's publication preflight. The full `origin/main` identity was also resolved locally with `git rev-parse origin/main`. The checkout remains based on the namespace SPEC baseline; remote implementation changes have not been merged. Remote `main` contains additional travel/AI changes outside this fixed SPEC baseline. Pushing this old-baseline candidate would revert those remote changes; no push, merge, or rebase has been performed.

D7 prohibits overwriting or moving an existing published tag and prohibits choosing a different version without the decision owner's instruction. The namespace candidate therefore cannot be published as `v0.2.6`. No new tag, GitHub Release, or receipt is created for this candidate. Existing v0.2.5 history and the remote v0.2.6 release remain intact.

The requested **v0.2.6 — Skill Names and Migration** title is retained only in the [blocked English draft](release-draft/RELEASE_NOTES.md) and [中文草稿](release-draft/RELEASE_NOTES.zh-CN.md). Fixed `#v0.2.6` commands select the existing travel-handbook snapshot, not this name migration. New-name installation templates are BLOCKED and must not be executed as migration instructions.

中文：本地名称迁移候选尚未发布。远端 v0.2.6 已于 2026-10-05 正式发布，内容为旅行手册并保留旧名。v0.2.5 是本 checkout 的已验证发布基线，不是最新远端稳定版本。按 D7，本次不能覆盖既有标签或自行改号；需决策所有者处理版本冲突后，才可继续发布。
