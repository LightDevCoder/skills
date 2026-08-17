# LightDevCoder/skills v0.1.5 发布收据

[English receipt](RELEASE_RECEIPT.md)

状态：`READY FOR RELEASE` — pre-release gate 已通过。本记录包含的是
pre-release gate；post-release verification 记录在 main 上，并从 GitHub
Release 链接。

## 身份

| 字段 | 值 |
| --- | --- |
| 仓库 | `LightDevCoder/skills`（公开） |
| Release | `v0.1.5` |
| Release commit | main 上的 `v0.1.5` tag（记录于 post-release verification） |
| Release tag | `v0.1.5` |
| Release URL | https://github.com/LightDevCoder/skills/releases/tag/v0.1.5 |
| 范围 | `light-kanban-worker` 行为契约：same-agent run 不得重叠、atomic claim 边界澄清、首次注册身份（ID + name + avatar）、release evidence 工作流清理 |

## 变更内容

- `light-kanban-worker` 现在明确禁止同一 `LIGHT_KANBAN_AGENT_ID` 的
  scheduled run 重叠执行：同一 agent id 任意时刻至多一个 invocation 活跃，
  上一 run 仍活跃时触发的唤醒必须 skip。不同 agent id 仍可并发。
- atomic claim 边界被准确记录：它保护两个不同 worker 同时 claim 同一张
  To Do；它不是同一 agent identity 多个 invocation 的并发锁。并发控制属于
  scheduler / agent runtime（`max concurrent runs = 1` 或等价的
  skip-while-active 设置）；worker 不新增 lock process、heartbeat 或 lease
  service。
- 首次注册现在明确要求 ID + name + avatar：本地图片通过
  `POST /api/avatars` 上传并使用返回的 `/api/avatars/...` 路径 claim。已存在
  的 agent id 复用服务器保存的 name/avatar——avatar 只在首次注册时需要，不是
  每次唤醒都需要。全新 agent id 缺 name 或 avatar 时报 identity
  configuration missing，不 claim、不改动任何任务。
- contract 与 behavior 套件扩展了新规则、两个对抗性 negative fixture 与
  行为场景 G、H（见 [TEST_SUMMARY.zh-CN.md](TEST_SUMMARY.zh-CN.md)）。
- release evidence 工作流澄清：本收据区分 pre-release gate 与 post-release
  verification，已发布 tag 中不再出现令人困惑的 `PENDING` 标记。

## Pre-release gate

| 门禁 | 状态 |
| --- | --- |
| Worker contract 测试 PASS | PASS |
| Worker behavior 测试 PASS | PASS |
| same-agent overlap 规则已测试（场景 G） | PASS |
| 首次注册 avatar 规则已测试（场景 H） | PASS |
| 场景 A–F 保持不变并继续通过 | PASS |
| 集合测试 PASS | PASS — review-loop 记录文件写入后，在 candidate commit 上的最终 green run（见 [TEST_SUMMARY.zh-CN.md](TEST_SUMMARY.zh-CN.md)） |
| `review-loop agent-skill` 验收 | PASS — 见 [AGENT_SKILL_REVIEW.zh-CN.md](AGENT_SKILL_REVIEW.zh-CN.md) |
| 文档同步（README、目录、安装、指南、changelog） | PASS |
| Changelog 已准备 | PASS |
| release candidate 干净（candidate commit 上 `git status` clean） | PASS |

## Post-release verification

以下内容只能在 `v0.1.5` tag 真正存在后确认。它们记录在 main 的 final
verification commit 中，并从 GitHub Release 链接：

| 检查项 | 记录 |
| --- | --- |
| 已发布 tag 身份与 release commit | 记录在 main |
| 从 `LightDevCoder/skills#v0.1.5` fresh install | [INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md) |
| Host discovery | [DISCOVERY_VERIFICATION.zh-CN.md](DISCOVERY_VERIFICATION.zh-CN.md) |
| 重复安装 | [INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md) |
| Release CI（`collection-quality`） | 记录在 main |
| GitHub Release body 链接本记录与 post-release receipt | 记录在 main |
