# v0.1.6 installation verification

[中文记录](INSTALLATION_VERIFICATION.zh-CN.md)

## Status

`PASS` for the tagged public repository using Skills CLI `1.5.23`, verified against
fresh destinations for both the generic `latest` form and the pinned
`#v0.1.6` form. Host refresh is host-specific and was not claimed; CLI
discovery was run from each fresh destination without a source checkout.

| Field | Whole collection | Per-Skill (`kb-init`) |
| --- | --- | --- |
| Command | `npx skills add LightDevCoder/skills --yes --copy --agent '*'` (latest) and `npx skills add LightDevCoder/skills#v0.1.6 --yes --copy --agent '*'` (tag) | `npx skills add LightDevCoder/skills --skill kb-init --yes --copy --agent '*'` (latest) and `npx skills add LightDevCoder/skills#v0.1.6 --skill kb-init --yes --copy --agent '*'` (tag) |
| CLI version | `1.5.23` | `1.5.23` |
| Released commit | `41b6e7169a1c68bb017f9ff6c464b220185b02ff` (`v0.1.6` tag) | same |
| Fresh destination | New empty temporary directory; found/installed 9 skills | New empty temporary directory; exactly 1 package (`kb-init`) |
| Install result | PASS | PASS |
| Discovery without source checkout | `npx --yes skills list` exit 0; `kb-init` listed; source checkout absent | `npx --yes skills list` exit 0; exactly `kb-init` listed; source checkout absent |
| Installed-package smoke | — | Installed `kb-init` files byte-identical to the tagged source and contract test OK |
| Repeat-install behavior | Same command exit 0; no-op overwrite | Same command exit 0; no-op overwrite |

## Limitations

- The CLI's per-agent copies under `agent/skills/` strip the `name` frontmatter
  field, so `skills list` prints a "missing required frontmatter field(s):
  name" warning for every copied package. This is CLI copy behavior, not a
  package defect; the `.agents/skills/` installs are byte-identical to the tag
  (`diff -r` clean against the tagged source) and their contract test passes
  when run with the shared test harness on `PYTHONPATH`.
- Only the installation scope recorded here was exercised; host refresh and
  model-runtime invocation are not claimed.
