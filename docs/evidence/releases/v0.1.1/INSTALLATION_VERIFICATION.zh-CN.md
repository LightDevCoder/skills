# v0.1.1 安装验证

[English record](INSTALLATION_VERIFICATION.md)

## 状态

只有公开 tag 能从 fresh destination 访问后才可更新为 verified。下列命令是 release target，不是 source-checkout scan 已经证明的事实。

| 字段 | 整个集合 | 单 Skill |
| --- | --- | --- |
| 命令 | `npx skills add LightDevCoder/skills#v0.1.1` | `npx skills add LightDevCoder/skills#v0.1.1 --skill review-loop` |
| CLI version | `NOT TESTED` | `NOT TESTED` |
| Release commit | `NOT TESTED` | `NOT TESTED` |
| Fresh destination | `NOT TESTED` | `NOT TESTED` |
| 脱离 source checkout 的 discovery | `NOT TESTED` | `NOT TESTED` |
| Success/boundary/missing-dependency smoke | `NOT TESTED` | `NOT TESTED` |
| 重复安装行为 | `NOT TESTED` | `NOT TESTED` |
| 限制 | 必须在执行后记录 host-specific destination/discovery。 | 同左。 |

执行时记录 CLI version 和 exact command，使用 disposable empty destination，让 discovery 阶段无法读取 source checkout；分别运行整仓和单包命令，刷新 host，捕获 discovery 和 smoke，再重复安装并记录 no-op/duplicate 行为。公开记录不得包含 token、用户名、绝对私人路径或敏感 host 信息。

## 历史 v0.1.0 摘要

本摘要根据 controller 的 T16 acceptance receipt 保留真实的 v0.1.0 安装证据；
不是当前重跑，也不提升当前 v0.1.1 candidate。

| 字段 | 整个集合 | 单 Skill |
| --- | --- | --- |
| CLI version | `1.5.20` | `1.5.20` |
| Host 选择 | `--agent codex` | `--agent codex` |
| 命令 | `npx skills add LightDevCoder/skills --yes --copy --agent codex` | `npx skills add LightDevCoder/skills --skill review-loop --yes --copy --agent codex` |
| 已发布 commit | `fb36fc2dad39ee94ad4aa25a5fee3c87c54f05f2` | 同左 |
| Fresh destination | disposable destination；不写绝对私人路径 | disposable destination；不写绝对私人路径 |
| Discovery / validator | 安装恰好五个准入包；全部通过 official validator | 只安装 `review-loop`，并通过 official validator |
| 资源完整性 | 完整包比较：mismatch 与 extra file 均为 0 | 完整包 validator 通过 |
| 成功 smoke | 记录中的安装和验证为 `PASS` | 记录中的安装和验证为 `PASS` |
| Boundary / missing-dependency smoke | 整理后的历史 receipt 未记录，`NOT RECORDED` | 整理后的历史 receipt 未记录，`NOT RECORDED` |
| 重复安装行为 | `NOT RECORDED` | `NOT RECORDED` |

无 fragment 命令只作为历史命令保留。官方 CLI 在没有 `#ref` 时遵循仓库
默认 revision；这不等于 shorthand 永久固定到 v0.1.0。
