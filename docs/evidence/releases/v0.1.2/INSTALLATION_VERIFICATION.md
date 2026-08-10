# v0.1.2 installation verification

[中文记录](INSTALLATION_VERIFICATION.zh-CN.md)

## Status

`PASS` for the tagged public repository using Skills CLI `1.5.22`, verified
against fresh destinations for both the generic `latest` form and the pinned
`#v0.1.2` form. Host refresh is host-specific and was not claimed; CLI
discovery was run from each fresh destination without a source checkout.

| Field | Whole collection | Per-Skill |
| --- | --- | --- |
| Command | `npx skills add LightDevCoder/skills --yes --copy --agent '*'` (latest) and `npx skills add LightDevCoder/skills#v0.1.2 --yes --copy --agent '*'` (tag) | `npx skills add LightDevCoder/skills --skill review-loop --yes --copy --agent '*'` (latest) and `npx skills add LightDevCoder/skills#v0.1.2 --skill review-loop --yes --copy --agent '*'` (tag) |
| CLI version | `1.5.22` | `1.5.22` |
| Released commit | `8de5ec1a453b0e93f71dcda160e17ea7b42c3997` (`v0.1.2` tag) | same |
| Fresh destination | New empty temporary project; exactly 7 packages under `.agents/skills/` | New empty temporary project; exactly 1 package under `.agents/skills/` |
| Install result | `PASS`, exit code 0 for both the `latest` and `#v0.1.2` forms | `PASS`, exit code 0 for both the `latest` and `#v0.1.2` forms |
| Discovery without source checkout | `npx --yes skills list` exit 0; 7 packages listed; source checkout absent | `npx --yes skills list` exit 0; 1 package listed; source checkout absent |
| Success/boundary/missing-dependency smoke | Installed `recap` output contract: 8 assertions/PASS; installed recap package byte-identical to source | Installed `review-loop` package byte-identical to source with `SKILL.md`, `agents/`, `references/`, and `tests/` present |
| Repeat-install behavior | Same command exit 0; CLI reported `overwrites:` for the agent groups (no-op overwrite) | Same command exit 0; CLI reported `overwrites:` for the agent groups (no-op overwrite) |
| Limitation | Host refresh and model-mediated runtime invocation were not tested. Transient GitHub TLS failures during verification required retries; the recorded result is from a successful run. | Same. |

## Procedure

1. Record `npx skills --version` and the exact command.
2. Use a disposable empty destination and make the source checkout
   unavailable to the host discovery step.
3. Run the whole and per-Skill commands separately for both the generic
   `latest` form and the pinned `#v0.1.2` form.
4. Refresh the Agent host, capture discovery, then run one success and one
   boundary/missing-dependency smoke for the installed package.
5. Repeat the same command and record whether it is a no-op or reports a
   duplicate.

The evidence records destination classes rather than absolute private paths. It
does not include tokens, usernames, or sensitive host details.

## Historical v0.1.1 summary

The verified v0.1.1 installation record remains authoritative for the
five-package release:
[v0.1.1 INSTALLATION_VERIFICATION](../v0.1.1/INSTALLATION_VERIFICATION.md).
That record includes the historical v0.1.0 summary and preserves the CLI
revision semantics: an unqualified source follows the repository's default
revision, and the v0.1.1 tag pinned `c50f1ef`.
