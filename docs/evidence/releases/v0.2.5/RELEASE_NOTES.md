# v0.2.5 — Routing, ticket IDs, and release checks

[中文发布说明](RELEASE_NOTES.zh-CN.md) · [Release Manifest](RELEASE_MANIFEST.md) · [Release Receipt](RELEASE_RECEIPT.md)

v0.2.5 fixes workflow routes that could appear ready when their evidence was missing or out of date. The collection remains at 36 Skills.

---

## What changed

### 1. Routes stop on uncertain state

`agent-config` needs a current Host record and a matching confirmed Profile before recommending execution. `ask-light --mode semantic` now applies the same project constraints and checks its final recommendation. Claimed tickets and review evidence of unknown freshness no longer produce a ready-to-run route.

### 2. Ticket producers share one sequence

`decision-map`, `project-spec`, and `project-tickets` number new tickets after the highest existing ID. A project with duplicate legacy IDs gets a migration instruction and no route until those IDs are resolved. Existing tickets are not rewritten automatically.

### 3. Skill handoffs use current contracts

`project-init` performs general bootstrap before `manuscript-ops` creates manuscript-specific state. Manuscript dependency checks use current runtime interfaces. `code-review` keeps separate Standards and Spec axes and returns Findings that `review-loop` can consume directly.

### 4. Validation covers the generated result

The travel-page generator and first sync enforce the same todo rules. CI runs the full Python suite, Node tests, and validation and build of a generated trip. Release checks stop when the remote tag or GitHub Release cannot be verified.

---

## Upgrade notes

Projects with duplicate ticket IDs need an explicit migration before routing resumes. If Host or Profile evidence is absent or stale, refresh and confirm it before requesting an execution plan. No packages were added or removed.

## Installation

For a fixed release snapshot:

```bash
npx skills add LightDevCoder/skills#v0.2.5
```

The unqualified command follows the current `main` branch:

```bash
npx skills add LightDevCoder/skills
```

## Verification

The annotated tag points to [`ecafc2f`](https://github.com/LightDevCoder/skills/commit/ecafc2f3da3ab25a62e7a31285658fac5a50b47f), which passed [candidate CI](https://github.com/LightDevCoder/skills/actions/runs/35858468222). Pinned and latest fresh installs each found all 36 Skills; all 367 installed package files matched the release snapshot byte for byte. The [release receipt](RELEASE_RECEIPT.md) records the commands and identities. The sibling `agent-config` MCP was checked for contract compatibility and is outside this release.
