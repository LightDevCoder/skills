# v0.1.4 发现验证

[English record](DISCOVERY_VERIFICATION.md)

## 状态

本 commit 时为 `PENDING` — 已发布 tag 的安装运行记录脱离 source checkout 的
discovery 结果后完成。见 [INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md)。

## 必须成立

- 整集合安装后，fresh destination 中 `npx --yes skills list` 列出
  `light-kanban-worker`；单 Skill 安装后只列出 `light-kanban-worker`。
- 安装包包含 `SKILL.md`、`agents/openai.yaml`、`references/api.md` 与
  `tests/`，与 tagged 源逐字节一致。
- destination 中不存在 source checkout。
