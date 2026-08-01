# 安装与 Fresh-Install 验证

[English installation guide](INSTALLATION.md)

公开第一方集合当前稳定版本是 [v0.1.1](https://github.com/LightDevCoder/skills/releases/tag/v0.1.1)，commit 为 `c50f1ef403a5f0bfe02e75d1aeff2c237556db63`。已发布 tag 的 fresh-install 证据见[发布证据](evidence/releases/v0.1.1/RELEASE_RECEIPT.zh-CN.md)。`skills/<name>/` 内的包契约仍是行为权威；本页只规定安装和验证证据。

## Revision 语义

官方 Skills CLI 支持 GitHub source 的 `#ref` fragment，并将其作为 Git revision；没有 fragment 的仓库简写使用仓库默认 revision。因此未加 fragment 的 shorthand 不是永久 release pin。可查看 [官方 source parser](https://raw.githubusercontent.com/vercel-labs/skills/main/src/source-parser.ts) 和 [Git helper](https://raw.githubusercontent.com/vercel-labs/skills/main/src/git.ts)。

## 历史 v0.1.0 验证

当前稳定版本是已发布的 v0.1.0 snapshot，commit 为
`fb36fc2dad39ee94ad4aa25a5fee3c87c54f05f2`。以下无 fragment 命令作为历史命令保留；其 CLI、host、destination、validator 和证据限制见[历史安装记录](evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md#历史-v0.1.0-摘要)：

```text
npx skills add LightDevCoder/skills
npx skills add LightDevCoder/skills --skill review-loop
```

该历史记录是整理摘要，不是当前重跑；原始 receipt 未记录的
boundary/missing-dependency smoke 和重复安装行为会明确标为 `NOT RECORDED`。

这份历史验证不改变 CLI 的 revision 语义：无 fragment source 遵循仓库默认 revision，并不是永久固定到 v0.1.0。下面的已发布 v0.1.1 命令使用显式 tag。

目标 v0.1.1 的命令为：

```text
npx skills add LightDevCoder/skills#v0.1.1 --yes --copy --agent codex
npx skills add LightDevCoder/skills#v0.1.1 --skill review-loop --yes --copy --agent codex
```

第一条安装五个包，第二条选择同一 tag 下的完整单包。已验证的 CLI version、destination 类别、discovery 和 smoke result 见 [v0.1.1 安装记录](evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md)。

## 未发布的 `recap` 包

`recap` 已通过纯提示型快速通道在本分支准入，但 v0.1.1 不包含它。它的 fresh-copy 安装与 discovery 检查见[准入记录](evidence/admissions/recap/README.zh-CN.md)。不要把无 fragment 的默认分支命令写成稳定 release pin；只有新 tag 已创建、并在 fresh 环境中针对已发布仓库成功运行后，才能发布 pinned `recap` 安装命令。

## 安装范围

| 范围 | destination 规则 | 必需证据 |
| --- | --- | --- |
| Project-local | 当前仓库认可的项目级 Skills location。 | 精确 host/path、完整包或 installer 结果、refresh 和脱离 source checkout 的 discovery。 |
| User/global | Agent host 认可的用户级或全局 Skills location。 | 精确 host/path、完整包或 installer 结果、refresh 和脱离 source checkout 的 discovery。 |
| Per-Skill | 包含 `SKILL.md`、metadata 和全部引用资源的完整目录。 | 包名、固定 revision、destination、discovery 和 behavioral smoke。 |

这些类别不保证每个 host 都支持；以 host 文档和 fresh discovery 为准。

## 手动 fallback

installer 不可用时，在 target tag 发布后 checkout，并将完整包复制到 host 认可的 root：

```powershell
$sourceRoot = "<v0.1.1-release-checkout>"
$skillName = "<admitted-skill-name>"
$destinationRoot = "<host-recognized-skills-root>"
Copy-Item -LiteralPath "$sourceRoot/skills/$skillName" -Destination "$destinationRoot/$skillName" -Recurse
```

手动复制本身不是 fresh-install proof。记录必须包含 release commit/tag、host、destination、refresh/restart、discovery、success/boundary/invocation/missing-dependency smoke。包引用资源时不能只复制 `SKILL.md`。

## Direct upstream 与第三方

未修改的 Matt Pocock Skill 保持在 [mattpocock/skills](https://github.com/mattpocock/skills)。修改版只能进入私有 [skills-3rdParty](https://github.com/LightDevCoder/skills-3rdParty)，不属于本公开第一方集合，并有独立的 pinned manifest 和 release evidence。

## 记录要求

每次验证保存 exact command、installer version、URL、commit/tag、host/scope/destination、脱离 source checkout 的 discovery、success/boundary/invocation/missing-dependency smoke、fallback 和 limitations。结构检查、source checkout scan 或未执行命令都不能写成 installation proof；collection discovery script 也不能替代 fresh host install。
