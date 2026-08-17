# 第一方维护与文档同步

[English maintenance contract](MAINTENANCE.md)

本页规定第一方 Skill 的生命周期和使集合可维护、可安装的文档同步要求。

## 权威记录

每个事实只保留一个 authority，其他位置链接过去：包行为/触发/调用/输入/输出/资源以 `skills/<skill-name>/SKILL.md` 为准；变换包的 provenance 在 `ATTRIBUTION.md`；可读目录是 `CATALOG.md`；安装与证据是 `docs/INSTALLATION.md`；审查和 verdict 规则是 `docs/REVIEW_POLICY.md`；历史和 release notes 是 `CHANGELOG.md` 与真实 release；组合验证资产在 `docs/workflows/`。

本分支的准入集合必须恰好包含 `review-loop`、`project-init`、`ask-light`、`learn-anything`、`manuscript-ops`、`recap`、`language-learning` 和 `light-kanban-worker`。`recap` 与 `language-learning` 经纯提示型快速通道准入，并在 v0.1.2 中发布；`light-kanban-worker` 是 model-invoked 包，涉及网络、文件系统和看板状态副作用，因此走完整准入路径（`review-loop agent-skill`），随 v0.1.4 发布；其 v0.1.5 调度边界与首次注册身份变更带有第二次 `review-loop agent-skill` `PASS`。稳定 v0.1.1 包含原来的五个已准入包，v0.1.3 保持 v0.1.2 的包集合并迁移了测试工具链。`tests/test_collection_discovery.py` 负责检查包名、metadata、目录、README 链接、头图、治理路径、双语配对和退休 orchestration 边界，但不证明 runtime 或 fresh installation。

## 变更流程与同步矩阵

新增、更新、改名、弃用或移除时：

1. 先执行 [Skill 准入](SKILL_ADMISSION.zh-CN.md) 的 reuse-before-invention 与 ownership gate。
2. 保留包边界、invocation direction、attribution 和必要资源。
3. 先判断是否符合低风险纯提示型快速通道，否则走完整路径；只收集对应路线要求的 evidence，并准确标注 evidence class。
4. 执行[审查策略](REVIEW_POLICY.zh-CN.md)的 review trigger。
5. 同步 README、目录、安装说明、治理链接、affected recipes、discovery tests、attribution 和 changelog。
6. 未通过真实 release gate 前，不把版本、tag 或安装命令写成已验证。

| 变更 | 必须检查 |
| --- | --- |
| Add | README、catalog、installation、governance、受影响 recipes、discovery tests、changelog、适用 attribution、fresh-install evidence，以及所选快速或完整路径的 verdict。 |
| Update | 包 contract/behavior evidence、受影响目录/安装/attribution/recipes/discovery、兼容性和 changelog。 |
| Rename | old-to-new migration、链接、目录、installer、测试、attribution 和 changelog。 |
| Deprecate | catalog 状态、replacement/migration、安装警告、示例、测试、changelog 和 release notes。 |
| Remove | 消费者检查、旧引用清理、迁移说明、catalog/installation 更新和 removal 记录。 |

## 上游、recipes、rollback 和 closeout

上游可以直接推荐而不复制；实质变换的第一方能力必须保留 attribution，仍主要是第三方能力的修改版进入 `skills-3rdParty`。`docs/workflows/` 只是验证资产，不能变成隐藏准入门槛或自动 workflow。

发布前检查 attribution/license、依赖、host location、安装行为、双语文档和已知差异。release candidate 验证失败时停止 promotion，不改写已发布历史或删除证据。closeout 必须记录最终位置、版本/tag、命令、catalog、direct upstream、modified third-party、证据、限制和迁移/归档状态，并区分 `implemented`、`verified`、`independently accepted`、`BLOCKED`、`NOT TESTED`、`out of scope`。
