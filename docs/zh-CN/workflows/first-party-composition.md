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
一个建议 + host 适用的 invocation
          |
          v
用户显式选择下一 Skill
```

可能选择 `project-init`、`project-clarify`、`clarify`、`decision-map`、`research`、`prototype`、`project-spec`、`project-tickets`、`implement`、`diagnosing-bugs`、`project-review`、`review-loop`、`learn-anything`、`recap`、`manuscript-ops` 或 `release-workflow`。其中 `recap` 仅在用户显式需要当前 session 一行摘要时适用。`ask-light` 在建议后停止，不执行、安装、delegate、创建 workflow state 或静默串联 user-invoked Skill；选中 Skill 保留自己的契约与证据边界。

## Evidence 与状态

- 33 个包的 `SKILL.md`（见 [CATALOG.zh-CN.md](../../../CATALOG.zh-CN.md)）。
- [ask-light discovery contract](../../../skills/ask-light/references/discovery-contract.md)。
- [collection discovery 测试](../../../tests/test_collection_discovery.py) 与 [composition](../../../tests/test_composition.py)。
- `docs/evidence/` 下的 release 与 admission 证据。

这是验证资产，不是 canonical workflow 或准入要求。
