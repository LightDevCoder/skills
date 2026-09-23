# v0.2.5 — 工作流路由与验证可靠性

[English release notes](RELEASE_NOTES.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md)

v0.2.5 修复证据不全时仍可能建议执行或发布的问题。`agent-config` 现在要求新鲜、规范的 Host 证据和匹配的已确认 Profile；`ask-light --mode semantic` 与主路由共用项目约束和最终校验。重复工单编号在明确迁移前阻断路由。

手稿项目先完成通用 `project-init` 初始化，再由 `manuscript-ops` 创建自己的 Profile 和状态。依赖检查按当前运行时接口进行；整包字节比对只针对明确指定的不可变发布引用。`code-review` 为 `review-loop` 输出规范 Findings；旅行页生成期和首次同步使用相同待办契约。

CI 发现完整 Python 测试，并运行 Node 运行时测试和生成旅程构建。远端发布验证拒绝缺失或不一致的标签以及无法查询的 GitHub Release。包数量仍为 36。标签和 GitHub Release 存在后，才记录已发布安装及发布事实。
