# v0.1.4 installation verification

[中文记录](INSTALLATION_VERIFICATION.zh-CN.md)

## Status

`PASS` for the tagged public repository using Skills CLI `1.5.22`, verified
against fresh destinations for both the generic `latest` form and the pinned
`#v0.1.4` form. Host refresh is host-specific and was not claimed; CLI
discovery was run from each fresh destination without a source checkout.

| Field | Whole collection | Per-Skill (`light-kanban-worker`) |
| --- | --- | --- |
| Command | `npx skills add LightDevCoder/skills --yes --copy --agent '*'` (latest) and `npx skills add LightDevCoder/skills#v0.1.4 --yes --copy --agent '*'` (tag) | `npx skills add LightDevCoder/skills --skill light-kanban-worker --yes --copy --agent '*'` (latest) and `npx skills add LightDevCoder/skills#v0.1.4 --skill light-kanban-worker --yes --copy --agent '*'` (tag) |
| CLI version | `1.5.22` | `1.5.22` |
| Released commit | `a9cc8aa029c926fc80f6ddc0022793f79dfd85bd` (`v0.1.4` tag) | same |
| Fresh destination | New empty temporary directory; exactly 8 packages under `.agents/skills/` (`Found 8 skills`, `Installing all 8 skills`) | New empty temporary directory; exactly 1 package (`light-kanban-worker`) under `.agents/skills/` |
| Install result | `PASS`, exit code 0 | `PASS`, exit code 0 |
| Discovery without source checkout | `npx --yes skills list` exit 0; `light-kanban-worker ./.agents/skills/light-kanban-worker` listed; source checkout absent | `npx --yes skills list` exit 0; exactly one package listed: `light-kanban-worker`; source checkout absent |
| Installed-package smoke | — | All 10 package files SHA-256 byte-identical to the tagged source; contract and behavior suites OK against the installed copy (collection test harness on `PYTHONPATH`) |
| Repeat-install behavior | Same command exit 0; CLI reported `overwrites:` for the agent groups (no-op overwrite) | Same command exit 0; no-op overwrite |
| Limitation | The CLI's own per-host copies under `agent/skills/` strip the `name` frontmatter field, so `skills list` prints a uniform "missing required frontmatter field(s): name" warning for every package (including the long-released ones). This is CLI copy behavior, not a package defect; the `.agents/skills/` installs are byte-identical to the tag. Host refresh and model-mediated runtime invocation were not claimed. | Same. |

## Procedure

1. Record `npx skills --version` and the exact command.
2. Use a disposable empty destination and make the source checkout
   unavailable to the host discovery step.
3. Run the whole and per-Skill commands separately for both the generic
   `latest` form and the pinned `#v0.1.4` form.
4. Capture discovery, then run the installed-package smoke for
   `light-kanban-worker`.
5. Repeat the same command and record whether it is a no-op or reports a
   duplicate.

The evidence records destination classes rather than absolute private paths.
It does not include tokens, usernames, or sensitive host details.
