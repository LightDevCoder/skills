# Installation and Fresh-Install Verification

[中文安装说明](INSTALLATION.zh-CN.md)

The public first-party collection's current stable release is
[v0.1.0](https://github.com/LightDevCoder/skills/releases/tag/v0.1.0). The
working tree also prepares v0.1.1 as a release candidate; its tag and
fresh-install proof are still release-gate evidence. Until those are recorded,
the v0.1.1 commands below are targets rather than verified installation claims.
Package contracts remain inside `skills/<name>/`; this document is the
installation authority and does not replace host-specific discovery rules.

## Revision semantics

The official Skills CLI accepts a `#ref` fragment in a GitHub source. The
fragment is passed as the Git revision; a source without a fragment uses the
repository's default revision. Therefore an unqualified shorthand is not a
permanent release pin. The parser and clone behavior are documented in the
[official Skills CLI source parser](https://raw.githubusercontent.com/vercel-labs/skills/main/src/source-parser.ts)
and [Git helper](https://raw.githubusercontent.com/vercel-labs/skills/main/src/git.ts).

## Historical v0.1.0 verification

The current stable release is the published v0.1.0 snapshot at commit
`fb36fc2dad39ee94ad4aa25a5fee3c87c54f05f2`. The following unqualified
commands are retained as historical commands from that published release. The
summarized CLI, host, destination, validator, and known evidence limits are
recorded in the [historical installation record](evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.md#historical-v0.1.0-summary):

```text
npx skills add LightDevCoder/skills
npx skills add LightDevCoder/skills --skill review-loop
```

That historical record is a summary, not a current rerun; it explicitly marks
boundary/missing-dependency smoke and repeat-install behavior when the original
receipt did not record them.

That historical verification does not change the CLI revision semantics: an
unqualified source follows the repository's default revision and is not a
permanent v0.1.0 pin. The v0.1.1 candidate commands below use an explicit tag.

The target release commands are:

```text
npx skills add LightDevCoder/skills#v0.1.1
npx skills add LightDevCoder/skills#v0.1.1 --skill review-loop
```

After the release gate passes, the first installs the five-package collection
and the second selects one complete package at the same tag. Always record the actual CLI version, host,
destination, discovery result, and smoke result; see the
[v0.1.1 installation record](evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.md).

## Supported installation scopes

| Scope | Destination policy | Required evidence |
| --- | --- | --- |
| Project-local | The active repository's recognized project-level Skills location. | Exact host/path, complete package copy or installer result, refresh step, and discovery without the source checkout. |
| User/global | The Agent host's recognized user-level or global Skills location. | Exact host/path, complete package copy or installer result, refresh step, and discovery without the source checkout. |
| Per-Skill | One complete admitted directory containing `SKILL.md`, metadata, and every referenced resource. | Selected package, pinned revision, destination, discovery, and behavioral smoke evidence. |

These categories do not imply that every Agent host supports every location.
The host's own documentation and the fresh discovery result control.

## Manual fallback

When the installer is unavailable or unsupported, check out the target tag
after it is published and copy the complete package into the host-recognized
root:

```powershell
$sourceRoot = "<v0.1.1-release-checkout>"
$skillName = "<admitted-skill-name>"
$destinationRoot = "<host-recognized-skills-root>"
Copy-Item -LiteralPath "$sourceRoot/skills/$skillName" -Destination "$destinationRoot/$skillName" -Recurse
```

This is a fallback procedure, not fresh-install proof by itself. The record
must identify the released commit or tag, exact host, resolved destination,
refresh/restart step, discovery result, and success, boundary, invocation, and
missing-dependency smoke results. Copy the complete package; never copy only
`SKILL.md` when the package references resources.

## Direct upstream and third-party packages

Unmodified Matt Pocock Skills stay on their original upstream path:
[mattpocock/skills](https://github.com/mattpocock/skills). Modified third-party
variants belong in the private
[skills-3rdParty](https://github.com/LightDevCoder/skills-3rdParty) repository;
they are not included in this public collection and have their own pinned
manifest and release evidence.

## Verification record

For every future verified release or per-Skill command, preserve:

- exact command and installer version;
- repository URL and released commit or tag;
- host, installation scope, and resolved destination;
- fresh-environment discovery without the source checkout;
- success, boundary, invocation, and missing-dependency smoke results;
- any manual fallback used; and
- known limitations.

Structural validation, a source-checkout scan, and an unexecuted command are
not installation evidence. The collection discovery script is a structural
cross-reference check; it does not replace fresh host installation.
