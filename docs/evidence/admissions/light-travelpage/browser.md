# Native Chrome mobile observation

Date: 2026-09-13. Tool: mcp__cua_repl native Chrome UI, not Playwright/DOM simulation. Chrome DevTools responsive mode: width 390, height 844, fit-to-window. Target: `http://127.0.0.1:4175`, Wrangler serving the same final dist whose runtime files were verified against the hosted deployment by remote-check.mjs. Local D1, fictional credentials and data only.

Observed via native accessibility tree and screenshots in the task tool transcript:

1. Entered local test group code in `/login`; actual form submission opened the travel page. This verifies the same-origin Referrer-Policy login repair.
2. Mobile homepage showed title, shared controls, schematic map and day cards without visible horizontal overflow. Expanded Day 1 to reveal activities, map buttons and ticket status.
3. Ticket dialog opened. Inline PDF showed Chrome's blocked-page state in mobile emulation. The visible fallback link opened `assets/tickets/demo.pdf` in a new tab; Chrome reported a one-page PDF fully loaded. The fictional demo PDF label was partially clipped by its page width; it is not a real ticket.
4. Opened ledger, added `测试同行甲`; member immediately appeared in the dialog. Closed it, entered 23.45 CNY, selected payer and saved. UI displayed `账单已保存`, `1 笔账单`, `¥23.45`.
5. Reloaded the page with Cmd+R. Member and exactly one 23.45 bill were still visible in the actual accessibility tree.

Limitations: no physical mobile device; this is local runtime browser evidence, not a second hosted-browser session. No screenshots are exported to a file; screenshots and AX observations are in the tool transcript. The attempt to enter a new draft for polling was interrupted by `The Mac is locked and automatic unlock is paused because physical input was detected`. Draft polling and external map navigation were not completed in actual browser. They remain outstanding; automated draft tests are separately labelled simulation.

## Resumed observation after user requested continuation

The Mac was unlocked and the same 390×844 Chrome viewport resumed. A new draft `31.50` was entered and focus moved to a heading. A separate local HTTP session then added member `轮询测试乙`. After more than one 15-second polling interval, screenshots and AX text showed `2 人`, the new member, a newer `已同步` time, and the amount field still `31.50`. This exercises actual browser re-render under a changed shared snapshot, not only a no-change poll.

Returned through the mobile travel menu to itinerary, expanded Day 1, tapped West Lake, and used `用 Google Maps 打开 ↗`. A new tab loaded Google Maps with title `西湖 - Google Maps`, search results including Xihu in Hangzhou and the visible map. External navigation is confirmed. The prior lock-related draft/navigation gaps are now resolved. The PDF inline-emulation limitation remains accurately recorded; fallback worked.

These observations used the final dist prior to the narrowly scoped pending-generation guard added at `6bee388`; that guard changes rejected-save recovery only, not these observed rendering/navigation paths. Its regression proof is separately supplied by independent recovery reviewers.
