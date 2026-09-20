# 变更记录

[English changelog](CHANGELOG.md)

所有变更都必须记录在实际版本/tag 对应的条目中，不能因为文档已起草就提前宣称 release。

## Unreleased — target v0.2.4

### 变更 — 发布完整性加固与 Git 对象严格绑定

- **Git 对象发布证据绑定：** 将发布清单与发布说明的校验直接绑定至不可变的 Git tree 对象快照（`candidate_commit` 与 `refs/tags/vX.Y.Z^{commit}`），彻底防止工作区未提交或未跟踪文件穿透门禁。
- **发布后收据快照严格隔离：** 发布收据中的准入包总数校验强制绑定至发布时不可变候选快照（`release_revision`），防止后续 `main` 分支包增减漂移污染已发布版本的事实证明。
- **Fail-Closed 单向 Tag Preflight 门禁：** Tag 预检默认校验 `origin` 远端状态，网络或鉴权失败时严格阻塞（`BLOCKED`）；本地或远端已存在 Tag 时严格阻断，确保单向、安全发布。
- **严格 Annotated Tag 校验：** 强制要求发布 Tag 必须为 Annotated Tag 对象（`git cat-file -t` 返回 `tag`），全生命周期拒绝 lightweight tag。
- **独立 TAGGED 阶段复审支持：** 明确 `check_receipt_absence_in_candidate` 在传入 `revision` 时仅检查 Git 快照，允许在完成 post-publication attestation 后重新执行 `stage=tagged` 复核通过，杜绝工作区收据干扰。
- **零 Traceback 结构化失败机制：** 审计校验分支与规范显示路径，确保所有异常或错误均以标准 `VerificationResult` 结构化返回，杜绝 Python 未定义变量 traceback。
- **公开文档质量门禁：** 全面统一 `README.md`、`CATALOG.md`、`INSTALLATION.md` 中英文术语及调用/状态对称性，去除 AI 写作痕迹。

## 0.2.3 — 2026-09-21

### 变更 — 发布证据生命周期与清单架构解耦

- **发布前清单与发布后收据分离：** 彻底解耦发布前不可变规格（`RELEASE_MANIFEST.md`，直接固化于 Release Tag 快照内）与发布后验证事实证明（`RELEASE_RECEIPT.md`，存于 `main` 分支）。
- **形式化六阶段发布生命周期模型：** 确立明确的状态流转架构：`PREPARED → CI_VERIFIED → TAGGED → INSTALL_VERIFIED → PUBLISHED → ATTESTED`。
- **v0.2.2 发布后事实证明与历史溯源追加：** 详细记录 v0.2.2 发布的历史事实、初始 CI 在浅检出环境下的失败根因以及后续纠正性提交（`0862a19...`）。
- **自动化发布完整性校验机制增强：** 在 `scripts/verify_release_integrity.py` 中增加对 v0.2.3+ 的清单校验及收据目标 commit 比对，并在 `tests/test_release_integrity.py` 中新增密封单元测试。

### 重构 — `project-retro` 正向指令风格与状态驱动架构

- **正向职责与流程指令表达：** 将面向 Agent 的指令全面调整为目标、职责、流程、信息流与状态转换驱动的正向表达。
- **建议动作生命周期状态机：** 显式定义复盘结论交付状态为 `AWAITING_SELECTION`；在人类用户做出显式选择后，将选定项流转为 `APPROVED_ACTION` 进而进入有界执行。
- **工程审计沟通：** 严格基于已验证的代码库事实、当前 HEAD 状态与测试结果展开，聚焦系统、流程、信息架构、防护栏与工具经济性。
- **已闭环经验隔离与顺畅运行处理：** 明确 `[CLOSED]` 结论代表已有持久防护机制保护的历史经验，保留于复盘事实中但坚决排除在 Suggested Actions 之外；无复发性系统摩擦的常规任务直接完成，不触发复盘。

## 0.2.2 — 2026-09-20

### 新增 — TypeSafe Jev System One 语义加速最终收敛（`ask-light`, `agent-config`, `project-init`）

- **`ask-light` 活跃消费者查询规划与有界语义路由：** 引入活跃消费者查询规划架构，Python 证据引擎独占工作流法定权威。Jev Choice 严格仅在多合法候选时（`len(allowed_actions) > 1`）发送；单一候选集自动跳过 Choice。有界 Noul 仅在存在活跃消费者时触发（关键歧义用于引导至 `project-clarify` 或在存在模糊实现请求时提示澄清；深度推理升级用于提示 `agent-config`）。彻底移除执行意图相关查询；Jev 绝不赋予工作流流转授权，零价值查询自动跳过。提供紧凑状态脱敏构建（<350 字符），杜绝源码与文件树泄露。
- **`project-init` 规范 Skills CLI 映射与 Jev 生态接入：** 增加可选交互式接入门禁（`--jev` / `--no-jev`）。完全遵循 `vercel-labs/skills` v1.7.0 CLI 规范 Agent 标识映射（`pi`, `claude-code`, `cursor`, `codex`, `antigravity`, `grok`, `hermes-agent`）与规范项目作用域（`.agents/skills` 适用于 Cursor、Codex 与 Antigravity；`.pi/skills` 适用于 Pi 等）。未支持环境（如 DSH）严格确定性 Fail-Closed（`TARGET_UNRESOLVED`）。安全凭据解析（优先环境变量，其次项目 `.env`），写入本地凭据前强制校验 `.env` 已加入 `.gitignore`；支持全局技能复用。
- **`agent-config` 抽象任务画像与临时非对称降级防御：** 引入跨厂商解耦的抽象任务画像（routine, standard, high）与推理需求评估（low, medium, high）。无标签泄露的独立干净评测，权威输入完全由代码独占。执行临时非对称降级防御策略（置信度 `>= 0.75` 且边界裕度 `>= 0.15`，策略状态：`PROVISIONAL`）。真实评测实证（AC-02）安全拦截临界降级提议（分值 0.41，置信度 0.59），正确保留标准基线档位（`claude-3-5-sonnet`）。
- **Fail-Closed 与零外部依赖平滑降级：** 采用软依赖机制；未配置 `TYPESAFE_API_KEY` 或离线时，所有技能优雅退回确定性规则基准，保持全量测试套件零回归。

### 新增 — 七大职责分类目录归整（36 个已准入 Skill）

- 将全部 36 个 Skill 收纳至 `skills/` 下的七大分类目录：`project/`, `thinking/`, `engineering/`, `review/`, `knowledge/`, `writing/`, `productivity/`。
- 丰富各分类中英文集合指南，更新源码发现、安装指引与 CI 验证，完全保留宿主端平铺安装（`<skills-root>/<name>/`）与官方 CLI 选装（`--skill <name>`）兼容性。

### 变更 — 发布完整性与 Release Tag 不可变性政策

- 正式确立自 v0.2.2 起的发布 Tag 永久不可变性政策：已发布的 Tag 绝不强制移动、绝不重指向、绝不重写代码边界。
- 阐明并修复了 v0.2.1 在 Jev 集成演进周期中因 Tag 重指向产生的发布溯源问题。发布证据见：[v0.2.2 发布收据](docs/evidence/releases/v0.2.2/RELEASE_RECEIPT.zh-CN.md)。

## 0.2.1 — 2026-09-16

*(发布溯源说明：v0.2.1 最初于 2026-09-16 在 commit `70a48ef4c81b9b9f40604a43f2914e5467be4269` [收据记录为 `cb17b17c8227b7d7211e4bf5b72223703d987d60`] 正式发布，包含 project-retro、light-travelpage 与 agent-config 的 Profile 架构重构。在随后的 Jev 集成加固迭代周期中其 Tag 曾被移动以跟随开发演进 [`6f9d173`，后至 `27f16e4`]。v0.2.2 为最终收敛的 Jev 集成确立全新的不可变发布边界。)*

### 新增 — project-retro 技能与工作流复盘集成（第 36 个包）

- **project-retro 技能：** 新增第一方模型调用（model-invoked）Skill，用于对已完成的项目或编码会话进行复盘，识别智能体环境、自动化守护线、文件导航、工具经济性、引导指令及运行信息中的具体改进点。移植并适配自 Matt Pocock 的 `retro`（`959a8e9f1edc3adbe2f7e3054bb6fbefa6696260`），完整保留归属，运行时完全自包含无外部依赖。
- **工作流终点自主复盘评估：** 在项目工作流终点（`project-review` 完成最终验收或 `release-workflow` 执行完成后），由 Agent 自主判断是否触发复盘。检查执行中是否存在摩擦信号（导航瓶颈、缺失自动化检查、规范歧义、引导指令膨胀、工具效率低、运行信息缺失），有摩擦时触发 `project-retro` 输出结构化建议，顺畅无阻时干净跳过，不产生任何干扰与 token 开销。

### 新增 — Light-TravelPage（第 35 个包）

- **Light-TravelPage：** 收录第 35 个第一方包 `light-travelpage`（模型调用）：移动优先旅行页面生成与展示，支持中英双语切换、航班/住宿卡片、区域地图生成、离线优先费用账本及 Cloudflare Pages/Functions/D1 协同多端同步。
- 保留上游 MIT 素材和固定版本 ATTRIBUTION；增加冲突/幂等恢复、严格校验和 34 项测试。

### 重构 — agent-config Profile 权威、执行配置与 Companion 运行时

- **Profile 权威驱动的执行配置器：** 将 `skills/agent-config` 重构为基于真实宿主能力证据与用户确认 Profile 档位（`routine`、`standard`、`high`、`review`）的执行配置器，映射为适配的执行拓扑（单模型/多模型 × 单次/拆票；Case A、B、C、D）。返回规范的 `AgentConfigResult`（`READY`、`NEED_INPUT`、`NEED_PROJECT_TICKETS`、`BLOCKED`、`UNSUPPORTED`）。
- **Profile 权威优于模型强弱猜测：** 彻底剔除启发式模型打分（`routing_rank`）与从模型名称猜测智能。档位绑定与推理需求完全由用户在 Profile 中确认，并对照宿主真实呈现的模型进行校验。
- **宿主中立推理与 Effort 精准解析：** 抽象推理策略直接解析为宿主真实支持的具体参数值（`supported_reasoning_efforts` 或 `reasoning_effort_hierarchy`），严禁凭空捏造未支持值。
- **Companion MCP 运行时与 10 个原生适配器：** 制定可选 Companion MCP 运行时契约（`protocol_version: 1`，8 个规范 MCP 工具：`get_setup_status`、`inspect_host`、`get_profile`、`save_profile`、`preview_configuration`、`apply_configuration`、`validate_configuration`、`reset_profile`），覆盖 10 种原生 Harness（Codex、Claude Code、Antigravity / agy、DeepSeek Harness / DSH、OpenCode、ZCode、Cursor、Grok Build、Hermes、Pi）以及通用 plan-only 回退（Pi MCP 需单独安装扩展）。Companion 运行时维护于 `LightDevCoder/agent-config`。在无 Companion 时保持纯计划模式正常可用。
- **Companion 健康度与 Setup Gate：** 增加 Companion 健康探测语义（`agent-config setup --check`、实时 MCP 传输协议版本、规范工具 schema 校验）与非阻塞 Setup Gate（`agent-config setup`、`NEED_INPUT` / `UNSUPPORTED`），支持显式宿主探测与先预览后应用的变更控制。
- **Skill ↔ Companion 集成闭环：** 下游工作流消费规范化 `AgentConfigResult`；`implement` 保持 agent-config 为可选增强而不阻塞独立执行；`ask-light` 将 setup 意图路由至 `agent-config setup`，同时严格保持就绪工单路由至 `implement`、复杂拆分路由至 `project-tickets`。
- **Pi 集成与 MCP 修复：** 纳入 Pi 适配器，明确扩展、版本、项目信任、provider/model 和 effort 证据边界。

### 变更 — 自主权边界与工作流完成度

- 明确 `tdd`、`clarify`、`implement`、`review-loop`、`manuscript-ops` 的授权复用与阶段完成边界。保留明确批准、调用、审阅轮数和独立验收要求；仅允许有证据支持的可选路由回退。[范围与验证](docs/evidence/maintenance/2026-09-16-autonomy-boundaries.md)。

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

合计 **34** 个第一方 Skill（见 [CATALOG.zh-CN.md](CATALOG.zh-CN.md)）——下文的 33 包架构之外新增 `humanizer`。

已批准的 Matt PORT（11 个）各带 `ATTRIBUTION.md` 且无上游运行时依赖：`research`、`prototype`、`tdd`、`handoff`、`diagnosing-bugs`、`wizard`、`teach`、`wait-what`、`to-questionnaire`、`writing-for-agents`、`resolving-merge-conflicts`。保留上游行为；Light 变更限于运行时解耦与 handoff 串联。

### 新增 — humanizer skill（第 34 个包）

- **humanizer skill：** 新的第一方 model-invoked Skill，将带有 AI 痕迹的中英文文本改写为自然行文，且不改变原意。改编自 blader/humanizer `e2e92e7`（版本 2.11.2），模式册逐字保留；新增 Language routing 节与 `references/zh-adaptation.md` 薄中文适配层（破折号/标题大写/弯引号/连字符合成词的中文覆盖规则、其余模式的中文映射与中文 AI 高频词表、反编造守则、中文误报豁免）。中文词汇参考 MIT 许可的 op7418/Humanizer-zh（`91f3d39`）。经 full-path `review-loop agent-skill` 验收准入——第 1 轮 `PASS`，一个 minor 归属措辞 finding 已修复；证据见 [docs/evidence/admissions/humanizer/](docs/evidence/admissions/humanizer/README.zh-CN.md)。

### 变更 — 发布后加固（agent-config / implement / ask-light）

- **agent-config 宿主中立化重构：** 将 `agent-config` 重构为区分当前可执行模型与模型可选择性（`model_selection` / `per_agent_model_selection`）。对于具备当前可执行模型但缺少模型选择器或子代理的宿主环境，安全降级至单模型多代理或单模型单代理路径，不再返回 `BOUNDARY`。
- **implement 中 agent-config 用户显式自选：** 重构 `implement` 使其绝不自动调用 `agent-config`。当编排（角色拆分、并行、评审隔离）有实质帮助时，向用户提供显式选择；用户拒绝或在无模型选择能力的宿主上运行时绝不阻塞正常实现。简单的独立任务直接执行，不打扰用户。
- **ask-light 模型主导混合顾问重构：** 将 `ask-light` 重构为模型主导的工作流顾问，采用五阶段架构：（1）请求意图解析（模型），（2）项目/宿主事实收集（代码），（3）候选 Skill 理解（模型 + 紧凑目录元数据），（4）最终工作流判断（模型），（5）选择验证与转换（代码 + 宿主能力）。
- **规范项目流对齐：** 在 `ask-light`、配方、地图与文档中恢复 `project-clarify → project-spec → project-tickets → implement → project-review` 规范链路，移除了在 `project-tickets` 前插入 SPEC-review 门禁的逻辑。
- **严格作用域与验证安全：** 增加严格作用域词汇校验（`current-workflow`、`independent`、`standalone`）、显式 `Skill: none` 仅在真实 accepted 阶段允许通过的验证，以及显式批准跨轮次的作用域保留与缺失/非法作用域 fail-closed 机制。
- **受信任宿主能力证据：** 明确已批准用户调用转换的受信任宿主能力通道要求，拒绝模型/上下文 JSON 伪造与未验证布尔值，在缺少真实宿主通道时安全降级为渲染精确调用（`host-transition-required`）。
- **内容验证的澄清就绪性：** 增强澄清就绪性判定，要求具备生产者契约标识与目标（`readyFor: project-spec`）。
- **ask_light.py 证据服务：** Python 辅助程序现纯粹作为事实证据、目录、配方与验证服务（`ask-light-evidence/1`）。移除了 `PROJECT_STATE_INTENT_PATTERN` 及所有基于正则/taskKind/评分的语义路由权威。返回结构化事实（projectContract、currentEffort、spec、tickets、review、artifactSignals）与作用域硬约束，不返回任何确定性 Skill 推荐。
- **工作流模式：** 重构 `recipes_result`（`--mode workflow`），发布带有步骤可用性与 handoff 的规范配方，移除了确定性正则胜者选择；由模型进行语义选择并锚定至当前实际状态。
- **全方位回归测试套件：** 覆盖评审事务一致性、源码/实现新鲜度、软件三字段基线验证、当前 effort 解析、发现与来源检查、严格作用域验证及 `agent-config`/`implement` 关系测试的完整矩阵。

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
- 上文的 `humanizer` 准入与发布后加固内容扩展了 `v0.2.0` 发布线；tag 已重指至 commit `e063753`，且对已发布仓库的全新安装验证通过（CLI `1.5.23`；整集合——34 个包、257 个文件逐字节一致——及单包 `humanizer`）——见 [INSTALLATION_VERIFICATION_ADDENDUM.zh-CN.md](docs/evidence/releases/v0.2.0/INSTALLATION_VERIFICATION_ADDENDUM.zh-CN.md)。
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
- 原有五个包的独立 `review-loop agent-skill` acceptance 仍为 `BLOCKED`；见 [发布收据](docs/evidence/releases)。

## 0.1.3 — 2026-08-10

### 变更

- 测试工具链从 Windows PowerShell 迁移为跨平台 Python：21 个 PowerShell 测试文件替换为 18 个 Python 套件（collection discovery、header assets、quick start、ask-light contract、project-init contract 与 behavior、recap 两个 contract、language-learning contract、review-loop 五个 profile 的 contract 与 behavior 套件及协议 helpers），保留断言集。
- ask-light behavior 套件在所有 host 直接执行可移植 Python router；`scripts/ask-light.ps1` 仅保留为轻量兼容 launcher。
- CI 迁至 `ubuntu-latest`（bash + python）；新增 retired-boundary 与 无 PowerShell 测试检查。
- 文档更新为新测试文件名与跨平台手动 fallback 片段；治理措辞不变。

### 证据

- [docs/evidence/releases/v0.1.3/](docs/evidence/releases/v0.1.3)

## 0.1.2 — 2026-08-10

### 新增

- 为 v0.1.2 准备第一方、仅 user-invoked 的 `recap` Skill。用户显式调用 `$recap` 后只返回一行当前 session 总结；不会运行工具、继续任务、修改文件、压缩历史或调用其他 Skill。
- 为 v0.1.2 准备第一方、仅 user-invoked 的 `language-learning` Skill。它通过六种学习模式辅导任意目标语言——每日课程、即时卡片、对话练习、语法解码、进度测验与沉浸翻译——并在多次调用之间复用会话上下文与已学词汇，而不是每次都重新询问。
- 新增低风险纯提示型准入快速通道：仅适用于 owner-authored、manual-only、只输出文本、无工具/副作用/runtime executable/外部依赖的 Skill；只需一个 fresh Evaluator，不再要求额外 Critic 或 Standards/Spec review。
- 发布通用 `latest` 安装命令（`npx skills add LightDevCoder/skills --yes --copy --agent '*'`）作为标准安装路径，并保留 pinned `#v0.1.2` 形式用于可复现安装。`recap` 与 `language-learning` 均由 fresh independent prompt-only fast-track Evaluator `PASS` 准入，见各自[准入证据](docs/evidence/admissions)。

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
