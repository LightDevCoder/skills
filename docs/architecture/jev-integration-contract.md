# TypeSafe Jev Integration Contract

This document defines the shared, hardened architectural integration contract for TypeSafe Jev System One judgments across the Light Skills collection (`project-init`, `ask-light`, and `agent-config`).

---

## 1. Architectural Principles

Code owns the deterministic workflow and safety invariants; Jev provides fast, typed System One judgments; code applies explicit policy and executes:

```text
code owns deterministic workflow state & safety boundaries
                    ↓
Jev provides bounded semantic judgments (Score, Noul, Choice)
                    ↓
code applies explicit policy
                    ↓
workflow / configuration execution
```

### Invariants

1. **Deterministic Authority:**
   Known facts, exact rules, permissions, side-effects, and file modifications remain owned strictly by deterministic code. Jev output cannot increase execution authority or grant transition permission (`RECOMMEND` never becomes `TRANSITION` without explicit deterministic user authorization).
2. **Minimal Query Planning:**
   Never call `Choice` when there are $\le 1$ legal candidate actions. Do not invoke unconsumed primitives.
3. **Correct Primitives:**
   Ordered degrees (complexity, reasoning effort) must use `Score`. Binary probabilities must use `Noul`. Mutually exclusive selections must use `Choice`.
4. **Dimension-Aware Uncertainty:**
   Uncertainty is evaluated per dimension; independent judgments are never collapsed into a single arbitrary confidence threshold.
5. **Fail-Closed and Graceful Degradation:**
   If TypeSafe is unconfigured, offline, or low-confidence, execution falls back cleanly to deterministic baselines without workflow blockage or safety degradation.

---

## 2. Eight-Stage Execution Pipeline

Every Skill integrating Jev follows this 8-stage sequence:

```text
1. Collect deterministic facts
       ↓
2. Construct minimal state
       ↓
3. Choose only necessary primitives
       ↓
4. Make Jev request
       ↓
5. Retain raw probabilities & confidence
       ↓
6. Apply explicit deterministic policy
       ↓
7. Validate result against legal & capability bounds
       ↓
8. Fall back safely
```

### Stage 1: Collect Deterministic Facts
Inspect files, Git status, host models, and tickets in Python code. Hard bounds (e.g. unknown tickets, multiple active efforts, stale or dirty review) trigger fail-closed halts before any Jev invocation.

### Stage 2: Construct Minimal State
Token-efficient, sanitized dictionary:
- Strip and cap length of user request.
- Redact obvious API keys, tokens, or credentials via regex.
- Omit repository source code, whole directories, and raw Git diffs.

### Stage 3: Choose Only Necessary Primitives
- If legal candidate actions $\le 1$: omit `Choice(next_action)` entirely.
- If semantic ambiguity is plausible: query `Noul(has_material_ambiguity)`.
- If architectural complexity is possible: query `Noul(needs_deep_reasoning_escalation)`.
- For task profiling: query `Score(task_complexity)` and `Score(reasoning_need)`.

### Stage 4: Make Jev Request
Invoke `ts_client.system_one(state=compact_state, questions=questions)` with graceful exception handling.

### Stage 5: Retain Raw Probabilities & Confidence
Store raw outputs: `execution_intent_probability`, `ambiguity_probability`, `escalation_probability`, `complexity_score`, `complexity_confidence`, `reasoning_score`, `reasoning_confidence`.

### Stage 6: Apply Explicit Deterministic Policy
- Calibrated thresholds from `JevPolicy`.
- Execution intent annotations do NOT change status to `TRANSITION`.
- Cost sensitivity selects cost-effective candidate within required tier, never downgrades capability.
- Precedence for effort: Explicit user request > confirmed profile policy > Jev reasoning need > host capability bounds.

### Stage 7: Validate Result Against Legal/Capability Bounds
- `selected_model` must belong to `valid_candidates`.
- `selected_action` must belong to `allowed_actions`.
- If invalid, defense-in-depth rejects the answer and restores the explicit fallback.

### Stage 8: Fall Back Safely
If Jev is disabled, offline, or returns low confidence, the workflow seamlessly uses `fallback_action` or `active_model`.

---

## 3. Skill Responsibilities & Terminology

| Skill | Hardened Boundary | Terminology |
| --- | --- | --- |
| `project-init` | Onboards TypeSafe skill (official `npx skills add` or global reuse), verifies SDK runtime, checks key without echoing. | **Jev ecosystem onboarding** |
| `ask-light` | Evaluates material ambiguity and candidate preference across $>1$ legal actions. Intent calibration never creates authority. | **Bounded Jev semantic workflow judgments** |
| `agent-config` | Profiles task complexity and reasoning need using `Score`; maps to host-evidenced candidates and effort. | **Jev semantic task profiling** |
