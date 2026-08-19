# 安装与 Fresh-Install 验证

[English installation guide](INSTALLATION.md)

公开第一方集合当前稳定版本是 [v0.1.6](https://github.com/LightDevCoder/skills/releases/tag/v0.1.6)，发布自 commit `41b6e7169a1c68bb017f9ff6c464b220185b02ff`。`skills/<name>/` 内的包契约仍是行为权威；本页只规定安装和验证证据。

标准安装命令是通用 `latest` 形式：它跟随仓库默认 revision，因此每次
`npx skills add LightDevCoder/skills` 都安装默认分支上的当前集合。当前
默认分支包含九个已准入 Skill，并已随 v0.1.6 发布。下面的 v0.1.6 命令是针对
该 tag 的 fresh destination 验证结果，见
[v0.1.6 安装验证](evidence/releases/v0.1.6/INSTALLATION_VERIFICATION.zh-CN.md)。

## Revision 语义

官方 Skills CLI 支持 GitHub source 的 `#ref` fragment，并将其作为 Git revision；没有 fragment 的仓库简写使用仓库默认 revision。可查看 [官方 source parser](https://raw.githubusercontent.com/vercel-labs/skills/main/src/source-parser.ts) 和 [Git helper](https://raw.githubusercontent.com/vercel-labs/skills/main/src/git.ts)。

下面的通用 `latest` 命令不带 fragment，因此跟随仓库默认 revision：它安装当前
集合，是标准安装方式。pinned `#v0.1.6` 形式选择已发布的 tag，用于可复现
安装与 release 验证。两者都不是对未来默认 revision 的声明；对 fresh
destination 重新运行 discovery，以获取解析后的实际内容。

通用 `latest` 形式（跟随当前默认 revision）为：

```text
npx skills add LightDevCoder/skills --yes --copy --agent '*'
npx skills add LightDevCoder/skills --skill review-loop --yes --copy --agent '*'
```


## v0.1.6 release 命令

v0.1.6 release 命令针对已发布的 v0.1.6 tag 验证，在该 revision 安装九包集合：

```text
npx skills add LightDevCoder/skills#v0.1.6 --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.6 --skill kanban-worker --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.6 --skill kb-init --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.6 --skill review-loop --yes --copy --agent '*'
```

第一条安装九包集合，其余从同一已验证 revision 选择完整单包。
各形式均已针对 fresh destinations 验证，见
[v0.1.6 安装记录](evidence/releases/v0.1.6/INSTALLATION_VERIFICATION.zh-CN.md)。

`latest` 形式与 `#v0.1.6` 形式在 release 时刻解析为相同内容；只有 pinned
形式对未来默认 revision 的变化保持稳定。

## 改名说明

`light-kanban-worker` 在 v0.1.6 中改名为 `kanban-worker`。下面的 v0.1.4 与
v0.1.5 历史记录和命令仍使用旧名 `light-kanban-worker`；当前安装使用
`kanban-worker`。

## 历史 v0.1.5 验证

上一稳定版本是已发布的 v0.1.5 snapshot，commit 为
`a56aa9d98de0b941ee2282144bc7e756ef5e48bd`。它安装八包集合。其已验证的 pinned 形式为：

```text
npx skills add LightDevCoder/skills#v0.1.5 --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.5 --skill light-kanban-worker --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.5 --skill review-loop --yes --copy --agent '*'
```

验证见 [v0.1.5 安装记录](evidence/releases/v0.1.5/INSTALLATION_VERIFICATION.zh-CN.md)。

## 历史 v0.1.4 验证

上一稳定版本是已发布的 v0.1.4 snapshot，commit 为
`a9cc8aa029c926fc80f6ddc0022793f79dfd85bd`。它引入 `light-kanban-worker`，
形成八包集合。其 pinned 形式为：

```text
npx skills add LightDevCoder/skills#v0.1.4 --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.4 --skill light-kanban-worker --yes --copy --agent '*'
```

两种形式均以 CLI `1.5.22` 针对 fresh destinations 验证；见
[v0.1.4 安装记录](evidence/releases/v0.1.4/INSTALLATION_VERIFICATION.zh-CN.md)。

## 历史 v0.1.3 验证

上一稳定版本是已发布的 v0.1.3 snapshot，commit 为
`f8b573a48f7d53da74cfb8d94eb2ee7ca467d5c4`。它是测试工具链迁移 release，
七个包与 v0.1.2 相同，其包级安装由
[v0.1.2 安装验证](evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.zh-CN.md)
覆盖；其 pinned 形式为：

```text
npx skills add LightDevCoder/skills#v0.1.3 --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.3 --skill review-loop --yes --copy --agent '*'
```

## 历史 v0.1.2 验证

上一稳定版本是已发布的 v0.1.2 snapshot，commit 为
`8de5ec1a453b0e93f71dcda160e17ea7b42c3997`。其已验证命令：

```text
npx skills add LightDevCoder/skills#v0.1.2 --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.2 --skill review-loop --yes --copy --agent '*'
```

两种形式均以 CLI `1.5.22` 针对 fresh destinations 验证；见
[v0.1.2 安装记录](evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.zh-CN.md)。

## 历史 v0.1.1 验证

上一稳定版本是已发布的 v0.1.1 snapshot，commit 为
`c50f1ef403a5f0bfe02e75d1aeff2c237556db63`。其已验证命令使用显式 tag 和 codex
host 选择：

```text
npx skills add LightDevCoder/skills#v0.1.1 --yes --copy --agent codex
npx skills add LightDevCoder/skills#v0.1.1 --skill review-loop --yes --copy --agent codex
```

已验证的 CLI version、destination 类别、discovery 和 smoke result 见
[v0.1.1 安装记录](evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md)。

## 历史 v0.1.0 验证

历史稳定版本是已发布的 v0.1.0 snapshot，commit 为
`fb36fc2dad39ee94ad4aa25a5fee3c87c54f05f2`。以下无 fragment 命令作为历史命令保留；其 CLI、host、destination、validator 和证据限制见[历史安装记录](evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md#历史-v0.1.0-摘要)：

```text
npx skills add LightDevCoder/skills
npx skills add LightDevCoder/skills --skill review-loop
```

该历史记录是整理摘要，不是当前重跑；原始 receipt 未记录的
boundary/missing-dependency smoke 和重复安装行为会明确标为 `NOT RECORDED`。

这份历史验证不改变 CLI 的 revision 语义：无 fragment source 遵循仓库默认
revision，并不是永久 pin。上面的历史命令使用通用 `latest` 形式或显式
`#v0.1.5` tag。

## 准备的 `recap` 与 `language-learning` 包

`recap` 与 `language-learning` 是经纯提示型快速通道在 v0.1.2 中发布的第一方包。
其准入记录见 [evidence/admissions/recap/README.zh-CN.md](evidence/admissions/recap/README.zh-CN.md) 与
[evidence/admissions/language-learning/README.zh-CN.md](evidence/admissions/language-learning/README.zh-CN.md)。
它们的 fresh install 作为
[collection discovery 测试](../tests/test_collection_discovery.py)与
[v0.1.2 安装记录](evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.zh-CN.md)的一部分被演练。

## 安装范围

| 范围 | destination 规则 | 必需证据 |
| --- | --- | --- |
| Project-local | 当前仓库认可的项目级 Skills location。 | 精确 host/path、完整包或 installer 结果、refresh 和脱离 source checkout 的 discovery。 |
| User/global | Agent host 认可的用户级或全局 Skills location。 | 精确 host/path、完整包或 installer 结果、refresh 和脱离 source checkout 的 discovery。 |
| Per-Skill | 包含 `SKILL.md`、metadata 和全部引用资源的完整目录。 | 包名、固定 revision、destination、discovery 和 behavioral smoke。 |

这些类别不保证每个 host 都支持；以 host 文档和 fresh discovery 为准。

## 手动 fallback

installer 不可用时，在 target tag 发布后 checkout，并将完整包复制到 host 认可的 root：

```bash
source_root="<current-release-checkout>"
skill_name="<admitted-skill-name>"
destination_root="<host-recognized-skills-root>"
cp -R "$source_root/skills/$skill_name" "$destination_root/$skill_name"
```

手动复制本身不是 fresh-install proof。记录必须包含 release commit/tag、host、destination、refresh/restart、discovery、success/boundary/invocation/missing-dependency smoke。包引用资源时不能只复制 `SKILL.md`。

## Direct upstream 与第三方

未修改的 Matt Pocock Skill 保持在 [mattpocock/skills](https://github.com/mattpocock/skills)。修改版只能进入私有 [skills-3rdParty](https://github.com/LightDevCoder/skills-3rdParty)，不属于本公开第一方集合，并有独立的 pinned manifest 和 release evidence。

## 记录要求

每次验证保存 exact command、installer version、URL、commit/tag、host/scope/destination、脱离 source checkout 的 discovery、success/boundary/invocation/missing-dependency smoke、fallback 和 limitations。结构检查、source checkout scan 或未执行命令都不能写成 installation proof；collection discovery script 也不能替代 fresh host install。
