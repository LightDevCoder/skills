# Ask Light 显式选择下一步

[英文版示例](../../workflows/first-party-composition.md)

## 场景

Agent 已有 goal、artifacts、blockers、project type、task kind、availability 和 invocation control，但下一步不清楚。用户显式调用 `ask-light` 检查当前环境并得到一个下一 Skill 建议。

## 组合边界

```text
用户目标和当前 artifacts
          |
          v
    $ask-light
          |
          v
检查项目阶段 → 一个建议 + 理由
          |
          v
用户批准（yes / 可以 / go ahead）
          |
          v
校验并遵循调用策略
          |
          +--> model-invoked：在受支持的 host 开始
          |
          `--> user-invoked：缺少直接通道时渲染精确调用 / host-transition-required
```

可能选择 `project-init`、`project-clarify`、`clarify`、`decision-map`、`research`、`prototype`、`project-spec`、`project-tickets`、`implement`、`diagnosing-bugs`、`project-review`、`review-loop`、`learn-anything`、`recap`、`manuscript-ops` 或 `release-workflow`。其中 `recap` 仅在用户显式需要当前 session 一行摘要时适用。`ask-light` 在用户批准前停止且不执行、安装、delegate、创建 workflow state 或静默串联 user-invoked Skill；用户以 `yes`/`可以`/`go ahead` 批准后，对 model-invoked 被接受 Skill 可在 host 支持时开始；对 user-invoked 被接受 Skill，在有验证过的 host 证据时可直接进入，否则渲染精确调用并请用户启动。选中 Skill 保留自己的契约与证据边界。

## Evidence 与状态

- 33 个包的 `SKILL.md`（见 [CATALOG.zh-CN.md](../../../CATALOG.zh-CN.md)）。
- [ask-light discovery contract](../../../skills/ask-light/references/discovery-contract.md)。
- [collection discovery 测试](../../../tests/test_collection_discovery.py) 与 [composition](../../../tests/test_composition.py)。
- `docs/evidence/` 下的 release 与 admission 证据。

这是验证资产，不是 canonical workflow 或准入要求。
