# `light-kanban-worker` 准入证据

[English record](README.md)

## 范围与状态

- 包：`skills/light-kanban-worker/`
- 调用类型：model-invoked，支持手动入口
- Profile：`review-loop` `agent-skill`
- 稳定版本边界：v0.1.3 包含七个包，不含 `light-kanban-worker`
- 准入状态：`PASS` — 完整准入路径（2026-08-16）；该 Skill 访问网络、读取 workspace 文件、改变 Light-Kanban 任务状态，纯提示型快速通道不适用

## 证据摘要

| 领域 | 结果 | 证据边界 |
| --- | --- | --- |
| 结构 | PASS | 包级 contract 与 behavior 套件（metadata、必需 workflow 章节、golden-flow 顺序、规则 checker）加 collection discovery/contract 组合；90 条 collection 断言与全部 19 个包套件通过。 |
| 安装与发现 | PASS | 干净复制安装至 `/tmp/lk-worker-fresh/codex/skills/light-kanban-worker`：10/10 文件 SHA-256 一致，安装树仅含声明的包内容，两个套件在安装副本上通过（共享 collection 测试 harness 在 PYTHONPATH 上）。已发布 tag 的 `npx skills add` 验证是 v0.1.4 release gate。 |
| 行为 | PASS | 针对真实 Light-Kanban 服务器（由 `LightDevCoder/light-kanban` main，commit `f49ace5` 构建）的场景 A–F：新任务、Request Changes 返工、双 worker 原子 claim（恰好一个 200 / 一个 409）、workspace 缺失 → block、空队列无变更、离线无变更。完整 transcript 已记录。 |
| 调用 | PASS | 全新只读探针：scheduled-task prompt 以正确的首步协议加载该 Skill；无关指令不触发；该 Skill 不调用任何其他 user-invoked Skill。 |
| 审查 | PASS | `review-loop` `agent-skill` Profile，Charter revision 1：Critic 候选 F-001/F-002/F-003 已修复解决，F-004 驳回；全新独立 Evaluator 逐条给出 `PASS`。 |
| 归属 | PASS | 第一方原创；无第三方内容或代码，无需 `ATTRIBUTION.md`。 |

行为证据：[behavioral-evidence.zh-CN.md](behavioral-evidence.zh-CN.md)。
最终验收记录：[review-loop/](review-loop/)（charter、findings、round-01 记录、verdict）。

准入不免除 release、安装命令验证或 Program 级验收 gate；这些记录在
[docs/evidence/releases/v0.1.4/](../../releases/v0.1.4/)。
