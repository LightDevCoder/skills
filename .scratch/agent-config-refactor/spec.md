# SPEC：Agent Config 重构 — Host-Aware Model & Execution Configuration

## 0. Task

对 `LightDevCoder/skills` 仓库中的 `skills/agent-config` 进行一次架构级重构。

本次重构不是继续增强当前的“安全多 Agent 执行规划器”，而是把 `agent-config` 拉回它真正的核心职责：

> **根据当前 Agent Host / Harness 实际支持的模型、模型层级、reasoning/effort、subagent/thread/parallelism 等能力，以及当前任务的执行规模，决定最合适的模型配置、effort 配置和执行方式。**

同时必须完成全仓兼容性迁移，保证它仍能自然融入现有 Light Skills 工作流，不能只修改 `skills/agent-config` 后留下旧调用契约、旧文档、旧测试或与 `project-tickets` / `implement` / `review-loop` 冲突的行为。

本次修改属于重大行为重构，应按仓库 `AGENTS.md` 的 full review path 处理。

完成全部实现、测试、文档同步和本地验证后：

* 创建一个本地 commit；
* 不 push；
* 不发布 release；
* 不创建 tag；
* 不修改稳定版本号；
* 等待人工复审。

建议 commit：

```text
refactor: restore agent-config model-aware execution routing
```

---

# 1. Problem Statement

当前 `agent-config` 已经从最初目标明显漂移。

现实现的主要问题不是 Host-agnostic 做错了，而是把大量设计重心放在：

* Controller / Explorer / Implementer / Reviewer / Merger 固定角色；
* exact file ownership；
* execution waves；
* merge rule；
* reviewer independence；
* worktree / concurrency planning。

这些能力本身有价值，但现在被提升成了每次调用都必须输出的核心 contract。

结果是：

> `agent-config` 更像一个 generic multi-agent execution planner，而不是一个真正的 Agent / Model Configurator。

与此同时，真正重要的能力反而缺失或非常薄弱：

* 不会根据任务难度选择不同智力层级的模型；
* 不会根据任务难度选择 reasoning / effort；
* `reasoning_control` 虽然存在于 Host evidence 中，但没有真正进入决策；
* 不会区分“小任务直接完成”和“大任务需要拆票执行”；
* 多模型 Provider 和单模型 Provider 虽然能降级，但没有形成明显不同的执行策略；
* 单模型环境仍然容易产出没有实际价值的角色分配；
* 大任务中的模型资源应该围绕 ticket 难度分配，而不是首先围绕固定抽象角色分配。

本次重构必须修正这个责任中心。

---

# 2. Core Principle

新的 `agent-config` 必须围绕两个主要维度做判断：

```text
                   Task Shape
              Single-pass     Decomposed
             ┌──────────────┬──────────────┐
Tiered       │ Multi +      │ Multi +      │
Multi-model  │ Single-pass  │ Decomposed   │
             ├──────────────┼──────────────┤
Fixed        │ Single +     │ Single +     │
Single-model │ Single-pass  │ Decomposed   │
             └──────────────┴──────────────┘
```

第一个维度：

```text
Provider / Host model mode
```

必须区分：

```text
tiered-multi-model
fixed-single-model
```

第二个维度：

```text
Task shape
```

必须区分：

```text
single-pass
decomposed
```

**禁止把 SPEC 字数作为判断依据。**

所谓短 SPEC / 长 SPEC，在实现层面必须解释成：

* `single-pass`：一个执行者能够在一个连续、受控的执行周期里安全完成；
* `decomposed`：任务应被拆成多个独立或有依赖关系的 work items / tickets，再分别实施和集成。

一个 700 字的跨数据库、API、UI、migration 的 SPEC 仍可能是 `decomposed`。

一个 3000 字但只要求修改一份文档的 SPEC 仍可能是 `single-pass`。

---

# 3. Responsibility Boundary

重构后的 `agent-config` 是：

> **Host-aware model and execution configuration capability**

它负责：

```text
inspect Host capability
        ↓
understand usable model topology
        ↓
assess task execution shape
        ↓
assess work-item difficulty/risk
        ↓
choose model tier
        ↓
choose reasoning/effort
        ↓
choose session/subagent topology
        ↓
recommend review context
        ↓
optionally request Host adapter to apply project-level config
```

它不是：

* ticket tracker；
* SPEC writer；
* persistent ticket generator；
* implementation engine；
* review engine；
* final acceptance engine；
* merge engine；
* release engine。

它可以设计 execution topology，但不能夺走已有 Skill 的职责。

---

# 4. Preserve Existing Workflow Ownership

必须保留现有 canonical project workflow：

```text
project-clarify
      ↓
project-spec
      ↓
project-tickets
      ↓
implement
      ↓
project-review
```

## 4.1 `project-tickets` 继续拥有正式拆票

`agent-config` 可以判断：

```text
Task shape: decomposed
```

但如果输入只有一个完整 SPEC、尚未存在正式 tickets：

**不得自己创建 `.scratch/<feature>/issues/*.md`。**

正确行为：

```text
Task shape: decomposed
Execution readiness: needs-project-tickets
Recommended handoff: project-tickets
```

可以同时给出一个粗粒度 routing policy，例如：

```text
When tickets exist:
- routine work → lower sufficient model tier
- moderate work → middle tier
- demanding/high-risk work → highest tier
- final/controller review → highest tier
```

但不能伪造尚不存在的 ticket assignments。

正式 ticket decomposition 仍由 `project-tickets` 完成。

## 4.2 已存在 ticket graph 时允许全局 routing

如果 `project-tickets` 已经产生：

```text
.scratch/<feature>/issues/
```

那么显式调用 `agent-config` 可以读取整个 ticket graph 或当前 frontier，并：

* 判断 ticket 难度；
* 判断 dependency；
* 判断哪些 ready tickets 可以并行；
* 给不同 ticket 配置 model tier；
* 给不同 ticket配置 effort；
* 规划执行 session / subagent；
* 指定 Controller 的模型与 effort；
* 指定返回 Controller 的 review/integration 方式。

但：

**不得修改 ticket contract 本身以绑定模型。**

不要增加类似：

```text
Model: xxx
Effort: high
```

作为 `project-tickets` 的 required fields。

模型配置属于 Host/runtime execution concern，不属于项目需求和 ticket semantics。

## 4.3 `implement` 继续一次执行一个 ticket

现有规则保持：

```text
one $implement run
=
one bounded ticket
=
one fresh execution context
```

`agent-config` 的全局 ticket routing plan 可以安排：

```text
Ticket 01 → context A
Ticket 02 → context B
Ticket 03 → context C
```

但每个 context 中仍然执行：

```text
$implement <one-ticket>
```

不得通过修改 `implement` 让一次 invocation 连续吞掉多个 sibling tickets。

---

# 5. Provider Mode Detection

## 5.1 `tiered-multi-model`

只有满足以下条件，才能认为当前 Host 能进行真正的 tiered routing：

* 至少存在两个当前可用、可选择的模型；
* 有可信证据证明这些模型存在相对能力层级；
* Host 存在一种实际可用的模型选择方式；
* 所推荐的执行 context 确实能够应用这种选择。

例如，Host 可能支持：

```text
current-session model switching
new-session model selection
per-subagent model selection
```

这些能力必须分别记录，不得互相推导。

例如：

```text
Host 可以切当前模型
```

不代表：

```text
Host 可以给每个 subagent 独立指定模型
```

## 5.2 `fixed-single-model`

以下情况均进入 fixed/single-model execution mode：

* Provider 实际只有一个模型；
* Host 当前只暴露一个可执行模型；
* 有多个模型名，但无法实际选择；
* 有多个可选模型，但没有可信的能力层级信息，无法安全进行 tier routing；
* per-agent model selection 不可用，而且当前执行 topology 无法通过其他 context selection 方式实现模型分层。

必须自然降级。

禁止为了保持 multi-model 路线而猜测模型能力。

---

# 6. Model Capability Evidence

当前 Host evidence 的严格原则继续保留：

> 不得根据模型记忆、模型名字或静态猜测声称某个 Host 能做什么。

但需要把“模型是否可用”和“模型智力层级”拆成两种不同证据。

## 6.1 Availability Evidence

模型是否当前可执行 / 可选择必须来自当前 Host。

例如：

```text
host-runtime
host model selector
current session
provider runtime
```

必须带 observation time。

## 6.2 Routing Metadata

模型相对能力层级可以来自：

* Host runtime；
* 当前 Provider adapter/plugin；
* 当前安装版本对应的 provider manifest；
* 经过明确验证的项目级 Provider configuration。

禁止来自：

* 模型自己的常识；
* 模型名字猜测；
* README 中过时的硬编码列表；
* “这个名字看起来应该比较强”。

建议给 selectable model 增加 provider-neutral 的：

```text
routing_rank
```

例如：

```yaml
id: model-alpha
routing_rank: 1

id: model-beta
routing_rank: 2

id: model-gamma
routing_rank: 3
```

约定：

```text
larger routing_rank = higher general reasoning capability
```

核心 Skill 不关心这些模型实际叫什么。

---

# 7. Reasoning / Effort Evidence

当前 schema 中已经存在 `reasoning_control`，本次必须真正用起来。

建议扩展成能够表达：

```yaml
reasoning_control:
  state: available
  levels:
    - low
    - medium
    - high
  assignment_scope:
    - current-session
    - new-session
    - per-agent
```

具体 level 名称不应被核心 Skill 写死。

Provider 可能暴露：

```text
low / medium / high
```

也可能暴露：

```text
standard / deep
```

或者其他名称。

Skill 只需要知道：

```text
ordered from lower effort → higher effort
```

以及可以在哪些 context 上设置。

---

# 8. Task Assessment

新增独立 reference，例如：

```text
skills/agent-config/references/task-assessment.md
```

不要把大量判断规则塞进 `SKILL.md`。

## 8.1 Task Shape

输出：

```text
single-pass
decomposed
```

判断时综合：

* 是否存在多个可独立验收的工作单元；
* 是否有明显 dependency graph；
* 是否跨越多个技术/业务 concern；
* 是否需要不同 context 才能保持上下文清晰；
* 是否存在多个可以并行的 tracer-bullet slices；
* 是否一次执行的 review/verification surface 过大；
* 是否已经存在正式 ticket graph。

禁止单纯：

```text
SPEC > N words → decomposed
```

## 8.2 Work-item Difficulty

对实际 work item 判断：

```text
routine
moderate
demanding
critical
```

不要求建立机械数字评分器。

模型应根据：

* reasoning depth；
* uncertainty；
* coupling；
* architectural consequences；
* debugging/research burden；
* reversibility；
* verification difficulty；
* failure risk。

进行语义判断。

目的不是精确打分，而是回答：

> **完成这个 work item 最低需要什么智力等级，没必要的高智力模型不要浪费。**

---

# 9. Four Required Execution Modes

## 9.1 Tiered Multi-model + Single-pass

典型情况：

```text
Provider 有多个不同智力等级模型
+
任务可以单次完成
```

行为：

1. 判断实现任务难度；
2. 选择**最低足够完成任务**的模型层级；
3. 选择合适 effort；
4. 默认保持单会话执行；
5. 不为了“看起来像多 Agent”而创建多 Agent；
6. research / exploration / isolated check 确实有帮助时才调用临时 subagent；
7. Review 可以选择高于 Implementer 的模型；
8. 如果当前 Controller 已经是高层模型，可以让较低层 Implementer subagent 实施，再由 Controller review；
9. 如果 implementation 本身在当前 session 完成，可以在 Host 支持时用 fresh higher-tier context 做 review；
10. 如果无法创建 fresh context，只能记为 self-check / controller check，不得伪称 independent review。

示例逻辑：

```text
Task: moderate bounded implementation

Implementation:
  model rank: 2
  effort: medium/high

Review:
  model rank: 3
  effort: max
  context: fresh thread if available
```

不要求输出：

```text
Explorer
Merger
Ownership matrix
Execution waves
```

除非任务真的需要。

---

# 10. Tiered Multi-model + Decomposed

典型情况：

```text
Provider 有多个模型层级
+
任务已经拆成多个 tickets
```

如果还没有 tickets：

```text
Execution readiness: needs-project-tickets
```

停止在 handoff，不自行持久化拆票。

如果 tickets 已存在：

## Controller

默认：

```text
highest evidenced model tier
high/max supported effort
```

负责：

* 理解整体 ticket graph；
* 根据 dependency/frontier 调度；
* 接收 worker outputs；
* 做 integration-level review；
* 判断下一轮 frontier；
* 管理 Host execution configuration。

## Worker assignment

每个 ticket 根据自身难度独立配置。

类似：

```text
routine
→ lower sufficient model
→ economical/medium effort

moderate
→ middle model tier
→ medium/high effort

demanding
→ high model tier
→ high effort

critical
→ highest model tier
→ max effort
```

具体 mapping 不应硬编码到 Provider 名称。

必须保持一个重要 invariant：

> 在没有特殊证据的情况下，更困难、更高风险的 ticket 不应被分配到比简单 ticket 更低的模型层级或更低 effort。

## Parallelism

仅当：

* tickets 当前 ready；
* dependency 不阻塞；
* ownership 不冲突；
* Host parallelism 有证据；
* concurrency cap 有证据；

才可以并行。

否则串行。

不要把“有 subagent”推导成“可并行”。

## Execution

每个 ticket 独立进入：

```text
$implement <ticket>
```

不得合并多个 ticket 为一个 implement invocation。

## Review

Worker 的结果返回 Controller。

Controller 可以进行：

```text
integration review
routing-level quality check
cross-ticket consistency check
```

但这不是最终项目验收。

需要正式 review convergence 时继续使用：

```text
review-loop
```

最终：

```text
project-review
```

仍拥有 PASS / FAIL / BLOCKED。

---

# 11. Fixed Single-model + Single-pass

典型情况：

```text
Provider / Host 只能使用一个模型
+
任务可以一次完成
```

这里必须极度简化。

行为：

```text
current executable model
+
maximum supported effort
+
direct execution
```

不要输出这种无意义配置：

```text
Controller: model-alpha
Explorer: model-alpha
Implementer: model-alpha
Reviewer: model-alpha
Merger: model-alpha
```

默认：

```text
one current session
```

只在这些场景调用 helper subagent/thread：

* 查询；
* repo exploration；
* research；
* 独立验证；
* 明确能减少 Controller context burden 的局部工作。

这些 helper 仍然使用同一个模型。

如果 reasoning control 可配置：

```text
use maximum supported effort
```

如果 Host 不暴露 reasoning control：

```text
continue with current/default reasoning behavior
```

不得因此 `BOUNDARY`。

---

# 12. Fixed Single-model + Decomposed

典型情况：

```text
Provider 只能使用一个模型
+
任务有多个 tickets
```

所有执行 context：

```text
same model
maximum supported effort
```

Controller：

```text
same model
maximum supported effort
```

Worker：

```text
same model
maximum supported effort
```

不做虚假的 model routing。

真正有价值的是：

* ticket scheduling；
* session/thread assignment；
* dependency；
* frontier；
* concurrency；
* Controller review/integration。

如果 Host 支持 subagents / threads：

```text
Controller
   ├─ ticket 01 → thread A
   ├─ ticket 02 → thread B
   └─ ticket 03 → thread C
```

如果不支持：

```text
Controller
   ↓
ticket 01
   ↓
ticket 02
   ↓
ticket 03
```

串行执行。

缺少 subagent / parallelism 不能使整个执行计划失败。

---

# 13. Adaptive Output Contract

当前固定要求：

```text
Evidence ledger
Role assignment
Ownership matrix
Execution waves
Review and merge gates
```

必须重构。

新的 plan schema 应该是 adaptive，而不是所有任务都打印完整 orchestration bureaucracy。

保留文件：

```text
skills/agent-config/references/plan-schema.md
```

避免不必要的路径迁移。

建议基础 contract：

```text
Status: READY | NEED-INPUT | BOUNDARY
Scope: current-item | spec-assessment | ticket-frontier | ticket-graph
Provider mode: tiered-multi-model | fixed-single-model
Task shape: single-pass | decomposed
Execution readiness: executable | needs-project-tickets | waiting-on-frontier | blocked-gate
Apply mode: plan-only | adapter-available-awaiting-approval | applied

Reason: <short explanation>
```

然后：

```text
## Host summary
## Task assessment
## Execution config
## Review strategy
## Limitations / unknowns
```

## Single-pass 输出

只需要类似：

```text
| Phase | Model / tier | Effort | Context | Purpose |
```

不要强制 ownership matrix。

## Decomposed 输出

只有此时才增加：

```text
## Work-item routing

| Ticket | Difficulty | Model / tier | Effort | Context | Dependencies | Review |
```

必要时增加：

```text
## Coordination

Controller:
Concurrency:
Frontier:
Integration:
```

只有确实存在 ownership / parallel wave 问题时才增加：

```text
Ownership
Execution waves
```

它们变成 conditional sections，而不是 universal contract。

---

# 14. Roles Are Conditional, Not Ontology

删除“每个 plan 都必须出现”：

```text
Controller
Explorer
Implementer
Reviewer
Merger
```

的 contract。

改成：

* Controller：decomposed execution 通常需要；
* Implementer：实际实施 work item 时存在；
* Explorer：只有 exploration/research 被单独委派时存在；
* Reviewer：需要独立/fresh review context 时存在；
* Merger：只有 Host/worktree/integration topology 真正需要独立 merger 时存在。

多数任务：

```text
Controller == current session
```

即可。

不要为了填 schema 创建角色。

---

# 15. Review Semantics

必须把三个概念分开。

## Controller Review

Controller 没有亲自实现某个 delegated ticket 时，可以审阅 worker return。

属于：

```text
controller review / integration review
```

这是大任务编排中的正常行为。

## Self-check

同一个 context 自己实现再自己检查：

```text
self-check
```

不能称为 independent review。

## Independent Review

只有真正不同的 fresh context / reviewer assignment 才能称为：

```text
independent review
```

`agent-config` 只负责推荐：

* reviewer model tier；
* reviewer effort；
* reviewer context topology。

它不复制 reviewer rubric。

正式 review 继续交：

```text
review-loop
→ code-review / generic-review / domain reviewer
```

项目最终验收继续：

```text
project-review
```

---

# 16. Optional Host / Provider Adapter

新增：

```text
skills/agent-config/references/provider-adapter-contract.md
```

核心 Skill 保持 provider-neutral。

不要在 `SKILL.md` 中硬编码：

```text
Codex config path
Claude config path
Gemini config path
specific model names
specific provider APIs
```

Adapter/plugin 的职责是：

```text
inspect Host
      ↓
report runtime capabilities
      ↓
normalize model routing metadata
      ↓
normalize effort controls
      ↓
optionally apply project-level Agent configuration
```

核心 Skill 负责：

```text
reasoning and planning
```

Adapter 负责：

```text
Host-specific mechanics
```

---

# 17. Adapter Evidence Contract

Adapter 至少应该能够表达：

```text
provider identity
adapter identity/version
observation time

current executable model

selectable models

routing rank / relative capability

reasoning/effort levels

model-selection scope

subagent support

session/thread support

parallelism

concurrency cap

worktree support

project-level configuration support
```

不要要求每个 Host 都支持所有字段。

缺失能力：

```text
unknown
```

或：

```text
unavailable
```

继续保留严格区分。

---

# 18. Project-level Configuration Apply

这是本次架构必须预留的能力。

如果 Host adapter/plugin 支持 project-level Agent configuration，`agent-config` 可以生成 apply request，例如语义上：

```text
Project root: <root>

Controller:
  model: highest-ranked-model
  effort: max

Ticket workers:
  routine: rank-1
  moderate: rank-2
  demanding: rank-3

Review:
  model: rank-3
  effort: max
```

然后交给 adapter。

但是：

## Read-only by default

`agent-config` 被隐式调用或普通规划调用时：

```text
Apply mode: plan-only
```

不得修改 Host/project configuration。

## Explicit approval before mutation

真正调用 adapter 修改项目级 Agent config 前，必须有明确用户批准。

例如：

```text
Apply this routing configuration to the current project?
```

只有批准后：

```text
Apply mode: applied
```

## Adapter unavailable

如果 adapter/plugin 不存在：

```text
Apply mode: plan-only
Limitation: no project-config adapter available
```

仍然返回可执行 plan。

不得 `BOUNDARY`。

## Adapter failure

Adapter 应用失败：

* 不要假装成功；
* 报告具体失败；
* 保留 plan；
* 可以继续由 Controller 手工遵循 plan；
* 除非任务有硬性要求，否则不要阻止 implementation。

---

# 19. Do Not Invent a Plugin Framework

本仓库如果当前没有正式 Provider plugin framework：

**不要为了这次重构顺手设计并加入一套新的插件系统。**

本次必须完成：

```text
provider-adapter semantic contract
+
runtime integration boundary
+
project-config apply request contract
```

如果目标 Host 已存在插件机制，可以适配。

如果不存在，只定义接口和 fallback。

Provider-specific plugin implementation 可以作为后续独立工作，不得污染核心 Skill。

---

# 20. Host Evidence Schema v2

修改：

```text
skills/agent-config/references/host-evidence-schema.md
```

建议升级：

```text
schema_version: 2
```

但必须考虑旧 schema 的 graceful compatibility。

已有 v1 evidence 如果没有：

```text
routing_rank
effort levels
```

不得解析失败。

应 normalize 为：

```text
tier routing unavailable
```

然后走 conservative fixed-model behavior。

至少保留现有重要能力：

```text
models.current
models.selectable

model_selection
subagents
per_agent_model_selection
parallelism
reasoning_control
session_threads
worktrees
concurrency_cap
```

新增或扩展：

```text
routing_rank
routing_metadata_evidence

reasoning levels
reasoning assignment scope

model selection scope

provider adapter identity
project config adapter capability
```

---

# 21. Status Semantics

继续保留：

```text
READY
NEED-INPUT
BOUNDARY
```

避免不必要破坏外部 consumer。

## READY

只要存在当前可执行模型，并且能给出安全执行方式，即可 READY。

即使：

* 只有一个模型；
* 没有 selector；
* 没有 subagent；
* 没有 worktree；
* 没有 reasoning control；

都可以：

```text
fixed-single-model
+
serial execution
```

## NEED-INPUT

只在缺失决定真正会改变：

* execution scope；
* model spend；
* safety/risk；
* task boundary；

时使用。

不要因为普通 metadata 不完整就问用户。

## BOUNDARY

只用于真正无法安全给出执行方式的情况，例如：

* 没有任何当前可执行模型；
* hard acceptance requirement 要求某种当前 Host 明确无法提供的能力；
* 无法确认任务的基本 execution authority。

如果只是某个 review gate 无法满足：

```text
mark that gate blocked
```

不要无脑阻塞全部 implementation。

---

# 22. `implement` Compatibility Migration

必须检查并更新：

```text
skills/implement/SKILL.md
skills/implement/references/WORKFLOW.md
skills/implement/references/EXAMPLES.md
skills/implement/tests/
```

如果 tests 存在。

## Preserve

必须保持：

```text
agent-config is optional
```

`implement` 不得恢复自动强制调用。

正确行为：

```text
routing/config materially useful?
    │
    ├─ no → direct implementation
    │
    └─ yes → offer agent-config
                  │
                  ├─ accept → use config
                  └─ decline → direct implementation
```

## Update trigger language

当前主要围绕：

```text
role splitting
parallel execution
ownership
reviewer isolation
```

重构后触发条件应覆盖：

* 当前 Host 有 tiered models，right-sizing model 会有明显价值；
* reasoning effort 可以针对任务调整；
* delegated implementation + stronger review 有价值；
* ticket routing / frontier scheduling 有价值；
* subagent/thread topology 有明显帮助。

同时继续跳过：

* typo；
* 极小 config change；
* 非复杂文档修改；
* 明显单次执行的小任务。

## Preserve one-ticket boundary

从 `implement` 调用 `agent-config` 时：

```text
Scope: current-item
```

不得让 `agent-config` 重新拆 sibling tickets 或扩大实现范围。

---

# 23. `project-tickets` Compatibility

默认不重构 `project-tickets`。

必须确认：

```text
skills/project-tickets/SKILL.md
references/TICKET-CONTRACT.md
references/WORKFLOW.md
```

仍然成立。

禁止为了 agent-config 添加 required fields：

```text
model
effort
agent
provider
```

Ticket 必须保持 provider-neutral。

`agent-config` 在运行时读取：

* What to build；
* acceptance criteria；
* Blocked by；
* frontier；
* ticket relationship；

自行判断 difficulty 与 routing。

如果确有兼容性文档需要补一句，只做最小修改。

---

# 24. `ask-light` Compatibility

检查并更新：

```text
skills/ask-light/SKILL.md
skills/ask-light/references/light-skill-map.json
skills/ask-light/tests/
```

必须继续保持：

```text
ready implementation ticket
→ implement
```

即使任务复杂，也不能因为 `agent-config` 变强就让 `ask-light` 把 canonical workflow 改成：

```text
ready ticket
→ agent-config
```

正确边界：

```text
User wants work implemented
→ implement

User explicitly wants to decide:
- which model?
- what effort?
- how should agents/threads be arranged?
- how should tickets be routed?
- what execution configuration should this Host use?
→ agent-config
```

更新 agent-config discovery patterns，使下面这些语义可以命中：

```text
which model should implement this
how should I configure agents
what effort should each ticket use
how should these tickets be distributed across models
single-model provider execution plan
multi-model routing
agent model configuration
```

但：

```text
split this SPEC into tickets
```

仍属于：

```text
project-tickets
```

---

# 25. `review-loop` / `project-review` Compatibility

审查：

```text
skills/review-loop/
skills/code-review/
skills/generic-review/
skills/project-review/
docs/workflows/review-system.md
```

原则：

`agent-config` 可以决定：

```text
review context
review model
review effort
```

但不能决定：

```text
review rubric
findings schema
repair loop semantics
PASS / FAIL / BLOCKED
```

不要复制 `review-loop` 或 reviewer Skill 的规则。

如果没有直接 contract 冲突，尽量不修改成熟 review Skills。

通过 integration tests 证明兼容即可。

---

# 26. Repository Documentation Compatibility

执行全仓 reference audit。

至少搜索：

```bash
rg -n \
  "agent-config|multi-model-multi-agent|single-model-multi-agent|single-model-single-agent|role-clear plan|execution waves|ownership matrix|Controller|Explorer|Implementer|Reviewer|Merger" \
  .
```

逐条区分：

```text
behavior contract
documentation
example
test
historical evidence
release record
```

历史 release evidence 不要为了当前行为强行重写。

必须检查并按实际受影响范围同步：

```text
README.md
README.zh-CN.md

CATALOG.md
CATALOG.zh-CN.md

docs/workflows/execution.md
docs/zh-CN/workflows/execution.md

AGENTS.md

CHANGELOG.md

skills/ask-light/references/light-skill-map.json

tests/test_composition.py
tests/test_collection_discovery.py
```

以及 `rg` 找到的其他 live documentation。

---

# 27. `AGENTS.md` Compatibility

当前 maintenance contract 对 `agent-config` 的描述不能继续把重点放在 generic abstract role fallback。

做最小更新，使设计原则表达为：

> Inspect Host first; remain provider-neutral; route by evidenced model capability, effort control, and execution topology; degrade safely on fixed-model Hosts.

必须继续保留：

```text
Do not guess Agent host capabilities.
```

不要把本 SPEC 复制进 `AGENTS.md`。

---

# 28. CATALOG / Workflow Docs

将旧描述：

```text
host-capability mapper
safe execution plan with role-clear fallbacks
multi-model/multi-agent / single-model/multi-agent / single-model/single-agent
```

更新成真正的新职责。

建议概念：

```text
Host-aware model and execution configurator
```

Purpose：

> Inspect current Host capabilities and task shape, then right-size model tier, reasoning effort, and agent/thread execution topology with safe fixed-model fallback.

Execution workflow 文档要体现：

```text
implement
   ↓ optional
agent-config
   ↓
right-size model / effort / execution topology
   ↓
implement bounded item
   ↓
review-loop
```

对于 ticket graph planning：

```text
project-tickets
   ↓
agent-config (optional execution configuration)
   ↓
one implement invocation per ready ticket
```

不要把 `agent-config` 插进 canonical project workflow 作为 mandatory stage。

---

# 29. `openai.yaml`

更新：

```text
skills/agent-config/agents/openai.yaml
```

当前 default prompt 过度强调：

```text
Controller, Explorer, Implementer, Reviewer, Merger plan
```

改为强调：

```text
inspect current Host
classify provider mode
classify task shape
right-size model tier
right-size effort
choose execution topology
```

继续保持：

```yaml
allow_implicit_invocation: true
```

前提是：

> implicit invocation 永远只能产生 read-only planning/config recommendation。

任何 Provider adapter project mutation：

```text
requires explicit approval
```

增加测试锁定这个边界。

---

# 30. Suggested Package Shape

最终结构可以类似：

```text
skills/agent-config/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── host-evidence-schema.md
│   ├── plan-schema.md
│   ├── task-assessment.md
│   └── provider-adapter-contract.md
└── tests/
    ├── fixtures/
    ├── test_agent_config_contract.py
    ├── test_agent_config_behavior.py
    └── ...
```

不要为了形式新建空目录或空文件。

`SKILL.md` 保持 concise。

详细：

* evidence schema；
* 2×2 behavior；
* task assessment；
* output format；
* adapter semantics；

放入 references。

---

# 31. Required Behavioral Tests

现有：

```text
test_agent_config_contract.py
test_agent_config_behavior.py
```

需要实质重写。

不要继续用 prose-presence tests 锁死旧架构。

优先测试 behavior / contract invariants。

---

# 32. Required Four-Quadrant Fixtures

至少建立以下 fixtures。

## Case A — tiered multi-model + single-pass

Host：

```text
3 selectable model ranks
reasoning control available
subagent available
fresh session available
```

Task：

```text
moderate bounded task
```

期望：

* task shape = single-pass；
* implementation 不默认使用最高模型；
* 使用最低足够模型；
* review 可以使用更高 rank；
* 不产生无意义 execution waves；
* 不强制 Explorer/Merger。

---

## Case B — tiered multi-model + decomposed

Host：

```text
3 model ranks
per-context model selection
reasoning levels
subagents
parallelism
concurrency cap
```

Tickets：

```text
01 routine
02 moderate
03 demanding
04 blocked
```

期望：

* Controller 使用最高 model rank；
* Controller effort 为 high/max；
* ticket assignments 随难度单调不下降；
* ready/disjoint tickets 才能并行；
* blocked ticket 不得执行；
* concurrency 不超过 cap；
* worker return 交 Controller；
* formal review 仍 handoff `review-loop`。

---

## Case C — fixed single-model + single-pass

Host：

```text
one current model
reasoning control available
```

期望：

```text
same model
max effort
direct execution
```

并且：

* 不创建虚假 role matrix；
* 不因为没有 model selector 而 BOUNDARY；
* helper subagent 仅按实际需要。

---

## Case D — fixed single-model + decomposed

Host：

```text
one model
subagents/threads available
parallelism available
```

Ticket graph：

```text
multiple ready items
```

期望：

* Controller 和 workers 全部同一模型；
* 全部 max effort；
* 仍然可以利用 threads/subagents；
* frontier independent tickets 可并行；
* 每个 worker 仍对应一个 ticket；
* Controller 做 integration review。

---

# 33. Required Degradation Tests

至少覆盖：

## Multiple models but no trusted rank

不得猜哪个更聪明。

应降级为：

```text
tier routing unavailable
```

使用当前可执行模型，或在真正影响安全/成本时 `NEED-INPUT`。

不得根据：

```text
model-pro
model-mini
model-ultra
```

名字自行排序。

## Reasoning control unavailable

继续执行。

不得 BOUNDARY。

## Per-agent model selection unavailable

如果 Host 仍可通过 fresh-session selection 实现分层，可以用对应 topology。

否则降级。

## Subagents unavailable

serial。

## Parallelism unavailable

serial。

## Session threads unavailable

不得声称 independent review。

## Worktrees unavailable

不得声称 isolated worktree。

但普通 implementation 不应被阻塞。

## Concurrency cap unknown

不得猜并发上限。

安全串行，或使用已证实的最低安全行为。

---

# 34. Adapter Tests

必须测试：

## Adapter absent

```text
plan still READY
Apply mode: plan-only
```

## Adapter metadata stale

不得使用 stale model rank。

## Adapter apply supported but user has not approved

不得写配置。

## Explicit approval + valid adapter

允许 apply。

必须能确认：

```text
what was applied
where
which project
which model/effort assignments
```

## Adapter failure

不得假成功。

保留 plan + limitation。

---

# 35. Workflow Integration Tests

扩展 repository-level composition tests。

至少证明：

## Implement opt-in preserved

```text
complex ticket
→ offer agent-config
→ decline
→ implementation continues
```

## Implement accepts

```text
complex ticket
→ accept agent-config
→ current-item config
→ implement only that ticket
```

## Small ticket

```text
implement
→ no unnecessary agent-config offer
```

## Ask Light

Ready ticket：

```text
ask-light
→ implement
```

Model-routing explicit request：

```text
ask-light / explicit request
→ agent-config
```

Split SPEC request：

```text
→ project-tickets
```

不能错路由到 agent-config。

## Project tickets

证明：

```text
agent-config
```

没有接管正式 ticket publication。

## Review

证明：

```text
agent-config review recommendation
```

不会绕过：

```text
review-loop
project-review
```

---

# 36. Old Contract Regression Cleanup

旧 tests 当前会锁定：

```text
Multi-model, multi-agent
Single-model / fixed-model, multi-agent
Single-model / fixed-model, single-agent

Controller
Explorer
Implementer
Reviewer
Merger

exact file ownership
execution waves
one named Merger
```

这些 assertions 不能为了让测试继续 PASS 而保留无意义旧 prose。

必须：

1. 识别旧 test 真正保护的安全 invariant；
2. 把 invariant 迁移到新 contract；
3. 删除仅锁 prose/layout 的 assertions。

例如：

旧：

```text
must contain Merger
```

应该改成：

```text
must not invent a Merger unless integration topology requires one
```

旧：

```text
must always contain Execution waves
```

应该改成：

```text
decomposed plan respects dependency/frontier/concurrency;
single-pass plan does not require waves
```

---

# 37. Important Invariants

无论如何重构，下面这些 invariant 必须继续成立。

### Host evidence

```text
unknown ≠ unavailable
unknown ≠ available
```

### No capability invention

```text
subagent support
≠
parallelism support
```

```text
parallelism
≠
worktree support
```

```text
model selector
≠
per-agent model selection
```

### Model routing

```text
no trusted rank
→
no guessed intelligence hierarchy
```

### Effort routing

```text
no reasoning control
→
do not pretend effort was configured
```

### Fixed-model fallback

```text
one usable model
→
valid execution path still exists
```

### Small task

```text
simple task
→
do not manufacture orchestration
```

### Project workflow

```text
formal decomposition
→
project-tickets owns it
```

### Implementation

```text
one implement invocation
→
one bounded work item
```

### Review

```text
agent-config
≠
review engine
≠
final acceptance authority
```

### Mutation

```text
implicit agent-config invocation
→
read-only
```

```text
project config mutation
→
explicit approval
```

---

# 38. Provider-neutrality Test

Live `agent-config` package必须保持 provider-neutral。

Core behavior中不得依赖具体：

```text
Sol
Terra
Luna
GPT-x
Claude-x
Gemini-x
```

不得依赖具体路径：

```text
.codex/*
.claude/*
```

除非这些内容只存在于明确隔离的 Provider adapter，并且核心 contract 不依赖它。

测试 fixtures 使用：

```text
model-alpha
model-beta
model-gamma
```

即可。

---

# 39. Documentation Examples

给 `agent-config` 增加至少四个短例子，对应四象限。

例子要体现“结果差异”，而不是换个 Host 名字重复同一份 plan。

### Multi + Small

重点：

```text
right-size implementer
stronger reviewer
minimal delegation
```

### Multi + Large

重点：

```text
Controller high
ticket-level model routing
ticket-level effort routing
frontier execution
```

### Single + Small

重点：

```text
direct max-effort execution
```

### Single + Large

重点：

```text
same-model workers
max effort
thread orchestration only
```

---

# 40. Validation Commands

至少执行：

```bash
python3 -m unittest discover -s skills/agent-config/tests
```

以及：

```bash
python3 -m unittest discover -s skills/implement/tests
```

如果 package 有 tests。

必须执行 repository-level：

```bash
python3 -m unittest discover -s tests
```

以及受影响的：

```text
ask-light tests
project-tickets tests
review composition tests
```

具体命令按仓库现有 test layout 执行。

执行安装副本 / isolated package test，确认 `agent-config` 单独复制安装后仍然自包含。

---

# 41. Static Audit

完成代码与测试后再次：

```bash
rg -n \
  "multi-model-multi-agent|single-model-multi-agent|single-model-single-agent|role-clear plan|one named Merger|Execution waves|Ownership matrix" \
  skills docs README.md README.zh-CN.md CATALOG.md CATALOG.zh-CN.md tests
```

对于每一个残留：

* 如果是历史 migration/release evidence：保留并说明；
* 如果是 live contract：迁移；
* 如果是 stale documentation：修复；
* 如果是 stale test：修复。

不得留下 live docs 描述旧行为。

---

# 42. Review Requirements

这是 architecture-level behavioral refactor，不按 prompt-only fast track。

按仓库 full path 完成：

```text
focused automated tests
negative tests
behavior fixtures
composition tests
fresh independent review
```

如修改 executable helper/script：

```text
code-review
```

也必须进入。

随后用：

```text
review-loop
```

按 `agent-skill` / 对应 Profile 收敛 findings。

最终需要准备给：

```text
project-review
```

的完整 evidence。

不要由实现 Agent 自己签发最终 PASS。

---

# 43. Acceptance Criteria

只有全部满足才算完成。

## AC-01 — Correct core purpose
## AC-02 — Four modes
## AC-03 — Model right-sizing
## AC-04 — Strong review
## AC-05 — Effort actually used
## AC-06 — Single-model simplicity
## AC-07 — Single-model large-task support
## AC-08 — No guessed model intelligence
## AC-09 — Project Tickets ownership preserved
## AC-10 — Implement boundary preserved
## AC-11 — Implement opt-in preserved
## AC-12 — Ask Light routing preserved
## AC-13 — Review ownership preserved
## AC-14 — Adaptive plan
## AC-15 — Host-agnostic
## AC-16 — Adapter optional
## AC-17 — Mutation approval
## AC-18 — Documentation synchronized
## AC-19 — Full test suite green
## AC-20 — Clean repository state

---

# 44. Required Completion Report

完成后给人工审阅者一份报告，至少包括：

```text
Verdict: READY FOR HUMAN REVIEW

Commit:
<local commit SHA>

Working tree:
clean

Push:
NO

Release:
NO
```

---

# 45. Final Design Test

重构完成后，用下面四句话检查架构。

如果当前 Host 是多模型 Provider：
> “这个任务值得用哪个等级的模型？应该给多少 effort？Review 是否应该上更强模型？”

如果当前 Host 是单模型 Provider：
> “既然只有一个模型，就别给我演模型编排；告诉我直接做还是拆 ticket，以及线程怎么跑。”

如果任务很小：
> “别为了有 Agent Config 就制造 Agent。”

如果任务很大：
> “正式拆票仍然走 project-tickets，但 ticket 出来以后，agent-config 要知道哪个 ticket 值得用多少模型智力和多少 effort，并能把执行 topology 配出来。”
