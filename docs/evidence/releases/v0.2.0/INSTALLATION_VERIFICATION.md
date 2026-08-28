# v0.2.0 installation verification

[中文记录](INSTALLATION_VERIFICATION.zh-CN.md)

## Status

`PASS` for the tagged public repository using Skills CLI `1.5.23`, verified against fresh isolated destinations for both the generic `latest` form and the pinned `#v0.2.0` form across the whole collection and all 33 individual Skills.

## Isolation and Name-Collision Policy

- Installation verification ran in isolated temporary project roots with isolated temporary `HOME`, `XDG_CONFIG_HOME`, and `XDG_DATA_HOME` environment variables.
- The developer's real home directory, global Skills directories, and active agent workspaces were never modified.
- No existing Matt Skills or external packages were overwritten.

## Verification Matrix Results

| Scope | Form | Command | CLI Version | Exit code | Installed count | Discovery (`skills list`) | Smoke / Integrity | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Whole Collection | `latest` | `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'` | `1.5.23` | `0` | 33 packages | `PASS` (all 33 listed) | Complete 33 packages installed | `PASS` |
| Whole Collection | `#v0.2.0` | `npx --yes skills add LightDevCoder/skills#v0.2.0 --yes --copy --agent '*'` | `1.5.23` | `0` | 33 packages | `PASS` (all 33 listed) | 100% byte-identical to tagged source | `PASS` |
| 33 Individual Skills | `latest` | `npx --yes skills add LightDevCoder/skills --skill <name> --yes --copy --agent '*'` | `1.5.23` | `0` (33/33) | 1 package each | `PASS` | Exact requested package installed | `PASS` |
| 33 Individual Skills | `#v0.2.0` | `npx --yes skills add LightDevCoder/skills#v0.2.0 --skill <name> --yes --copy --agent '*'` | `1.5.23` | `0` (33/33) | 1 package each | `PASS` | Exact requested package installed | `PASS` |

## Repeat Install Behavior

- Re-running the pinned whole collection install against an already-installed destination completed with exit code `0` (clean no-op overwrite).

## Limitations

- The CLI copies under `.agents/skills/` are structural installations verified via CLI discovery (`skills list`). Live host refresh and model invocation remain host-specific.
