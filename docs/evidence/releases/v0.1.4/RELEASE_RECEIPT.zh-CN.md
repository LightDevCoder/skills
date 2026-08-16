# LightDevCoder/skills v0.1.4 发布收据

状态：本 commit 时为 `TAG PENDING` — 发布 `v0.1.4` tag 并完成针对已发布 tag 的
fresh-install 验证后，收据在 [INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md) 中补齐。

## 身份

| 字段 | 值 |
| --- | --- |
| 仓库 | `LightDevCoder/skills`（公开） |
| Release | `v0.1.4` |
| Release commit | main 上的 `v0.1.4` tag |
| Release URL | https://github.com/LightDevCoder/skills/releases/tag/v0.1.4 |
| 范围 | 新的第一方 `light-kanban-worker` Skill（完整准入路径）、scheduled Light-Kanban worker 工作流、版本/文档同步清理、安装验证 |

## 变更内容

- 新的第一方 model-invoked Skill `light-kanban-worker`：每次 scheduled
  agent 运行最多处理一张 Light-Kanban 任务；先检查持有的 in-progress 任务
  与 `reviewFeedback` 再领取新任务；原子 claim 带有限冲突重试；workspace
  校验失败时 block 并附具体原因；`complete` 交回人工验收；绝不 archive /
  accept / delete / recycle / unblock；无 daemon、轮询或运行时脚本。
- 包级 contract 与 behavior 套件，含对抗性单规则 negative fixtures；已接入
  collection CI。
- 准入：`review-loop agent-skill` Profile，Charter revision 1，完整独立性；
  三项确认 findings 已修复，一项驳回；全新 Evaluator 逐条 `PASS`。证据见
  [docs/evidence/admissions/light-kanban-worker/](../../admissions/light-kanban-worker/README.zh-CN.md)。
- 行为证据：针对真实 Light-Kanban 服务器的场景 A–F（新任务、退回返工、
  双 worker 原子 claim、workspace 缺失 block、空队列无变更、离线无变更）。
- 版本/文档同步：v0.1.4 为当前稳定 release；v0.1.3、v0.1.2、v0.1.1、
  v0.1.0 保持历史记录；README、目录、安装指南、维护基线、discovery 与
  contract 测试、双语指南、changelog 更新为八包集合。

## Gates

| Gate | 状态 |
| --- | --- |
| `light-kanban-worker` 准入 PASS | PASS（review-loop agent-skill，完整独立性） |
| 完整测试套件 PASS | 本地 PASS（90 条 collection 断言、19 个包套件）；main 上 CI |
| Catalog 同步 | PASS |
| 安装文档同步 | PASS |
| 针对已发布 v0.1.4 tag 的 fresh installation | PENDING — 记录于 [INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md) |
