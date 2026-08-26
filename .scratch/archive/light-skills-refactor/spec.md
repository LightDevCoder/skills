# SPEC — Light Skills Workflow & Package Refactor

> status: superseded
> superseded_by: ../light-skills-lean-refactor/spec.md
> execution_authority: none

## 1. Objective

将 `LightDevCoder/skills` 重构为一套完整的：

> **First-party, general-purpose, composable Agent workflow system.**

本次不是简单增加 Skill，也不是创建一个巨型 orchestrator。

最终由：

```text
Project Workflow
+
Clarification & Research
+
Execution
+
Review
+
Reusable Capabilities
+
Specialized Workflows
+
Router
```

组成完整工作流。

同时修正上一轮重构暴露出的 Skill 写作问题：

> **系统架构可以完整，但单个 `SKILL.md` 不应该变成系统架构文档。**

本次必须同时做到：

```text
恢复并实现完整 Light workflow architecture
+
用成熟 Agent Skill 的方式实现每个 package
```

---

# 2. Starting Point

本地实施目录当前为空。

首先 clone 三个 LightDevCoder 仓库：

```bash
git clone https://github.com/LightDevCoder/skills.git
git clone https://github.com/LightDevCoder/ELI5.git
git clone https://github.com/LightDevCoder/release-workflow.git
```

主实施仓库：

```text
LightDevCoder/skills
```

另外两个仓库作为第一方 Skill 迁移来源：

```text
LightDevCoder/ELI5
LightDevCoder/release-workflow
```

最终：

```text
eli5
release-workflow
```

迁入：

```text
LightDevCoder/skills/skills/
```

两个来源仓库本身不要修改或删除。

---

# 3. Reference Repositories

## 3.1 Matt Pocock Skills

主要 Skill 写法和 package 设计参考：

```text
https://github.com/mattpocock/skills
```

不要求 clone。

实施 Matt-derived Skill 前直接阅读对应 upstream Skill/package。

重点参考不同形态：

```text
grilling
→ focused behavior Skill

grill-with-docs
→ composition Skill

teach
→ Skill + supporting documents

research
prototype
tdd
handoff
diagnosing-bugs
...
→ concise execution-oriented Skills
```

Matt Skills 提供的是：

```text
Skill writing style
package organization
progressive disclosure
composition style
execution feel
```

不是统一模板。

不要要求所有 Skill：

```text
相同行数
相同 headings
相同目录
相同 references 数量
相同 package shape
```

---

## 3.2 Sol Advisor

`agent-config` 的主要参考：

```text
https://github.com/DannyMac180/sol-advisor
```

重点吸收其：

```text
runtime inspection
available model / agent awareness
role assignment
reasoning-level selection
execution routing
capability-aware fallback
```

等思想。

不要复制固定：

```text
Sol
Terra
Luna
Codex-only topology
```

Light `agent-config` 必须是 host-agnostic。

核心原则：

> **Inspect the real Agent environment first, then configure execution from capabilities that actually exist.**

无法确认的：

```text
model
agent
reasoning level
parallelism
worktree
subagent support
```

不得猜测。

---

# 4. Current First-party Baseline

当前 `LightDevCoder/skills` 中已有：

```text
ask-light
project-init
review-loop
manuscript-ops
kb-init
learn-anything
language-learning
kanban-worker
recap
```

另外迁入：

```text
eli5
release-workflow
```

因此本次有 11 个现有 Light first-party baseline。

其中绝大多数不是本次重写对象。

---

# 5. Target Architecture

完成后仓库包含 **33 个 Skill**。

---

## 5.1 Project Workflow

```text
project-init
project-clarify
project-spec
project-tickets
implement
project-review
release-workflow
```

推荐完整项目流程：

```text
project-init
      ↓
project-clarify
      ↓
project-spec
      ↓
project-tickets
      ↓
implement
      ↓
project-review
      ↓
release-workflow
```

这是推荐主流程，不是强制流水线。

任务已经进入中间阶段时可以直接从相应 Skill 开始。

---

# 6. Clarification & Research

包含：

```text
socratic
clarify
project-clarify
decision-map
research
prototype
to-questionnaire
```

核心关系：

```text
                    socratic
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       clarify   project-clarify  decision-map
```

### socratic

参考：

```text
Matt grilling
```

作为底层 clarification capability。

负责：

```text
动态追问
沿着用户回答继续展开
避免固定 questionnaire
区分事实问题和用户决策
持续收敛未解决决策
```

它不是完整项目 workflow。

---

### clarify

参考：

```text
Matt grill-me
```

轻量 standalone clarification entry。

用于：

```text
idea
requirement
brainstorm
process
vague request
```

调用：

```text
clarify
→ socratic
```

不要求生成正式 SPEC。

---

### project-clarify

主要参考：

```text
Matt grill-with-docs
```

用于已有项目。

在提问前先读取真实项目上下文，例如：

```text
README
AGENTS.md
CLAUDE.md
existing docs
source
existing specs
task state
```

项目已经可以回答的事实不要重新询问用户。

调用：

```text
project-clarify
→ socratic
```

必要时使用：

```text
research
prototype
```

大型任务可以升级：

```text
decision-map
```

---

### decision-map

主要参考：

```text
Matt wayfinder
```

用于：

```text
large project
multi-session work
many dependent decisions
mixed research / prototype / human decisions
```

它负责维持长期可恢复的决策地图。

任务足够明确后进入：

```text
project-spec
```

---

### Unknown Routing

Clarification family 中遇到未知信息：

```text
Unknown
  │
  ├─ 用户必须决定
  │      → socratic
  │
  ├─ 外部事实
  │      → research
  │
  ├─ 需要实验
  │      → prototype
  │
  └─ 信息掌握在另一个人手里
         → to-questionnaire
```

---

# 7. Planning

包含：

```text
project-spec
project-tickets
```

### project-spec

主要参考：

```text
Matt to-spec
```

将已经完成澄清的信息整理成正式 project SPEC。

不要重新开始一次 clarification interview。

如果仍存在真正阻塞的用户决策：

```text
return to project-clarify
```

---

### project-tickets

主要参考：

```text
Matt to-tickets
```

将正式 SPEC 转为 Agent 可执行 task graph。

优先按：

```text
vertical / tracer-bullet slices
```

组织任务。

支持：

```text
dependencies
ready work
parallelizable tasks
verification
```

详细 ticket workflow 和 examples 应放 supporting documents，而不是把全部规则堆进 `SKILL.md`。

---

# 8. Execution

包含：

```text
implement
agent-config
tdd
diagnosing-bugs
resolving-merge-conflicts
```

---

## agent-config

参考：

```text
https://github.com/DannyMac180/sol-advisor
```

负责在复杂执行前检查当前真实 Agent Host。

可以识别：

```text
available models
available agents
subagents
parallelism
reasoning levels
multi-session support
per-agent model selection
worktrees
concurrency
```

使用抽象执行角色，例如：

```text
Controller
Explorer
Implementer
Reviewer
Merger
```

再根据当前真实环境进行映射。

Fallback：

```text
multi-model + multi-agent
→ 可充分编排

single-model + multi-agent
→ 同模型不同 context / role

single-model + single-agent
→ 顺序执行
```

不要为了“发挥 agent-config”而强行多 Agent。

简单任务不需要调用它。

---

## implement

主要参考：

```text
Matt implement
```

但 Light 版本必须是：

> **general-purpose bounded work executor**

可以执行：

```text
code
document
configuration
research artifact
Skill
generic project task
```

不是 Coding-only Skill。

通用关系：

```text
clear work item
→ inspect relevant context
→ agent-config when useful
→ execute
→ verify
→ review-loop when appropriate
```

Coding 时可以：

```text
implement
→ tdd when appropriate
→ code changes
→ tests
→ review-loop
→ code-review
```

Non-coding：

```text
implement
→ produce artifact
→ review-loop
→ generic-review / domain reviewer
```

不要把 `agent-config`、`tdd`、`review-loop` 或 reviewer 的完整 instructions 复制进 `implement/SKILL.md`。

---

# 9. Review Architecture

包含：

```text
review-loop
generic-review
code-review
project-review
```

核心关系：

```text
                 review-loop
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
generic-review   code-review   domain-review
```

---

## review-loop

当前 Light `review-loop` 必须重构。

新的职责只保留：

```text
review
→ findings
→ repair
→ re-review
```

它负责：

```text
resolve reviewer
invoke reviewer
receive findings
return repair to Producer
re-run reviewer
stop when clean or bounded limit reached
```

普通 review-loop 不再默认维护完整项目 acceptance system。

---

## generic-review

新的默认 reviewer。

用于没有专业 reviewer 的工作。

检查：

```text
missing requirements
incorrect result
contradictions
obvious usability issues
unnecessary scope expansion
```

保持简单。

不要创建巨大的领域规则库。

---

## code-review

主要参考：

```text
Matt code-review
```

保留其成熟代码审查方法。

适配为：

```text
read-only reviewer
→ findings
```

它不能：

```text
自己修代码
自己运行 repair loop
决定整个项目最终 PASS
```

---

## project-review

新的项目最终验收能力。

回答：

> Does the completed project actually satisfy the approved project target?

它可以组合：

```text
generic-review
code-review
domain reviewers
```

并使用：

```text
review-loop
```

处理 review / repair convergence。

当前旧 `review-loop` 中真正属于：

```text
frozen acceptance baseline
final verdict
PASS / FAIL / BLOCKED
final acceptance evidence
scope-change boundary
```

的有效逻辑迁移到 `project-review`。

不要删除已经验证有效的 final-acceptance 能力后从零重写。

---

# 10. Specialized Workflows

继续保留：

```text
manuscript-ops
kb-init
learn-anything
kanban-worker
```

它们拥有自己的专业 workflow。

不要强迫它们变成：

```text
project-init
→ project-clarify
→ ...
```

的内部组成部分。

它们可以在合适位置调用新的 reusable capabilities。

---

# 11. Productivity & Communication

包含：

```text
handoff
recap
wizard
wait-what
writing-for-agents
```

其中：

```text
handoff
wizard
wait-what
writing-for-agents
```

直接以 Matt upstream package 为 baseline Port。

`recap` 使用当前 Light 版本。

---

# 12. Learning & Explanation

包含：

```text
eli5
teach
language-learning
```

`eli5` 从：

```text
https://github.com/LightDevCoder/ELI5
```

迁入。

`teach` 从 Matt Port。

`language-learning` 使用当前 Light 版本。

---

# 13. Router

## ask-light

当前 `ask-light` 重构为：

> **Light Skills Workflow Router**

它最后实施。

原因：

> **先把路修好，再画地图。**

它需要理解：

```text
current intent
project context
existing artifacts
available first-party Skills
current project stage
specialized workflow
host capabilities
```

典型 routing：

```text
vague idea
→ clarify

existing project + unclear requirements
→ project-clarify

large foggy project
→ decision-map

missing fact
→ research

need experiment
→ prototype

information is held by another person
→ to-questionnaire

SPEC exists
→ project-tickets

ticket is ready
→ implement

hard bug
→ diagnosing-bugs

implementation complete
→ project-review

ready to publish
→ release-workflow

previous explanation did not land
→ wait-what
```

`ask-light` 不重新实现这些能力。

---

# 14. Skills That Must Not Be Rewritten

以下 Skill **禁止进行主体重构或重新设计**：

```text
manuscript-ops
kb-init
learn-anything
language-learning
kanban-worker
recap
eli5
release-workflow

research
prototype
tdd
handoff
diagnosing-bugs
wizard
teach
wait-what
to-questionnaire
writing-for-agents
resolving-merge-conflicts
```

共 19 个。

---

## Existing Light Skills

以下当前 Light Skill 保留现有成熟实现：

```text
manuscript-ops
kb-init
learn-anything
language-learning
kanban-worker
recap
```

处理方式：

```text
保留主体
→ 验证 standalone behavior
→ 验证能否参与新 workflow
→ 只在确实需要串联时增加最小 handoff / invocation 描述
```

如果当前行为无需修改：

> **不要修改 `SKILL.md`。**

不要因为：

```text
本次仓库正在重构
SKILL.md 比较长
新的 package philosophy
希望统一风格
```

而顺手重写它们。

---

## Migrated Light Skills

```text
eli5
release-workflow
```

分别从：

```text
https://github.com/LightDevCoder/ELI5
https://github.com/LightDevCoder/release-workflow
```

迁入。

原则：

```text
完整保留成熟 package
→ 迁入主仓库
→ 验证 discovery / installation
→ 加入 catalog / router / workflow
```

不要借迁仓机会：

```text
重新设计
重新拆文件
压缩 SKILL.md
改变 workflow
```

除非迁移本身发现真实 bug。

---

## Matt Skills Direct Port

以下 Skill 使用 Matt 当前实现作为 baseline：

```text
research
prototype
tdd
handoff
diagnosing-bugs
wizard
teach
wait-what
to-questionnaire
writing-for-agents
resolving-merge-conflicts
```

处理方式：

```text
read full upstream package
→ port useful package
→ preserve mature behavior
→ remove incompatible upstream coupling
→ add only necessary Light integration
```

禁止：

```text
读 Matt Skill
→ 根据 Light architecture 自己重写一份
```

如果只需要改一个调用名称或 handoff：

> **只改这一处。**

---

# 15. Skills That Actually Require Architecture-level Work

真正需要职责级设计或改造的是：

```text
ask-light
project-init
review-loop

socratic
clarify
project-clarify
decision-map
project-spec
project-tickets

implement
code-review

generic-review
project-review
agent-config
```

---

## Existing Light Refactors

```text
ask-light
project-init
review-loop
```

这是现有 Skill 中真正需要职责级修改的三个。

---

## Adapted Skills

主要参考成熟 upstream，但因为 Light 架构产生真实差异：

```text
socratic
clarify
project-clarify
decision-map
project-spec
project-tickets
implement
code-review
```

---

## New Light Capabilities

```text
generic-review
project-review
agent-config
```

其中：

```text
project-review
```

必须优先迁移旧 `review-loop` 的成熟 final-acceptance 能力。

```text
agent-config
```

必须参考：

```text
https://github.com/DannyMac180/sol-advisor
```

而不是凭空设计。

---

# 16. Migration Matrix

| Skill                     | Source                               | Action                |
| ------------------------- | ------------------------------------ | --------------------- |
| ask-light                 | current Light                        | REFACTOR              |
| project-init              | current Light                        | REFACTOR              |
| review-loop               | current Light                        | REFACTOR + SPLIT      |
| manuscript-ops            | current Light                        | PRESERVE — NO REWRITE |
| kb-init                   | current Light                        | PRESERVE — NO REWRITE |
| learn-anything            | current Light                        | PRESERVE — NO REWRITE |
| language-learning         | current Light                        | PRESERVE — NO REWRITE |
| kanban-worker             | current Light                        | PRESERVE — NO REWRITE |
| recap                     | current Light                        | PRESERVE — NO REWRITE |
| eli5                      | LightDevCoder/ELI5                   | MIGRATE — NO REWRITE  |
| release-workflow          | LightDevCoder/release-workflow       | MIGRATE — NO REWRITE  |
| research                  | Matt                                 | PORT — NO REDESIGN    |
| prototype                 | Matt                                 | PORT — NO REDESIGN    |
| tdd                       | Matt                                 | PORT — NO REDESIGN    |
| handoff                   | Matt                                 | PORT — NO REDESIGN    |
| diagnosing-bugs           | Matt                                 | PORT — NO REDESIGN    |
| wizard                    | Matt                                 | PORT — NO REDESIGN    |
| teach                     | Matt                                 | PORT — NO REDESIGN    |
| wait-what                 | Matt                                 | PORT — NO REDESIGN    |
| to-questionnaire          | Matt                                 | PORT — NO REDESIGN    |
| writing-for-agents        | Matt                                 | PORT — NO REDESIGN    |
| resolving-merge-conflicts | Matt                                 | PORT — NO REDESIGN    |
| code-review               | Matt                                 | ADAPT                 |
| implement                 | Matt                                 | ADAPT                 |
| socratic                  | Matt grilling                        | ADAPT                 |
| clarify                   | Matt grill-me                        | ADAPT                 |
| project-clarify           | Matt grill-with-docs                 | ADAPT                 |
| decision-map              | Matt wayfinder                       | ADAPT                 |
| project-spec              | Matt to-spec                         | ADAPT                 |
| project-tickets           | Matt to-tickets                      | ADAPT                 |
| generic-review            | Light architecture                   | NEW                   |
| project-review            | old review-loop + Light architecture | NEW / MIGRATE LOGIC   |
| agent-config              | Light architecture + Sol Advisor     | NEW / ADAPT DESIGN    |

---

# 17. Skill Package Writing Rules

这些规则主要适用于：

```text
NEW
ADAPT
REFACTOR
```

以及真正需要修改的 PORT Skill。

**不要用这些规则回头格式化 NO REWRITE Skill。**

---

## SKILL.md Is the Entry

`SKILL.md` 尽量保持精简。

它主要负责：

```text
when to use the Skill
what capability it provides
core execution behavior
which supporting document to read
which Skill to invoke / hand off to when needed
completion / stopping boundary when necessary
```

它不是：

```text
architecture document
complete workflow manual
example library
format specification
maintenance document
migration record
```

---

## Detailed Workflow Belongs in Supporting Files

复杂 Skill 的详细 workflow 默认拆到 supporting documents。

例如：

```text
skill-name/
├── SKILL.md
├── references/
│   ├── WORKFLOW.md
│   ├── EXAMPLES.md
│   ├── OUTPUT-FORMAT.md
│   └── ...
├── templates/
├── scripts/
└── tests/
```

这里只是示例。

每个 package 根据自己真实需要决定：

```text
references 数量
文件名
目录结构
templates
scripts
tests
```

不要创建空目录或占位文件。

---

## Examples Belong Outside SKILL.md

大量案例、完整输入输出示例和 edge-case examples 放 supporting docs。

`SKILL.md` 只在需要时：

```text
Read `references/EXAMPLES.md` when ...
```

不要用几十个 examples 把主 Skill 撑大。

---

## Composition Before Duplication

如果已有 Skill 能完成某项能力：

```text
call it
```

不要重新复制它的 instructions。

例如：

```text
project-clarify
→ socratic
```

不意味着 `project-clarify` 要重新写一套 socratic。

```text
implement
→ review-loop
→ code-review
```

不意味着 `implement` 要复制 review 和 code-review 方法。

---

# 18. Small-task Paths

完整项目：

```text
project-init
→ project-clarify
→ project-spec
→ project-tickets
→ implement
→ project-review
→ release-workflow
```

模糊想法：

```text
clarify
```

明确小任务：

```text
implement
→ review-loop when useful
```

困难 Bug：

```text
diagnosing-bugs
→ implement
→ review-loop
```

完成项目：

```text
project-review
```

仅发布：

```text
release-workflow
```

不知道入口：

```text
ask-light
```

---

# 19. Specialized Workflow Integration

对于：

```text
manuscript-ops
kb-init
learn-anything
kanban-worker
language-learning
eli5
recap
release-workflow
```

先运行：

```text
standalone verification
+
composition verification
```

如果现有输出已经可以自然交给下一 Skill：

> 不修改 Skill。

如果缺少明确串联关系：

只增加类似：

```text
When this workflow reaches <state>, the caller may continue with <skill>.
```

或：

```text
Return <artifact/result> to the calling workflow.
```

这样的最小 handoff 描述。

**增加串联关系不是重写 Skill 的理由。**

---

# 20. Repository Documentation

本次必须同步调整仓库维护文档。

核心规则：

> **Repository documentation explains the repository.
> Skill documentation explains the Skill.**

不要互相复制。

---

## README.md / README.zh-CN.md

面向用户。

负责：

```text
what Light Skills is
installation
quick start
main workflow
small-task examples
ask-light entry
representative capabilities
```

展示主流程即可：

```text
project-init
→ project-clarify
→ project-spec
→ project-tickets
→ implement
→ project-review
→ release-workflow
```

不要在 README 重新解释每个内部 Contract。

---

## CATALOG.md / CATALOG.zh-CN.md

只负责 Skill discovery：

```text
Skill
Purpose
When to use
Invocation where useful
Package path
```

最终 catalog 与真实 33 个 package 一致。

不要复制完整 Skill 文档。

---

## docs/workflows/

负责仓库级 Skill composition。

至少维护：

```text
project-workflow.md
clarification-system.md
execution.md
review-system.md
specialized-workflows.md
```

这里解释：

```text
Skill A
→ Skill B
→ Skill C
```

以及：

```text
entry
handoff
stop
optional path
```

不要复制各个 Skill 内部详细 workflow。

---

## AGENTS.md

这是以后 Agent 维护仓库时的主要长期规则。

必须明确：

```text
Matt Pocock Skills is the primary Skill-writing reference.

Sol Advisor is the primary design reference for agent-config.

Inspect the relevant upstream/reference Skill before modifying a derived Skill.

Do not rewrite mature Light Skills unless their actual responsibility must change.

Do not redesign direct Matt PORT Skills.

Keep new/refactored SKILL.md files concise.

Put detailed workflows, examples, formats and reusable guidance in supporting files.

Do not impose one Skill package shape.

Prefer composition over duplicated instructions.

Do not duplicate repository architecture into Skill packages.

Update only repository documents actually affected by a change.

Tests should protect behavior and composition, not prose layout.

Preserve required upstream attribution.

Do not guess Agent host capabilities.
```

AGENTS.md 不要重新膨胀成 Architecture SPEC。

---

## docs/MAINTENANCE.md

更新为实际仓库维护流程。

重点说明：

```text
add
update
rename
remove
port
adapt
documentation synchronization
catalog synchronization
tests
attribution
release handoff
```

不要复制 AGENTS 或 Architecture 内容。

---

## docs/SKILL_ADMISSION.md

当前旧规则如果禁止一切 upstream Port，需要更新。

新的规则允许：

```text
approved upstream Port
+
required attribution
+
Light-specific integration
+
no upstream runtime dependency
```

但：

```text
Port
≠ arbitrary copying
```

本 SPEC 中列出的 Matt PORT Skill 已经获得本次架构层面的迁入授权。

---

## docs/REVIEW_POLICY.md

更新到新的：

```text
reviewer
vs
review-loop
vs
project-review
```

关系。

避免未来再次把 final project acceptance 塞回 `review-loop`。

---

## CHANGELOG

更新：

```text
CHANGELOG.md
CHANGELOG.zh-CN.md
```

记录本次重构为 unreleased change。

不要创建版本号、tag 或 GitHub Release。

---

# 21. Historical Records

旧：

```text
release evidence
admission evidence
historical changelog
released version records
```

属于历史事实。

不要为了适配新架构重写旧历史。

Active documentation 可以指向新的架构。

Historical evidence 保持原样。

---

# 22. Third-party / Upstream Policy

最终 Light 主 workflow 不得要求：

```text
install Matt skills first
install sol-advisor first
```

Port / Adapt 后的 Skill 属于 Light repository 自包含 package。

如果内容实质来源于 upstream：

根据 license 要求维护：

```text
ATTRIBUTION.md
```

至少记录：

```text
source repository
original Skill/path
revision or tag when practical
license / notice
Light-specific changes
```

`agent-config` 可以参考 Sol Advisor 的思想，但不要复制不需要的固定模型配置。

---

# 23. Hero Image

用户会把新的头图放入：

```text
Assets/
```

实施时检查实际文件名。

更新：

```text
README.md
README.zh-CN.md
```

使用新头图。

不要猜测文件名。

当前旧 header 如果已经不再被任何文档引用，可以删除。

其他仍使用的 assets 不要动。

---

# 24. Tests

保留仍然有效的现有测试。

旧测试如果锁定：

```text
old Skill count
old upstream policy
old Skill names
old wording
old architecture structure
old review-loop ownership
```

则根据新架构更新。

---

## Repository Tests

至少验证：

```text
33 expected Skill packages exist

every SKILL.md frontmatter is valid

all supporting-file references resolve

CATALOG matches real packages

README links resolve

workflow docs reference real Skills

no stale old Skill names remain

no required Matt runtime dependency exists

no required sol-advisor runtime dependency exists

hero asset exists

EN / zh-CN discovery docs remain synchronized
```

---

## Composition Tests

至少验证：

```text
clarify
→ socratic

project-clarify
→ socratic

decision-map
→ socratic / research / prototype / to-questionnaire

project-spec
→ project-tickets

implement
→ appropriate review path

review-loop
→ generic-review / code-review

project-review
→ review-loop + relevant reviewers

ask-light
→ routes to actually existing first-party Skills
```

---

## Behavior Tests

测试保护：

```text
observable behavior
important boundaries
handoff compatibility
real output
```

不要主要测试：

```text
specific heading
specific paragraph
exact prose
internal wording
```

如果旧测试只是为了保留某段文字：

> 重写测试，而不是为了通过测试把膨胀文字重新加回 Skill。

---

# 25. Implementation Order

## Phase 1 — Clone and inspect

Clone：

```text
LightDevCoder/skills
LightDevCoder/ELI5
LightDevCoder/release-workflow
```

检查：

```text
current packages
cross-skill references
tests
README
CATALOG
AGENTS
maintenance docs
review policy
installation docs
assets
historical evidence
```

先建立真实 baseline。

---

## Phase 2 — Migrate existing Light Skills

迁入：

```text
eli5
release-workflow
```

完整保留主体。

验证：

```text
package integrity
discovery
installation
references
```

---

## Phase 3 — Port Matt capabilities

直接 Port：

```text
research
prototype
tdd
handoff
diagnosing-bugs
wizard
teach
wait-what
to-questionnaire
writing-for-agents
resolving-merge-conflicts
```

先读完整 upstream package。

只进行：

```text
required attribution
runtime decoupling
Light naming / handoff integration
```

禁止重新设计。

---

## Phase 4 — Clarification architecture

实现：

```text
socratic
clarify
project-clarify
decision-map
```

参考：

```text
grilling
grill-me
grill-with-docs
wayfinder
```

确保：

```text
socratic
→ core clarification behavior

clarify
→ lightweight entry

project-clarify
→ project-aware entry

decision-map
→ large / persistent clarification
```

详细 workflows / examples 放 supporting docs。

---

## Phase 5 — Planning

实现：

```text
project-spec
project-tickets
```

分别参考：

```text
to-spec
to-tickets
```

---

## Phase 6 — Execution

实现：

```text
agent-config
implement
```

`agent-config` 参考：

```text
https://github.com/DannyMac180/sol-advisor
```

`implement` 参考 Matt `implement`，再适配为 general-purpose executor。

---

## Phase 7 — Review

重构：

```text
review-loop
```

实现：

```text
generic-review
project-review
```

Adapt：

```text
code-review
```

迁移旧 `review-loop` 中有价值的 project final-acceptance 逻辑到：

```text
project-review
```

---

## Phase 8 — project-init

在：

```text
project-clarify
```

已经存在后再调整 `project-init`。

删除其完整 clarification 职责。

只保留 minimum initialization。

---

## Phase 9 — Verify untouched Light Skills

对：

```text
manuscript-ops
kb-init
learn-anything
language-learning
kanban-worker
recap
eli5
release-workflow
```

执行串联验证。

只有真实 integration 缺口才允许最小 patch。

---

## Phase 10 — ask-light

最后重构：

```text
ask-light
```

此时完整 Skill map 已经真实存在。

只根据真实第一方能力建立 routing。

---

## Phase 11 — Repository documentation

更新：

```text
README*
CATALOG*
AGENTS.md
docs/workflows/*
docs/MAINTENANCE.md
docs/SKILL_ADMISSION.md
docs/REVIEW_POLICY.md
CHANGELOG*
```

清理：

```text
stale names
obsolete upstream assumptions
duplicate architecture prose
broken links
```

---

## Phase 12 — Hero image

接入：

```text
Assets/<actual-new-header-file>
```

---

## Phase 13 — Validation

运行：

```text
existing tests
updated repository tests
composition tests
relevant package tests
link checks
discovery checks
```

最终检查 git diff，确保没有误改 NO REWRITE Skill。

---

# 26. Final No-Redesign Check

结束前，对以下 19 个 Skill 单独检查 git diff：

```text
manuscript-ops
kb-init
learn-anything
language-learning
kanban-worker
recap
eli5
release-workflow
research
prototype
tdd
handoff
diagnosing-bugs
wizard
teach
wait-what
to-questionnaire
writing-for-agents
resolving-merge-conflicts
```

对于前 8 个成熟 Light Skill：

任何 substantive behavior change 都必须能指出真实 integration requirement。

对于后 11 个 Matt PORT Skill：

任何相对 upstream 的 substantive rewrite 都必须能指出真实 Light incompatibility。

否则撤销该修改。

---

# 27. Acceptance Criteria

完成后必须满足：

* `LightDevCoder/skills` 包含全部 33 个目标 Skill；
* `eli5` 已从 `LightDevCoder/ELI5` 迁入；
* `release-workflow` 已从 `LightDevCoder/release-workflow` 迁入；
* 19 个明确 NO REWRITE / NO REDESIGN Skill 未被无目的重构；
* Matt PORT Skills 以 upstream package 为真实 baseline；
* `agent-config` 明确基于 Sol Advisor 的 runtime-aware 思想设计；
* `agent-config` 不绑定 Sol/Terra/Luna 或单一 Agent Host；
* `socratic / clarify / project-clarify / decision-map` 构成 clarification family；
* `project-spec / project-tickets` 构成正式 planning stages；
* `implement` 为 general-purpose bounded executor；
* `review-loop` 已恢复为轻量 review/repair engine；
* `generic-review` 可作为默认 reviewer；
* `code-review` 是 read-only specialist reviewer；
* `project-review` 承接项目级 final acceptance；
* 旧 `review-loop` 有价值的 final acceptance 能力没有丢失；
* `project-init` 不再承担完整需求澄清；
* `ask-light` 最后完成并能理解全部真实第一方 workflow；
* Specialized Workflows 保持独立；
* 完整 Project Workflow 可以串联；
* Small-task Paths 可以独立使用；
* 新建/重构 Skill 的 `SKILL.md` 保持执行入口感；
* detailed workflow / examples / formats 合理放入 supporting files；
* 不存在强制统一的 Skill package shape；
* README / CATALOG / workflow docs / AGENTS 各自职责明确；
* active governance 已允许本 SPEC 明确批准的 upstream Port；
* attribution / license 正确；
* Light 主 workflow 不需要安装 Matt Skills；
* `agent-config` 不需要安装 Sol Advisor；
* 新 `Assets/` 头图已经正确接入 README；
* 所有真实行为测试、composition tests、discovery tests 和 links 检查通过；
* 没有创建新 release / tag。

---

# Final Direction

本次重构有两个同等重要的目标：

```text
Build the Light workflow architecture correctly.
+
Write the individual Skills correctly.
```

架构负责：

> **有哪些能力，以及这些能力如何组合。**

Matt Pocock Skills 负责提供：

> **一个 Skill/package 应该怎样写得简洁、自然、可执行。**

Sol Advisor 负责给 `agent-config` 提供：

> **如何根据真实 Agent runtime 做能力感知和执行配置的参考。**

对于已经成熟的 Skill：

> **能不改就不改。**

对于需要串联的成熟 Skill：

> **只加串联。**

对于直接 Port 的成熟 upstream Skill：

> **先 Port，再做最小适配，不重新发明。**

对于真正需要创建或重构的 Skill：

> **保持 `SKILL.md` 精简，把详细 workflow、examples、formats 和 reference material 放在最适合它自己的 supporting files 中。**

最终得到的不是一套由巨大 `SKILL.md` 拼出来的 Agent framework。

而是一组：

> **小而清晰、各司其职、可以组合成完整工作流的 Light Skills。**
