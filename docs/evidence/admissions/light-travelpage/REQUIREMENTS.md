# Light-TravelPage acceptance baseline

Revision: 1. Approved source: user requests in this task, 2026-09-12.

Create an installable, substantially transformed first-party Skill named Light-TravelPage (package id `light-travelpage`) for the Light Skills repository. Preserve the upstream mobile travel template and its MIT attribution at commit ed869d21b19b7afb4a33fef97715c1091f087563. No unsolicited visual redesign or replacement of travel content with invented facts.

1. Generate from supplied travel materials; update an existing trip without changing its identity, unrelated records, or browser/cloud runtime data. Ask only unresolved material questions. Unknown facts remain visibly pending.
2. Default delivery is GitHub plus Cloudflare Pages, Functions, and D1. Local preview is development evidence, not the final hosted outcome. Use fictional data for this task's reusable demonstration.
3. Group members share travelers, bills, ledger settings, todos and ticket status. Changes become visible through refresh/focus and bounded foreground polling. Saving, disconnected, failed and conflict states are visible. Never silently overwrite a concurrent change or duplicate a retried bill. Preserve edits during polling and failed saves.
4. The starter targets one travel group per deployment. A high-entropy group access code grants that group's members equal edit access via a signed HttpOnly cookie. All trip APIs, JSON and ticket assets require authentication. API rejects other trip IDs. No public ticket/booking data in GitHub or generated reusable fixtures. Per-member roles, SSO and separate groups within one deployment are outside this starter scope.
5. Validate calendar dates, day span/order, times/UTC offsets, record IDs/references and ticket assets. Include positive and negative tests. Map output is labelled schematic and selection is stable for unchanged regions during normal updates.
6. Build only declared runtime files and referenced trip assets into an isolated dist directory; private sources and notes are excluded. Export/import runtime backups with trip identity and explicit overwrite/conflict checks. Source updates retain recoverable versions.
7. Verify real mobile browser interactions, protected deployment routes and two independent session synchronization, concurrency, retry, and error recovery. Track evidence classes honestly; no live D1 claim from mocks.
8. Package has concise SKILL.md, metadata, linked references, necessary executable resources, pinned provenance, focused automated tests, isolated installation/discovery and independent forward-use observations, Standards/Spec code review, and a fresh Evaluator. Only after admission PASS copy into skills/ and synchronize affected catalog/docs/tests/changelog. Do not create a version tag or release.

Deployment credentials stay in existing local authentication stores or ignored local files, never in committed Skill files, logs or chat. Use a private demo repository and access-protected fictional demo deployment. Cloudflare resources are scoped to this project.
