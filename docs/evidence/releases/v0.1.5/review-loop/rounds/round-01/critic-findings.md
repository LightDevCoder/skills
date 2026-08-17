# Critic Findings - Round 1

Fresh read-only Critic context (independent subagent) against the frozen
Charter revision 1. Candidate record; dispositions belong to the Core.

## Finding F-001
- Severity: High
- Related acceptance criterion: AC-12
- Evidence: `git tag -l 'v0.1.5'` empty; HEAD `d526ef3`; candidate changes
  uncommitted. README.md asserted "v0.1.5 … is published from the `v0.1.5`
  release tag"; CATALOG.md "Released v0.1.5"; docs/INSTALLATION.md "current
  stable release … published from the `v0.1.5` release tag"; the discovery
  and contract tests hard-asserted the published framing.
- Expected behavior: a candidate must not claim a published/tagged state
  before the tag exists.
- Observed behavior: published framing asserted pre-tag, and encoded into
  the acceptance gate tests.
- Recommended minimal repair: candidate ("tag pending") phrasing in
  README/CATALOG/INSTALLATION and matching test expectations; flip to
  published framing in the post-release commit.
- Disposition: confirmed
- Resolution evidence: [repair-evidence.md](repair-evidence.md)
- Related finding: F-002

## Finding F-002
- Severity: High
- Related acceptance criterion: AC-11, AC-13
- Evidence: SKILL.md (tail) and both worker guides say "recommended
  integration version is Light-Kanban v1.0.6"; `references/api.md` line 4
  still says "v1.0.5 is the recommended integration version". api.md was
  not in the change set.
- Expected behavior: the package's own files must agree on the recommended
  version; compatibility claim stays v1.0.4+.
- Observed behavior: intra-package version drift.
- Recommended minimal repair: sync api.md to the SKILL.md sentence.
- Disposition: confirmed
- Resolution evidence: [repair-evidence.md](repair-evidence.md)
- Related finding: F-001

## Finding F-003
- Severity: Medium
- Related acceptance criterion: AC-12
- Evidence: `python3 -m unittest tests.test_collection_discovery` red with
  unresolved links to AGENT_SKILL_REVIEW.md / findings.md / verdict.md;
  RELEASE_RECEIPT gate row already said "Collection tests PASS".
- Expected behavior: gate rows reflect an actually green suite.
- Observed behavior: pre-asserted PASS while the suite was red.
- Recommended minimal repair: reword the gate row to state the final green
  run happens after the review records are written; ensure the committed
  candidate state has a green suite.
- Disposition: confirmed
- Resolution evidence: [repair-evidence.md](repair-evidence.md)
- Related finding: none

## Areas verified clean (no finding)

- AC-1–AC-4: non-overlap rule, canonical atomic-claim boundary sentence,
  scheduler ownership, different-agent concurrency, no resident lock
  service.
- AC-5–AC-7: first-registration identity, reuse, missing-identity
  no-mutation.
- AC-8: A–F unchanged.
- AC-9: 100 contract + 23 behavior assertions reproduced; negative fixtures
  flip exactly their target checker.
- AC-10: G/H fixtures record honest verification boundaries.
- AC-11: EN ↔ zh-CN parity accurate modulo F-002.
- AC-13: no new REST API requirement.
- Clean-copy install to /tmp: 13 files, discoverable, suites run
  self-contained.
- openai.yaml parses; invocation boundary clean.
