# 第一方维护与文档同步

[English maintenance contract](MAINTENANCE.md)

本页规定第一方 Skill 的生命周期和使集合可维护、可安装的文档同步要求。不复制 [AGENTS.md](../AGENTS.md) 或架构文档。

## 权威记录

每个事实只保留一个权威位置，其他位置链接过去：包行为/触发/调用/输入/输出/资源以 `skills/<skill-name>/SKILL.md`（及 supporting files）为准；Port/变换包的来源在 `ATTRIBUTION.md`；可读目录是 [CATALOG.md](../CATALOG.md)；安装与验证是 [docs/INSTALLATION.md](INSTALLATION.md)；审查与 verdict 是 [docs/REVIEW_POLICY.md](REVIEW_POLICY.md) 与 [REVIEWER_CONTRACT.md](REVIEWER_CONTRACT.md)；历史是 [CHANGELOG.md](../CHANGELOG.md) 与真实 release；组合验证资产在 [docs/workflows/](workflows/)。

## 当前同步基线

准入集合包含 `skills/` 下 **33 个第一方 Skill**（见 [CATALOG.zh-CN.md](../CATALOG.zh-CN.md)）。当前稳定版本为包含 33 个第一方包的 `v0.2.0`（见 [CHANGELOG.zh-CN.md](../CHANGELOG.zh-CN.md)）；上一稳定版本为 9 个包的 `v0.1.6`。

历史：`v0.1.1` 五个、`v0.1.2` 七个、`v0.1.3` 工具链迁移、`v0.1.4`（`light-kanban-worker`）、`v0.1.5` 调度与身份加固、`v0.1.6`（`kb-init`）。结构发现检查在 [tests/test_collection_discovery.py](../tests/test_collection_discovery.py) 与 [tests/test_composition.py](../tests/test_composition.py)，仅为结构证据，不是 fresh-install 证明。

## 变更流程

每次 **新增 / 更新 / 改名 / 弃用 / 移除 / Port / Adapt**：

1. 先执行 [Skill 准入](SKILL_ADMISSION.md) 的 reuse-before-invention 与 ownership gate——已批准的 Matt PORT（SPEC §14）只要带 `ATTRIBUTION.md` 且无运行时依赖即获架构授权。
2. 保留包边界、invocation direction、attribution 与必要资源。
3. 判断是否符合低风险纯提示型快速通道，否则走完整路径；只收集对应路线要求的 evidence。
4. 执行[审查策略](REVIEW_POLICY.md) 的 review trigger——`review-loop` 为引擎，`project-review` 拥有最终验收。
5. 同步 README、目录、安装说明、治理链接、受影响组合示例、discovery/composition 测试、attribution 与 changelog。
6. 先写未发布变更记录；未通过真实 release gate 前不宣称版本/tag/已验证命令。

## 同步矩阵

| 变更 | 必须检查 |
| --- | --- |
| **新增** | README、目录、安装指南、治理链接、受影响组合示例、discovery + composition 测试、changelog、适用 `ATTRIBUTION.md`、fresh-install 证据及所选快速/完整路径 verdict。 |
| **更新** | 包契约与行为证据；受影响目录/安装/attribution/示例/测试、兼容性与 changelog。 |
| **改名** | old-to-new 迁移指引；全部链接、目录记录、installer 示例、测试、示例、attribution 与 changelog。 |
| **弃用** | 目录状态、README 指引、替代/迁移路径、安装警告、示例、测试、changelog 与 release notes。 |
| **移除** | 确认无兼容 shim 需求；清理旧引用、保留迁移说明、更新目录/安装面并记录移除。 |
| **Port** | 已读上游源码、`ATTRIBUTION.md`（来源/路径/revision/license/Light 变更）、Light handoff 适配、无上游运行时依赖，外加新增矩阵的文档/测试。 |
| **Adapt** | 说明参照的上游模式与 Light 集成必要性，保留适用 `ATTRIBUTION.md`，外加更新矩阵的文档/测试。 |

## 目录与安装维护

目录条目须写明作用、when to use（适用时）、调用方式、包路径、状态、安装范围与证据。以包 metadata 为准，不另建静态路由表。

发布示例必须指向真实已发布来源并与当前目录一致。针对 fresh 环境验证全仓与单包安装，保留精确命令、已发布 revision、host 与离线 discovery 结果；未验证前保持模板标记。

## 上游归属与兼容性

已批准的 Matt PORT 为自包含第一方包，带 `ATTRIBUTION.md`，运行时**不需要**安装 `mattpocock/skills`。其他上游可直接推荐而不复制；仍以第三方为主的修改版进入 `skills-3rdParty`。

发布前检查 attribution/license、依赖、host 位置、安装行为与已知行为差异。Light 主流程运行时不得要求 `mattpocock/skills` 或 `sol-advisor`。

## 组合示例

`docs/workflows/` 仅为验证资产，说明 Skill 组合与 handoff（`entry → handoff → stop → optional`），不复制 Skill 内部详细流程。不得成为隐藏准入门槛或自动 workflow。

## 弃用、回滚与发布

弃用需显式标记目录与安装指引、写明替代或声明无替代、在发布支持期内保留迁移信息并记入 changelog。

候选发布验证失败时停止 promotion，按适用 review 流程修复；不重写已发布历史或删除证据。稳定发布仅需已准入包、同步文档、已验证安装命令、必需 review 证据与真实版本/tag。

## Closeout 记录

收尾时记录最终仓库位置、已发版本/tag、已验证命令、第一方目录（33）、已批准 Port / direct upstream / modified third-party 区分、证据、限制与迁移/归档指引。不得把结构或模拟证据写成 runtime proof。Historical closeout must be recorded with exact identifiers and limitations — closeout is not structural proof. 历史证据（`docs/evidence/`）保持不变。
