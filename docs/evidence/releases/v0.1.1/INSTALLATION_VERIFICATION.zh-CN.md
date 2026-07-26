# v0.1.1 安装验证

[English record](INSTALLATION_VERIFICATION.md)

## 状态

使用 Skills CLI `1.5.20` 从公开 tag 安装后为 `PASS`。host refresh 仍是
host-specific 行为，因此不宣称已经完成；但每个 fresh destination 都在没有
source checkout 的条件下执行了 CLI discovery。

| 字段 | 整个集合 | 单 Skill |
| --- | --- | --- |
| 命令 | `npx skills add LightDevCoder/skills#v0.1.1 --yes --copy --agent codex` | `npx skills add LightDevCoder/skills#v0.1.1 --skill review-loop --yes --copy --agent codex` |
| CLI version | `1.5.20` | `1.5.20` |
| Release commit | `c50f1ef403a5f0bfe02e75d1aeff2c237556db63` | 同左 |
| Fresh destination | 新建空临时项目；在 `.agents/skills/` 下恰好安装 5 个包 | 新建空临时项目；在 `.agents/skills/` 下恰好安装 1 个包 |
| 安装结果 | `PASS`，exit code 0 | `PASS`，exit code 0 |
| 脱离 source checkout 的 discovery | `npx --yes skills list` exit 0；列出 5 个包；不存在 source checkout | `npx --yes skills list` exit 0；列出 1 个包；不存在 source checkout |
| Success/boundary/missing-dependency smoke | 已安装 `ask-light` behavior suite：52 assertions/PASS；已安装 `manuscript-ops` CLI help/PASS | 已安装 `review-loop` generic profile contract：`PASS`；包资源存在 |
| 重复安装行为 | 同命令 exit 0；CLI 对 5 个包均报告 `overwrites: Codex` | 未单独重复；整仓重复已覆盖安装器路径 |
| 限制 | 未测试 host refresh 和模型介导的 runtime invocation。 | 同左。 |

本次记录了 CLI version 和 exact command，使用 disposable empty destination，让
discovery 阶段无法读取 source checkout；分别运行整仓和单包命令，捕获
discovery 和 smoke，并重复整仓安装记录覆盖行为。公开记录只写 destination
类别，不包含 token、用户名、绝对私人路径或敏感 host 信息。

## 历史 v0.1.0 摘要

本摘要根据 controller 的 T16 acceptance receipt 保留真实的 v0.1.0 安装证据；
不是当前 v0.1.1 release 的重跑。

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
