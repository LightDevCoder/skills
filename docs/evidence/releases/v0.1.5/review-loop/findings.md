# Finding Registry

## Finding F-001
- First recorded: round-01
- Status: resolved
- Severity: High
- Related acceptance criterion: AC-12 (candidate must not claim a published
  tag that does not exist)
- Canonical summary: README / CATALOG / INSTALLATION presented v0.1.5 as
  already published while the tag does not exist, and the collection tests
  hard-asserted the published framing.
- Related finding: G-001
- Current evidence: [round-01/critic-findings.md](rounds/round-01/critic-findings.md)
- Resolution evidence: [round-01/repair-evidence.md](rounds/round-01/repair-evidence.md) and [round-02/repair-evidence.md](rounds/round-02/repair-evidence.md) (residual sentence closed under G-001)

## Finding F-002
- First recorded: round-01
- Status: resolved
- Severity: High
- Related acceptance criterion: AC-11, AC-13 (package-internal version
  agreement)
- Canonical summary: `references/api.md` still said "v1.0.5 is the
  recommended integration version" while SKILL.md and the guides say
  v1.0.6.
- Related finding: F-001
- Current evidence: [round-01/critic-findings.md](rounds/round-01/critic-findings.md)
- Resolution evidence: [round-01/repair-evidence.md](rounds/round-01/repair-evidence.md)

## Finding F-003
- First recorded: round-01
- Status: resolved
- Severity: Medium
- Related acceptance criterion: AC-12 (gate rows must reflect actual suite
  state)
- Canonical summary: RELEASE_RECEIPT pre-release gate recorded "Collection
  tests PASS" while the discovery suite was red due to the not-yet-written
  review-record links.
- Related finding: none
- Current evidence: [round-01/critic-findings.md](rounds/round-01/critic-findings.md)
- Resolution evidence: [round-01/repair-evidence.md](rounds/round-01/repair-evidence.md)

## Finding G-001
- First recorded: round-01 (fresh Evaluator)
- Status: resolved
- Severity: High
- Related acceptance criterion: AC-11, AC-12 (no pre-tag "published" claim)
- Canonical summary: after the F-001 repair, a residual "published v0.1.5
  collection" sentence survived in README.md / README.zh-CN.md, and no gate
  asserted its absence.
- Related finding: F-001
- Current evidence: [round-01/evaluator-verdict.md](rounds/round-01/evaluator-verdict.md)
- Resolution evidence: [round-02/repair-evidence.md](rounds/round-02/repair-evidence.md)
