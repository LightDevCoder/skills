# First-Party Skill Admission

[中文准入契约](SKILL_ADMISSION.zh-CN.md)

This document is the admission and evidence contract for a first-party Skill. It applies before a package is added to `skills/` and whenever a change alters the package's behavior, invocation boundary, dependencies, resources, or ownership claim.

## Reuse-before-invention decision

Assess the candidate in this order:

1. Use an upstream Skill directly when it already solves the need.
2. Configure or adapt it at the boundary.
3. Add a local Profile or internal Layer when that preserves the upstream boundary.
4. Create a wrapper only when necessary.
5. Put a necessary local modification in `skills-3rdParty`.
6. Create a new first-party Skill only for a genuinely missing capability.

Convenience, a different directory layout, or a desire for a local copy is not a reason to fork or admit an upstream Skill.

## Ownership gate

A candidate is eligible only when one of these is true:

- It is authored by the collection owner; or
- It is substantially transformed into a distinct, owned capability and includes `ATTRIBUTION.md` with the original repository and path, pinned revision or tag, applicable license or notice, and a precise transformation summary; or
- It is an **approved upstream Port** — the SPEC (§14/§16) explicitly authorizes it, it carries `ATTRIBUTION.md`, it has a Light-specific integration (handoff/naming/decoupling), and it has **no upstream runtime dependency**. (Approved PORT)

Reject an unmodified third-party or upstream copy that is not SPEC-authorized. Point users to the original upstream installation path instead. A modified third-party package that remains principally a third-party capability belongs in `skills-3rdParty` when not SPEC-authorized; it must satisfy that repository's provenance and fork-necessity rules.

**Approved Ports in this repository (SPEC §14):** `research`, `prototype`, `tdd`, `handoff`, `diagnosing-bugs`, `wizard`, `teach`, `wait-what`, `to-questionnaire`, `writing-for-agents`, `resolving-merge-conflicts` — each is a self-contained first-party package with `ATTRIBUTION.md` and no required install of `mattpocock/skills`. Light-specific changes are limited to runtime decoupling, naming, and handoff wiring; substantive redesign is not permitted.

> **Port ≠ arbitrary copying.** An architecture-level import authorization does not waive attribution, license/notice preservation, or the requirement that the Port be self-contained without upstream runtime installation. Arbitrary upstream snapshots without SPEC authorization remain ineligible.

## Admission questions

The reviewer must establish all of the following:

- **Independent value:** The Skill provides a reusable capability, not a one-off narration or a duplicate of an existing package.
- **Triggers:** Its use and non-use triggers are clear enough to distinguish it from nearby Skills.
- **Bounded responsibility:** Inputs, outputs, decision points, constraints, dependencies, and failure states are explicit and do not create a second orchestration hierarchy.
- **Invocation type:** It intentionally declares user-invoked or model-invoked behavior and obeys the invocation-direction rule.
- **Dynamic composition:** Where relevant, it can participate safely with other available Skills without requiring a canonical workflow membership.
- **Independence:** It does not rely on unavailable resources, undeclared host assumptions, or an uninstalled dependency — including an uninstalled upstream runtime for Ports.
- **Package quality:** `SKILL.md`, resources, scripts, templates, and assets are necessary, complete, linked correctly, and free of placeholder-only directories.

Membership in a canonical workflow, route table, or combination example is not an admission requirement. Validated combinations are useful examples and test assets only.

## Low-risk prompt-only fast track

A candidate may use the fast track only when every condition below is true:

- it is owner-authored and has no copied third-party code or assets;
- it is user-invoked only and both host metadata surfaces prohibit implicit invocation;
- its only product output is bounded text and it cannot run tools, access the network, read or write files, mutate state, handle credentials, or call another Skill;
- it has no runtime scripts, hooks, installers, binaries, external services, or dependencies; and
- it does not change migration, security, privacy, licensing, or other high-risk behavior.

Self-contained tests that only validate the static prompt and output contract do not count as runtime executable resources. They must still contain non-zero assertions and positive and negative fixtures.

The fast track requires structure and metadata validation, an isolated per-Skill copy/discovery check, deterministic contract tests, representative explicit-use and non-trigger observations, synchronized catalog/docs/changelog, and one fresh independent Evaluator. It does not require a separate Critic or Standards/Spec `code-review`. The Evaluator records the final `PASS`, `FAIL`, or `BLOCKED` in a compact admission record.

Any eligibility doubt, side effect, implicit trigger, runtime executable, external dependency, provenance issue, or confirmed finding that challenges eligibility or product behavior moves the candidate to the full evidence and `review-loop`/`project-review` path below. Documentation or test-label findings may be repaired within the fast track. The fast track cannot waive release or published-install verification.

## Required evidence

The candidate must have the following evidence before a final admission verdict. Record exact commands, environment facts, inputs, outputs, and limitations with the change or its acceptance record.

| Evidence area | Required demonstration | What it does not prove |
| --- | --- | --- |
| Structural | Package tree, `SKILL.md` metadata, internal links and resources validate with the applicable structure tooling. | Runtime behavior, fresh installation, or actual host discovery. |
| Installation and discovery | A fresh environment installs both the relevant scope and package form, then discovers the installed Skill without relying on the source checkout. | Correct behavior beyond discovery. |
| Behavioral | At least one success, one boundary, and one failure or missing-dependency scenario exercise the declared contract. An eligible fast-track Skill may use explicit-use and non-trigger observations because dependencies and runtime failure modes are prohibited. | Acceptance without independent review. |
| Invocation | A scenario confirms the declared invocation type and proves a user-invoked Skill does not silently or implicitly invoke another user-invoked Skill (an explicitly approved transition into an exact recommended target requires explicit user consent and verified host evidence). | Broader behavior not exercised by the scenario. |
| Review | For full path, `review-loop` (engine) with the applicable Profile, or `project-review` for project-level acceptance; for fast track, one fresh independent Evaluator — each using Producer evidence and a fresh Evaluator. | Permission to expand the frozen scope. |
| Attribution | Original or transformed ownership, source, revision, notice or license, and local transformation are inspectable where applicable; Ports carry `ATTRIBUTION.md` and no upstream runtime requirement. | That an unmodified copy became first-party. |
| Executable scripts, when present | Focused automated tests, negative tests, adversarial or mutation fixtures where appropriate, and `code-review` evidence. The test command must fail when assertions are absent or the fixture is a no-op. | That a passing static validator covers script behavior. |

Static, inferred, simulated, or keyword-only checks must be labeled by their actual evidence class. They must never be reported as runtime proof.

## Final decision

The reviewer may admit only a package that:

1. passes the ownership gate and all applicable admission questions;
2. supplies the required evidence with accurate labels;
3. passes either the prompt-only fast-track independent verdict or the applicable full `review-loop`/`project-review` final acceptance; and
4. completes the documentation and catalog updates required by [maintenance](MAINTENANCE.md).

Only a final `PASS` may enter the first-party collection. `FAIL` and `BLOCKED` results remain outside the catalog and must state the unmet evidence or authority. Admission does not waive release, installation-command verification, or Program-level acceptance gates.
