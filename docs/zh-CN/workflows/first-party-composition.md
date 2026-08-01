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

可能选择 `project-init`、`learn-anything`、`recap`、`manuscript-ops` 或 `review-loop`。其中 `recap` 只有在用户显式需要当前 session 的一行摘要时才适用。`ask-light` 在建议后停止，不执行、安装、delegate、创建 workflow state 或静默串联 user-invoked Skill；选中的 Skill 保留自己的 contract 和 evidence boundary。

## Evidence 与状态

- 六个包的 `SKILL.md`。
- [ask-light discovery contract](../../../skills/ask-light/references/discovery-contract.md)。
- [collection discovery test](../../../tests/collection-discovery-tests.ps1)。
- [v0.1.1 发布证据](../../evidence/releases/v0.1.1/RELEASE_RECEIPT.zh-CN.md)。
- [recap 准入证据](../../evidence/admissions/recap/README.zh-CN.md)。

这是验证资产，不是 canonical workflow 或准入要求。
