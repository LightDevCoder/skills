# 变更记录

[English changelog](CHANGELOG.md)

所有变更都必须记录在实际版本/tag 对应的条目中，不能因为文档已起草就提前宣称 release。

## 0.1.6 — 2026-08-19

### 新增

- 第一方 `kb-init` Skill v1.0.0：正式版知识库初始化包替换之前未发布的草稿。
  新增扩展核心原则（决策 provenance、开放决策 surfacing、depth before
  settlement）、readiness 检查、人类导航设计、research contract、
  connection setup/validation、backup/recovery 语义，以及 38 个回归 eval
  用例。按 owner 决定，它仍是仅 user-invoked。
- 针对 v1.0.0 更新 contract 测试与双语使用指南。
- v0.1.6 发布九包集合：v0.1.1 的五个包、`recap` 与 `language-learning`
  （v0.1.2）、`light-kanban-worker`（v0.1.4），以及 `kb-init` v1.0.0。

### 变更

- `kb-init` 保持 explicit-only：`SKILL.md` 中 `disable-model-invocation: true`，
  `agents/openai.yaml` 中 `allow_implicit_invocation: false`。
- README、目录、安装指南、维护基线、discovery 测试与双语指南从 v0.1.5
  八包发布边界更新为 v0.1.6 九包发布。

### Release 证据

- Release tag：`v0.1.6`，commit `<release-commit>`。
- GitHub Actions `collection-quality`：release commit 上 PASS。
- 整集合与单 Skill fresh installs：通用 `latest` 与 pinned `#v0.1.6` 形式
  PASS；见
  [INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.6/INSTALLATION_VERIFICATION.zh-CN.md)。
- Host discovery：
  [DISCOVERY_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.6/DISCOVERY_VERIFICATION.zh-CN.md)。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.6
- 最终收据：
  [RELEASE_RECEIPT.zh-CN.md](docs/evidence/releases/v0.1.6/RELEASE_RECEIPT.zh-CN.md)。

## 0.1.5 — 2026-08-17

### 变更

- `light-kanban-worker` 现在明确禁止同一 `LIGHT_KANBAN_AGENT_ID` 的
  scheduled run 重叠执行：同一 agent id 任意时刻至多一个 invocation 活跃，
  上一 run 仍活跃时触发的唤醒必须 skip；不同 agent id 仍可并发。atomic
  claim 边界被准确记录——它保护的是两个不同 worker 同时 claim 同一张 To Do，
  并不是同一 agent identity 多个 invocation 的并发锁；并发控制属于
  scheduler / agent runtime（`max concurrent runs = 1` 或等价的
  skip-while-active 设置），worker 不新增 lock process、heartbeat 或 lease
  service。
- 首次注册现在明确要求 ID + name + avatar：本地图片通过
  `POST /api/avatars` 上传并使用返回的 `/api/avatars/...` 路径 claim；已存在
  的 agent id 复用服务器保存的 name/avatar，后续唤醒无需重复 avatar。全新
  agent id 缺 name 或 avatar 时报 identity configuration missing，不 claim、
  不改动任何任务。
- `agents/openai.yaml` default prompt 更新为可完成首次注册的 one-shot
  形式（Agent ID / Name / Avatar），全新看板也能注册新身份。

### 测试

- worker contract 套件新增调度边界规则：same-agent 不得重叠、不同 agent
  并发允许、atomic claim 边界、scheduler 拥有并发控制、无常驻 lock
  service、首次注册身份、身份复用、缺身份不得改动任务、本地 avatar
  上传路径。
- 新增对抗性 negative fixtures `overlap-allowed-variant.md` 与
  `avatar-optional-first-registration.md`，各自只违反一条规则且必须被拒绝。
- behavior 套件新增 Scenario G（同 agent 并发唤醒：run #1 活跃时第二个 run
  不得开始处理，经 scheduler-guard fixture 验证——Light-Kanban 自身不提供
  run lease）与 Scenario H（无 avatar 的新身份：不 claim、不改动、明确配置
  失败；提供合法 avatar 后注册与 claim 成功）。Scenarios A–F 保持不变并继续
  通过。
- release evidence 工作流澄清：receipt 现在区分 pre-release gate（candidate
  测试、准入、catalog 同步——`READY FOR RELEASE`）与 post-release
  verification（已发布 tag 身份、fresh install、host discovery、release
  CI），已发布 tag 中不再出现令人困惑的 `PENDING` 标记。

### 证据

- Release tag：`v0.1.5`，commit `a56aa9d98de0b941ee2282144bc7e756ef5e48bd`。
- GitHub Actions `collection-quality`：release commit 上 `PASS`（run
  `31985455493`）。
- 契约变更的 `review-loop agent-skill` 验收：完全独立的 PASS（findings
  F-001/F-002/F-003/G-001 已修复）——
  [AGENT_SKILL_REVIEW.zh-CN.md](docs/evidence/releases/v0.1.5/AGENT_SKILL_REVIEW.zh-CN.md)。
- Fresh installs：整集合与单 Skill、通用 `latest` 与 pinned `#v0.1.5`
  形式，CLI `1.5.22` —— PASS；安装包与 tag 逐字节一致且套件可独立运行。见
  [INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.5/INSTALLATION_VERIFICATION.zh-CN.md)。
- Host discovery：
  [DISCOVERY_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.5/DISCOVERY_VERIFICATION.zh-CN.md)。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.5
- 最终收据（pre-release gate + post-release verification）：
  [RELEASE_RECEIPT.zh-CN.md](docs/evidence/releases/v0.1.5/RELEASE_RECEIPT.zh-CN.md)。

## 0.1.4 — 2026-08-16

### 新增

- 新的第一方 model-invoked Skill `light-kanban-worker`：每次 scheduled
  agent 运行最多处理一张 Light-Kanban 任务——稳定 agent identity、先检查
  自己持有的 in-progress 任务与 `reviewFeedback` 再领取新任务、原子 claim
  带有限次冲突重试、workspace 校验（不可访问的 workspace 变成 `block` 并带
  具体原因）、`complete` 交回人工验收。worker 绝不 archive、accept、delete、
  recycle、unblock，也绝不循环或常驻进程。因其涉及网络/文件系统/看板状态
  副作用，走完整准入路径（`review-loop agent-skill`），不走纯提示型快速通道。
- worker 包的 contract 与 behavior 测试套件，包含 positive fixtures 与
  negative fixtures（对抗性单规则 fixture 文件）及 frontmatter YAML 安全门。
- ask-light behavior 套件新增 outside-readable-path negative 场景。

### 变更

- 版本文档同步：v0.1.4 为当前稳定 release，v0.1.3 及更早版本保持历史
  记录。README、目录、安装指南、维护基线、discovery 测试与 CI 更新为八包集合。
- 修复 ask-light scanner 的 `Test-PathUnder` 路径比较（硬编码 Windows
  分隔符），该问题使 collection-quality workflow 自 v0.1.3 Python 移植起在
  ubuntu-latest 上失败。

### Release 证据

- Release tag：`v0.1.4`，commit `a9cc8aa029c926fc80f6ddc0022793f79dfd85bd`。
- GitHub Actions `collection-quality`：release commit 上 `PASS`（run
  `31962459531`）。
- 整集合与单 Skill fresh installs：`PASS`（CLI `1.5.22`，通用 `latest` 与
  pinned `#v0.1.4` 形式）。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.4
- 整集合与单 Skill fresh-install 证据：
  [INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.4/INSTALLATION_VERIFICATION.zh-CN.md)。
- 结构与包级证据：[TEST_SUMMARY.zh-CN.md](docs/evidence/releases/v0.1.4/TEST_SUMMARY.zh-CN.md)。
- 准入：[light-kanban-worker 证据](docs/evidence/admissions/light-kanban-worker/README.zh-CN.md)。
- scanner code-review：[CODE_REVIEW.zh-CN.md](docs/evidence/releases/v0.1.4/CODE_REVIEW.zh-CN.md)。
- 原有五个包的独立 `review-loop agent-skill` acceptance 仍为 `BLOCKED`；见
  [发布收据](docs/evidence/releases/)。

## 0.1.3 — 2026-08-10

### 变更

- 测试工具链从 Windows PowerShell 迁移为跨平台 Python：21 个 PowerShell
  测试文件替换为 18 个 Python 套件（collection discovery、header assets、
  quick start、ask-light contract、project-init contract 与 behavior、
  recap 两个 contract、language-learning contract、review-loop 五个
  profile 的 contract 与 behavior 套件及协议 helpers），保留断言集。
- ask-light scanner behavior 套件仍通过 `pwsh` 执行真实的
  `scripts/ask-light.ps1`，pwsh 缺失时优雅跳过；CI（ubuntu-latest）自带
  pwsh 并运行。
- CI 迁至 `ubuntu-latest`（bash + python）；新增 retired-boundary 与
  无 PowerShell 测试检查。
- 文档更新为新测试文件名与跨平台手动 fallback 片段；治理措辞不变。

### 证据

- [docs/evidence/releases/v0.1.3/](docs/evidence/releases/v0.1.3/)

## 0.1.2 — 2026-08-10

### 新增

- 为 v0.1.2 准备第一方、仅 user-invoked 的 `recap` Skill。用户显式调用 `$recap`
  后只返回一行当前 session 总结；不会运行工具、继续任务、修改文件、压缩历史或调用其他 Skill。
- 为 v0.1.2 准备第一方、仅 user-invoked 的 `language-learning` Skill。它通过六种
  学习模式辅导任意目标语言——每日课程、即时卡片、对话练习、语法解码、
  进度测验与沉浸翻译——并在多次调用之间复用会话上下文与已学词汇，而不是
  每次都重新询问。
- 新增低风险纯提示型准入快速通道：仅适用于 owner-authored、manual-only、
  只输出文本、无工具/副作用/runtime executable/外部依赖的 Skill；只需一个
  fresh Evaluator，不再要求额外 Critic 或 Standards/Spec review。
- 发布通用 `latest` 安装命令（`npx skills add LightDevCoder/skills --yes --copy
  --agent '*'`）作为标准安装路径，并保留 pinned `#v0.1.2` 形式用于可复现
  安装。`recap` 与 `language-learning` 均由 fresh independent prompt-only
  fast-track Evaluator `PASS` 准入，见各自[准入证据](docs/evidence/admissions/)。

### Release 证据

- Release tag：`v0.1.2`，commit `8de5ec1a453b0e93f71dcda160e17ea7b42c3997`。
- 合并后的 release commit 上 GitHub Actions `collection-quality`：`PASS`。
- 整仓和单 Skill fresh install：使用 CLI `1.5.22`，通用 `latest` 与 pinned
  `#v0.1.2` 两种形式均为 `PASS`。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.2
- 整仓与单 Skill fresh-install 证据：[INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.zh-CN.md)。
- 结构与包测试证据：[TEST_SUMMARY.zh-CN.md](docs/evidence/releases/v0.1.2/TEST_SUMMARY.zh-CN.md)。
- 原有五个包的独立 `review-loop agent-skill` acceptance 仍为 `BLOCKED`；见
  [发布收据](docs/evidence/releases/v0.1.2/RELEASE_RECEIPT.zh-CN.md)。

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
- 五个包组成的集合仍可安装，`collection-quality` 检查已通过。`review-loop
  agent-skill` acceptance gate 的独立 evaluator 证据仍为 `BLOCKED`；这不影响
  一般安装或使用。准确证据边界见[发布收据](docs/evidence/releases/v0.1.1/RELEASE_RECEIPT.zh-CN.md)。

## 0.1.0 — 2026-07-23

- 建立第一方治理基础并准入五个第一方 Skill。
- 已发布于 https://github.com/LightDevCoder/skills。
- 稳定 tag：v0.1.0。
- v0.1.0 的整集合与单 Skill 安装命令曾针对 fresh destination 和已发布包内容完成验证；这份历史证据与 v0.1.1 release 证据一并保留。
- 历史命令：`npx skills add LightDevCoder/skills` 和
  `npx skills add LightDevCoder/skills --skill review-loop`。
- 历史安装明细：[v0.1.0 摘要](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md#历史-v0.1.0-摘要)。
