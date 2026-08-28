# v0.2.0 installation verification

[中文记录](INSTALLATION_VERIFICATION.zh-CN.md)

## Status

`NOT TESTED` — Candidate commit prepared. Fresh installation verification against the published tag and generic latest in disposable isolated environments will occur in Phase 3 following explicit publication approval.

## Isolation and Name-Collision Policy

- Installation verification runs in fresh, temporary directories with isolated temporary `HOME`, `XDG_CONFIG_HOME`, and `XDG_DATA_HOME` environments.
- Real user home, global Skills directories, and active agent workspaces are never modified.
- No existing Matt Skills or external packages are overwritten.

## Planned Verification Matrix

| Scope | Generic `latest` command | Pinned `#v0.2.0` command | Status |
| --- | --- | --- | --- |
| Whole Collection (33 packages) | `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'` | `npx --yes skills add LightDevCoder/skills#v0.2.0 --yes --copy --agent '*'` | `NOT TESTED` |
| Individual Skills Matrix (33 skills) | `npx --yes skills add LightDevCoder/skills --skill <name> --yes --copy --agent '*'` | `npx --yes skills add LightDevCoder/skills#v0.2.0 --skill <name> --yes --copy --agent '*'` | `NOT TESTED` |

## Results Record (To be populated in Phase 3)

| Target | Form | Exit code | Installed count | Discovery (`skills list`) | Smoke / Integrity | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Whole Collection | latest | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| Whole Collection | #v0.2.0 | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| 33 Individual Skills | latest | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| 33 Individual Skills | #v0.2.0 | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |

## Limitations

- To be recorded after fresh-install matrix execution.
