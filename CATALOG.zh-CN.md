# 第一方 Skill 目录

[English catalog](CATALOG.md)

本目录从 `skills/` 下八个已准入包同步生成，是可读 inventory，不是静态 workflow router，也不代表某个 Agent host 当前已经安装了哪些 Skill。

## 集合状态

| 字段 | 值 |
| --- | --- |
| 集合 | Personal Skills Collection |
| 包数量 | 8 个已准入第一方 Skill |
| 当前状态 | 已发布 v0.1.4；`light-kanban-worker` 经独立 `review-loop agent-skill` `PASS` 准入 |
| 稳定版本 | [v0.1.4](https://github.com/LightDevCoder/skills/releases/tag/v0.1.4) |
| 安装权威 | [docs/INSTALLATION.zh-CN.md](docs/INSTALLATION.zh-CN.md) |
| 发现检查 | [test_collection_discovery.py](tests/test_collection_discovery.py) |
| 证据 | [v0.1.4 发布证据](docs/evidence/releases/v0.1.4/RELEASE_RECEIPT.zh-CN.md) |

稳定 `v0.1.1` 包含原来的五个包；v0.1.2 加入 `recap` 与 `language-learning`，
共七个已准入第一方 Skill；v0.1.3 保持同样的七个包并迁移了测试工具链；
v0.1.4 加入 `light-kanban-worker`，共八个已准入包。

## 已准入 Skill

### ask-light

- **作用：** 从当前上下文推荐一个下一 Skill 或一个 bounded workflow recipe。
- **调用：** 仅 user-invoked；永不执行推荐结果。
- **包：** [skills/ask-light/](skills/ask-light/)
- **状态：** 第一方已准入；支持显式 `next` 和 `workflow` 模式。
- **证据：** [scanner tests](skills/ask-light/tests/)；[使用指南](docs/zh-CN/skills/ask-light.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/ask-light/`。

### language-learning

- **作用：** 通过六种学习模式辅导任意目标语言——每日课程、即时卡片、对话练习、语法解码、进度测验与沉浸翻译。
- **调用：** 仅 user-invoked。
- **包：** [skills/language-learning/](skills/language-learning/)
- **状态：** 已通过纯提示型快速通道 `PASS` 准入；v0.1.2 中发布。
- **证据：** [package tests](skills/language-learning/tests/)、[使用指南](docs/zh-CN/skills/language-learning.md)与[准入证据](docs/evidence/admissions/language-learning/README.zh-CN.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/language-learning/`。

### learn-anything

- **作用：** 将证据充分的对话、笔记、workflow 或资料转成可复用 Agent Skill 方法。
- **调用：** 仅 user-invoked。
- **包：** [skills/learn-anything/](skills/learn-anything/)
- **状态：** 第一方已准入；保留 source-sufficiency 与 deterministic package-build 边界。
- **证据：** [package contract](skills/learn-anything/SKILL.md)；[使用指南](docs/zh-CN/skills/learn-anything.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/learn-anything/`。

### light-kanban-worker

- **作用：** 每次定时运行领取并执行一张 Light-Kanban 任务，交回人工验收；先继续自己持有的任务和 review feedback，再领取新任务。
- **调用：** Model-invoked，支持手动入口。
- **包：** [skills/light-kanban-worker/](skills/light-kanban-worker/)
- **状态：** 通过完整准入路径（`review-loop agent-skill` `PASS`）准入；v0.1.4 中发布。
- **证据：** [contract 与 behavior 测试](skills/light-kanban-worker/tests/)、[使用指南](docs/zh-CN/skills/light-kanban-worker.md)与[准入证据](docs/evidence/admissions/light-kanban-worker/README.zh-CN.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/light-kanban-worker/`。

### manuscript-ops

- **作用：** 管理从小型笔记到多语言、多格式交付的文稿工程。
- **调用：** Model-invoked，支持手动入口。
- **包：** [skills/manuscript-ops/](skills/manuscript-ops/)
- **状态：** 第一方已准入；generic review mechanics 委托给 `review-loop`。
- **证据：** [package contract](skills/manuscript-ops/SKILL.md)；[使用指南](docs/zh-CN/skills/manuscript-ops.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/manuscript-ops/`。

### project-init

- **作用：** 从最小 preset 初始化项目，保留既有指令并验证结果路径。
- **调用：** 仅 user-invoked。
- **包：** [skills/project-init/](skills/project-init/)
- **状态：** 第一方已准入。
- **证据：** [package tests](skills/project-init/tests/)；[使用指南](docs/zh-CN/skills/project-init.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/project-init/`。

### recap

- **作用：** 用严格一行总结当前 Agent session，不继续工作，也不改变会话历史。
- **调用：** 仅 user-invoked；唯一入口是 `$recap`。
- **包：** [skills/recap/](skills/recap/)
- **状态：** 已通过纯提示型快速通道 `PASS` 准入；v0.1.2 中发布。
- **证据：** [package tests](skills/recap/tests/)、[使用指南](docs/zh-CN/skills/recap.md)与[准入证据](docs/evidence/admissions/recap/README.zh-CN.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/recap/`。

### review-loop

- **作用：** 在 target 和 acceptance source 已定义后，执行通用的 final-acceptance 和 bounded-repair loop。
- **调用：** Model-invoked，支持手动入口。
- **包：** [skills/review-loop/](skills/review-loop/)
- **状态：** 第一方已准入；包含 generic、software、specification、manuscript、agent-skill Profiles。
- **证据：** [Profile tests](skills/review-loop/tests/)；[使用指南](docs/zh-CN/skills/review-loop.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/review-loop/`。

## 来源边界

| 状态 | 所属位置 | 目录处理 |
| --- | --- | --- |
| First-party | 本仓库 | 准入后列在上方。 |
| Direct upstream | 原始上游仓库 | 作为 dependency 说明，不能复制到这里。 |
| Modified third-party | `skills-3rdParty` | 仅在私有仓库的 source catalog 中列出。 |
| Deprecated / archived | 已发布 migration record | 写明 replacement 和迁移路径。 |

参见 [维护说明](docs/MAINTENANCE.zh-CN.md) 与 [准入说明](docs/SKILL_ADMISSION.zh-CN.md)。
