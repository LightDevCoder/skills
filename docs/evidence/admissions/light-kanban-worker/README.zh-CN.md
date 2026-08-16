# `light-kanban-worker` 准入证据

[English record](README.md)

## 范围与状态

- 包：`skills/light-kanban-worker/`
- 调用类型：model-invoked，支持手动入口
- Profile：`review-loop` `agent-skill`
- 稳定版本边界：v0.1.3 包含七个包，不含 `light-kanban-worker`
- 准入状态：`IN PROGRESS` — 完整准入路径；该 Skill 访问网络、读取 workspace 文件、改变 Light-Kanban 任务状态，纯提示型快速通道不适用

## 证据计划（完整路径）

| 领域 | 需要证明的内容 |
| --- | --- |
| 结构 | 包结构、`SKILL.md` metadata、内部链接与资源通过包级 contract 与 behavior 套件。 |
| 安装与发现 | 全新环境安装该包，并在不依赖 source checkout 的情况下发现已安装 Skill。 |
| 行为 | 针对真实 Light-Kanban 服务器运行场景 A–F：新任务、Request Changes 返工、双 worker 原子 claim、workspace 缺失 → block、空队列 → 无变更、离线 → 无变更且失败清晰。 |
| 调用 | scheduled 风格 prompt 与一次性手动 prompt 都能命中 worker；model-invoked metadata 与 `SKILL.md` 一致。 |
| 审查 | `review-loop` 以 `agent-skill` Profile 评估候选，使用 Producer evidence 与全新 Evaluator。 |
| 归属 | 第一方原创；无第三方内容，无需 `ATTRIBUTION.md`。 |

## 结果

每个 gate 完成后，用确切命令、环境事实、输入、输出和限制填写上表。最终裁决
由 `review-loop agent-skill` 拥有；只有 `PASS` 才能进入第一方集合。

- contract 与 behavior 套件：`skills/light-kanban-worker/tests/`
  （positive/negative fixtures、非零断言）。
- 真实 Light-Kanban 服务器的行为证据：见
  [behavioral-evidence.md](behavioral-evidence.md)。
- 最终验收：`review-loop agent-skill` 运行完成后记录在 [review-loop/](review-loop/)。
