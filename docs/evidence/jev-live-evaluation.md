# TypeSafe Jev Live Evaluation & Calibration Evidence

- **Timestamp:** `2026-09-20T05:42:34Z`
- **Mode:** `live`
- **Model Version:** `jev-latest`
- **Total Scenarios:** `36`
- **Overall Passed:** `36`
- **Overall Failed:** `0`
- **Overall Accuracy:** `100.0%`
- **ask-light Workflow Safety:** `22/22 (100.0%)`
- **ask-light Semantic Accuracy:** `100.0%` (Evaluated: 4, Not Evaluated: 18, Passed: 4)
- **agent-config Config Correctness:** `14/14 (100.0%)`
- **agent-config Complexity Semantic Accuracy:** `100.0%` (Evaluated: 12, Not Evaluated: 2)
- **agent-config Reasoning Semantic Accuracy:** `100.0%` (Evaluated: 13, Not Evaluated: 1)
- **Duration:** `11.137s`

## 1. ask-light Evaluation Results (22 scenarios)

| ID | Scenario Name | Status | Observed Primary | Ambiguity | Escalation | Choice Skipped | Safety | Semantic Status | Overall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AL-01 | Standard frontier query: ready ticket exists | `RECOMMEND` | `implement` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-02 | Progress inquiry / where is project now | `EXPLAIN` | `None` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-03 | Workflow explanation request | `EXPLAIN` | `None` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-04 | Explicit execution command: Go ahead | `TRANSITION` | `implement` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-05 | Hesitant inquiry: Should we start implementing? | `RECOMMEND` | `implement` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-06 | Advice only constraint: I only want advice | `RECOMMEND` | `implement` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-07 | Initial project state: No SPEC exists | `RECOMMEND` | `project-clarify` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-08 | Clarification complete: Clarification is ready | `RECOMMEND` | `project-spec` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-09 | Active SPEC exists but tickets do not | `RECOMMEND` | `project-tickets` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-10 | Ready ticket exists at frontier | `RECOMMEND` | `implement` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-11 | All tickets resolved | `RECOMMEND` | `project-review` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-12 | Stale review verdict | `RECOMMEND` | `project-review` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-13 | Dirty working tree invalidating review | `RECOMMEND` | `project-review` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-14 | Unknown ticket requested (fail-closed) | `BLOCKED` | `None` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-15 | Multiple active efforts without explicit target (fail-closed) | `NEED_INPUT` | `None` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-16 | Ambiguous user request with trade-offs | `RECOMMEND` | `implement` | 0.88 | N/A | Yes | PASS | PASS | **PASS** |
| AL-17 | Complex architectural overhaul request | `RECOMMEND` | `implement` | N/A | 0.87 | Yes | PASS | PASS | **PASS** |
| AL-18 | Clear status question negative case (no false ambiguity) | `EXPLAIN` | `None` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-19 | Negative ambiguity case: unambiguous disjunction query | `RECOMMEND` | `implement` | 0.35 | N/A | Yes | PASS | PASS | **PASS** |
| AL-20 | Negative escalation case: simple refactor task | `RECOMMEND` | `implement` | N/A | 0.03 | Yes | PASS | PASS | **PASS** |
| AL-21 | Adversarial: what is next, do not execute | `RECOMMEND` | `implement` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-22 | Adversarial: explain whether implementation is next | `EXPLAIN` | `None` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |

### 1.1 Confusion Matrices for Evaluated Semantic Dimensions

- **Material Ambiguity (p >= 0.65):** TP=1, FP=0, TN=1, FN=0 (Total evaluated: 2)
- **Reasoning Escalation (p >= 0.60):** TP=1, FP=0, TN=1, FN=0 (Total evaluated: 2)
- **Choice Routing:** N/A — no multi-action candidates in current canonical state machine (singleton queries skip Choice).

## 2. agent-config Evaluation Results (14 scenarios)

| ID | Scenario Name | Observed Model | Observed Effort | Topology | Config Correct | Complexity Semantic | Reasoning Semantic | Overall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AC-01 | Routine documentation edit | `gpt-4o-mini` | `default` | `Case C` | PASS | PASS | PASS | **PASS** |
| AC-02 | Small bug fix | `claude-3-5-sonnet` | `default` | `Case A` | PASS | PASS | PASS | **PASS** |
| AC-03 | Standard feature implementation | `claude-3-5-sonnet` | `default` | `Case A` | PASS | PASS | PASS | **PASS** |
| AC-04 | Large refactor | `o3-mini` | `high` | `Case C` | PASS | PASS | PASS | **PASS** |
| AC-05 | Security-critical change | `o3-mini` | `high` | `Case C` | PASS | PASS | PASS | **PASS** |
| AC-06 | Complex concurrency work | `o3-mini` | `high` | `Case C` | PASS | PASS | PASS | **PASS** |
| AC-07 | Cost-sensitive complex work | `o3-mini` | `high` | `Case C` | PASS | PASS | PASS | **PASS** |
| AC-08 | Latency-sensitive routine work | `gpt-4o-mini` | `default` | `Case C` | PASS | PASS | PASS | **PASS** |
| AC-09 | Fixed-model harness | `fixed-sonnet` | `default` | `Case A` | PASS | PASS | PASS | **PASS** |
| AC-10 | Multi-model decomposed harness | `o3-mini` | `default` | `Case D` | PASS | PASS | PASS | **PASS** |
| AC-11 | Host with no effort selector | `gpt-4o` | `default` | `Case A` | PASS | PASS | PASS | **PASS** |
| AC-12 | Limited effort selector bounds Jev output | `model-x` | `medium` | `Case A` | PASS | NOT_EVALUATED | NOT_EVALUATED | **PASS** |
| AC-13 | User explicitly requests high effort (overrides Jev) | `model-x` | `high` | `Case A` | PASS | PASS | PASS | **PASS** |
| AC-14 | User rejects configuration change preview | `active-stay` | `default` | `Case A` | PASS | NOT_EVALUATED | PASS | **PASS** |

## 3. Calibration Invariant Proofs

- **Invariant 1: Jev output cannot grant TRANSITION authority:** Verified in deterministic state machine where question phrasing remains RECOMMEND and execution intent noul is removed from queries.
- **Invariant 2: Query economy eliminates consumer-less questions:** Unambiguous queries on single-action states plan 0 Jev queries (e.g. AL-01, AL-02, AL-03, AL-07, AL-08, AL-09, AL-10, AL-11, AL-18, AL-21, AL-22).
- **Invariant 3: Reasoning need influences effort without overriding explicit policy:** Verified in AC-04/06 (reasoning need mapped to high effort) and AC-13 (explicit minimal policy overrode Jev).
- **Invariant 4: Host capabilities bound Jev output:** Verified in AC-12 where host without 'high' bounded Jev output to 'medium' without inventing unsupported values.
- **Invariant 5: Cost sensitivity does not downgrade capability tier:** Verified in AC-07 where task remained in 'high' tier while honoring cost preference.
- **Invariant 6: Honest cost policy:** Cost optimization tie-breaking is explicitly deferred when host lacks pricing metadata.

