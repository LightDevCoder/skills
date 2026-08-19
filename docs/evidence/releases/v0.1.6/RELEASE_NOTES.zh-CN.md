# v0.1.6 — kb-init & kanban-worker 发布说明

[English release notes](RELEASE_RECEIPT.md)

## 本次更新

- 将 `light-kanban-worker` 改名为 `kanban-worker`：名称更短，调用更方便。
- 大幅优化 `kb-init` 内部逻辑：新增决策 provenance（决策来源追踪）、开放决策 surfacing、depth-before-settlement（先深入再定稿）、readiness 检查、人类导航设计、research contract、连接设置/验证，以及备份/恢复语义。
- 技能名称不再携带任何版本后缀。

## kb-init

知识库初始化技能。通过知识库专属访谈设计并初始化可维护的知识库：先访谈了解你的真实工作流，再调研所选知识库的实际可操作方法，产出实施方案 SPEC，并在你明确批准后才开始实施、验证和交接。仅在你显式调用且上下文很少时自动开始访谈。

## kanban-worker

看板工作处理技能。每次定时唤醒处理一张 Light-Kanban 任务：先继续自己持有的 in-progress 任务与 review feedback，再领取新任务，在当前 agent host 上校验 workspace，执行后交回人工验收。支持手动入口。

## 验证

已针对新的 v0.1.6 tag 实测安装：整集合（9 个 skill）与单装 `kanban-worker` / `kb-init` 均通过，安装副本与 tag 源码一致；CI `collection-quality` 通过。
