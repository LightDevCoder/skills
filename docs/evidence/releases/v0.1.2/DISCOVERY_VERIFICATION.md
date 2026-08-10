# v0.1.2 discovery verification

[中文记录](DISCOVERY_VERIFICATION.zh-CN.md)

## Status

`NOT TESTED — fill after the tagged artifact is installed into fresh
destinations and listed without a source checkout.`

The local collection test on this branch currently returns 951 assertions and
`COLLECTION_DISCOVERY=PASS`, which is structural/discovery evidence for the
admitted tree, not fresh host installation proof.

## Required observations

- Exactly seven first-party package names are present.
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
npx --yes skills add LightDevCoder/skills#v0.1.2 --yes --copy --agent '*'
npx --yes skills list
npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'
npx --yes skills list
npx --yes skills add LightDevCoder/skills#v0.1.2 --skill review-loop --yes --copy --agent '*'
npx --yes skills list
```

Observed result: `NOT TESTED — fill after the release tag is created`.

## Structural command

```text
powershell -File tests/collection-discovery-tests.ps1
```

Observed local result: `COLLECTION_DISCOVERY_ASSERTIONS=951`,
`COLLECTION_DISCOVERY=PASS`. This is structural/discovery evidence only.
