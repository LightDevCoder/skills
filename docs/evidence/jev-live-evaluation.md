# TypeSafe Jev Live Evaluation & Calibration Evidence

> **Notice:** The previous 12/12 complexity and 13/13 reasoning live semantic figures are **SUPERSEDED** because declared difficulty was previously included in the semantic state payload (label leakage). The figures below represent independent, label-clean evaluation.

- **Timestamp:** `2026-09-20T06:26:25Z`
- **Mode:** `live`
- **Model Version:** `jev-latest`
- **Total Scenarios:** `36`
- **Overall Passed:** `35`
- **Overall Failed:** `1`
- **Overall Accuracy:** `97.2%`
- **ask-light Workflow Safety:** `22/22 (100.0%)`
- **ask-light Semantic Accuracy:** `100.0%` (Evaluated: 4, Not Evaluated: 18, Passed: 4)
- **agent-config Config Correctness:** `13/14 (92.9%)`
- **agent-config Complexity Semantic Accuracy:** `90.9%` (Authoritative code-owned: 3, Jev Evaluated: 11, Passed: 10, Failed: 1, Fallback: 0, Not Evaluated: 3)
- **agent-config Reasoning Semantic Accuracy:** `100.0%` (Explicit-policy owned: 1, Jev Evaluated: 11, Passed: 11, Failed: 0, Fallback: 2, Not Evaluated: 3)
- **Duration:** `10.652s`

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
| AL-16 | Ambiguous user request with trade-offs | `RECOMMEND` | `implement` | 0.89 | N/A | Yes | PASS | PASS | **PASS** |
| AL-17 | Complex architectural overhaul request | `RECOMMEND` | `implement` | N/A | 0.87 | Yes | PASS | PASS | **PASS** |
| AL-18 | Clear status question negative case (no false ambiguity) | `EXPLAIN` | `None` | N/A | N/A | Yes | PASS | NOT_EVALUATED | **PASS** |
| AL-19 | Negative ambiguity case: unambiguous disjunction query | `RECOMMEND` | `implement` | 0.37 | N/A | Yes | PASS | PASS | **PASS** |
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
| AC-02 | Small bug fix | `gpt-4o-mini` | `default` | `Case C` | FAIL | FAIL | PASS | **FAIL** |
| AC-03 | Standard feature implementation | `claude-3-5-sonnet` | `default` | `Case A` | PASS | PASS | NOT_EVALUATED | **PASS** |
| AC-04 | Large refactor | `o3-mini` | `high` | `Case C` | PASS | PASS | PASS | **PASS** |
| AC-05 | Security-critical change | `o3-mini` | `high` | `Case C` | PASS | PASS | NOT_EVALUATED | **PASS** |
| AC-06 | Complex concurrency work | `o3-mini` | `high` | `Case C` | PASS | PASS | PASS | **PASS** |
| AC-07 | Cost-sensitive complex work | `o3-mini` | `high` | `Case C` | PASS | PASS | PASS | **PASS** |
| AC-08 | Latency-sensitive routine work | `gpt-4o-mini` | `default` | `Case C` | PASS | PASS | PASS | **PASS** |
| AC-09 | Fixed-model harness | `fixed-sonnet` | `default` | `Case A` | PASS | PASS | PASS | **PASS** |
| AC-10 | Multi-model decomposed harness | `o3-mini` | `default` | `Case D` | PASS | NOT_EVALUATED | PASS | **PASS** |
| AC-11 | Host with no effort selector | `o3-mini` | `default` | `Case C` | PASS | PASS | PASS | **PASS** |
| AC-12 | Limited effort selector bounds Jev output | `model-x` | `medium` | `Case A` | PASS | PASS | PASS | **PASS** |
| AC-13 | User explicitly requests high effort (overrides Jev) | `model-x` | `high` | `Case A` | PASS | NOT_EVALUATED | NOT_EVALUATED | **PASS** |
| AC-14 | User rejects configuration change preview | `active-stay` | `default` | `Case A` | PASS | NOT_EVALUATED | PASS | **PASS** |

## 3. Calibration Invariant Proofs

- **Invariant 1: Jev output cannot grant TRANSITION authority:** Verified in deterministic state machine where question phrasing remains RECOMMEND and execution intent noul is removed from queries.
- **Invariant 2: Query economy eliminates consumer-less questions:** Unambiguous queries on single-action states plan 0 Jev queries (e.g. AL-01, AL-02, AL-03, AL-07, AL-08, AL-09, AL-10, AL-11, AL-18, AL-21, AL-22).
- **Invariant 3: Reasoning need influences effort without overriding explicit policy:** Verified in AC-04/06 (reasoning need mapped to high effort) and AC-13 (explicit minimal policy overrode Jev).
- **Invariant 4: Host capabilities bound Jev output:** Verified in AC-12 where host without 'high' bounded Jev output to 'medium' without inventing unsupported values.
- **Invariant 5: Cost sensitivity does not downgrade capability tier:** Verified in AC-07 where task remained in 'high' tier while honoring cost preference.
- **Invariant 6: Honest cost policy:** Cost optimization tie-breaking is explicitly deferred when host lacks pricing metadata.

