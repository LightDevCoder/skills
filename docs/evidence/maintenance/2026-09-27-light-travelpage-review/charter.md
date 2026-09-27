# Acceptance Charter

## Revision
- Charter revision: 1
- Supersedes: none
- Created at: 2026-09-27

## Acceptance baseline
- Source: User's 2026-09-27 request in the Hokkaido-TravelPage-Test task
- Source revision or identity: Fix desktop flight paging and use real matching map outlines; update light-travelpage Skill and push it to the remote; real outlines are the default for known places, without a user style choice.
- Approval state: approved
- Approval evidence: Direct user requests in this task

## Review Profile
- Profile: agent-skill
- Selection reason: Existing first-party Skill has changed instructions, executable web template, map builder, and tests.

## Original goal
Make generated travel pages usable on desktop flight cards and map known destinations against a real matching geographic outline with coordinate-based stops; propagate this behavior into the Skill.

## User-visible outcome
Desktop visitors can reach each flight card with controls and a wheel. The Hokkaido page depicts its real coastline and accurately positioned stops. Future known-coordinate trips follow the Skill's geographic-outline default.

## In scope
- Flight carousel desktop controls, keyboard and wheel access, preserving mobile scrolling.
- Geographic map builder and Hokkaido source integration, labels, route display and attribution.
- Skill behavior contract, generated template, focused tests and affected collection metadata.

## Out of scope
- New release tag; changes to unrelated Skills; D1 schema or shared travel state.

## Acceptance criteria
- AC-1: Template flight cards can be paged on desktop and retain mobile overflow; focused test and browser observation.
- AC-2: The Hokkaido page uses a sourced real coastline and places remain at their WGS84-projected coordinates; build/test and rendered browser observation.
- AC-3: Skill instructions select matching geography by default for known-coordinate destinations and honestly label fallback as schematic; package review.
- AC-4: Generated Skill template builds and tests from a clean copy, including a negative geographic input; collection validation and independent review.
- AC-5: Attribution, catalog and unreleased changelog reflect the change; review identifies no unresolved blocking finding.

## Required evidence
- Source: exact package revision and diff from 7a98ed9574e6ffb69f533cdcbdf16a22633ef0e6.
- Structural: Skill quick validation, resource and reference inspection.
- Behavioral: focused assertion-bearing tests, including negative coordinate bounds case.
- Installation: clean local template creation, dependency install, fixture build and test.
- Manual: desktop browser control, wheel and map appearance observations.
- Review: separate Standards and Spec code-review findings and fresh independent Evaluator.

## Required validation scenarios
- VS-1: Create fresh page from package, prepare fixture, build and run tests; all pass.
- VS-2: Build geographic fixture with two placed coordinates; out-of-bounds coordinate fails.
- VS-3: In desktop browser, page flight cards with button and wheel; map shows Hokkaido's coastline and route inset.
- VS-4: Inspect fallback instruction and exclusion from real-geography claims.

## Constraints, assumptions, and risks
- Existing map route lines indicate visit order, not roads or tracks. Source geography must be attributed.
- Do not change runtime shared state or create a new release.

## Approved exceptions
- None
