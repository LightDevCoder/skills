# Installation and Fresh-Install Verification

This repository contains the stable v0.1.0 five-Skill release at
[LightDevCoder/skills](https://github.com/LightDevCoder/skills/releases/tag/v0.1.0).
The commands below were verified against the published repository from a
fresh destination and are the release installation authority.

## Supported installation scopes

| Scope | Destination policy | Required evidence |
| --- | --- | --- |
| Project-local | The active repository's recognized project-level Skills location. | Exact host/path, complete package copy or installer result, refresh step, and discovery without the source checkout. |
| User/global | The Agent host's recognized user-level or global Skills location. | Exact host/path, complete package copy or installer result, refresh step, and discovery without the source checkout. |
| Per-Skill | One complete admitted directory containing SKILL.md and every referenced resource. | Selected package, immutable released revision, destination, discovery, and behavioral smoke evidence. |

These categories do not imply that every Agent host supports every location.
The host's own documentation and fresh discovery result control.

## Verified v0.1.0 installer commands

Install the whole first-party collection:

~~~
npx skills add LightDevCoder/skills
~~~

Install one admitted Skill:

~~~
npx skills add LightDevCoder/skills --skill review-loop
~~~

The commands target the immutable v0.1.0 release. The exact installer version,
host, destination, refresh step, and discovery result are preserved in the
T16 release receipt.

## Manual fallback

When the installer is unavailable or unsupported, use the complete v0.1.0
package snapshot and follow the host's recognized Skills location:

~~~
$sourceRoot="<v0.1.0-release-checkout>"
$skillName="<admitted-skill-name>"
$destinationRoot="<host-recognized-skills-root>"
Copy-Item -LiteralPath "$sourceRoot/skills/$skillName" -Destination "$destinationRoot/$skillName" -Recurse
~~~

This is a fallback procedure. A valid manual verification record must identify
the released commit or tag, exact host, resolved destination, refresh/restart
step, discovery result, and success, boundary, and missing-dependency smoke
results. Copy the complete package; never copy only SKILL.md when the package
references resources.

## Direct upstream Skills

Unmodified Matt Pocock Skills stay on their original upstream path:
[mattpocock/skills](https://github.com/mattpocock/skills). They are not copied
into this repository. Use the upstream repository's current instructions and
record the exact package, revision, host, and discovery result in the local
evidence record when documenting a supported composition.

## Modified third-party Skills

A locally modified third-party Skill belongs in the separate
skills-3rdParty repository. Its installation must use that repository's
released source-grouped package and its completed provenance, patch, license,
and synchronization records. No modified third-party package is included in
this first-party collection.

## Verification record

For every future verified release or per-Skill command, preserve:

- exact command and installer version;
- repository URL and immutable released commit or tag;
- host, installation scope, and resolved destination;
- fresh-environment discovery result;
- success, boundary, invocation, and missing-dependency smoke results;
- any manual fallback used; and
- known limitations.

Structural validation, a source-checkout scan, and an unexecuted command are
not installation evidence. The collection discovery script is a structural
cross-reference check; it does not replace fresh host installation.
