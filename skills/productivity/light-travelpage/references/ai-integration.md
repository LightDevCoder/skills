# Optional AI connection

Read this reference when the traveler chooses AI for a new page or asks to configure an existing AI page. Preserve choices and authorization already given. Enabling the generator is a local source change; provisioning a Tunnel, CPA server or remote deployment is a separate action.

## Generate and scope

```bash
node <skill>/scripts/create.mjs <new-project-directory>              # off
node <skill>/scripts/create.mjs <new-project-directory> --ai off     # explicit off
node <skill>/scripts/create.mjs <new-project-directory> --ai openai  # enabled
```

`ai-config.json` contains only `provider: off|openai`. The build adds the AI entry, dialog and client only for `openai`. Off builds contain no AI entry or client, and the protected AI handler returns 404 before accessing D1 or an upstream. Generation/build never calls the model. Editing `ai-config.json` followed by rebuilding changes an existing page's switch; source updates preserve it.

The enabled page keeps the complete handbook: flight/stay cards, itinerary, geographic maps, original tickets, ledger and task checks. Its assistant reads authored trip context and can add/update tasks, check existing ticket status, add ledger travelers and record expenses. Actions follow enabled modules. It cannot rewrite itinerary, bookings, maps or original attachments. It cannot purchase, pay, cancel or change merchant orders. The UI reports the exact confirmed actions separately from the model's prose.

All browser traffic stays on this page's origin: `/api/ai/<tripId>` and the existing `/api/trip/<tripId>`. The existing group session, same-origin check and trip identity protect both handlers. AI prepares a plan, validates it with `applyChanges`, durably caches the plan, then submits that exact plan to `handleTrip` with `expectedRevision` and `mutationId`. A stale revision returns 409. An identical retry reuses the plan and D1 mutation receipt instead of adding another expense. Reusing an ID for different content returns 409. Apply `0002_ai_requests.sql` through the same scoped D1 migration flow; it adds a table and does not reset state.

## Three connection topologies

| Topology | Server `OPENAI_BASE_URL` | Conditions |
| --- | --- | --- |
| Pages → existing local CPA through an authorized Tunnel | The actual Tunnel HTTPS origin, normally ending in `/v1` | CPA stays on the owner's computer. The computer, CPA and Tunnel must be running; expose only the authorized CPA route with its API authentication. A Tunnel changes inbound reachability, not the machine's outbound access to its upstream. |
| Pages → an existing overseas CPA | The verified HTTPS CPA origin and API prefix, normally `/v1` | Use the CPA's server API key and a model that it actually exposes. Hosting geography alone does not prove upstream connectivity or account permission. |
| Pages → OpenAI or another compatible provider | `https://api.openai.com/v1` for OpenAI; the provider's verified API base for another service | Use that provider's server API key, model ID and supported protocol. This adapter supports function calling, not every provider/model combination. |

For **local testing only**, Wrangler Functions may connect directly to the existing CPA at `http://127.0.0.1:8317/v1` when that is the owner's confirmed listener. Remote Pages cannot reach a computer's loopback address. Do not start a Tunnel or deploy a CPA to make a local test pass. Reuse the existing CPA without installing another copy, restarting it or repeating its account authorization.

The base must be an HTTP(S) API prefix, without embedded credentials, query parameters or a final `/chat/completions` or `/responses` path. An origin with no path becomes `/v1`; a supplied custom prefix is preserved. Set the following only on the server:

```dotenv
OPENAI_BASE_URL=http://127.0.0.1:8317/v1
OPENAI_API_KEY=<server API key for this CPA or provider>
OPENAI_MODEL=<model ID actually available on that service>
OPENAI_API_STYLE=chat-completions
```

Use `OPENAI_API_STYLE=responses` when the upstream and selected model support Responses tool calling. The default is `chat-completions`. Query the service's `/models` through authorized server tooling to select an available model; a listed ID is only discovery evidence, so test a real tool round trip too. The API key may be empty only for an explicitly verified private endpoint that requires no key. Never put the CPA's OAuth tokens or account login material in these settings.

Use ignored `.dev.vars` (mode 0600) for local Wrangler, alongside the existing group auth settings and matching `TRIP_ID`. Production uses Pages server variables/secrets; store `OPENAI_API_KEY` with the same local secret tooling described in [deployment.md](deployment.md). Keep keys, `.dev.vars`, `.env*`, raw source documents, extraction notes and local source paths out of the client, `dist/` and commits. The build copies an explicit asset list and a validated public switch. Keep deliberate protected trip/ticket publication within the original [deployment contract](deployment.md).

## API requirements and limits

Chat Completions requires `POST <base>/chat/completions` with `messages`, JSON-schema `tools` and assistant `tool_calls`; subsequent requests include `role: tool` and matching `tool_call_id`. A text-only chat endpoint cannot perform these actions. Responses requires `POST <base>/responses`, `function_call` output, matching `function_call_output` input, and preserved prior response items, including encrypted reasoning when provided. The adapter uses `store: false` and retains that continuation only on the server. Neither protocol name nor the provider's “OpenAI compatible” label proves a usable model. Some current OpenAI models require Responses for tool calling; check the [official function calling guide](https://developers.openai.com/api/docs/guides/function-calling) for the selected model.

The shipped UI accepts text. It sends authored trip context and current shared records to the configured upstream only after a traveler submits a request. Original PDF/image bytes and API credentials are excluded from model context. Image understanding is not shipped: adding it requires a vision-capable model, the appropriate image content conversion, protected upload handling and a real image test. A model that only supports text/tools cannot read ticket photos.

Expense amounts use integer cents, known traveler IDs and the ledger's existing base currency (`CNY` until configured). A foreign expense requires the user's actual converted base amount; the assistant cannot invent an exchange rate. Missing or ambiguous facts remain pending. Tool loops are bounded; a model failure before plan completion saves no shared change.

## Verify the chosen environment

1. Build both switch modes in fresh generated projects. Off must show no AI entry/client and must make no upstream request. Inspect enabled `dist/` for only the public switch, ordinary page assets and AI UI; server transport and credentials remain outside it.
2. Use synthetic local group secrets and the existing local D1 binding. Apply migrations locally, build and run `npm run preview` from the generated root. Test unauthenticated 401, wrong trip 403, foreign Origin 403, a real tool-created task, visible task refresh, expense cents, stale-revision 409 and the identical retry without duplicates. Test both API styles if claiming both work with that upstream.
3. Keep labels separate: mocked transport plus SQLite tests prove the tested contracts; local Wrangler proves local Functions/D1 integration; an actual provider tool round trip proves only that provider/model/protocol; authenticated hosted sessions prove remote behavior. The owner's browser trial and content approval are separate gates. Report any unavailable gate directly.

For a quick local trial after configuration: “添加 to-do：出发前带上雨衣”, “把带上雨衣这项 to-do 标为完成”, “有哪些票据还未标记购票？”. To test expenses, first add actual test travelers and specify payer, participants, currency and amount. Use “修改明天的酒店预订” as a boundary test: it must explain the read-only limit and make no booking claim.
