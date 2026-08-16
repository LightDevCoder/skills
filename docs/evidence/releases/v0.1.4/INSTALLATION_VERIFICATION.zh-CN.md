# v0.1.4 安装验证

[English record](INSTALLATION_VERIFICATION.md)

## 状态

本 commit 时为 `PENDING`。验证在已发布的 `v0.1.4` tag 存在后执行，使用全新
destination 且不依赖 source checkout，符合 release gate 要求。运行完成后，
把已验证结果、CLI 版本和 discovery 输出填入下表。

## 流程

1. 记录 `npx skills --version` 与确切命令。
2. 使用一次性空 destination，并让 host discovery 步骤无法访问 source checkout。
3. 对通用 `latest` 形式与 pinned `#v0.1.4` 形式，分别运行整集合与单 Skill 命令。
4. 捕获 discovery（`npx --yes skills list`），确认脱离 source checkout 仍列出 `light-kanban-worker`。
5. 对安装的 `light-kanban-worker` 包运行一个 success 与一个 boundary smoke（对安装副本运行 contract + behavior 套件）。
6. 重复同一命令，记录是无操作还是报告重复。

| 字段 | 整集合 | 单 Skill（`light-kanban-worker`） |
| --- | --- | --- |
| 命令 | `npx skills add LightDevCoder/skills --yes --copy --agent '*'` 与 `npx skills add LightDevCoder/skills#v0.1.4 --yes --copy --agent '*'` | `npx skills add LightDevCoder/skills --skill light-kanban-worker --yes --copy --agent '*'` 与 `npx skills add LightDevCoder/skills#v0.1.4 --skill light-kanban-worker --yes --copy --agent '*'` |
| CLI 版本 | PENDING | PENDING |
| Released commit | PENDING | PENDING |
| Fresh destination | PENDING | PENDING |
| 安装结果 | PENDING | PENDING |
| 脱离 source checkout 的 discovery | PENDING | PENDING |
| 安装副本 smoke | PENDING | PENDING |
| 重复安装行为 | PENDING | PENDING |
| 限制 | PENDING | PENDING |
