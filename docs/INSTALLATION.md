# Installation and Fresh-Install Verification

This repository currently contains a five-Skill local release candidate. It
has no public remote identity, stable tag, or released version yet. Therefore
this document deliberately does not publish a final owner/repository command.
A command becomes a verified release instruction only after it succeeds in a
fresh environment against the actual released repository and is recorded by
the T14/T16 evidence gates.

## Supported installation scopes

| Scope | Destination policy | Required evidence |
| --- | --- | --- |
| Project-local | The active repository's recognized project-level Skills location. | Exact host/path, complete package copy or installer result, refresh step, and discovery without the source checkout. |
| User/global | The Agent host's recognized user-level or global Skills location. | Exact host/path, complete package copy or installer result, refresh step, and discovery without the source checkout. |
| Per-Skill | One complete admitted directory containing SKILL.md and every referenced resource. | Selected package, immutable released revision, destination, discovery, and behavioral smoke evidence. |

These categories do not imply that every Agent host supports every location.
The host's own documentation and fresh discovery result control.

## Release installer form

The general installer syntax is retained here as a release template only:

~~~
npx skills add <owner>/<repository>
npx skills add <owner>/<repository> --skill <skill-name>
~~~

The syntax is described by the [Skills CLI documentation](https://www.skills.sh/docs/cli),
but the commands above are not a verified command for this local candidate:
the owner, repository, release revision, installer version, destination, and
host discovery result are intentionally unresolved. Do not replace the
placeholders and publish them as release instructions before T14/T16.

## Manual fallback

When a verified installer is unavailable or unsupported, use the complete
released package snapshot and follow the host's recognized Skills location:

~~~
$sourceRoot="<released-checkout>"
$skillName="<admitted-skill-name>"
$destinationRoot="<host-recognized-skills-root>"
Copy-Item -LiteralPath "$sourceRoot/skills/$skillName" -Destination "$destinationRoot/$skillName" -Recurse
~~~

This is a procedure template, not a release command. A valid manual
verification record must identify the released commit or tag, exact host,
resolved destination, refresh/restart step, discovery result, and success,
boundary, and missing-dependency smoke results. Copy the complete package;
never copy only SKILL.md when the package references resources.

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
