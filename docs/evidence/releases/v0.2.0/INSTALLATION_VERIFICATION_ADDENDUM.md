# v0.2.0 Installation Verification Addendum — re-pointed tag (34 packages)

[中文记录](INSTALLATION_VERIFICATION_ADDENDUM.zh-CN.md)

Status: `VERIFIED` — 2026-08-30, post-publication.

## Release identity

- Tag: `v0.2.0`, re-pointed by force-push from the original publication
  (commit `9c2572b`, tag object `29bfd22`) to the extended release commit
  **`e063753d880afec760f1c7b7a64b3ac601073ff9`**. The release line now
  carries 34 first-party packages: the original 33-package architecture plus
  the `humanizer` admission, with the post-publication hardening of
  `agent-config` / `implement` / `ask-light` folded in.
- Rationale: the collection owner directed that no new version be cut; the
  extension and the `humanizer` admission are recorded on the official
  `v0.2.0` line (CHANGELOG, `## 0.2.0`).
- CI: `collection-quality` **PASS** on the release commit
  (`e063753`, run `33292549793`).

## Fresh released-repository installation (PASS)

Environment: isolated temporary directories on macOS; Skills CLI
**`1.5.23`** via `npx --yes skills@latest`; source: the actual published
repository tag (`LightDevCoder/skills#v0.2.0`); `--copy` mode; no reliance
on any local source checkout.

| Scope | Command | Result |
| --- | --- | --- |
| Per-Skill | `npx --yes skills add LightDevCoder/skills#v0.2.0 --skill humanizer --yes --copy` | `PASS` — installed into detected agent scopes (`.agents/skills/`, `.zcode/skills/`); all 4 package files byte-identical to the tag; discovery scan on the installed copies passed (`name: humanizer`, model-invoked policy, resolvable `references/zh-adaptation.md`, `ATTRIBUTION.md` present). |
| Whole collection | `npx --yes skills add LightDevCoder/skills#v0.2.0 --yes --copy` | `PASS` — 34 packages installed; 257 package files checked against `git show v0.2.0:` content, 0 missing, 0 differing (collection assets under `skills/docs/` are not installed package content). |

## Boundary

- This addendum covers released-repository installation verification for the
  re-pointed tag. Host-level discovery on the owner's personal machines is
  recorded in the [humanizer admission record](../../admissions/humanizer/README.md).
- The original v0.2.0 verification records
  ([INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md),
  [RELEASE_RECEIPT.md](RELEASE_RECEIPT.md)) remain immutable descriptions of
  the original 33-package publication; this addendum documents the extension.
- The generic `latest` install command follows the repository default
  revision and installs the same 34-package tree from `main`.
