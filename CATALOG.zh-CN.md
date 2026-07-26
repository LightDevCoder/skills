# 第一方 Skill 目录

[English catalog](CATALOG.md)

本目录从 `skills/` 下的五个准入包同步生成，是可读 inventory，不是静态 workflow router，也不代表某个 Agent host 当前已经安装了哪些 Skill。

## 集合状态

| 字段 | 值 |
| --- | --- |
| 集合 | Personal Skills Collection |
| 包数量 | 5 个第一方 Skill |
| 当前状态 | v0.1.1 已发布；独立 `review-loop agent-skill` acceptance 仍为 BLOCKED |
| 稳定版本 | [v0.1.1](https://github.com/LightDevCoder/skills/releases/tag/v0.1.1) |
| 安装权威 | [docs/INSTALLATION.zh-CN.md](docs/INSTALLATION.zh-CN.md) |
| 发现检查 | [collection-discovery-tests.ps1](tests/collection-discovery-tests.ps1) |
| 证据 | [v0.1.1 release evidence](docs/evidence/releases/v0.1.1/) |

## 已准入 Skill

### review-loop

- **作用：** 在 target 和 acceptance source 已定义后，执行通用的 final-acceptance 和 bounded-repair loop。
- **调用：** Model-invoked，支持手动入口。
- **包：** [skills/review-loop/](skills/review-loop/)
- **状态：** 第一方已准入；包含 generic、software、specification、manuscript、agent-skill Profiles。
- **证据：** [Profile tests](skills/review-loop/tests/)；[使用指南](docs/zh-CN/skills/review-loop.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/review-loop/`。

### project-init

- **作用：** 从最小 preset 初始化项目，保留既有指令并验证结果路径。
- **调用：** User-invoked only。
- **包：** [skills/project-init/](skills/project-init/)
- **状态：** 第一方已准入。
- **证据：** [package tests](skills/project-init/tests/)；[使用指南](docs/zh-CN/skills/project-init.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/project-init/`。

### ask-light

- **作用：** 从当前上下文推荐一个下一 Skill 或一个 bounded workflow recipe。
- **调用：** User-invoked only；永不执行推荐结果。
- **包：** [skills/ask-light/](skills/ask-light/)
- **状态：** 第一方已准入；支持显式 `next` 和 `workflow` 模式。
- **证据：** [scanner tests](skills/ask-light/tests/)；[使用指南](docs/zh-CN/skills/ask-light.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/ask-light/`。

### learn-anything

- **作用：** 将证据充分的对话、笔记、workflow 或资料转成可复用 Agent Skill 方法。
- **调用：** User-invoked only。
- **包：** [skills/learn-anything/](skills/learn-anything/)
- **状态：** 第一方已准入；保留 source-sufficiency 与 deterministic package-build 边界。
- **证据：** [package contract](skills/learn-anything/SKILL.md)；[使用指南](docs/zh-CN/skills/learn-anything.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/learn-anything/`。

### manuscript-ops

- **作用：** 管理从小型笔记到多语言、多格式交付的文稿工程。
- **调用：** Model-invoked，支持手动入口。
- **包：** [skills/manuscript-ops/](skills/manuscript-ops/)
- **状态：** 第一方已准入；generic review mechanics 委托给 `review-loop`。
- **证据：** [package contract](skills/manuscript-ops/SKILL.md)；[使用指南](docs/zh-CN/skills/manuscript-ops.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/manuscript-ops/`。

## 来源边界

| 状态 | 所属位置 | 目录处理 |
| --- | --- | --- |
| First-party | 本仓库 | 准入后列在上方。 |
| Direct upstream | 原始上游仓库 | 作为 dependency 说明，不能复制到这里。 |
| Modified third-party | `skills-3rdParty` | 仅在私有仓库的 source catalog 中列出。 |
| Deprecated / archived | 已发布 migration record | 写明 replacement 和迁移路径。 |

参见 [维护说明](docs/MAINTENANCE.zh-CN.md) 与 [准入说明](docs/SKILL_ADMISSION.zh-CN.md)。
