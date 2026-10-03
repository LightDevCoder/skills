# Producer evidence — Round 3

- Charter revision: travel-handbook-2026-10-03-v1
- Profile: software with agent-skill package checks
- Scope: complete light-travelpage package, affected collection docs and maintenance evidence
- Package invocation: model-invoked; implicit invocation permitted in agents/openai.yaml
- Runtime package identity: package-hashes-round3.json; committed implementation recorded by Round 3 specialist packet
- This record supplies Producer evidence; it is not final acceptance.

Each item has one primary evidence label. Commands, environment, inputs and limits are in context.md; original findings and repairs remain separate.

| ID | Evidence label | Run or observation; expected → observed | Artifact | Validates |
| --- | --- | --- | --- | --- |
| E-001 | source | User selected C, requested serif typography and remote push; exact source retained | charter.md and linked direction-approved.md/C.html | AC1, AC2, AC8 |
| E-002 | structural | quick_validate.py on the complete package; valid entry → Skill is valid. Collection discovery/composition: 15 pass. All 61 package files and synthetic input hashes are explicit | skill-validation.txt, collection-tests.txt, package-hashes-round3.json, input-hashes.json | AC8 |
| E-003 | installation | Fresh isolated project-local Skills CLI 1.7.0 copy with only --skill light-travelpage --agent codex; whole package equality and discovery expected → 61/61 hashes equal, list shows only intended local package | local-install-round3.txt, local-discovery-round3.txt, local-install-equality-round3.json | Package installation/discovery |
| E-004 | behavioral | Run installed create.mjs into a fresh destination, then repeat same destination and omit argument; complete copy / safe refusal expected → source template byte equality, nonzero refusal, existing hashes unchanged, usage error | installed-generator-scenarios.json | Package success/boundary/failure |
| E-005 | behavioral | npm test --prefix work/skill-generated; success, disabled modules, escaped materials, deep anchors, actual-HTML map examples, refreshed real-ledger pocket and retained forms expected → 48 tests pass | template-tests-round3.txt | AC3, AC4, AC5, AC6 |
| E-006 | runtime | npm run build --prefix work/skill-generated with preserved D1-configured generated-input.json; complete build expected → dist built successfully; map disabled by input. Ticket fixture build retained original PDF/generated PNG | template-build-round3.txt, context.md, ticket-input.json | AC5, AC6 |
| E-007 | manual | Actual IAB desktop and 390px layouts, both languages, dates/chapters, skip/bookings, ledger draft, ticket dialog and original PDF; expected layout and state → observed and measured. Latest task body/menu 14px/13px | observations.md, context.md, desktop.jpg, mobile.jpg, ledger-mobile.jpg, ticket.jpg, task-menu-mobile.jpg | AC1, AC2, AC3, AC4, AC5, AC7 |
| E-008 | review | Independent Standards and Spec inspect fixed baseline candidate; original issues retained and repaired → Round 2 Standards clean, Spec retained old closed IDs and added F-005/F-006 | round1-findings.json, round2-findings.json, repair-evidence.md; Round 3 reports follow | AC9 |
| E-009 | invocation | User's current request names light-travelpage maintenance; contract applied to authorized package scope. Ordinary travel questions/purchases are outside its declared trigger; no unrelated user-invoked Skill is called by this package. Fresh Evaluator independently assesses these cases | SKILL.md, agents/openai.yaml, direction-approved.md, final Evaluator record | Package invocation/composition |

Installation is local source evidence until a separately observed published-source install succeeds. CLI discovery is distinct from current Codex session reload. Synthetic DOM adapters do not establish remote D1 behavior. Actual browser screenshot/DOM evidence does not establish physical-phone touch or third-party map App behavior. No production deployment is in this Charter.
