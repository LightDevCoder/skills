# Travel handbook UI maintenance acceptance

- Charter revision: travel-handbook-2026-10-03-v2
- Profile: software with agent-skill package checks
- Fixed point: 49e7cbe8be1b978bfbe5f22745b0c0dfefbb89a7
- Implementation scope: skills/productivity/light-travelpage/
- Review limit: 4 rounds; the user explicitly approved one additional final round on 2026-10-04. Prior three rounds remain preserved.

Approved source: user selected direction C and requested serif typography plus remote push on 2026-10-03. The C draft is at /Users/light/Documents/Codex/2026-10-03/ai-travel-mvp/outputs/design-demos/C.html; decision at outputs/direction-approved.md in that workspace. This maintenance target is the reusable Skill package; the separate local MVP is checked in its own workspace.

Acceptance criteria:
1. The generated sharing page uses the selected travel-handbook structure: paper palette, chapter navigation, daily reading page and adjacent source-derived pocket page; mobile stacks the pages.
2. Titles, chapter/content headings and large dates use a system serif stack. Forms, buttons and operational feedback use a readable UI font; body >=14px, secondary >=12px.
3. Enabled itinerary, flight/stay bookings, maps, driving, tasks, ledger and provided ticket materials remain reachable. Disabled modules stay absent; missing material stays pending.
4. Chapter/date switching, deep links and browser navigation preserve actual content, existing form drafts, local/shared state and language behavior.
5. Existing ticket image/PDF fallback, carousel, geographic map navigation and source/authentication boundaries remain intact; no AI or fabricated travel facts are added.
6. New runtime navigation has assertion-bearing success and boundary tests; template tests and generated-project build pass.
7. A freshly generated package renders in an actual browser; desktop and 390px layouts, chapter/date selection, material/ticket entry and both languages are observed.
8. Skill entry, design reference, attribution and affected collection maintenance docs agree with the template. Naming, invocation and unrelated contracts stay stable.
9. Standards and Spec reviewers inspect the committed diff independently; a fresh evaluator inspects this baseline and evidence before promotion.

Remote push is separately verified after acceptance. No new tag/release or production deployment is authorized by this request. Third-party map App opening is outside this UI maintenance check.
