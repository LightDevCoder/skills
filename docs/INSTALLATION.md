# Installation and Fresh-Install Verification

This repository's installation documentation distinguishes command templates
from verified release instructions. The collection currently has no admitted
packages, remote identity, release tag, or verified command. Do not copy a
template below into user-facing release documentation until it has been tested
against the actual published repository.

## Supported installation scopes

The collection supports a host only after that host has passed fresh-install
and discovery verification for one of these scopes:

| Scope | Location policy | Required release evidence |
| --- | --- | --- |
| Project-local | The Agent host's recognized project-level Skills location for the active repository. | Exact host and path, installer or manual command, restart or reload step, and successful discovery without a source checkout. |
| User/global | The Agent host's recognized user-level or global Skills location. | Exact host and path, installer or manual command, restart or reload step, and successful discovery without a source checkout. |
| Per-Skill | A single admitted package directory containing `SKILL.md` and every required resource. | Exact selected package, released revision, installation path, and successful discovery and behavioral smoke evidence. |

The release documentation must name the actual supported hosts and locations;
these categories do not imply that every Agent host or arbitrary directory is
supported.

## General installer templates

Where the general Skills installer supports the target host and repository
layout, the expected forms are:

```text
# Template only — verify exact installer behavior before publication.
npx skills@latest add <owner>/skills
npx skills@latest add <owner>/skills --skill <skill-name>
```

The first form is for a whole-repository installation; the second requests one
Skill. Before publishing them, verify the actual installer version, repository
identity, argument semantics, resulting location, resource completeness, and
host discovery. Replace placeholders only with values tested against the
released remote.

## Manual fallback

When an installer is unavailable or unsupported:

1. Obtain the exact released repository revision from its authoritative source.
2. Copy the complete admitted `skills/<skill-name>/` directory, including
   `SKILL.md` and every referenced resource, into the target host's recognized
   project-local or user/global Skills location.
3. Preserve any required attribution or notice supplied with the package.
4. Reload or restart the host if its discovery model requires it.
5. Verify discovery and run the documented smoke, boundary, and
   missing-dependency checks in a fresh environment.

Manual copying is a fallback installation mechanism, not permission to copy an
unmodified third-party Skill into this repository.

## Direct upstream and modified third-party Skills

An unmodified upstream Skill must be installed from its original upstream
repository. For example, direct-use Matt Pocock Skills are obtained from
[mattpocock/skills](https://github.com/mattpocock/skills), not duplicated here.

If a locally modified third-party Skill is justified, install it from the
separate `skills-3rdParty` repository using that repository's provenance,
version-pinning, and installation instructions. Do not describe it as an
original first-party Skill.

## Required verification record

For every published whole-repository or per-Skill command, preserve:

- the exact command and installer version;
- repository URL, released commit, version, or tag;
- host, installation scope, and resolved destination;
- fresh-environment discovery result;
- success, boundary, and missing-dependency smoke results where applicable;
- any manual fallback used; and
- known limitations.

Structural validation, a copied package tree, and an unexecuted command are
not installation evidence. See [admission](SKILL_ADMISSION.md) and
[maintenance](MAINTENANCE.md) for the larger evidence and release gates.
