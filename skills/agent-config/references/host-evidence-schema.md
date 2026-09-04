# Host evidence schema

Supply a current, structured observation rather than a remembered inventory.
This is a bounded input contract, not a claim that every Agent Host exposes
these fields.

```json
{
  "schema_version": "2",
  "host": {
    "id": "opaque-current-host",
    "observed_at": "2026-08-24T00:00:00Z"
  },
  "models": {
    "current": {
      "id": "opaque-model-id",
      "state": "available",
      "evidence": {
        "kind": "host-runtime",
        "locator": "current session model",
        "observed_at": "2026-08-24T00:00:00Z"
      }
    },
    "selectable": [
      {
        "id": "opaque-model-alpha",
        "state": "available",
        "evidence": {
          "kind": "host-runtime",
          "locator": "host model selector",
          "observed_at": "2026-08-24T00:00:00Z"
        }
      },
      {
        "id": "opaque-model-beta",
        "state": "available",
        "evidence": {
          "kind": "host-runtime",
          "locator": "host model selector",
          "observed_at": "2026-08-24T00:00:00Z"
        }
      },
      {
        "id": "opaque-model-gamma",
        "state": "available",
        "evidence": {
          "kind": "host-runtime",
          "locator": "host model selector",
          "observed_at": "2026-08-24T00:00:00Z"
        }
      }
    ]
  },
  "capabilities": {
    "model_selection": {
      "state": "available",
      "scope": ["current-session", "new-session", "per-agent"],
      "evidence": {
        "kind": "host-runtime",
        "locator": "cli --model switch and subagent config",
        "observed_at": "2026-08-24T00:00:00Z"
      }
    },
    "subagents": {
      "state": "available",
      "evidence": {
        "kind": "host-runtime",
        "locator": "task tool / subagent runner",
        "observed_at": "2026-08-24T00:00:00Z"
      }
    },
    "per_agent_model_selection": {
      "state": "available",
      "evidence": {
        "kind": "host-runtime",
        "locator": "subagent launch parameter subagent_model",
        "observed_at": "2026-08-24T00:00:00Z"
      }
    },
    "parallelism": {
      "state": "available",
      "evidence": {
        "kind": "host-runtime",
        "locator": "concurrent task execution",
        "observed_at": "2026-08-24T00:00:00Z"
      }
    },
    "reasoning_control": {
      "state": "available",
      "levels": ["low", "medium", "high"],
      "assignment_scope": ["current-session", "new-session", "per-agent"],
      "evidence": {
        "kind": "host-runtime",
        "locator": "effort parameter / configuration",
        "observed_at": "2026-08-24T00:00:00Z"
      }
    },
    "session_threads": {
      "state": "available",
      "evidence": {
        "kind": "host-runtime",
        "locator": "fresh session context tool",
        "observed_at": "2026-08-24T00:00:00Z"
      }
    },
    "worktrees": {
      "state": "unknown",
      "evidence": null
    },
    "concurrency_cap": {
      "state": "available",
      "limit": 4,
      "evidence": {
        "kind": "host-runtime",
        "locator": "host pool limit",
        "observed_at": "2026-08-24T00:00:00Z"
      }
    }
  },
  "adapter": {
    "identity": "optional-adapter-id",
    "version": "1.0.0",
    "project_config_support": "available",
    "evidence": {
      "kind": "host-runtime",
      "locator": "adapter manifest",
      "observed_at": "2026-08-24T00:00:00Z"
    }
  }
}
```

## Claim rules

- `state` is exactly `available`, `unavailable`, or `unknown`.
- An `available` or `unavailable` claim has evidence from the current Host:
  `kind`, `locator`, and `observed_at`. `host-runtime` is the preferred kind
  for a model, reasoning, or scheduling capability.
- `models.current` records the executable model of the active session.
- `models.selectable` records models that the Host can actively select or switch.
- **Strict separation of availability from tier mapping:** Host evidence records ONLY
  what models and capabilities are available from the host runtime. It does not
  record intelligence rankings, tier assignments, or capability scores. Tier assignments
  are defined exclusively in user-confirmed profiles (see `profile-schema.md`).
- **No intelligence ranking fields:** Models record presence only (`id`, `state`, `evidence`).
  Fields attempting to rank models (such as legacy `routing_rank`) are prohibited.
  Automated guessing of model intelligence is forbidden.
- `reasoning_control` records whether reasoning effort is tunable:
  - `levels` is an ordered list from lower effort to higher effort (e.g. `["low", "medium", "high"]` or `["standard", "deep"]`).
  - `assignment_scope` records where effort can be applied: `current-session`, `new-session`, or `per-agent`.
  - When `reasoning_control` is `unavailable` or `unknown`, execution proceeds with default reasoning behavior without returning `BOUNDARY`.
- `capabilities.model_selection` records model switching support and its scope:
  `current-session`, `new-session`, `per-agent`.
- `capabilities.per_agent_model_selection` records whether subagents can each be
  launched with independently assigned models.
- An executable model (`models.current` available) does not require or imply
  that `model_selection` or `per_agent_model_selection` is available.
- `unknown` has `evidence: null`; it is not an error and must not be filled
  from model memory, static heuristics, or unverified user assertion.
- A `concurrency_cap` is available only when `limit` is a positive integer and
  the evidence verifies that limit. Do not derive it from a count of models or
  documentation marketing numbers.
- `session_threads` means the Host can create a fresh execution context. It
  does not alone prove an independent Reviewer; reviewer independence also
  requires a distinct, fresh context and no implementation ownership.
- `worktrees` means the Host can create and use isolated worktrees for the
  task. A generic filesystem or source-control tool does not prove this claim.
- `adapter` records optional provider adapter metadata. If absent or unavailable,
  agent-config continues in `plan-only` mode without error.

## Backward compatibility (Schema v1 → v2)

Schema v1 evidence payloads (where `schema_version` is `"1"` or omitted, and
`routing_rank` or `reasoning_control.levels` are absent) are valid input:
- Missing or ignored `routing_rank` across selectable models normalizes to `tier routing unavailable`
  when no user profile exists, causing conservative fallback to `fixed-single-model` mode using `models.current`.
- Missing `reasoning_control` fields normalize to `state: unknown`, continuing with
  current/default host reasoning.
- Missing `adapter` field normalizes to `project_config_support: unavailable` (plan-only).
- No schema v1 input produces a parsing error or unhandled exception.

Reject a false inventory claim by normalizing it to `unknown` and recording
why: missing evidence, malformed evidence, stale evidence, contradictory
evidence, or a non-host source. Do not delete the rejected claim from the
evidence ledger.
