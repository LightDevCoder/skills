# `light-kanban-worker` 行为证据

[English record](behavioral-evidence.md)

状态：`IN PROGRESS` — 每个场景完成后，用确切命令、环境事实、输入、输出和结果
填写。标注 `PENDING` 的场景尚未运行。

| 场景 | 预期 | 结果 |
| --- | --- | --- |
| A — 新任务 | todo → worker 领取 → 执行 → complete → awaiting_confirmation | PENDING |
| B — Request Changes | awaiting_confirmation → 人工退回并附反馈 → in_progress → 下次运行先找到自己持有的任务 → 读取反馈 → 修复 → complete | PENDING |
| C — 两个 worker | 两个不同 agentId 同时领取同一张 To Do；只有一个 claim 成功 | PENDING |
| D — workspace 缺失 | 任务 workspacePath 不存在 → claim → block 并附具体原因 | PENDING |
| E — 空队列 | 没有持有的 in_progress 也没有 todo → 无变更、干净退出 | PENDING |
| F — Light-Kanban 离线 | 服务不可达 → 无变更、失败清晰 | PENDING |
