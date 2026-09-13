# GitHub + Cloudflare deployment

Prerequisites: Node 22.13+ (Node SQLite is used by tests), npm, GitHub CLI or equivalent authorized API, and the generated project's pinned Wrangler. Check `gh auth status` and `npx wrangler whoami` without printing tokens. Use the user's selected account/project; if multiple accounts are available ask for the target. Do not create paid resources or broaden account permissions as a fallback.

## Initial deployment

1. Create/fill the project, `npm ci`, `npm run build`, `npm test`. Inspect `dist/` and referenced assets. It is a protected group website, not a public static export.
2. Create or reuse a private GitHub repository for this project's code. Preserve `.gitignore`; never add local secrets. For fictional demos the explicitly labelled synthetic trip can be checked in. For real trip data apply the destination authorization described in [update-and-export.md](update-and-export.md).
3. Create scoped resources, using actual names: `npx wrangler d1 create <database-name>` and `npx wrangler pages project create <project-name> --production-branch main`. Check existing resources before creating duplicates. Preserve the returned database ID in the project config; it is an identifier, not an API credential.
4. Create `wrangler.jsonc` with the actual project name, a supported pinned `compatibility_date`, `pages_build_output_dir: "./dist"`, and `d1_databases: [{binding:"DB",database_name:"...",database_id:"...",migrations_dir:"migrations"}]`. Set `vars.TRIP_ID` to the existing data ID. Do not include credentials.
5. Run `npx wrangler d1 migrations apply <database-name> --remote`. The initial migration adds only the two scoped state/receipt tables. Review later migrations before applying; never reset an existing live database to update an itinerary.
6. Generate a random group access code and an independent session secret using a cryptographic RNG. Store only the access code SHA-256 hash as `ACCESS_CODE_HASH`, plus `SESSION_SECRET`, through `npx wrangler pages secret bulk <ignored-secret-json-file> --project-name <project-name>`. Local files containing credentials must be mode 0600 and ignored; never echo their contents. Keep the group access code in a separate protected local handoff file. Secrets must be set before serving the trip.
7. From the project root deploy using `npx wrangler pages deploy dist --project-name <project-name> --branch main`. Functions are compiled from the adjacent `functions/` directory and import the project's `server/` modules. Verify the deployment output reports Functions compilation. A bare upload of dist to a static host would omit protection and is not supported.
8. Test the actual URL: unauthenticated HTML/JSON/PDF redirect to login and API returns 401; wrong group returns 403; two separately authenticated cookie sessions share state. Test concurrent writes and retry the exact same mutation. Inspect mobile UI and expense/ticket/task interactions. Deliver URL, code-repository link and a secure local access-code handoff.

GitHub source plus Wrangler deployment is the baseline. GitHub auto-build integration is optional and requires a deliberate source for authorized trip data and secrets; do not advertise continuous deployment until configured and observed.

## Local integration testing

Use ignored `.dev.vars` with synthetic-only `ACCESS_CODE_HASH` and `SESSION_SECRET`, the matching `TRIP_ID`, and the same D1 binding. Run `npx wrangler d1 migrations apply <database-name> --local`, build, then `npm run preview`. Use the actual printed loopback URL. Local Wrangler serves the same Functions with local D1; it does not prove remote D1. Retain no temporary access credential in the Skill itself.

## Subsequent updates

Preserve cloud project, D1 ID, trip ID, group secrets and runtime rows. Apply a reviewed source update, rebuild and deploy from the same root. Users reload to see a new itinerary deployment; runtime writes continue through D1 without a deployment. Run changed-feature checks plus protected route smoke. On failure, keep the last verified production version available and report the exact stage; do not recreate the database.

Official references: [Pages Functions bindings](https://developers.cloudflare.com/pages/functions/bindings/), [Wrangler configuration](https://developers.cloudflare.com/pages/functions/wrangler-configuration/), [D1 migrations](https://developers.cloudflare.com/d1/reference/migrations/).
