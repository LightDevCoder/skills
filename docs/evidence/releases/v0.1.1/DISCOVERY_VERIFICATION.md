# v0.1.1 discovery verification

[中文记录](DISCOVERY_VERIFICATION.zh-CN.md)

## Status

`STRUCTURAL PASS` — the local collection test returned 668 assertions and
`COLLECTION_DISCOVERY=PASS`. Fresh released-artifact discovery remains
`NOT TESTED` until the final release is inspected from a fresh destination.

## Required observations

- Exactly five first-party package names are present.
- Each package has `SKILL.md`, complete frontmatter, and
  `agents/openai.yaml` with interface and invocation policy.
- Referenced resources are present and the package is discoverable without the
  source checkout.
- `ask-light` next/workflow output retains source category, invocation type,
  availability gap, expected input/output, and stop condition.
- User-invoked packages are not silently model-invoked.
- `project-workflow` and `to-manuscript-spec` remain outside the admitted tree.

## Structural command

```text
powershell -File tests/collection-discovery-tests.ps1
```

Observed local result: `COLLECTION_DISCOVERY_ASSERTIONS=668`,
`COLLECTION_DISCOVERY=PASS`. This is structural/discovery evidence only.
