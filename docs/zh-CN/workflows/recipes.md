# Workflow Recipes

[English recipes](../../workflows/recipes.md)

这些 recipe 是有边界的文档和验证资产，只描述显式 handoff；不会创建 canonical pipeline、永久 state machine 或自动多 Skill orchestrator。每个包的 `SKILL.md` 仍是行为权威。

## 来源与共同规则

- **First-party：** 本仓库的 `review-loop`、`project-init`、`ask-light`、`learn-anything`、`manuscript-ops`。
- **Matt upstream：** `mattpocock/skills` 中的 `to-spec`、`to-tickets`、`implement`、`code-review`、`handoff`、`diagnosing-bugs`、`grill-me`、`wayfinder`、`writing-great-skills`，或可见的 pinned third-party package。
- **Private modified third-party：** `skills-3rdParty` 内的包；私有 root 不可见时必须报告 availability gap，不能编造 fallback。

每行都写明 handoff artifact 和 stop condition。`user-invoked` 必须由用户显式选择；`model-invoked` 仍受包自身 policy 约束。specialist findings 不能成为最终 verdict；需要验收时由 `review-loop` 拥有 `PASS`、`FAIL`、`BLOCKED`。

## 1. 软件项目

**Entry condition：** 软件 feature/implementation 的目标、约束和验收方向已经明确。

顺序为 `to-spec`（Matt upstream，user-invoked）→ `review-loop` specification（first-party，model-invoked）→ `to-tickets`（Matt upstream，user-invoked）→ `implement`（Matt upstream，user-invoked）→ `code-review`（Matt upstream，model-invoked，只提供 specialist findings）→ `review-loop` software（first-party，拥有最终 verdict）→ `handoff`（Matt upstream，user-invoked）。每一步的输入、输出、handoff 和 stop condition 见 [English recipe](../../workflows/recipes.md#1-software-feature)。

缺少 acceptance authority、上游 Skill、批准 ticket、实现依赖或 independent evaluator 时 `BLOCKED`。证据包括 spec、ticket graph、commit、focused tests、specialist findings、review-loop state/verdict 和 handoff；到 `PASS`/`FAIL`/`BLOCKED` 停止。

## 2. 新项目初始化

`ask-light`（first-party，user-invoked）接收 goal、project type、task kind、artifacts、blockers、availability、invocation control，返回下一 Skill/recipe；停止等待用户选择。随后 `project-init`（first-party，user-invoked）接收确认 preset 和 root，写入最小指令并验证；初始化后停止，不等于 discovery/specification/implementation/final review。下一能力由用户选择，最终验收若需要则归 `review-loop`。

## 3. 文稿项目

顺序为 `manuscript-ops` → 按需选择 `grill-me`/`wayfinder` → `project-init` → `review-loop init` → manuscript production → `review-loop` manuscript Profile。Project route 选择 discovery handoff 后必须停；只有用户显式 `resume` 才能继续。root、dependency、brief、Charter、render/round-trip evidence 缺失时 `BLOCKED`，最终 verdict 归 `review-loop`。

## 4. 从资料提炼 Skill

`learn-anything`（first-party，user-invoked）输出内部 Method Contract、`not_promoted` 或精确 `BLOCKED`；随后 deterministic package builder 输出 `created`/`updated`/`no-op`/`duplicate`/`blocked`。`writing-great-skills` 只能作为可选 authoring knowledge，不是 runtime dependency。完整包交给 `review-loop agent-skill`，到 verdict 后再进入 admission 和 collection sync。

## 5. Skill 维护与发布

顺序为 ownership/reuse gate → bounded implementation → package tests 与 negative/mutation fixtures → script 变更时的 `code-review` → `review-loop agent-skill` → collection sync、双语 docs、fresh whole/per-Skill install、discovery、release/tag/closeout。ownership ambiguity、测试失败、独立审查缺失、安装未验证、私有依赖不可见或 release 凭据失败都应 `BLOCKED`。结构检查不是 runtime proof，source checkout scan 不是 fresh-install proof。

## 6. Bug 与 final review

Bug recipe 为 `diagnosing-bugs` → `implement` → `code-review` → `review-loop`；final-review recipe 只有一个 `review-loop` step。两者都在 reproduction/authority 缺失或最终 verdict 时停止，不自动调用 user Skill。
