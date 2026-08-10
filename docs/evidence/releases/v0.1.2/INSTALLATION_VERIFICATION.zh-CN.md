# v0.1.2 安装验证

[English record](INSTALLATION_VERIFICATION.md)

## 状态

`PASS` — 使用 Skills CLI `1.5.22` 针对已发布的公共仓库 tag 验证，对通用
`latest` 形式和 pinned `#v0.1.2` 形式分别在 fresh destination 上验证。Host
refresh 因 host 而异，不做声明；CLI discovery 在无 source checkout 的 fresh
destination 上运行。

| 字段 | 整个集合 | 单 Skill |
| --- | --- | --- |
| 命令 | `npx skills add LightDevCoder/skills --yes --copy --agent '*'`（latest）与 `npx skills add LightDevCoder/skills#v0.1.2 --yes --copy --agent '*'`（tag） | `npx skills add LightDevCoder/skills --skill review-loop --yes --copy --agent '*'`（latest）与 `npx skills add LightDevCoder/skills#v0.1.2 --skill review-loop --yes --copy --agent '*'`（tag） |
| CLI version | `1.5.22` | `1.5.22` |
| 已发布 commit | `8de5ec1a453b0e93f71dcda160e17ea7b42c3997`（`v0.1.2` tag） | 同左 |
| Fresh destination | 新建空临时项目；`.agents/skills/` 下恰好 7 个包 | 新建空临时项目；`.agents/skills/` 下恰好 1 个包 |
| 安装结果 | `PASS`，`latest` 与 `#v0.1.2` 两种形式均 exit 0 | `PASS`，`latest` 与 `#v0.1.2` 两种形式均 exit 0 |
| 脱离 source checkout 的 discovery | `npx --yes skills list` exit 0；列出 7 个包；无 source checkout | `npx --yes skills list` exit 0；列出 1 个包；无 source checkout |
| Success/boundary/missing-dependency smoke | 已装 `recap` 输出契约：8 断言/PASS；已装 recap 包与 source 逐字节一致 | 已装 `review-loop` 包与 source 逐字节一致，含 `SKILL.md`、`agents/`、`references/`、`tests/` |
| 重复安装行为 | 同一命令 exit 0；CLI 对各 agent group 报告 `overwrites:`（no-op overwrite） | 同一命令 exit 0；CLI 对各 agent group 报告 `overwrites:`（no-op overwrite） |
| 限制 | Host refresh 与 model-mediated runtime invocation 未测试。验证期间的瞬时 GitHub TLS 故障需要重试；记录的是成功运行的结果。 | 同左。 |

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
