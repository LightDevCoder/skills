# v0.1.1 installation verification

[中文记录](INSTALLATION_VERIFICATION.zh-CN.md)

## Status

`NOT TESTED` until the tagged public release is reachable from a fresh
destination. The commands below are the release targets, not a claim that a
source-checkout scan already proved them.

| Field | Whole collection | Per-Skill |
| --- | --- | --- |
| Command | `npx skills add LightDevCoder/skills#v0.1.1` | `npx skills add LightDevCoder/skills#v0.1.1 --skill review-loop` |
| CLI version | `NOT TESTED` | `NOT TESTED` |
| Released commit | `NOT TESTED` | `NOT TESTED` |
| Fresh destination | `NOT TESTED` | `NOT TESTED` |
| Discovery without source checkout | `NOT TESTED` | `NOT TESTED` |
| Success/boundary/missing-dependency smoke | `NOT TESTED` | `NOT TESTED` |
| Repeat-install behavior | `NOT TESTED` | `NOT TESTED` |
| Limitation | Host-specific destination/discovery must be recorded after execution. | Same. |

## Procedure

1. Record `npx skills --version` and the exact command.
2. Use a disposable empty destination and make the source checkout
   unavailable to the host discovery step.
3. Run the whole and per-Skill commands separately.
4. Refresh the Agent host, capture discovery, then run one success and one
   boundary/missing-dependency smoke for the installed package.
5. Repeat the same command and record whether it is a no-op or reports a
   duplicate.

Do not include tokens, usernames, absolute private paths, or sensitive host
details in this public record.

## Historical v0.1.0 summary

This summary preserves the actual v0.1.0 installer evidence from the controller
T16 acceptance receipt. It is not a rerun and does not promote the current
v0.1.1 candidate.

| Field | Whole collection | Per-Skill |
| --- | --- | --- |
| CLI version | `1.5.20` | `1.5.20` |
| Host selection | `--agent codex` | `--agent codex` |
| Command | `npx skills add LightDevCoder/skills --yes --copy --agent codex` | `npx skills add LightDevCoder/skills --skill review-loop --yes --copy --agent codex` |
| Released commit | `fb36fc2dad39ee94ad4aa25a5fee3c87c54f05f2` | same |
| Fresh destination | disposable destination; absolute private path intentionally omitted | disposable destination; absolute private path intentionally omitted |
| Discovery / validator | exactly five admitted packages installed; every package passed the official validator | exactly `review-loop` installed and passed the official validator |
| Resource integrity | complete-package comparison: zero mismatches and zero extra files | complete package validator passed |
| Success smoke | `PASS` for the recorded install and validation | `PASS` for the recorded install and validation |
| Boundary / missing-dependency smoke | `NOT RECORDED` in the summarized historical receipt | `NOT RECORDED` in the summarized historical receipt |
| Repeat-install behavior | `NOT RECORDED` | `NOT RECORDED` |

The unqualified commands remain historical commands only. The official CLI
follows the repository default revision when no `#ref` is supplied; that does
not make the shorthand a permanent v0.1.0 pin.
