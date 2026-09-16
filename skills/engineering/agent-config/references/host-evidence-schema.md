# Host evidence schema

Supply a current, structured observation from the host runtime rather than a remembered inventory.
This represents the output of Companion `inspect_host` and conforms strictly to `host-capabilities.schema.json`.

```json
{
  "host_id": "opaque-current-host",
  "adapter_id": "host-adapter-id",
  "workspace": "/path/to/project",
  "observed_at": "2026-08-24T00:00:00Z",
  "platform": "darwin-arm64",
  "available_models": [
    {
      "id": "model-alpha",
      "label": "Model Alpha",
      "state": "available",
      "features": ["tools", "chat"],
      "evidence": {
        "kind": "host-runtime",
        "locator": "host runtime model registry",
        "observed_at": "2026-08-24T00:00:00Z"
      }
    },
    {
      "id": "model-beta",
      "label": "Model Beta",
      "state": "available",
      "features": ["tools", "reasoning"],
      "evidence": {
        "kind": "host-runtime",
        "locator": "host runtime model registry",
        "observed_at": "2026-08-24T00:00:00Z"
      }
    },
    {
      "id": "model-gamma",
      "label": "Model Gamma",
      "state": "available",
      "features": ["tools", "reasoning"],
      "evidence": {
        "kind": "host-runtime",
        "locator": "host runtime model registry",
        "observed_at": "2026-08-24T00:00:00Z"
      }
    }
  ],
  "supported_effort_values": ["low", "medium", "high"],
  "default_effort_value": "medium",
  "capabilities": {
    "model_selection": {
      "state": "available",
      "scopes": ["current-session", "new-session", "per-agent"],
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
    "threads": {
      "state": "available",
      "evidence": {
        "kind": "host-runtime",
        "locator": "fresh session context tool",
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
    "concurrency": {
      "state": "available",
      "max_concurrency": 4,
      "evidence": {
        "kind": "host-runtime",
        "locator": "host pool limit",
        "observed_at": "2026-08-24T00:00:00Z"
      }
    },
    "reasoning": {
      "state": "available",
      "evidence": {
        "kind": "host-runtime",
        "locator": "effort parameter / configuration",
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
    "configuration_mutation": {
      "state": "available",
      "supports_native_files": true,
      "supports_session_mutation": false,
      "evidence": {
        "kind": "host-config",
        "locator": "host config file"
      }
    }
  }
}
```

## Claim rules

- `state` is exactly `available`, `unavailable`, or `unknown`.
- An `available` or `unavailable` claim has evidence from the current Host:
  `kind`, `locator`, and optional `observed_at`.
- **Verified evidence sources only:** `kind` must strictly be a verified evidence source:
  `host-runtime`, `host-config`, `host-schema`, `adapter-probe`, or `user-confirmed`.
  `host-runtime` is the preferred kind for a model, reasoning, or scheduling capability.
- **Elimination of `fallback-default`:** Synthetic or guessed evidence kinds (including
  legacy `fallback-default`, `fallback`, or `default`) are strictly prohibited.
  Unobserved capabilities must be recorded as `state: "unknown"` with no fabricated evidence.
- `available_models` lists the factual inventory of models verified from the host runtime or config.
  Each entry includes `id`, `state`, optional `label`, `features`, and `evidence`.
- **Strict separation of availability from tier mapping:** Host evidence records ONLY
  what models and capabilities are available from the host runtime. It does not
  record intelligence rankings, tier assignments, or capability scores. Tier assignments
  are defined exclusively in user-confirmed profiles (see `profile-schema.md`).
- **No intelligence ranking fields:** Models record presence only (`id`, `state`, `evidence`).
  Fields attempting to rank models (such as legacy `routing_rank`) are prohibited.
  Automated guessing of model intelligence is forbidden.
- `supported_effort_values` lists the exact discrete strings supported by the host runtime
  for reasoning effort (e.g. `["low", "medium", "high"]` or `["standard", "deep"]`).
  `default_effort_value` indicates the default when none is specified.
- `capabilities.reasoning` indicates whether the host supports reasoning effort configuration.
  When `reasoning` is `unavailable` or `unknown`, execution proceeds with default reasoning behavior.
- `capabilities.model_selection` records model switching support and its scopes:
  `current-session`, `new-session`, `per-agent`.
- `capabilities.subagents` records whether the host can launch isolated subagents.
- `capabilities.threads` records whether the host supports distinct session contexts.
- `capabilities.parallelism` records whether the host can execute workers simultaneously.
- `capabilities.concurrency` records maximum concurrency when supported (`max_concurrency: int >= 1`).
- `capabilities.per_agent_model_selection` records whether subagents can each be launched with independently assigned models.
- `capabilities.configuration_mutation` records whether host configuration files or session parameters can be mutated with user consent.
