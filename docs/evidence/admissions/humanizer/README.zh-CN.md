# `humanizer` 准入证据

[English record](README.md)

## 范围与状态

- 包：`skills/humanizer/`
- 来源：ADAPT —— 经实质性转换的第一方能力，基于 blader/humanizer
  `e2e92e7b4b8229253ed5c8e81dc65463fdeddda5`（版本 2.11.2），外加一层薄的
  中文适配；见 [ATTRIBUTION.md](../../../../skills/humanizer/ATTRIBUTION.md)
- 调用类型：Model-invoked（`allow_implicit_invocation: true`）
- 准入路径：full path —— `review-loop` `agent-skill` Profile（因包内携带
  上游内容，prompt-only 快速通道不可用）；最终结论由 `project-review` 持有
- 准入状态：`PASS`（第 1 轮；一个 minor finding 已在范围内修复）
- 发布边界：记录在 `v0.2.0` 发布线上；pinned per-Skill 安装命令需待集合
  tag 重新发布并完成 fresh released-repository 验证后方可转正

## 证据摘要

| 领域 | 结果 | 证据边界 |
| --- | --- | --- |
| 归属 | PASS | `ATTRIBUTION.md` 记录两个上游来源、pinned 修订、两份 MIT 声明与编号转换摘要；独立评审确认 pinned 修订与上游检出一致。 |
| 结构 | PASS | 脚本化逐字校验：`SKILL.md` 正文（去除集合 frontmatter 与新增 Language routing 节后）与 pinned 上游修订逐字节一致；仅四个文件；链接可解析；无占位内容；无已退役引用。 |
| 新鲜复制安装 | PASS | 完整包隔离复制：文件集一致、SHA-256 全部匹配、仅对副本做发现扫描全部通过（name、description、model-invoked 元数据、可解析 zh 引用、归属记录）。属于本地源准入证据，不是已发布安装命令的证明。 |
| 行为 | PASS | 四个 producer fixture（英文 AI 腔成功；干净人写文本边界保持不变；中文 AI 腔成功且中文引号保持原样；编造压力下拒绝）外加一个独立自编中文 fixture——每次改写都保留全部事实、未编造任何细节、正确应用中文覆盖规则。 |
| 调用 | PASS | 声明为 model-invoked；`SKILL.md` frontmatter 与 `agents/openai.yaml` policy 一致（由集合契约测试重新断言）。 |
| 集合质量 | PASS | 注册后重跑仓库全套测试；见 `v0.2.0` 行的 changelog 条目。 |

## 评审记录

- Charter: [review-loop/charter.md](review-loop/charter.md)
- State: [review-loop/state.md](review-loop/state.md)
- Producer 证据：[review-loop/rounds/round-01/producer-evidence.md](review-loop/rounds/round-01/producer-evidence.md)
- Findings: [review-loop/findings.md](review-loop/findings.md) —— 一个
  minor（HUM-01，归属措辞），处置见
  [review-loop/rounds/round-01/finding-disposition.md](review-loop/rounds/round-01/finding-disposition.md)
- 独立评估结论：
  [review-loop/rounds/round-01/evaluator-verdict.md](review-loop/rounds/round-01/evaluator-verdict.md)
- 最终结论（project-review）：[review-loop/verdict.md](review-loop/verdict.md)

## 源 skill 退役

本包安装时，两个源 skill 已从本地主机退役：blader/humanizer git 克隆
（此前经符号链接接入 `~/.agents/skills/` 与 `~/.claude/skills/`）以及全部
三份 `humanizer-zh` 副本（此前安装自 `LightDevCoder/skills-3rdParty`
v0.2.1，其 `UPSTREAM.md`/`PATCHES.md` 来源记录载明零行为补丁）。集合不依赖
其中任何一个；两个上游仓库仍是其未修改英文/中文形态的推荐直接安装来源。
