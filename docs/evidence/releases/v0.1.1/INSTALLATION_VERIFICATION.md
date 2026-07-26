# v0.1.1 installation verification

[中文记录](INSTALLATION_VERIFICATION.zh-CN.md)

## Status

`PASS` for the tagged public repository using Skills CLI `1.5.20`. Host refresh
is host-specific and was not claimed; CLI discovery was run from each fresh
destination without a source checkout.

| Field | Whole collection | Per-Skill |
| --- | --- | --- |
| Command | `npx skills add LightDevCoder/skills#v0.1.1 --yes --copy --agent codex` | `npx skills add LightDevCoder/skills#v0.1.1 --skill review-loop --yes --copy --agent codex` |
| CLI version | `1.5.20` | `1.5.20` |
| Released commit | `c50f1ef403a5f0bfe02e75d1aeff2c237556db63` | same |
| Fresh destination | New empty temporary project; exactly 5 packages under `.agents/skills/` | New empty temporary project; exactly 1 package under `.agents/skills/` |
| Install result | `PASS`, exit code 0 | `PASS`, exit code 0 |
| Discovery without source checkout | `npx --yes skills list` exit 0; 5 packages listed; source checkout absent | `npx --yes skills list` exit 0; 1 package listed; source checkout absent |
| Success/boundary/missing-dependency smoke | Installed `ask-light` behavior suite: 52 assertions/PASS; installed `manuscript-ops` CLI help/PASS | Installed `review-loop` generic profile contract: `PASS`; package resources present |
| Repeat-install behavior | Same command exit 0; CLI reported `overwrites: Codex` for all 5 packages | Not repeated separately; whole-collection repeat covered the installer path |
| Limitation | Host refresh and model-mediated runtime invocation were not tested. | Same. |

## Procedure

1. Record `npx skills --version` and the exact command.
2. Use a disposable empty destination and make the source checkout
   unavailable to the host discovery step.
3. Run the whole and per-Skill commands separately.
4. Refresh the Agent host, capture discovery, then run one success and one
   boundary/missing-dependency smoke for the installed package.
5. Repeat the same command and record whether it is a no-op or reports a
   duplicate.

The evidence records destination classes rather than absolute private paths. It
does not include tokens, usernames, or sensitive host details.

## Historical v0.1.0 summary

This summary preserves the actual v0.1.0 installer evidence from the controller
T16 acceptance receipt. It is not a rerun and does not promote the current
v0.1.1 release.

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
