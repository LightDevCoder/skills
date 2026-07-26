[English README](README.md)

![LightDevCoder/skills — 可组合的 Agent 工作流](skills/docs/assets/skills-header.png)

# Personal Skills Collection

`LightDevCoder/skills` 是公开的第一方 Agent Skills 集合，包含五个可以独立安装、独立发现、明确声明调用边界的 Skill。包内 `SKILL.md` 仍是行为权威；本 README 与用户指南负责说明使用方式。

> **About：** Personal Skills Collection — Drive your creativity

> **Release candidate：** 当前工作树准备的是 v0.1.1。发布记录和 fresh-install 证据见 [docs/evidence/releases/v0.1.1/](docs/evidence/releases/v0.1.1/)，promotion 仍受其中 release gate 约束。
>
> 当前已发布的稳定版本仍是 [v0.1.0](https://github.com/LightDevCoder/skills/releases/tag/v0.1.0)。

## Quick Start

release gate 通过后，安装目标版本的整个第一方集合：

```text
npx skills add LightDevCoder/skills#v0.1.1
```

release gate 通过后，只安装同一目标版本下的一个 Skill：

```text
npx skills add LightDevCoder/skills#v0.1.1 --skill review-loop
```

刷新 Agent host，然后在其 Skill catalog 中确认发现结果。若 host 提供文件系统，检查已安装包的 `SKILL.md` 与 `agents/openai.yaml`；脱离 source checkout 后仍能发现，才是有意义的验证。CLI 版本、destination 和结果见 [INSTALLATION_VERIFICATION.md](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.md)。

第一次不知道下一步时，推荐显式调用 `$ask-light`：

```text
$ask-light next
```

三个最短示例：

```text
$ask-light next       # 推荐下一 Skill，不执行它
$project-init         # 初始化已确认的最小项目 preset
$review-loop init     # 冻结已有验收标准的 baseline
```

`ask-light` 只返回建议或一个有边界的 recipe，然后停止；不会执行、安装或自动串联。阅读 [Quick Start](examples/quick-start/README.zh-CN.md)、[Skill 使用指南](docs/zh-CN/skills/)、[workflow recipes](docs/zh-CN/workflows/) 了解输入、输出、handoff 和停止点。

## 第一方目录

| Skill | 作用 | 调用方式 | 包路径 |
| --- | --- | --- | --- |
| [review-loop](skills/review-loop/SKILL.md) | 执行有边界的证据、修复和最终验收循环。 | Model-invoked；支持手动入口。 | skills/review-loop/ |
| [project-init](skills/project-init/SKILL.md) | 从最小 preset 初始化已确认的软件、文稿、研究、知识、数据或 Skill-development 项目。 | User-invoked only。 | skills/project-init/ |
| [ask-light](skills/ask-light/SKILL.md) | 检查 host 并推荐一个下一 Skill 或 bounded recipe，不执行建议。 | User-invoked only。 | skills/ask-light/ |
| [learn-anything](skills/learn-anything/SKILL.md) | 从有足够证据的资料中提炼可复用 Agent Skill 方法。 | User-invoked only。 | skills/learn-anything/ |
| [manuscript-ops](skills/manuscript-ops/SKILL.md) | 治理跨格式、批次、审查和 handoff 的可复现文稿工程。 | Model-invoked；支持手动入口。 | skills/manuscript-ops/ |

完整目录见 [CATALOG.zh-CN.md](CATALOG.zh-CN.md)。组合示例是文档和验证资产，不是固定 pipeline，也不是自动编排器；退休的 `project-workflow` 不会重新引入。

## 所有权与上游边界

| 来源状态 | 权威 | 本仓库处理方式 |
| --- | --- | --- |
| First-party | 本仓库及其包契约 | 放在 `skills/` 下。 |
| Direct upstream | 原始上游仓库 | 直接安装，不复制未修改 Skill。 |
| Modified third-party | 私有 `LightDevCoder/skills-3rdParty` | 保存 provenance、patch、license、sync lock 和安装证据。 |
| Deprecated / archived | 已发布迁移记录 | 保留历史并指向当前权威来源。 |

未纳入第一方集合的 Matt Pocock Skills 仍在
[mattpocock/skills](https://github.com/mattpocock/skills)。指定的私有第三方快照独立维护于 [LightDevCoder/skills-3rdParty](https://github.com/LightDevCoder/skills-3rdParty)，不会复制到本公开仓库。

## 治理与证据

- [维护契约](AGENTS.md)
- [Skill 准入](docs/SKILL_ADMISSION.zh-CN.md)
- [维护与同步](docs/MAINTENANCE.zh-CN.md)
- [安装与 fresh-install 验证](docs/INSTALLATION.zh-CN.md)
- [审查策略](docs/REVIEW_POLICY.zh-CN.md)
- [目录](CATALOG.zh-CN.md)
- [变更记录](CHANGELOG.zh-CN.md)
- [发布收据](docs/evidence/releases/v0.1.1/RELEASE_RECEIPT.zh-CN.md)
