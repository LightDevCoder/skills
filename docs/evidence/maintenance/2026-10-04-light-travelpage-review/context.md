# Exact producer evidence context

Date: 2026-10-04. Fixed point: `49e7cbe8be1b978bfbe5f22745b0c0dfefbb89a7`.
Round 1 committed candidate: `e1f1f4b84088f5d8bfd6b5f15431d2b81a403191`.
Round 2 package identity: all package files are listed in [package-hashes.json](package-hashes.json); the committed candidate is identified in the subsequent specialist/evaluator record. This context supplements the abbreviated historical commands in observations.md.

Host: macOS; Node.js v26.7.0, npm 12.2.0, Python 3.9.6. Browser: Codex In-app Browser, adapter ID 2. The browser adapter does not expose an engine version; no engine-version claim is made. Actual DOM and screenshots were observed with the CUA browser adapter.

Working directory for commands below: `/Users/light/Documents/Codex/2026-10-03/ai-travel-mvp`.
Repository worktree: `work/skills-ui`, branch `codex/travel-handbook-ui`.
Package: `work/skills-ui/skills/productivity/light-travelpage`.

## Structural and script evidence

Executed commands:

```sh
node work/skills-ui/skills/productivity/light-travelpage/scripts/create.mjs work/skill-generated
npm test --prefix work/skill-generated
npm run build --prefix work/skill-generated
python3 /Users/light/.codex/skills/.system/skill-creator/scripts/quick_validate.py work/skills-ui/skills/productivity/light-travelpage
python3 -m pytest -q work/skills-ui/tests/test_collection_discovery.py work/skills-ui/tests/test_composition.py
```

The generated project contains an independent copy of runtime source. Its dependency directory was moved out of the package into the generated project after installation; no node_modules directory is included in the package. Round 2 source repairs were copied to the generated project before tests/build. Runtime source equality is checked in the final evidence receipt. Existing package dependency versions remain unchanged.

- Round 1: 44 template tests passed; raw [receipt](template-tests.txt).
- Round 2: 46 assertion-bearing tests passed; raw [receipt](template-tests-round2.txt). Includes current-chapter skip, disabled ledger hash and actual-HTML demo map insertion regressions.
- Latest Round 2 build: succeeded; raw [receipt](template-build-round2.txt).
- Collection: 15 tests passed; [receipt](collection-tests.txt).
- Skill metadata/entry: valid; [receipt](skill-validation.txt).

Inputs are preserved as [generated-input.json](generated-input.json) and [ticket-input.json](ticket-input.json), with SHA-256 in [input-hashes.json](input-hashes.json). They are explicitly synthetic examples. Ticket fixture was created with the existing `tests/prepare-build-fixture.mjs` in `work/skill-ticket`, then `npm run build --prefix work/skill-ticket`; the validated source contains fixture.pdf and build produced fixture.png. Original PDF plus loaded PNG were observed in the real browser. Poppler warned about fontconfig cache writes but exited successfully.

## Behavioral/browser evidence

Generated preview: `python3 -m http.server 4176 --bind 127.0.0.1`, working directory `work/skill-generated/dist`.
Ticket preview: same command on port 4177, working directory `work/skill-ticket/dist`.
Build outputs alone are overridden for local isolated preview by reading `dist/trip-data.json`, setting `config.persistence = {"mode":"local"}`, and saving that file. Source inputs retain their D1 configuration. This is not remote D1 evidence.

Round 1 desktop 1440×900 and English 390×844 observations are in [observations.md](observations.md), with [desktop](desktop.jpg), [mobile](mobile.jpg), [ticket](ticket.jpg). Date 08, deep stay link, authored missing translations, ledger draft retention, original PDF and image load were observed.

Round 2:
- English ledger at 390×844: clientWidth/scrollWidth both 390. Category labels 14px; live feedback 12px. Three-column mobile category layout displays complete English labels. [Screenshot](ledger-mobile.jpg).
- At 1280px, amount 128 and note “修复后章节草稿” were entered into the existing ledger form. Bookings → Skip to content reached #main with data-chapter=bookings and stays visible. Returning to Ledger preserved both draft fields. A later intentional reload cleared the unsaved test draft.
- Runtime node preservation and disabled-module boundaries are also asserted by template tests; real browser observations are separate from synthetic DOM tests.
- A browser-only flight fixture in ticket preview dist exercised two journeys. Flight codes were 29px with dark ink, times 12px, countdown 27px; next control changed 1/2 to 2/2. These synthetic flight entries were added only after the validated ticket build and are not supplied booking facts or the build-input identity.

No physical-phone touch, deployed Cloudflare, remote D1 synchronization or third-party map App result is claimed. The local preview mode does not represent shared/authenticated production behavior. Installation and review evidence are separately labeled in their receipts.
