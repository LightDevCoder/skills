# v0.1.5 安装验证

[English record](INSTALLATION_VERIFICATION.md)

## 状态

本 commit 时点为 `PENDING`。验证在已发布的 `v0.1.5` tag 存在后执行，针对
fresh destination、脱离 source checkout，完全符合 release gate 要求。运行
完成后，验证结果、CLI 版本与 discovery 输出填入下表（post-release
verification 记录在 main）。

## 步骤

1. 记录 `npx skills --version` 与精确命令。
2. 使用一次性空 destination，并让 host discovery 步骤无法访问 source checkout。
3. 分别对通用 `latest` 形式与 pinned `#v0.1.5` 形式运行整集合与单 Skill 命令。
4. 捕获 discovery（`npx --yes skills list`），确认脱离 source checkout 仍能发现 `light-kanban-worker`。
5. 对已安装的 `light-kanban-worker` 包运行一次 success 与一次 boundary smoke（对安装副本运行包级 contract + behavior 套件）。
6. 重复同一命令，记录结果是 no-op 还是报告重复。

| 字段 | 整集合 | 单 Skill（`light-kanban-worker`） |
| --- | --- | --- |
| 命令 | `npx skills add LightDevCoder/skills --yes --copy --agent '*'` 与 `npx skills add LightDevCoder/skills#v0.1.5 --yes --copy --agent '*'` | `npx skills add LightDevCoder/skills --skill light-kanban-worker --yes --copy --agent '*'` 与 `npx skills add LightDevCoder/skills#v0.1.5 --skill light-kanban-worker --yes --copy --agent '*'` |
| Installer 版本 | pending | pending |
| Host / destination | pending | pending |
| 结果 | pending | pending |
| 脱离 source checkout 的 discovery | pending | pending |
| Success smoke（安装副本上的 contract + behavior 套件） | pending | pending |
| Boundary smoke | pending | pending |
| 重复安装 | pending | pending |
