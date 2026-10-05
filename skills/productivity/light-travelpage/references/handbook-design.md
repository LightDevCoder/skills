# Travel handbook design

The generator's default is a readable travel handbook: warm paper, restrained ink, rust accents and chapter tabs. Use `assets/template/handbook.css` as the visual source of truth. Preserve an existing trip's chosen design during a data-only update.

## Pages and navigation

The trip heading precedes the book. Chapters expose itinerary, bookings, ledger, to-do and the whole-trip route. When original materials are the only secondary chapter, expose Materials directly in the topbar. When driving is also enabled, use More for those secondary chapters. Keep only destinations not already represented by a visible chapter in that menu. Enable only modules supported by the trip. Bookings combine the existing flight and stay modules; each daily map stays beside its itinerary, while the whole-trip map also has its own visible chapter. Original materials list the supplied ticket records and open the existing protected ticket dialog. Unknown bookings or absent attachments stay visibly pending.

Show one day per reading page. Date controls switch directly to that day's complete itinerary and map; return to the beginning of the daily content instantly rather than animate down a continuous feed. Retain every supplied day, record and ticket control; switching dates must not delete them, reset shared state or lose the selected date during a runtime refresh. On desktop, put the day's route map beside its reading page. Map points derive from that day's supplied schedule; numbered locations have a complete place list with the existing regional navigation controls. A grouped marker expands all its members at once and retains the rest of the route. Selecting a schedule item or place-list entry automatically expands the selected place’s entire group and highlights it. Keep all other places visible. Switching to another schedule item updates the expansion target; switching dates clears it. Other chapters retain the pocket page derived from actual stays, ledger records, to-do items and materials. The ledger keeps its full working surface. On narrow screens, show the daily map before its schedule; stack other reading and pocket pages and retain visible chapter/date controls. Deep links and browser navigation must reveal the target chapter.

Use whole travel content rather than a product introduction. Photos and tickets are optional attachments. A card without a file contains its text and actions directly. Real maps and source documents keep their existing geographic, privacy and authentication contracts.

## Typography

Trip titles, chapter/content headings and large dates use Georgia with Chinese system serif fallbacks: Songti SC, Noto Serif CJK SC, Source Han Serif SC, STSong and SimSun. Buttons, forms, small metadata and operation feedback use the system UI sans stack. Keep body text at least 14px and secondary text at least 12px, with sufficient contrast and room for English and long Chinese text. The device chooses its available system font; the package does not download or redistribute proprietary fonts.

## Check

Inspect actual generated desktop and 390px layouts, chapter/date switching, a deep stay link, materials and both languages. Confirm that switching chapters and language preserves an unfinished ledger/task form. Ticket PNG zoom and the original PDF link remain available. Keep these browser observations separate from hosted authentication, cross-session synchronization and physical-device evidence.

The group sign-in page is the handbook cover: reuse the paper (#eeeae0), surface (#fffdf6), ink (#2b2e27), rust (#954434), thin borders and 3px corners. Use the same system serif stack for its heading and the UI sans-serif stack for input, label and buttons. Keep the language control compact. The feature name is to-do in both languages throughout chapters, pocket page, forms and AI confirmations. Preserve authored wording such as 核对机票 inside trip materials. Preserve authentication, errors and language switching while restyling. Verify sign-in, wrong-code recovery and narrow-screen layout in the actual browser.

The palette covers sign-in, reading pages, map selection and zoom, ticket preview, ledger forms/settings/confirmation dialogs and optional AI. Secondary components use the variables in `handbook.css`. Preserve geographic basemap colors, ledger category colors and user-selected avatar colors. For undated drafts, use numbered DAY labels in date controls instead of assuming calendar dates; initialization and chapter switching must retain the supplied content.
