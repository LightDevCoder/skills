# v0.2.2 — Jev 集成稳定化与发布完整性

[English Release Notes](RELEASE_NOTES.md) · [中文发布收据](RELEASE_RECEIPT.zh-CN.md)

Light Skills v0.2.2 为全部 36 个第一方 Skill 确立了永久、不可变的正式发布边界。本次发布正式交付在 `ask-light`、`agent-config` 和 `project-init` 中完成收敛的 TypeSafe Jev System One 语义加速能力，将全量 Skill 归整至七大按职责划分的分类目录，并在早期 release 经历 tag 移动后完整修复并阐明了发布 Provenance（发布溯源）。

---

## v0.2.2 更新要点

### 1. 发布完整性与不可变 Release 边界
- **Tag 不可变性政策：** 从 v0.2.2 起，已发布的 Release Tag 具有永久不可变性。已发布的 Tag 绝不强制移动（force-move）、绝不重指向（retarget）、绝不重写代码边界。发布后的元数据修正仅限通过不移动 Tag 的显式文档修正或递增 Patch 版本进行。
- **发布溯源问题修复：** v0.2.1 最初于 commit `70a48ef`（收据记录为 `cb17b17c8227b7d7211e4bf5b72223703d987d60`）发布。在后续 Jev 集成快速迭代周期中，`v0.2.1` tag 被多次重新指向。v0.2.2 为所有下游使用者建立了一个全新的、不可变的干净发布快照。

### 2. 最终收敛的 `ask-light` 语义路由与查询规划
- **代码独占的工作流权威：** Python 证据引擎独占底层真实项目事实收集与合法工作流候选行为计算。语义推断绝不越权覆盖确定性状态机的不变量。
- **活跃消费者查询规划（Active Consumer Query Planning）：** 有界 Jev 查询**仅在**存在能实质改变工作流决策的活跃消费者时触发：
  - **Choice（单选）：** 严格仅在存在多个合法候选动作时（`len(allowed_actions) > 1`）调用；单一候选集完全跳过 Choice。
  - **Material Ambiguity（关键歧义 Noul）：** 仅在多个候选中包含 `project-clarify`（用于在澄清与执行间做消歧），或当前仅有 `implement` 且用户语句显式表达歧义时触发。若合法动作本身仅有 `project-clarify`，则跳过该查询以避免零价值推理（Zero-value inference）。
  - **Reasoning Escalation（深度推理升级 Noul）：** 仅在候选包含 `implement` 且用户表达高架构复杂度时触发，用于评估是否推荐升级至 `agent-config`。
- **工作流授权不变量：** Jev 输出绝不赋予工作流流转授权（Workflow transition authority）。已完全移除执行意图相关查询；工作流流转与执行严格由代码管理且必须经用户显式批准。
- **紧凑状态构建（Compact State Builder）：** 经过脱敏的紧凑上下文（<350 字符），不泄露原始源码树或未过滤文件路径。
- **Fail-Closed 与离线平滑降级：** 当缺失 `TYPESAFE_API_KEY` 或未安装 SDK 时，`ask-light` 平滑降级至零依赖的确定性基线，全量测试套件零回归。

### 3. `project-init` 官方 Skills CLI 映射与可选 Jev 生态接入
- **可选生态初始化：** 交互式接入网关（支持 `--jev` / `--no-jev` 非交互参数），用于在新脚手架项目中初始化 TypeSafe Jev 加速能力。未选择或拒绝时，标准项目初始化流程完全保持不变。
- **遵循官方 Skills CLI 规范：** 严格遵循 `vercel-labs/skills` v1.7.0 CLI 规范映射：
  - 规范 Agent 标识符：`pi`, `claude-code`, `cursor`, `codex`, `antigravity`, `grok`, `hermes-agent`。
  - 规范项目级目录作用域：Cursor、Codex 与 Antigravity 统一使用 `.agents/skills`；Pi 使用 `.pi/skills`；Claude Code 使用 `.claude/skills`；Grok 使用 `.grok/skills`；Hermes 使用 `.hermes/skills`。
- **不支持环境 Fail-Closed：** 官方 CLI 尚不支持的环境（如 DeepSeek Harness / DSH）严格确定性 Fail-Closed（报 `TARGET_UNRESOLVED`，0 次外部安装器调用，不猜测 CLI ID）。
- **安全凭据解析：** 优先从当前进程环境变量（`os.environ`）解析 `TYPESAFE_API_KEY`，其次读取当前活跃项目根目录的 `.env`。
- **Gitignore 凭据保护：** 在项目本地写入任何凭据前，强制校验并确保 `.env` 已加入 `.gitignore`。API Key 等机密绝对不会出现在日志、收据、Diff 或发布制品中。
- **全局 Skill 复用：** 检测到全局已安装官方 `typesafe-ai` 时优先复用，避免重复下载。

### 4. `agent-config` 抽象任务分析与非对称降级防御
- **清晰的职责与权威划分：**
  - **Jev：** 提供跨厂商中立的抽象任务画像（复杂度等级、推理需求）与建议性判决。
  - **agent-config 确定性策略：** 独占权威边界、基线保护、候选校验、宿主能力适配、Fallback 以及预览审批门禁。
  - **用户 / Profile：** 用户确认的 Profile 独占配置生效的最终授权。
- **跨厂商抽象表达：** 抽象分档（`routine`, `standard`, `high`）与推理需求（`low`, `medium`, `high`）将任务需求与特定模型名称彻底解耦。
- **无标签泄露的干净评测（Label-Clean Evaluation）：** 权威任务输入（`explicit-user`, `verified-ticket`, `explicit-policy`）完全由代码独占，不向 Jev 发送复杂度查询。真实评测用例绝不将基准真实难度标签泄露给 Jev Prompt。
- **临时非对称降级防御策略（Provisional Asymmetric Downgrade Policy）：**
  - 能力升级（安全方向）：标准置信度阈值 `0.50`。
  - 维持基线（Hold）：标准置信度阈值 `0.50`。
  - 能力降级（将模型档位调低于基线）：属于潜在非安全方向，要求更高置信度阈值 `0.75` 且边界裕度（boundary margin） `>= 0.15`。
  - **策略状态：** `PROVISIONAL`（暂定；基于实测证据，不夸大标定完备性）。
  - **真实评测实证（AC-02）：** 提议将基线 `standard` 降级为 `routine` 的请求因置信度不足（0.59 < 0.75）且临近分档边界（分值 0.41）被安全拦截，正确保留基线 `standard` 档位（`claude-3-5-sonnet`）。

### 5. 七大职责分类目录归整（36 个第一方 Skill）
全部 36 个第一方 Skill 按职责分类收纳在 `skills/` 下的七大目录中：
- **`project/`（8 个）：** `project-init`, `project-clarify`, `project-spec`, `project-tickets`, `implement`, `kanban-worker`, `project-retro`, `release-workflow`。
- **`thinking/`（5 个）：** `clarify`, `decision-map`, `research`, `socratic`, `to-questionnaire`。
- **`engineering/`（5 个）：** `agent-config`, `diagnosing-bugs`, `prototype`, `resolving-merge-conflicts`, `tdd`。
- **`review/`（4 个）：** `code-review`, `generic-review`, `project-review`, `review-loop`。
- **`knowledge/`（5 个）：** `eli5`, `kb-init`, `language-learning`, `learn-anything`, `teach`。
- **`writing/`（3 个）：** `humanizer`, `manuscript-ops`, `writing-for-agents`。
- **`productivity/`（6 个）：** `ask-light`, `handoff`, `light-travelpage`, `recap`, `wait-what`, `wizard`。

宿主端安装依然保持平铺结构（`<skills-root>/<name>/`），CLI 选装命令（`npx skills add ... --skill <name>`）完全兼容。

---

## 安装方法

### 稳定版本快照锁定安装（v0.2.2）
若需安装不可变、可复现的 v0.2.2 发布快照，请锁定 `#v0.2.2` tag：

```bash
# 安装完整 36 个 Skill 集合：
npx skills add LightDevCoder/skills#v0.2.2 -y

# 安装单个指定 Skill：
npx skills add LightDevCoder/skills#v0.2.2 --skill agent-config -y
npx skills add LightDevCoder/skills#v0.2.2 --skill ask-light -y
npx skills add LightDevCoder/skills#v0.2.2 --skill project-init -y
```

### 默认主分支安装（main）
安装 default 分支最新开发状态：

```bash
npx skills add LightDevCoder/skills -y
```

---

## 发布溯源说明（Provenance Note）

Release `v0.2.1` 最初于 2026-09-16 在 commit `70a48ef`（发布收据中记录为 `cb17b17c8227b7d7211e4bf5b72223703d987d60`）发布，引入了 `project-retro` 与 `light-travelpage`。在随后的 TypeSafe Jev 集成加固迭代周期（2026-09-20）中，`v0.2.1` tag 曾被移动以跟随当时的集成提交（`6f9d173`，后至 `27f16e4`）。

本次 `v0.2.2` 发布确立了全新的不可变发布边界，将最终完成的 Jev 集成、目录分类重构及准确的文档修订正式固化于不可变 Tag 中。
