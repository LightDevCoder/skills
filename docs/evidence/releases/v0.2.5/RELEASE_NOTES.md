# v0.2.5 — Reliable Workflow Routing and Verification

[中文发布说明](RELEASE_NOTES.zh-CN.md) · [Release Manifest](RELEASE_MANIFEST.md)

This release fixes cases where a Skill could recommend execution or publication from incomplete evidence. `agent-config` now requires fresh canonical Host evidence and a matching confirmed Profile, while `ask-light --mode semantic` follows the same project constraints and final validation as the primary route. Duplicate ticket numbers block routing until explicitly migrated.

Manuscript projects can now complete generic `project-init` bootstrap and then create their manuscript-specific Profile and state. Dependency checks use current runtime interfaces; exact package-byte comparison is reserved for an explicit immutable release ref. `code-review` emits normalized findings for `review-loop`, and the travel-page generator and first sync enforce the same todo contract.

CI discovers the full Python suite and runs Node runtime tests plus a generated-trip build. Remote release verification rejects missing or divergent tags and unavailable GitHub Releases. Package count remains 36. Published installation and release evidence will be recorded after the tag and GitHub Release exist.
