# v0.1.5 discovery verification

[中文记录](DISCOVERY_VERIFICATION.zh-CN.md)

## Status

`PASS` — discovery verified against the published `v0.1.5` tag: `npx skills
add LightDevCoder/skills#v0.1.5 --skill light-kanban-worker --yes --copy
--agent '*'` into a fresh destination, then `npx --yes skills list` from
that destination (no source checkout anywhere on the path).

| Field | Value |
| --- | --- |
| Command | `npx skills add LightDevCoder/skills#v0.1.5 --skill light-kanban-worker --yes --copy --agent '*'` |
| Installer version | `1.5.22` |
| Host / destination | disposable empty temporary directory |
| Discovery result (`npx --yes skills list`) | exit 0; `light-kanban-worker ./.agents/skills/light-kanban-worker` listed with `Agents: …` and `Source: LightDevCoder/skills` |
| Package completeness | 14 files: SKILL.md, agents/openai.yaml, references/api.md, tests/ (2 suites + helpers + 8 fixtures) — byte-identical to the tag checkout |
| Metadata | frontmatter `name: light-kanban-worker`; display_name / short_description / `allow_implicit_invocation: true` present |
| Contract tests on the installed copy | PASS — 100 assertions, run standalone from the installed package |
| Behavior tests on the installed copy | PASS — 23 assertions, run standalone from the installed package |

Known CLI display quirk (not a package defect): the CLI's own per-host
copies under `agent/skills/` omit the `name` frontmatter field, so
`skills list` prints a uniform "missing required frontmatter field(s):
name" warning for every package; the `.agents/skills/` copies are
byte-identical to the tag.
