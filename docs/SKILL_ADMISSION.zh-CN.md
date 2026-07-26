# 第一方 Skill 准入契约

[English admission contract](SKILL_ADMISSION.md)

本契约适用于新包进入 `skills/` 前，以及改变行为、invocation boundary、dependency、resource 或 ownership claim 的变更。

## Reuse-before-invention 与 ownership gate

优先顺序是：直接使用 upstream；在边界配置/适配；增加 local Profile 或 internal Layer；必要时 wrapper；必要的本地修改放入 `skills-3rdParty`；只有确实缺少能力时才创建新的第一方 Skill。目录美观、便利或想要本地副本不是 fork/admit 的理由。

第一方候选必须是 collection owner 编写的，或已实质变换为独立 owned capability，并有 `ATTRIBUTION.md` 记录原仓库、路径、pinned revision/tag、license/notice 和具体变换。未修改的 upstream/third-party copy 必须拒绝，修改版仍主要是第三方能力时进入 `skills-3rdParty`。

## Admission questions

审查必须确认：independent value、明确 triggers、bounded responsibility、user/model invocation type、动态组合安全、依赖和 host 假设可用、包及其 scripts/templates/assets 完整且没有 placeholder-only 目录。进入某个 canonical workflow 不是准入条件。

## 必需 evidence

| Evidence | 必须展示 | 不证明 |
| --- | --- | --- |
| Structural | 包树、metadata、内部链接和资源通过结构工具。 | runtime、fresh install 或 host discovery。 |
| Installation/discovery | fresh environment 安装并脱离 source checkout 发现。 | 除 discovery 外的行为。 |
| Behavioral | success、boundary、failure 或 missing-dependency 场景。 | 没有 independent review 的 acceptance。 |
| Invocation | 调用类型一致，且 user-invoked 不会自动调用另一个 user-invoked。 | 未覆盖的广泛行为。 |
| Review | `review-loop agent-skill` 使用 Producer evidence 和 fresh Evaluator。 | 扩大冻结 scope 的权限。 |
| Attribution | owner/source/revision/notice/license/transformation 可检查。 | 把未修改 copy 变成第一方。 |
| Executable scripts | focused、negative、adversarial/mutation tests 和 `code-review`。 | 一个静态 validator 覆盖全部行为。 |

所有 static、inferred、simulated、keyword-only 检查必须标注真实 evidence class，不能写成 runtime proof。只有通过 ownership、准入问题、证据、`review-loop agent-skill` `PASS` 和维护文档同步，包才可进入第一方集合；`FAIL`/`BLOCKED` 必须留在集合外并写明缺口。
