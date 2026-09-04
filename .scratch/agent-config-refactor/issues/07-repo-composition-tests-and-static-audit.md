# 07 — Repo Composition Tests & Static Reference Audit

**What to build:** Update repository-level composition and discovery tests to validate new agent-config contracts and integration boundaries, and conduct a static audit removing obsolete legacy patterns from active documentation and tests.

**Blocked by:** 04 — Four-Quadrant Behavior Fixtures & Unit Test Suite, 05 — Downstream implement & ask-light Migration, 06 — Repository Governance, Catalog & Workflow Documentation Sync

**Status:** resolved

- [x] `tests/test_composition.py` includes end-to-end composition assertions verifying `implement` opt-in, `ask-light` routing separation, `project-tickets` non-preemption, and review delegation handoffs.
- [x] `tests/test_collection_discovery.py` verifies `agent-config` discoverability, provider-neutrality, and absence of hardcoded vendor topology.
- [x] Static grep audit across `skills/`, `docs/`, `tests/`, `README*`, `CATALOG*` finds zero stale live occurrences of `multi-model-multi-agent`, `single-model-multi-agent`, `single-model-single-agent`, mandatory "one named Merger", or mandatory "execution waves / ownership matrix".
- [x] Any occurrences in historical release receipts or archived scratch files are properly audited and left intact as immutable history.
- [x] `python3 -m unittest discover -s tests` passes completely with zero errors.

## Comments

Source: .scratch/agent-config-refactor/spec.md. §26, §35, §36, §40, §41.

## Answer

Updated `tests/test_composition.py` to assert agent-config 4 modes, optional implement opt-in, project-tickets boundaries (`needs-project-tickets`), and review composition handoffs. Ran static reference audit across live skills, docs, tests, README, and CATALOG, verifying that all stale mandatory roles, waves, and legacy route names are fully cleaned up from live code and documentation. 28 repository tests passing.
