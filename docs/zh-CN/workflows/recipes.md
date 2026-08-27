# 工作流 Recipes

[英文版 recipes](../../workflows/recipes.md)

这些 recipe 是有边界的文档和验证资产，只描述显式 handoff；不会创建 canonical pipeline、永久 state machine 或自动多 Skill orchestrator。每个包的 `SKILL.md` 仍是行为权威。

## 来源与共同规则

- **第一方（33 个）：** 本仓库全部 Skill——`project-init`、`project-clarify`、`project-spec`、`project-tickets`、`implement`、`project-review`、`release-workflow`、`socratic`、`clarify`、`decision-map`、`research`、`prototype`、`to-questionnaire`、`agent-config`、`tdd`、`diagnosing-bugs`、`resolving-merge-conflicts`、`review-loop`、`generic-review`、`code-review`、`handoff`、`wizard`、`wait-what`、`writing-for-agents`、`teach`、`eli5`、`language-learning`、`recap`、`learn-anything`、`manuscript-ops`、`kb-init`、`kanban-worker`、`ask-light`（见 [CATALOG.zh-CN.md](../../../CATALOG.zh-CN.md)）。
- **已批准 PORT：** `research`、`prototype`、`tdd`、`handoff`、`diagnosing-bugs`、`wizard`、`teach`、`wait-what`、`to-questionnaire`、`writing-for-agents`、`resolving-merge-conflicts` 为带 `ATTRIBUTION.md` 的自包含第一方包，运行时不要求上游。
- **历史 Matt 名称：** `grill-me` → `clarify`、`grilling` → `socratic`、`grill-with-docs` → `project-clarify`、`wayfinder` → `decision-map`、`to-spec` → `project-spec`、`to-tickets` → `project-tickets` —— 仅用于归属说明，工作流以 Light 名称为准。
- **私有第三方修改版：** `skills-3rdParty` 内的包；不可见时属 availability gap，不编造 fallback。

`socratic` 为 model-invoked 引擎；`clarify` 为轻量用户入口，`project-clarify` 为项目感知入口，`decision-map` 为大型决策地图。把 `clarify → socratic` 等视为组合，非独立步骤。

每行均写明 handoff (stop condition) 与停止点。`user-invoked` 须用户显式选择；`model-invoked` 受包 policy 约束。specialist findings 不能成为最终 verdict；需验收时由 `project-review` 经 `review-loop` 拥有 `PASS`/`FAIL`/`BLOCKED`。 Each row declares the handoff artifact and stop condition — handoff/stop.

## 1. 软件项目

入口已明确时，顺序为 `project-spec`（user-invoked）→ `project-review`（经 `review-loop` + `generic-review`）→ `project-tickets`（user-invoked）→ `implement`（user-invoked）→ `code-review`（model-invoked）→ `project-review`（经 `review-loop` 拥有最终 verdict）→ `handoff`（user-invoked）。每步的输入/输出/handoff/停止见[英文版](../../workflows/recipes.md#1-software-feature)。

缺 acceptance authority、未批准 ticket、实现依赖或 independent evaluator 时 `BLOCKED`。证据含 SPEC、ticket 图、commit、focused tests、specialist findings、`project-review`/`review-loop` verdict 与 handoff；到 `PASS`/`FAIL`/`BLOCKED` 停止。

## 2. 新项目初始化

`ask-light`（user-invoked）收 goal/project type/task kind/artifacts/blockers/availability/invocation control，返回下一 Skill/recipe；用户批准后按调用策略处理（model-invoked 可开始；user-invoked 渲染为下一次显式调用）。随后 `project-init`（user-invoked）收确认 preset 与 root，写入最小指令并验证后停止。下一能力由用户选，最终验收归 `project-review`。

## 3. 文稿项目

顺序为 `manuscript-ops` → 按需 `socratic`（经 `clarify`/`decision-map`）→ `project-init` → `project-review init` → manuscript production → `project-review` manuscript Profile。这里 `socratic` 为引擎，不作为第二个用户步骤单独选择。Project route 选 discovery handoff 后必须停；仅用户显式 `resume` 才继续。缺 root/dependency/brief/Charter/渲染证据时 `BLOCKED`，最终 verdict 归 `project-review`。

## 4. 从资料提炼 Skill

`learn-anything`（user-invoked）输出内部 Method Contract/`not_promoted`/精确 `BLOCKED`；随后 deterministic builder 输出 `created`/`updated`/`no-op`/`duplicate`/`blocked`。`writing-for-agents` 仅作 authoring knowledge，非 runtime 依赖。完整包交 `project-review`（经 `review-loop`）至 verdict 后再进入 admission 与 collection sync。

## 5. Skill 维护与发布

顺序为 ownership/reuse gate → 有界实现 → 包测试与负向/mutation fixtures → 脚本变更时的 `code-review` → `project-review` verdict → collection sync、双语、fresh 安装、discovery、release/tag/closeout。ownership 模糊、测试失败、独立审查缺失、安装未验证或双语未同步均 `BLOCKED`。结构检查非 runtime proof。

## 6. Bug 与 final review

Bug 路径为 `diagnosing-bugs` → `implement` → `code-review` → `project-review`（经 `review-loop`）；final-review 为单步 `project-review`。两者在复现/authority 缺失或最终 verdict 时停止，不自动调用 user Skill。

## 7. 独立 session recap

`recap` 为单步、user-invoked 停止边界。用户显式 `$recap`，只消费当前 session，输出严格一行，不调其他能力。
