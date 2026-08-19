# v0.1.5 发布说明（中文）

[English release notes](RELEASE_RECEIPT.md)

## 本次更新

- `light-kanban-worker` 明确禁止同一 `LIGHT_KANBAN_AGENT_ID` 的 scheduled run 重叠执行：同一 agent id 任意时刻至多一个 invocation 活跃，上一 run 仍活跃时触发的唤醒必须 skip；不同 agent id 仍可并发。
- 首次注册现在明确要求 ID + name + avatar：本地图片通过 `POST /api/avatars` 上传并使用返回的 `/api/avatars/...` 路径；已存在的 agent id 复用服务器保存的 name/avatar。
- 补充了 same-agent 不得重叠、首次注册身份等对抗性 negative fixtures 与行为场景 G/H。
- release evidence 工作流澄清：receipt 区分 pre-release gate 与 post-release verification。
