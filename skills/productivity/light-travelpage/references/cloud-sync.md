# Shared group contract

One deployment serves one `TRIP_ID`; members share a high-entropy group access code and have equal edit access. This is not per-member roles or a multi-tenant service. Rotating the code hash invalidates existing cookies. Protect the entire site, including JSON, PDF and API routes, through `functions/_middleware.js`; `_routes.json` includes all paths. Never deploy this dist as an unprotected static site.

Authentication uses a random access code (at least 24 random bytes), its SHA-256 hash in `ACCESS_CODE_HASH`, and a separate random `SESSION_SECRET` (at least 32 bytes). Successful same-origin login issues a seven-day Secure, HttpOnly, SameSite=Strict cookie. API checks the session and configured trip ID again. Writes require same origin. Missing settings fail closed.

D1 owns travelers, bills, settings, tasks and ticket status. A trip-state row holds a monotonically increasing revision; writes carry `expectedRevision` plus `mutationId`. Conditional updates and durable request receipts execute in one D1 batch. Stale revisions return 409; identical retries are recognized without adding another bill; reusing an ID with different content fails. Conflict detection is conservatively trip-wide, so even unrelated simultaneous changes may require refresh and reapply. This protects correctness with a simple small-group model.

The client retains an uncertain request in sessionStorage before sending and retries that exact body. Do not automatically generate another request after an ambiguous response. After 409 refresh the shared state and reapply the intended change; never force overwrite. Do not close the browser session while an uncertain write remains; export confirmed state separately. Failed reads remain visibly failed, not an assertion of an empty database.

Refresh/focus and foreground polling (15 seconds) update views. Polling skips active inputs/dialogs; expense drafts are captured before rendering. Online-only writes are deliberate: offline input is not represented as synchronized. Backup export is a trip-labelled snapshot; restore requires explicit user confirmation and matching trip ID/revision, and uses the same validation/concurrency API.

Ticket PDFs remain protected deployed assets. D1 stores ticket completion status, not PDF blobs. New itinerary content is deployed as a site version; the UI should reload after a new trip-data version is published. For later task imports or member updates use the shared API/UI, not a database reset.

Test local D1 via Wrangler, then actual deployed independent sessions. Do not treat the local SQLite engine, mocked fetch or a unit test as proof of the remote deployment. Preserve integer-cent expense semantics from the template and verify allocation/conservation when altering its math.
