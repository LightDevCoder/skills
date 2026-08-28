# 变更记录

[English changelog](CHANGELOG.md)

所有变更都必须记录在实际版本/tag 对应的条目中，不能因为文档已起草就提前宣称 release。

## 未发布

### 变更

- **ask-light 混合路由器：** `ask_light.py` 现为确定性证据检查器。对于已初始化但无活跃 SPEC 的项目，返回结构化证据（`projectEvidence`），不再给出确定性 Skill 推荐。模型拥有语义工作流判断权——根据证据、对话上下文和 Skill 合约在 `project-clarify`、`project-spec`、`research`、`prototype` 等候选者中做出决策。硬确定性路由（未初始化 → `project-init`、活跃评审 → `project-review`、模糊 effort → fail closed 等）保持代码所有权不变。
- **ask-light 证据字段：** `inspect_project_state` 返回 `projectContract`（目标/产出/约束状态）、`researchArtifacts` 和 `clarificationArtifacts` 供模型推理。`initialized-no-spec` 与 `initialized-unclear` 阶段替换为单一 `initialized` 阶段加事实性证据字段。
- **ask-light SKILL.md：** 记录混合架构、模型拥有的工作流判断、Skill 前置条件、澄清就绪性、推荐质量合约及硬证据覆盖规则。
- **ask-light discovery-contract.md：** Layer 0 更新为证据检查器/模型推理分离。

### 新增

- **混合路由器回归测试：** Worktable 回归测试（init + research + 无澄清 → `project-clarify` 证据）、已澄清项目反向回归测试（澄清就绪文件 → `project-spec` 证据）、硬确定性路由保护、模糊 effort fail-closed、证据检查器单元测试及可用 Skill 合约验证。`HybridRouterRegressionTest` 新增 15 个测试。

## 0.2.0 — 2026-08-28

### 新增 — 33 包 Light 工作流架构

- **Project Workflow（7）：** `project-init`（重构为最小初始化）、`project-clarify`、`project-spec`、`project-tickets`、`implement`、`project-review`、`release-workflow`（自 `LightDevCoder/release-workflow` 迁移）。
- **Clarification & Research（7）：** `socratic`（核心引擎，来自 Matt `grilling`）、`clarify`（`grill-me`）、`project-clarify`（`grill-with-docs`）、`decision-map`（`wayfinder`）、`research`、`prototype`、`to-questionnaire`——以 `socratic` 为共享引擎。
- **Planning（2）：** `project-spec`（`to-spec`）、`project-tickets`（`to-tickets`）。
- **Execution（5）：** `agent-config`（新增，host-agnostic，参照 Sol Advisor）、`implement`（Matt `implement` → 通用执行器）、`tdd`、`diagnosing-bugs`、`resolving-merge-conflicts`。
- **Review（4）：** `review-loop` 重构为轻量引擎 + `generic-review`（新增默认 reviewer）+ `code-review`（Adapt）+ `project-review`（新增，拥有冻结 baseline 与最终 `PASS`/`FAIL`/`BLOCKED`，自旧 `review-loop` 迁移）。
- **Productivity & Communication（4）：** `handoff`、`wizard`、`wait-what`、`writing-for-agents`（Matt PORT）。
- **Learning（3）：** `eli5`（源自上游 `DreambigOu/ELI5` @ `a766623`，经临时迁移 fork `LightDevCoder/ELI5`）、`teach`（PORT）、`language-learning`（保留）。
- **Router（1）：** `ask-light` 最后重构为跨 33 Skill 的 Light Workflow Router。
- **Specialized Workflows（8）：** `manuscript-ops`、`kb-init`、`learn-anything`、`language-learning`、`kanban-worker`、`recap`、`eli5`、`release-workflow`——已做 standalone + composition 验证，仅在真实缺口处加最小 handoff。

合计 **33** 个第一方 Skill（见 [CATALOG.zh-CN.md](CATALOG.zh-CN.md)）。

已批准的 Matt PORT（11 个）各带 `ATTRIBUTION.md` 且无上游运行时依赖：`research`、`prototype`、`tdd`、`handoff`、`diagnosing-bugs`、`wizard`、`teach`、`wait-what`、`to-questionnaire`、`writing-for-agents`、`resolving-merge-conflicts`。保留上游行为；Light 变更限于运行时解耦与 handoff 串联。

### 变更

- **治理：** `AGENTS.md` 明确权威参照（Matt Pocock Skills 用于 Skill 写作；Sol Advisor 用于 `agent-config`）与 14 条维护规则（检查上游、不重写成熟 Skill、不重设 PORT、`SKILL.md` 精简、supporting-files 披露、不统一包形态、组合优于复制、不重复架构等），不膨胀为 SPEC。
- **准入：** `docs/SKILL_ADMISSION.zh-CN.md` 允许 SPEC 授权的 Port（需 attribution、Light 集成且无上游运行时依赖，`Port ≠ 任意复制`）。
- **审查：** `docs/REVIEW_POLICY.zh-CN.md` 区分 `reviewer`（→ findings） vs `review-loop`（引擎） vs `project-review`（最终验收），与 [Reviewer 契约](docs/REVIEWER_CONTRACT.zh-CN.md) 同步；final-acceptance 已从 `review-loop` 迁至 `project-review`。
- **维护：** `docs/MAINTENANCE.zh-CN.md` 更新为真实流程（add/update/rename/remove/port/adapt + 文档/目录/测试/attribution 同步 + release handoff）。
- **安装：** `docs/INSTALLATION.zh-CN.md` 同步 33 包（当前分支 33，最后稳定版 `v0.1.6` 9 包），明确 Light 主流程运行时不需要 `mattpocock/skills` 或 `sol-advisor`。
- **工作流：** `docs/zh-CN/workflows/` 负责仓库级组合（`project-workflow.md`、`clarification-system.md`、`execution.md`、`review-system.md`、`specialized-workflows.md`——各讲 `entry → handoff → stop → optional`，不复制 Skill 内流）。
- **头图：** `README.zh-CN.md` 首行改为 `Assets/header.png`；可编辑遗留头图仍在 `skills/docs/assets/skills-header.svg` / `.png`。
- **测试：** 保留有效行为测试；将锁旧架构的测试更新为 33 包、组合 handoff 与头图/双语检查。

### 变更 — Lean 架构重构

- **SKILL.md 作为最小可执行接口：** 全量重构 Skill（`agent-config`、`ask-light`、`clarify`、`code-review`、`decision-map`、`generic-review`、`implement`、`project-clarify`、`project-init`、`project-review`、`project-spec`、`project-tickets`、`review-loop`、`socratic`）现在直接暴露核心执行行为，条件性格式/示例/专项指导保留在 Skill 自有的 supporting files。
- **组合优于复制：** `review-loop` 是轻量评审引擎；`project-review` 拥有最终 `PASS`/`FAIL`/`BLOCKED`；调用方只命名 Skill，不再复述其内部 runbook。
- **测试：** 非契约的字面措辞断言已放宽；根 discovery/composition 测试已更新为 `project-review` 作为最终验收命令。
- **规划状态：** 旧 `.scratch/light-skills-refactor/` 已归档/废弃；`.scratch/light-skills-lean-refactor/` 成为唯一活动规划集，含逻辑重构分析与实施 tickets。
- **Frozen 完整性：** 五个 Frozen Skills（`eli5`、`language-learning`、`kb-init`、`kanban-worker`、`learn-anything`）保持逐字节不变并通过 hash 验证。2026-08-27 用户明确修改活动范围：`recap` 删除说明性正文，只保留一条手动执行语句。

### 变更 — 功能闭环

- **ask-light：** 新增 Light 自有 33-Skill 语义地图，分离逻辑路由与 host availability；UI metadata 改为可选；generic root 不再作为第一方来源；补齐 Codex/Claude/通用调用展示；Python router 成为全平台测试实现，PowerShell 保留为兼容 launcher。
- **项目 bootstrap：** `project-init` 现在幂等写入 `docs/agents/light-project.md` 与 issue-tracker 契约；下游 Project Skills 只消费所需字段。preset 有歧义时必须简要比较并给出推荐。
- **澄清：** 一次 `$clarify` 调用可通过普通回复持续推进；Socratic 状态默认仅内部维护，对话在有依据时给建议，完成前必须确认共同理解；unknown routing 只归 `socratic`。
- **Review 所有权：** 轻量 reviewer packet 只归 `review-loop`；acceptance registry 与 verdict 归 `project-review`；migration reference 明确为历史材料。
- **测试：** 新增代表性 top routing、空仓库 bootstrap/rerun、clarification lifecycle、本地 pointer、所有权与历史/runtime 边界测试；通过行为测试消除已修复的 prose coupling，而非恢复旧措辞。
- **recap：** 根据用户明确修订，`SKILL.md` 现在只含必需 frontmatter 与一条手动 `$recap` 执行语句；输出当前 session 的一句简洁摘要，不替换或压缩对话历史。

### No-Redesign 验证

对 18 个 `NO REWRITE/PORT` 按 `git diff` 逐个检查（SPEC §26）：`manuscript-ops`、`kb-init`、`learn-anything`、`language-learning`、`kanban-worker`、`eli5`、`release-workflow`、`research`、`prototype`、`tdd`、`handoff`、`diagnosing-bugs`、`wizard`、`teach`、`wait-what`、`to-questionnaire`、`writing-for-agents`、`resolving-merge-conflicts`——仅在真实集成需求处加最小 handoff/attribution。`recap` 是上文单独记录、经用户批准的例外。

### 发布证据

- 本重构未创建新版本、tag 或 GitHub Release。
- Discovery/composition/link/hero/双语与包契约检查：见 `tests/` 与 `python -m unittest discover`。

## 0.1.6 — 2026-08-19

### 新增

- 第一方 `kb-init` Skill：正式版知识库初始化包替换之前未发布的草稿。新增扩展核心原则（决策 provenance、开放决策 surfacing、depth before settlement）、readiness 检查、人类导航设计、research contract、connection setup/validation、backup/recovery 语义，以及 38 个回归 eval 用例。按 owner 决定，它仍是仅 user-invoked。
- 针对 `kb-init` 更新 contract 测试与双语使用指南。
- v0.1.6 发布九包集合：v0.1.1 的五个包、`recap` 与 `language-learning`（v0.1.2）、`kanban-worker`（v0.1.6 中由 `light-kanban-worker` 改名；首次发布于 v0.1.4），以及 `kb-init`。

### 变更

- `light-kanban-worker` 改名为 `kanban-worker`。包目录、`SKILL.md` name/frontmatter、`agents/openai.yaml`、测试、指南、目录、README 与安装面统一使用 `kanban-worker`。v0.1.4/v0.1.5 历史记录保留旧名并附迁移说明。
- `kb-init` 保持 explicit-only：`SKILL.md` 中 `disable-model-invocation: true`，`agents/openai.yaml` 中 `allow_implicit_invocation: false`。
- README、目录、安装指南、维护基线、discovery 测试与双语指南从 v0.1.5 八包发布边界更新为 v0.1.6 九包发布。

### Release 证据

- Release tag：`v0.1.6`，commit `e8c3589031bbc1cb76d7f928761ce3f60ebea3e1`。
- GitHub Actions `collection-quality`：release commit 上 PASS（run `32232850422`）。
- 整集合与单 Skill fresh installs：通用 `latest` 与 pinned `#v0.1.6` 形式 PASS；见 [INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.6/INSTALLATION_VERIFICATION.zh-CN.md)。
- Host discovery：[DISCOVERY_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.6/DISCOVERY_VERIFICATION.zh-CN.md)。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.6
- 最终收据：[RELEASE_RECEIPT.zh-CN.md](docs/evidence/releases/v0.1.6/RELEASE_RECEIPT.zh-CN.md)。

## 0.1.5 — 2026-08-17

### 变更

- `light-kanban-worker` 现在明确禁止同一 `LIGHT_KANBAN_AGENT_ID` 的 scheduled run 重叠执行：同一 agent id 任意时刻至多一个 invocation 活跃，上一 run 仍活跃时触发的唤醒必须 skip；不同 agent id 仍可并发。atomic claim 边界被准确记录——它保护的是两个不同 worker 同时 claim 同一张 To Do，并不是同一 agent identity 多个 invocation 的并发锁；并发控制属于 scheduler / agent runtime（`max concurrent runs = 1` 或等价的 skip-while-active 设置），worker 不新增 lock process、heartbeat 或 lease service。
- 首次注册现在明确要求 ID + name + avatar：本地图片通过 `POST /api/avatars` 上传并使用返回的 `/api/avatars/...` 路径 claim；已存在的 agent id 复用服务器保存的 name/avatar，后续唤醒无需重复 avatar。全新 agent id 缺 name 或 avatar 时报 identity configuration missing，不 claim、不改动任何任务。
- `agents/openai.yaml` default prompt 更新为可完成首次注册的 one-shot 形式（Agent ID / Name / Avatar），全新看板也能注册新身份。

### 测试

- worker contract 套件新增调度边界规则：same-agent 不得重叠、不同 agent 并发允许、atomic claim 边界、scheduler 拥有并发控制、无常驻 lock service、首次注册身份、身份复用、缺身份不得改动任务、本地 avatar 上传路径。
- 新增对抗性 negative fixtures `overlap-allowed-variant.md` 与 `avatar-optional-first-registration.md`，各自只违反一条规则且必须被拒绝。
- behavior 套件新增 Scenario G（同 agent 并发唤醒：run #1 活跃时第二个 run 不得开始处理，经 scheduler-guard fixture 验证——Light-Kanban 自身不提供 run lease）与 Scenario H（无 avatar 的新身份：不 claim、不改动、明确配置失败；提供合法 avatar 后注册与 claim 成功）。Scenarios A–F 保持不变并继续通过。
- release evidence 工作流澄清：receipt 现在区分 pre-release gate（candidate 测试、准入、catalog 同步——`READY FOR RELEASE`）与 post-release verification（已发布 tag 身份、fresh install、host discovery、release CI），已发布 tag 中不再出现令人困惑的 `PENDING` 标记。

### 证据

- Release tag：`v0.1.5`，commit `a56aa9d98de0b941ee2282144bc7e756ef5e48bd`。
- GitHub Actions `collection-quality`：release commit 上 `PASS`（run `31985455493`）。
- 契约变更的 `review-loop agent-skill` 验收：完全独立的 PASS（findings F-001/F-002/F-003/G-001 已修复）—— [AGENT_SKILL_REVIEW.zh-CN.md](docs/evidence/releases/v0.1.5/AGENT_SKILL_REVIEW.zh-CN.md)。
- Fresh installs：整集合与单 Skill、通用 `latest` 与 pinned `#v0.1.5` 形式，CLI `1.5.22` —— PASS；安装包与 tag 逐字节一致且套件可独立运行。见 [INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.5/INSTALLATION_VERIFICATION.zh-CN.md)。
- Host discovery：[DISCOVERY_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.5/DISCOVERY_VERIFICATION.zh-CN.md)。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.5
- 最终收据（pre-release gate + post-release verification）：[RELEASE_RECEIPT.zh-CN.md](docs/evidence/releases/v0.1.5/RELEASE_RECEIPT.zh-CN.md)。

## 0.1.4 — 2026-08-16

### 新增

- 新的第一方 model-invoked Skill `light-kanban-worker`：每次 scheduled agent 运行最多处理一张 Light-Kanban 任务——稳定 agent identity、先检查自己持有的 in-progress 任务与 `reviewFeedback` 再领取新任务、原子 claim 带有限次冲突重试、workspace 校验（不可访问的 workspace 变成 `block` 并带具体原因）、`complete` 交回人工验收。worker 绝不 archive、accept、delete、recycle、unblock，也绝不循环或常驻进程。因其涉及网络/文件系统/看板状态副作用，走完整准入路径（`review-loop agent-skill`），不走纯提示型快速通道。
- worker 包的 contract 与 behavior 测试套件，包含 positive fixtures 与 negative fixtures（对抗性单规则 fixture 文件）及 frontmatter YAML 安全门。
- ask-light behavior 套件新增 outside-readable-path negative 场景。

### 变更

- 版本文档同步：v0.1.4 为当前稳定 release，v0.1.3 及更早版本保持历史记录。README、目录、安装指南、维护基线、discovery 测试与 CI 更新为八包集合。
- 修复 ask-light scanner 的 `Test-PathUnder` 路径比较（硬编码 Windows 分隔符），该问题使 collection-quality workflow 自 v0.1.3 Python 移植起在 ubuntu-latest 上失败。

### Release 证据

- Release tag：`v0.1.4`，commit `a9cc8aa029c926fc80f6ddc0022793f79dfd85bd`。
- GitHub Actions `collection-quality`：release commit 上 `PASS`（run `31962459531`）。
- 整集合与单 Skill fresh installs：`PASS`（CLI `1.5.22`，通用 `latest` 与 pinned `#v0.1.4` 形式）。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.4
- 整集合与单 Skill fresh-install 证据：[INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.4/INSTALLATION_VERIFICATION.zh-CN.md)。
- 结构与包级证据：[TEST_SUMMARY.zh-CN.md](docs/evidence/releases/v0.1.4/TEST_SUMMARY.zh-CN.md)。
- 准入：[light-kanban-worker 证据](docs/evidence/admissions/light-kanban-worker/README.zh-CN.md)。
- scanner code-review：[CODE_REVIEW.zh-CN.md](docs/evidence/releases/v0.1.4/CODE_REVIEW.zh-CN.md)。
- 原有五个包的独立 `review-loop agent-skill` acceptance 仍为 `BLOCKED`；见 [发布收据](docs/evidence/releases/)。

## 0.1.3 — 2026-08-10

### 变更

- 测试工具链从 Windows PowerShell 迁移为跨平台 Python：21 个 PowerShell 测试文件替换为 18 个 Python 套件（collection discovery、header assets、quick start、ask-light contract、project-init contract 与 behavior、recap 两个 contract、language-learning contract、review-loop 五个 profile 的 contract 与 behavior 套件及协议 helpers），保留断言集。
- ask-light behavior 套件在所有 host 直接执行可移植 Python router；`scripts/ask-light.ps1` 仅保留为轻量兼容 launcher。
- CI 迁至 `ubuntu-latest`（bash + python）；新增 retired-boundary 与 无 PowerShell 测试检查。
- 文档更新为新测试文件名与跨平台手动 fallback 片段；治理措辞不变。

### 证据

- [docs/evidence/releases/v0.1.3/](docs/evidence/releases/v0.1.3/)

## 0.1.2 — 2026-08-10

### 新增

- 为 v0.1.2 准备第一方、仅 user-invoked 的 `recap` Skill。用户显式调用 `$recap` 后只返回一行当前 session 总结；不会运行工具、继续任务、修改文件、压缩历史或调用其他 Skill。
- 为 v0.1.2 准备第一方、仅 user-invoked 的 `language-learning` Skill。它通过六种学习模式辅导任意目标语言——每日课程、即时卡片、对话练习、语法解码、进度测验与沉浸翻译——并在多次调用之间复用会话上下文与已学词汇，而不是每次都重新询问。
- 新增低风险纯提示型准入快速通道：仅适用于 owner-authored、manual-only、只输出文本、无工具/副作用/runtime executable/外部依赖的 Skill；只需一个 fresh Evaluator，不再要求额外 Critic 或 Standards/Spec review。
- 发布通用 `latest` 安装命令（`npx skills add LightDevCoder/skills --yes --copy --agent '*'`）作为标准安装路径，并保留 pinned `#v0.1.2` 形式用于可复现安装。`recap` 与 `language-learning` 均由 fresh independent prompt-only fast-track Evaluator `PASS` 准入，见各自[准入证据](docs/evidence/admissions/)。

### Release 证据

- Release tag：`v0.1.2`，commit `8de5ec1a453b0e93f71dcda160e17ea7b42c3997`。
- 合并后的 release commit 上 GitHub Actions `collection-quality`：`PASS`。
- 整仓和单 Skill fresh install：使用 CLI `1.5.22`，通用 `latest` 与 pinned `#v0.1.2` 两种形式均为 `PASS`。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.2
- 整仓与单 Skill fresh-install 证据：[INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.zh-CN.md)。
- 结构与包测试证据：[TEST_SUMMARY.zh-CN.md](docs/evidence/releases/v0.1.2/TEST_SUMMARY.zh-CN.md)。
- 原有五个包的独立 `review-loop agent-skill` acceptance 仍为 `BLOCKED`；见 [发布收据](docs/evidence/releases/v0.1.2/RELEASE_RECEIPT.zh-CN.md)。

## 0.1.1 — 2026-07-26

### 新增

- 五个第一方 Skill 的双语用户指南、已验证的 workflow recipes 和可运行大小的 Quick Start 示例。
- `docs/evidence/releases/v0.1.1/` release 证据目录，以及覆盖结构、metadata、链接、双语配对、包测试、退休引用和头图的 CI 检查。
- 显式 `$ask-light next` 与 `$ask-light workflow` 模式，包含 bounded recipe、availability gap、handoff 字段和不执行测试。
- 可编辑 SVG 与 1600 × 480 PNG 头图：平面叠层的 `LightDevCoder` / `/skills` wordmark 和 serif slogan。

### 修复

- 为 user-invoked 的 `learn-anything`、`ask-light`、`project-init` 补齐 `policy.allow_implicit_invocation: false` 及对应 frontmatter。
- 修正安装语义：无 fragment 的仓库来源遵循 CLI 默认 revision，发布后 `#v0.1.1` 才是固定 target tag。

### Release 证据

- Release tag：`v0.1.1`，commit `c50f1ef403a5f0bfe02e75d1aeff2c237556db63`。
- 合并后的 release commit 上 GitHub Actions `collection-quality`：`PASS`。
- 整仓和单 Skill fresh install：使用 CLI `1.5.20`，均为 `PASS`。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.1
- 整仓与单 Skill fresh-install 目标记录：[INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md)。
- 结构与包测试证据：[TEST_SUMMARY.zh-CN.md](docs/evidence/releases/v0.1.1/TEST_SUMMARY.zh-CN.md)。
- 五个包组成的集合仍可安装，`collection-quality` 检查已通过。`review-loop agent-skill` acceptance gate 的独立 evaluator 证据仍为 `BLOCKED`；这不影响一般安装或使用。准确证据边界见[发布收据](docs/evidence/releases/v0.1.1/RELEASE_RECEIPT.zh-CN.md)。

## 0.1.0 — 2026-07-23

- 建立第一方治理基础并准入五个第一方 Skill。
- 已发布于 https://github.com/LightDevCoder/skills。
- 稳定 tag：v0.1.0。
- v0.1.0 的整集合与单 Skill 安装命令曾针对 fresh destination 和已发布包内容完成验证；这份历史证据与 v0.1.1 release 证据一并保留。
- 历史命令：`npx skills add LightDevCoder/skills` 和 `npx skills add LightDevCoder/skills --skill review-loop`。
- 历史安装明细：[v0.1.0 摘要](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md#历史-v0.1.0-摘要)。
