# v0.1.2 安装验证

[English record](INSTALLATION_VERIFICATION.md)

## 状态

`NOT TESTED — GitHub release 创建后，对已发布的 v0.1.2 tag 与通用 `latest` 命令执行。`

本页将记录 v0.1.2 tag 与已发布通用 `latest` 安装命令的精确 CLI version、
fresh destinations、discovery 结果，以及 success、boundary、invocation、
missing-dependency smoke。

| 字段 | 整个集合 | 单 Skill |
| --- | --- | --- |
| 命令 | `npx skills add LightDevCoder/skills --yes --copy --agent '*'`（latest）与 `npx skills add LightDevCoder/skills#v0.1.2 --yes --copy --agent '*'`（tag） | `npx skills add LightDevCoder/skills --skill review-loop --yes --copy --agent '*'`（latest）与 `npx skills add LightDevCoder/skills#v0.1.2 --skill review-loop --yes --copy --agent '*'`（tag） |
| CLI version | `NOT TESTED` | `NOT TESTED` |
| 已发布 commit | `NOT TESTED — 创建 release tag 后填写` | 同左 |
| Fresh destination | 新建空临时项目 | 新建空临时项目 |
| 安装结果 | `NOT TESTED` | `NOT TESTED` |
| 脱离 source checkout 的 discovery | `NOT TESTED` | `NOT TESTED` |
| Success/boundary/missing-dependency smoke | `NOT TESTED` | `NOT TESTED` |
| 重复安装行为 | `NOT TESTED` | `NOT TESTED` |

## 过程

1. 记录 `npx skills --version` 与 exact command。
2. 使用 disposable empty destination，并让 discovery 阶段无法读取 source checkout。
3. 对通用 `latest` 形式和 pinned `#v0.1.2` 形式分别运行整仓与单包命令。
4. 刷新 Agent host、捕获 discovery，再对已安装包运行一次 success 与一次 boundary/missing-dependency smoke。
5. 重复同一命令，记录是 no-op 还是报告重复。

公开记录只写 destination 类别，不包含 token、用户名、绝对私人路径或敏感
host 信息。

## 历史 v0.1.1 摘要

已验证的 v0.1.1 安装记录仍对五包 release 具有权威性：
[v0.1.1 INSTALLATION_VERIFICATION.zh-CN.md](../v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md)。
该记录包含历史 v0.1.0 摘要，并保留 CLI revision 语义：无 fragment source
遵循仓库默认 revision，v0.1.1 tag 固定到 `c50f1ef`。
