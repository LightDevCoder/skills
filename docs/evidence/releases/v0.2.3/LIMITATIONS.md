# Release Limitations — v0.2.3

[中文记录](LIMITATIONS.zh-CN.md)

1. **Pi Coding Agent Harness MCP Requirement:** The Pi adapter in `agent-config` requires the `@earendil-works/pi-coding-agent` MCP extension to interact with companion MCP tools. Without it, `agent-config` runs in session-local plan-only fallback mode.
2. **Companion MCP Server Independence:** The optional companion MCP runtime is maintained in a separate repository (`LightDevCoder/agent-config`). The collection package functions fully in plan-only mode without the companion.
3. **Cloudflare Credentials for TravelPage:** Running remote sync for `light-travelpage` requires user-supplied Cloudflare API tokens and a configured D1 database; local previews function offline without credentials.
4. **TypeSafe Jev API Key Requirement & Policy Status:** Optional semantic acceleration in `ask-light`, `agent-config`, and `project-init` requires `TYPESAFE_API_KEY` and the `typesafe-sdk` package. When unavailable or unconfigured, all skills automatically fall back to deterministic baselines without functional disruption or security compromise. The asymmetric downgrade policy status is `PROVISIONAL` pending broader benchmark calibration. In non-interactive environments without `--jev`, `project-init` defaults safely to standard bootstrapping.
5. **Release Receipt Attestation Topology:** In accordance with the v0.2.3 release lifecycle, `RELEASE_MANIFEST.md` is committed inside the release tag, while full post-publication `RELEASE_RECEIPT.md` attestation is committed directly to `main` following tag publication, remote CI verification, and GitHub Release creation.
