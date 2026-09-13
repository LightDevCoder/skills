---
name: light-travelpage
description: Generate or update a mobile travel page from supplied itinerary and booking materials, with shared expenses, tasks and ticket status deployed through GitHub and Cloudflare Pages/D1. Use for travel webpage creation or maintenance, not ordinary travel questions or booking purchases.
---

# Light-TravelPage

Turn travel materials into a maintained page for a travel group. This is a model-invoked capability. The default delivery uses GitHub for code and Cloudflare Pages, Functions and D1 for the website and shared state. Local preview is a development step.

## Prepare

Read supplied materials and any existing trip once. Extract confirmed itinerary, dates, places, bookings, tickets and explicit tasks; collect actual conflicts. Honor choices already made. Ask only questions needed to resolve a material ambiguity; leave unknown facts visibly pending. Do not invent bookings, coordinates or travel advice to fill the template.

Use [data-contract.md](references/data-contract.md) when preparing or validating data. Keep a small private source index for conflicting or easily misread dates, times, locations and booking details; do not publish raw documents, extraction notes or local paths.

## Generate or update

- **New page:** run `node <skill>/scripts/create.mjs <new-project-directory>`, then fill its `trip-data.json` and explicitly supplied ticket assets. Retain the supplied visual template unless the user requests a redesign. Enable modules matching the requested content.
- **Existing page:** read its current data and runtime/deployment settings first. Prepare a complete next data file preserving the trip ID, unchanged entity IDs, existing map selection and unrelated user edits. Apply it with `node <skill>/scripts/update.mjs <project-directory> <next-trip.json>`. See [update-and-export.md](references/update-and-export.md) for backup and publication boundaries. Changes to source data do not reset shared runtime state.

Run `npm ci`, `npm run build` and `npm test` in the generated project. Fix invalid facts/references or report the precise unresolved input; do not weaken the validator to produce a green result. Dates may remain null in an explicitly undated draft. Explain that maps are schematic; use place navigation links for actual navigation. Retain the builder's chosen template for existing regions.

## Share and deploy

Read [cloud-sync.md](references/cloud-sync.md) for the single-group access and shared-state contract, then follow [deployment.md](references/deployment.md). Reuse existing authorized GitHub/Cloudflare login and scoped resources. Deployment authorization does not permit unrelated account changes. When a login or an essential deployment choice is unavailable, complete the local package and report that exact remaining step; do not call localhost a deployed page.

Private material belongs only in the user's authorized trip and hosting destination. The generated Git ignore excludes trip data and tickets by default; publish them to a code repository only when that destination is explicitly authorized for those materials. Deploy only `dist/` with the protected Functions. Group access codes and session secrets are generated securely and passed through local secret tooling, never embedded in the page or committed. Preserve [ATTRIBUTION.md](ATTRIBUTION.md) and the template license when distributing reused assets.

## Verify and deliver

Verify the actual hosted URL, authentication on the page, JSON, ticket assets and API, then two independent sessions: shared member/settings/bill/task/ticket changes, conflict response, failed-save recovery and idempotent retry. In a narrow mobile viewport check the itinerary, ticket opening/fallback, navigation and saved expense after refresh. Polling must not erase a form draft. Run focused changed-feature tests during updates rather than repeat unrelated checks.

Deliver the live link, repository location, implemented sharing scope, concise verification evidence and any remaining limitations. Provide access material through a protected local file or the user's chosen secure channel. Do not claim deployment, independent review, or synchronization from a build log or mock alone. No booking, payment, new release/tag, or unrelated Skill invocation is implied.
