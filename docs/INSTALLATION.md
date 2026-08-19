# Installation and Fresh-Install Verification

[中文安装说明](INSTALLATION.zh-CN.md)

The public first-party collection's current stable release is
[v0.1.6](https://github.com/LightDevCoder/skills/releases/tag/v0.1.6),
published from commit `41b6e7169a1c68bb017f9ff6c464b220185b02ff`. Package
contracts remain inside `skills/<name>/`; this document is the installation
authority and does not replace host-specific discovery rules.

The standard install command is the generic `latest` form: it follows the
repository's default revision, so every `npx skills add
LightDevCoder/skills` install gets the current collection on the default
branch. As of this branch the default revision contains nine admitted Skills
and is published as v0.1.6. The v0.1.6 commands below
were verified against fresh destinations at that tag in the
[v0.1.6 installation verification](evidence/releases/v0.1.6/INSTALLATION_VERIFICATION.md).

## Revision semantics

The official Skills CLI accepts a `#ref` fragment in a GitHub source. The
fragment is passed as the Git revision; a source without a fragment uses the
repository's default revision. The parser and clone behavior are documented in the
[official Skills CLI source parser](https://raw.githubusercontent.com/vercel-labs/skills/main/src/source-parser.ts)
and [Git helper](https://raw.githubusercontent.com/vercel-labs/skills/main/src/git.ts).

The generic `latest` command below uses no fragment and therefore follows the
repository's default revision: it installs the current collection and is the
standard way to install. The pinned `#v0.1.6` form selects the published tag
and is retained for reproducible installs and release verification. Neither
form is a claim about a future default revision; re-run discovery against the
fresh destination for the resolved content.

For the generic `latest` forms, which follow the current default revision,
use:

```text
npx skills add LightDevCoder/skills --yes --copy --agent '*'
npx skills add LightDevCoder/skills --skill review-loop --yes --copy --agent '*'
```


## v0.1.6 release commands

The v0.1.6 release commands were verified against the published v0.1.6 tag and
installed the nine-package collection at that revision:

```text
npx skills add LightDevCoder/skills#v0.1.6 --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.6 --skill kb-init --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.6 --skill review-loop --yes --copy --agent '*'
```

The first installs the nine-package collection and the others select one
complete package from the same verified revision. The forms are
verified against fresh destinations in the
[v0.1.6 installation record](evidence/releases/v0.1.6/INSTALLATION_VERIFICATION.md).

The `latest` form and the `#v0.1.6` form resolve to the same content at
release time; only the pinned form is stable against future
default-revision changes.

## Historical v0.1.5 verification

The previous stable release was the published v0.1.5 snapshot at commit
`a56aa9d98de0b941ee2282144bc7e756ef5e48bd`. It installed the eight-package
collection at that revision. Its verified pinned forms were:

```text
npx skills add LightDevCoder/skills#v0.1.5 --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.5 --skill light-kanban-worker --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.5 --skill review-loop --yes --copy --agent '*'
```

Verified against fresh destinations in the
[v0.1.5 installation record](evidence/releases/v0.1.5/INSTALLATION_VERIFICATION.md).

## Historical v0.1.4 verification

The previous stable release was the published v0.1.4 snapshot at commit
`a9cc8aa029c926fc80f6ddc0022793f79dfd85bd`. It introduced
`light-kanban-worker` for the eight-package collection. Its pinned form was:

```text
npx skills add LightDevCoder/skills#v0.1.4 --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.4 --skill light-kanban-worker --yes --copy --agent '*'
```

Both forms were verified against fresh destinations with CLI `1.5.22`; see
the [v0.1.4 installation record](evidence/releases/v0.1.4/INSTALLATION_VERIFICATION.md).

## Historical v0.1.3 verification

The previous stable release was the published v0.1.3 snapshot at commit
`f8b573a48f7d53da74cfb8d94eb2ee7ca467d5c4`. It is a toolchain-migration
release with the same seven packages as v0.1.2, so its package-level installs
are covered by the
[v0.1.2 installation verification](evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.md);
its pinned form was:

```text
npx skills add LightDevCoder/skills#v0.1.3 --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.3 --skill review-loop --yes --copy --agent '*'
```

## Historical v0.1.2 verification

The previous stable release was the published v0.1.2 snapshot at commit
`8de5ec1a453b0e93f71dcda160e17ea7b42c3997`. Its verified commands were:

```text
npx skills add LightDevCoder/skills#v0.1.2 --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.2 --skill review-loop --yes --copy --agent '*'
```

Both forms were verified against fresh destinations with CLI `1.5.22`; see
the [v0.1.2 installation record](evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.md).

## Historical v0.1.1 verification

The previous stable release was the published v0.1.1 snapshot at commit
`c50f1ef403a5f0bfe02e75d1aeff2c237556db63`. Its verified commands used an
explicit tag and a codex host selection:

```text
npx skills add LightDevCoder/skills#v0.1.1 --yes --copy --agent codex
npx skills add LightDevCoder/skills#v0.1.1 --skill review-loop --yes --copy --agent codex
```

The verified CLI version, destination class, discovery result, and smoke result
are recorded in the [v0.1.1 installation record](evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.md).

## Historical v0.1.0 verification

The historical stable release was the published v0.1.0 snapshot at commit
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
permanent pin. The current release commands above use the generic `latest` form
or the explicit `#v0.1.5` tag.

## `recap` and `language-learning` packages

`recap` and `language-learning` are admitted first-party packages released in
v0.1.2 through the prompt-only fast track. Their admission evidence is recorded
in
[evidence/admissions/recap/README.md](evidence/admissions/recap/README.md) and
[evidence/admissions/language-learning/README.md](evidence/admissions/language-learning/README.md).
Their fresh installs are exercised as part of the
[collection discovery test](../tests/test_collection_discovery.py) and the
[v0.1.2 installation record](evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.md).

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

```bash
source_root="<current-release-checkout>"
skill_name="<admitted-skill-name>"
destination_root="<host-recognized-skills-root>"
cp -R "$source_root/skills/$skill_name" "$destination_root/$skill_name"
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
