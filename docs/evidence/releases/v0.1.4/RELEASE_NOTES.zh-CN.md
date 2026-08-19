# v0.1.4 发布说明（中文）

[English release notes](RELEASE_RECEIPT.md)

## 本次更新

- 新增第一方 model-invoked Skill `light-kanban-worker`：每次 scheduled agent 运行最多处理一张 Light-Kanban 任务——稳定 agent identity、先检查自己持有的 in-progress 任务与 review feedback 再领取新任务、原子 claim 带有限次冲突重试、workspace 校验、`complete` 交回人工验收。
- 集合扩展为八个已准入第一方 Skill。
- 修复 ask-light scanner 的 `Test-PathUnder` 跨平台路径比较问题。
