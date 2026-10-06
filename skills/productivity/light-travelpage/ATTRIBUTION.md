# Attribution and transformation

Source: https://github.com/do-tongxue/Travel-Plan-Page
Pinned revision: `ed869d21b19b7afb4a33fef97715c1091f087563`.
License: MIT, copyright 2026 Travel Template contributors; preserved in `assets/template/LICENSE`.

Reused source paths: `index.html`, `styles.css`, `ledger.css`, `app.js`, `overview-map.js`, `route-ui.js`, `site-navigation.js`, `ledger.js`, `trip-data.json`, `scripts/build-map.mjs`, and `assets/maps/templates/`. The former `ticket-pdf-preview.js` was removed; the unified ticket dialog now uses build-generated PNG previews. The original display modules, map assets and expense calculation originate upstream, with targeted changes. The current travel-handbook shell, `handbook.css`, `handbook.js`, chapter/date navigation and their design reference are Light-authored changes. `currencies.js` extracts the upstream `ledger.js` currency catalog so the browser and server share one supported set. No Natural Earth, geoBoundaries or OpenStreetMap boundary datasets are bundled; their upstream legacy paths are not used by this package.

Light-specific owned capability: concise generation/update/deployment workflow; protected single-group session access for all routes; D1 revision checking and durable idempotency receipts; shared ledger settings; observable failures and retry recovery; polling and draft preservation; scoped data validation; deterministic isolated build allowlist; recoverable trip updates; runtime backup/restore; desktop flight paging controls; source-backed geographic outline rendering from a project-supplied, attributed dataset; integrated tests and deployment evidence. The runtime adapter, server, validation/build/update tooling and Skill contract are newly authored for this transformation, not an unmodified upstream Skill repackage.

There is no runtime download or installation dependency on the upstream repository. Each generated project contains its complete runtime, map templates and license. Node/npm and Cloudflare tooling dependencies are declared by the generated package.
