# v0.2.6 — A clearer travel handbook, with optional AI

[中文发布说明](RELEASE_NOTES.zh-CN.md) · [Release manifest](RELEASE_MANIFEST.md)

This release focuses on `light-travelpage`. Generated pages bring daily plans and routes together, preserve supplied travel and booking details, and let the owner choose whether to include AI. The collection still contains 36 Skills.

## What changed

### Daily plans and maps stay together

Each date opens its own daily page immediately. Its route appears beside the schedule on desktop and above it on mobile. Selecting a place in the schedule or place list expands its whole group and highlights it; the other places remain visible. Changing dates clears the previous expansion, and refreshing shared records preserves the selected day. Drafts without dates use `DAY n` labels and initialize normally.

Route has a visible chapter alongside Itinerary, Bookings, Ledger and to-do. Materials gets a direct topbar link when it is the only secondary section; More contains only additional sections. Flight and hotel cards, ticket status and protected original materials remain available. Geographic outlines retain their sources and distinguish visit order from actual roads.

### One visual style across the page

The handbook uses warm paper, ink and rust accents. Headings and large dates use system serif fonts; controls use system UI fonts. Sign-in, map controls, ticket previews, ledger forms and optional AI use the same palette. Map, expense-category and member colors keep their meaning. Bilingual display and unfinished form drafts are preserved.

### AI is a choice before generation

The Skill asks whether to enable AI before generating a new page when the choice is unknown. It reuses an existing answer and defaults to off. Off builds omit the AI entry and client.

Enabled pages use a protected server connection compatible with Chat Completions or Responses tool calling. Configuration can point to an existing local CPA through an authorized Tunnel, an existing overseas CPA, or an API provider. The Skill does not provision those services as part of choosing AI.

The assistant can read itinerary and bookings and use enabled to-do, ticket-status and shared-expense actions. It keeps source travel content and merchant orders read-only. Credentials remain on the server. Confirmed actions are shown separately from the model's prose; uncertain saves retry the same request. Failed preflight reads preserve unsent drafts, and storage errors remain visible in an operable dialog.

## Upgrade notes

New projects use the handbook template; AI stays off unless selected. Data-only updates preserve the existing page design, trip identity, record IDs and shared state. To add AI to an existing compatible page, follow the connection reference, rebuild with `provider: openai`, configure server variables and apply `0002_ai_requests.sql` to the existing scoped D1 database. No state reset is required.

AI input is text-only. Ticket-image understanding is not included. An upstream must support the selected tool-calling protocol; its compatibility label alone is insufficient.

## Verification

The local candidate passes 77 template tests, 3 generator tests and builds for AI off, AI on and undated drafts. Desktop and 390px browser checks retain 7 days, 53 schedule items, 2 flight cards, 4 hotel cards and 14 material entries. AI browser checks use a synthetic local upstream; they do not establish a hosted provider connection or physical-device behavior.

Collection checks pass 528 pytest tests, 156 unittest tests, compilation and public documentation checks. Candidate-version detection is tested with isolated version folders instead of a fixed previous-release number.

Independent final review, exact-commit CI, published-tag installation and publication checks are pending. This file describes the local release candidate until those gates complete.
