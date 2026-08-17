# v0.1.4 安装验证

[English record](INSTALLATION_VERIFICATION.md)

## 状态

`PASS` — 使用 Skills CLI `1.5.22`，对已发布 tag 的通用 `latest` 形式与
pinned `#v0.1.4` 形式，均以 fresh destination 验证。host refresh 是
host 专属行为，未声称；CLI discovery 均在脱离 source checkout 的 fresh
destination 上运行。

| 字段 | 整集合 | 单 Skill（`light-kanban-worker`） |
| --- | --- | --- |
| 命令 | `npx skills add LightDevCoder/skills --yes --copy --agent '*'`（latest）与 `npx skills add LightDevCoder/skills#v0.1.4 --yes --copy --agent '*'`（tag） | `npx skills add LightDevCoder/skills --skill light-kanban-worker --yes --copy --agent '*'`（latest）与 `npx skills add LightDevCoder/skills#v0.1.4 --skill light-kanban-worker --yes --copy --agent '*'`（tag） |
| CLI 版本 | `1.5.22` | `1.5.22` |
| Released commit | `a9cc8aa029c926fc80f6ddc0022793f79dfd85bd`（`v0.1.4` tag） | 同左 |
| Fresh destination | 全新空临时目录；`.agents/skills/` 下恰好 8 个包（`Found 8 skills`，`Installing all 8 skills`） | 全新空临时目录；`.agents/skills/` 下恰好 1 个包（`light-kanban-worker`） |
| 安装结果 | `PASS`，exit code 0 | `PASS`，exit code 0 |
| 脱离 source checkout 的 discovery | `npx --yes skills list` exit 0；列出 `light-kanban-worker ./.agents/skills/light-kanban-worker`；无 source checkout | `npx --yes skills list` exit 0；只列出 `light-kanban-worker`；无 source checkout |
| 安装副本 smoke | — | 10/10 文件与 tagged 源 SHA-256 逐字节一致；contract 与 behavior 套件在安装副本上通过（collection 测试 harness 在 `PYTHONPATH` 上） |
| 重复安装行为 | 同一命令 exit 0；CLI 对 agent 组报告 `overwrites:`（无操作覆盖） | 同一命令 exit 0；无操作覆盖 |
| 限制 | CLI 自身在 `agent/skills/` 下的按 host 副本会去掉 `name` frontmatter 字段，因此 `skills list` 对每个包（包括早已发布的包）都打印统一的 "missing required frontmatter field(s): name" 警告。这是 CLI 复制行为，不是包缺陷；`.agents/skills/` 下的安装与 tag 逐字节一致。未声称 host refresh 与模型介导的运行时调用。 | 同左。 |

## 流程

1. 记录 `npx skills --version` 与确切命令。
2. 使用一次性空 destination，并让 host discovery 步骤无法访问 source checkout。
3. 对通用 `latest` 形式与 pinned `#v0.1.4` 形式，分别运行整集合与单 Skill 命令。
4. 捕获 discovery，并对 `light-kanban-worker` 运行安装副本 smoke。
5. 重复同一命令，记录是无操作还是报告重复。

证据记录 destination 类别而非绝对私有路径；不含 token、用户名或敏感主机信息。
