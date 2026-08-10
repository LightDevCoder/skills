# v0.1.2 release receipt

[中文收据](RELEASE_RECEIPT.zh-CN.md)

Status: `VERIFIED` — the seven-package collection, tag `v0.1.2`, GitHub
release, fresh-install verification, and the publish commit are complete.

## Identity

| Field | Value |
| --- | --- |
| Repository | `LightDevCoder/skills` |
| Release | `v0.1.2` |
| Release commit | `8de5ec1a453b0e93f71dcda160e17ea7b42c3997` |
| Release URL | https://github.com/LightDevCoder/skills/releases/tag/v0.1.2 |
| Date | `2026-08-10` |
| Scope | Seven first-party packages (the five in v0.1.1 plus `recap` and `language-learning`), bilingual docs, Quick Start, workflow recipes, header, CI, and the generic `latest` install command. |

## Acceptance evidence

- Structure and discovery: [DISCOVERY_VERIFICATION.md](DISCOVERY_VERIFICATION.md)
- Package and collection tests: [TEST_SUMMARY.md](TEST_SUMMARY.md)
- Fresh install and host discovery: [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md)
- Limitations and evidence labels: [LIMITATIONS.md](LIMITATIONS.md)
- Review policy: [../../../REVIEW_POLICY.md](../../../REVIEW_POLICY.md)
- Admission contract: [../../../SKILL_ADMISSION.md](../../../SKILL_ADMISSION.md)

## Release gate

| Gate | Status | Evidence |
| --- | --- | --- |
| Ownership and scope | `VERIFIED` | Seven first-party package list and public ownership boundary. |
| Metadata/invocation consistency | `VERIFIED` | Collection test plus package frontmatter and `agents/openai.yaml`. |
| Package behavior | `VERIFIED` for the listed local contract/behavior checks | See [TEST_SUMMARY.md](TEST_SUMMARY.md); fresh installation and independent acceptance remain separate gates. |
| Fresh whole-repository install | `VERIFIED` | CLI `1.5.22`; `PASS` for both the `latest` and `#v0.1.2` forms. See [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md). |
| Fresh per-Skill install | `VERIFIED` | CLI `1.5.22`; `PASS` for both the `latest` and `#v0.1.2` forms. See [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md). |
| Independent `review-loop agent-skill` acceptance | `VERIFIED` for the two newly admitted packages; `BLOCKED` for the original five | `recap` and `language-learning` each carry a fresh independent fast-track Evaluator `PASS`; the original five still lack a fresh independent evaluator record. |
| GitHub Actions | `PASS` on the release commit | Run `31362999381` (`collection-quality`). See `.github/workflows/quality.yml`. |

Do not call this receipt an independent acceptance record for the original five
packages while their independent evaluator row is `BLOCKED`. Do not call
structural evidence runtime proof.
