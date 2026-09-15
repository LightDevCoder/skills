# Light-TravelPage main update — 2026-09-15

Source: Light-TravelPage authoring candidate at `64fe84b`; existing admitted package and attribution preserved. No new package, invocation, global configuration, version tag or release.

Scope: bilingual display, authored translation fallback, flight/stay cards, shared ticket actions, region-aware external maps, fine serif typography, and navigation menu anchored to its trigger. Destination data stays outside the blank template.

Evidence: producer template and demo each passed 34 Node tests; build and byte comparison of shared runtime files passed. Standards/Spec review converged with no remaining findings at `7ce78af`; later menu positioning was browser-checked on desktop and 390px width. Integration checks: 6 collection tests, 11 composition tests and 85 ask-light tests passed.

Demo source `eae2bd2` pushed to main; Cloudflare deployment `91f6254f` completed with Functions. Canonical production URL passed unauthenticated HTML/JSON/PDF redirects and API 401, authenticated cards/translations/assets, byte comparison of four changed runtime resources, PDF access and shared-state GET. Existing secrets and database rows were preserved; smoke checks made no state mutations.

Google British Museum and Yandex Bolshoi target results were observed. Kakao/Apple precise results and native mobile App launching remain unverified. This main update does not claim complete cross-provider/mobile acceptance or a tagged release. Published source installation verification follows after push.

Published verification: `f466ff9` pushed to origin/main. From a fresh isolated project, `npx --yes skills add LightDevCoder/skills --skill light-travelpage --agent codex --yes --copy` succeeded. All 55 installed files match the candidate byte for byte. No global installation was modified. Integration review found only the missing Chinese catalog update; repaired and re-reviewed to `Findings: []`.
