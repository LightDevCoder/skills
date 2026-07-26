# v0.1.1 discovery verification

[中文记录](DISCOVERY_VERIFICATION.zh-CN.md)

## Status

`PASS` — the local collection test returned 683 assertions and
`COLLECTION_DISCOVERY=PASS`; the tagged artifact was installed into fresh
destinations and listed successfully without a source checkout.

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

## Fresh artifact command

```text
npx --yes skills add LightDevCoder/skills#v0.1.1 --yes --copy --agent codex
npx --yes skills list
npx --yes skills add LightDevCoder/skills#v0.1.1 --skill review-loop --yes --copy --agent codex
npx --yes skills list
```

Observed: the whole-collection destination listed exactly 5 packages and the
single-Skill destination listed exactly `review-loop`; both destinations had no
`skills/` source checkout. Installed `review-loop` contract tests passed, and
the installed whole collection's `ask-light` behavior suite returned 52
assertions/PASS.

## Structural command

```text
powershell -File tests/collection-discovery-tests.ps1
```

Observed local result: `COLLECTION_DISCOVERY_ASSERTIONS=683`,
`COLLECTION_DISCOVERY=PASS`. This is structural/discovery evidence only.
