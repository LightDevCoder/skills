# v0.1.5 安装验证

[English record](INSTALLATION_VERIFICATION.md)

## 状态

`PASS` — 针对已发布 tag 的公开仓库，Skills CLI `1.5.22`，通用 `latest` 与
pinned `#v0.1.5` 两种形式均在 fresh destination 验证。host refresh 属于各
host 自身，未作声明；CLI discovery 均在无 source checkout 的 fresh
destination 运行。

| 字段 | 整集合 | 单 Skill（`light-kanban-worker`） |
| --- | --- | --- |
| 命令 | `npx skills add LightDevCoder/skills --yes --copy --agent '*'`（latest）与 `npx skills add LightDevCoder/skills#v0.1.5 --yes --copy --agent '*'`（tag） | `npx skills add LightDevCoder/skills --skill light-kanban-worker --yes --copy --agent '*'`（latest）与 `npx skills add LightDevCoder/skills#v0.1.5 --skill light-kanban-worker --yes --copy --agent '*'`（tag） |
| CLI 版本 | `1.5.22` | `1.5.22` |
| 已发布 commit | `a56aa9d98de0b941ee2282144bc7e756ef5e48bd`（`v0.1.5` tag） | 同左 |
| Fresh destination | 全新空临时目录；`Found 8 skills`、`Installing all 8 skills`；`.agents/skills/` 下恰好 8 个包 | 全新空临时目录；`.agents/skills/` 下恰好 1 个包（`light-kanban-worker`） |
| 安装结果 | `PASS`，exit code 0 | `PASS`，exit code 0 |
| 脱离 source checkout 的 discovery | `npx --yes skills list` exit 0；列出 `light-kanban-worker ./.agents/skills/light-kanban-worker`；无 source checkout | `npx --yes skills list` exit 0；恰好列出一个包 `light-kanban-worker`；无 source checkout |
| 安装副本 smoke | — | 全部 14 个文件与 tag 源码逐字节一致（对 `v0.1.5` tag checkout 做 `diff -r` 干净）；对安装副本独立运行 contract（100 断言）与 behavior（23 断言）套件均 OK |
| 重复安装 | 同一命令 exit 0；CLI 报告各 agent 组的 `overwrites:`（no-op 覆盖） | 同一命令 exit 0；no-op 覆盖 |
| 局限 | CLI 自身在 `agent/skills/` 下的各 host 副本会去掉 `name` frontmatter 字段，因此 `skills list` 对每个包（包括发布已久的包）都打印统一的 "missing required frontmatter field(s): name" 警告。这是 CLI 复制行为，不是包缺陷；`.agents/skills/` 下的安装与 tag 逐字节一致。host refresh 与模型介导的运行时调用未作声明。 | 同左。 |

## 步骤

1. 记录 `npx skills --version` 与精确命令。
2. 使用一次性空 destination，并让 host discovery 步骤无法访问 source checkout。
3. 分别对通用 `latest` 形式与 pinned `#v0.1.5` 形式运行整集合与单 Skill 命令。
4. 捕获 discovery，然后对 `light-kanban-worker` 运行安装副本 smoke（与 tag checkout 逐字节对比 + 在安装副本上运行包自带 contract/behavior 套件）。
5. 重复同一命令，记录结果是 no-op 还是报告重复。

证据记录 destination 类别而非私有绝对路径，不含 token、用户名或敏感 host 信息。
