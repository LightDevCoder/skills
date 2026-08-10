# v0.1.2 installation verification

[中文记录](INSTALLATION_VERIFICATION.zh-CN.md)

## Status

`NOT TESTED — run against the published v0.1.2 tag and the generic `latest`
command after the GitHub release exists.`

This page will record the exact CLI version, fresh destinations, discovery
results, and success, boundary, invocation, and missing-dependency smoke for
the v0.1.2 tag and for the published generic `latest` install command.

| Field | Whole collection | Per-Skill |
| --- | --- | --- |
| Command | `npx skills add LightDevCoder/skills --yes --copy --agent '*'` (latest) and `npx skills add LightDevCoder/skills#v0.1.2 --yes --copy --agent '*'` (tag) | `npx skills add LightDevCoder/skills --skill review-loop --yes --copy --agent '*'` (latest) and `npx skills add LightDevCoder/skills#v0.1.2 --skill review-loop --yes --copy --agent '*'` (tag) |
| CLI version | `NOT TESTED` | `NOT TESTED` |
| Released commit | `NOT TESTED — fill after the release tag is created` | same |
| Fresh destination | New empty temporary project | New empty temporary project |
| Install result | `NOT TESTED` | `NOT TESTED` |
| Discovery without source checkout | `NOT TESTED` | `NOT TESTED` |
| Success/boundary/missing-dependency smoke | `NOT TESTED` | `NOT TESTED` |
| Repeat-install behavior | `NOT TESTED` | `NOT TESTED` |

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
