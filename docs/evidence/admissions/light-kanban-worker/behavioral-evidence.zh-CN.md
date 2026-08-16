# `light-kanban-worker` 行为证据

[English record](behavioral-evidence.md)

状态：`PASS` — 六个场景均已在真实 Light-Kanban 服务器上按 `SKILL.md` 协议
完成（运行中的 agent 以 scheduled agent 的方式执行 worker 的 HTTP + shell 步骤）。

## 环境事实

| 事实 | 值 |
| --- | --- |
| Light-Kanban 二进制 | 由 `LightDevCoder/light-kanban` main（v1.0.4+，commit `f49ace5`）经 `make build` 构建 |
| 服务器命令 | `./dist/light-kanban -db /tmp/lk-worker-smoke/data/kanban.db -avatars /tmp/lk-worker-smoke/data/avatars -no-open -addr 127.0.0.1:8641` |
| 日期 | 2026-08-16（transcript 内为 UTC 时间戳） |
| Worker agent | `codex-main`（名称 `Codex`）、`claude-code`（名称 `Claude Code`）；经 `POST /api/avatars` 上传的 1×1 PNG 图标 |
| 工具 | 一次性 bash + curl + jq 脚本 `/tmp/lk-worker-smoke/run-scenarios.sh`（不随 Skill 发布）；完整 transcript 在 `/tmp/lk-worker-smoke/transcript.txt` |

## 结果

| 场景 | 预期 | 结果 |
| --- | --- | --- |
| A — 新任务 | todo → worker 领取 → 执行 → complete → awaiting_confirmation | `PASS` — 任务 `1d2cfffb…` 以 `todo` 创建；解析 identity（`GET /api/agents` 为空 → 首次注册：上传头像 `/api/avatars/5efb83c4….png`）；先检查持有的 in-progress（为空）；领取 FIFO 第一张 todo（`200`，`claimedBy=codex-main`，`in_progress`）；workspace 可访问；应用修复；`POST complete` → `200` `awaiting_confirmation`。 |
| B — Request Changes | awaiting_confirmation → 人工退回并附反馈 → in_progress → 下次运行先找到自己持有的任务 → 读取反馈 → 修复 → complete | `PASS` — 人工 `POST reject`（`{"feedback":"Add a regression test for the redirect fix."}`）把任务退回 `in_progress` 并写入 `reviewFeedback`；下次唤醒复用已有 identity（`GET /api/agents` → `codex-main` 已存 name/avatar）；在任何 todo 检查之前先找到带 `reviewFeedback` 的持有任务；在 workspace 写入回归测试；`POST complete` → `awaiting_confirmation`；人工 `POST archive` → `archived`（worker 自身从未 archive）。 |
| C — 两个 worker | 两个不同 agentId 同时领取同一张 To Do；只有一个 claim 成功 | `PASS` — 并发 claim 同一 todo：`claude-code` → `200` `in_progress`，`codex-main` → `409 conflict`；`claimedBy=claude-code`，恰好一个赢家；输家重读 todo（`[]`）后结束——有限重试，无死循环。 |
| D — workspace 缺失 | workspacePath 不存在 → claim → block 并附具体原因 | `PASS` — 领取后 `test -d` 失败，`POST block`（`{"reason":"Workspace path is not accessible from this agent host."}`）→ `200` `blocked`，卡片可见完整 `blockReason`。 |
| E — 空队列 | 没有持有的 in_progress 也没有 todo → 无变更、干净退出 | `PASS` — `in_progress` → `[]`、`todo` → `[]`；"No task available"；数据库 SHA-1 前后一致（`53ad3992…`），活跃任务 0 → 0，未创建任务、未等待。 |
| F — Light-Kanban 离线 | 服务不可达 → 无变更、失败清晰 | `PASS` — 对 `http://127.0.0.1:19999` 的健康探测返回 `000`（拒绝连接）；worker 报告不可达并结束；数据库 SHA-1 不变（`53ad3992…`）。 |

## 覆盖说明

- 既有工作优先：B 场景证明（先找到持有任务再做任何 todo claim），A 场景的协议顺序也做了检查。
- Identity：A 中首次注册（本地图标上传）；B 中复用服务器 identity、无需重新上传。
- 人工验收边界：worker 从未调用 `archive`/`reject`/`recycle`/`unblock`/`delete`；harness 中这些调用均来自人类角色（reject、archive、delete），已在记录中注明。
- 原子 claim：看板的单条条件 `claim` 转换在真实并发下产生恰好一个 `200` 与一个 `409`。
- 局限：这是单机（localhost）集成 smoke，不是跨机器 LAN 测试；远程主机上网络可达与 workspace 可达的区分遵循同一 block 规则（场景 D），并已在 `SKILL.md` 中说明。
