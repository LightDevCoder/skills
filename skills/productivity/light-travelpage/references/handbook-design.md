# Travel handbook design

The generator's default is a readable travel handbook: warm paper, restrained ink, rust accents and chapter tabs. Use `assets/template/handbook.css` as the visual source of truth. Preserve an existing trip's chosen design during a data-only update.

## Pages and navigation

The trip heading precedes the book. Chapters expose itinerary, bookings, ledger, tasks and original materials. Enable only modules supported by the trip. Bookings combine the existing flight and stay modules; maps and driving remain reachable through the travel menu and pocket page. Original materials list the supplied ticket records and open the existing protected ticket dialog. Unknown bookings or absent attachments stay visibly pending.

On desktop, show the daily reading page beside a pocket page derived from actual stays, ledger records, tasks and provided materials. Date controls select one supplied day without rebuilding its content or ticket controls. The ledger keeps its full working surface. On narrow screens, stack the reading and pocket pages; retain visible chapter/date controls. Deep links and browser navigation must reveal the target chapter.

Use whole travel content rather than a product introduction. Photos and tickets are optional attachments. A card without a file contains its text and actions directly. Real maps and source documents keep their existing geographic, privacy and authentication contracts.

## Typography

Trip titles, chapter/content headings and large dates use Georgia with Chinese system serif fallbacks: Songti SC, Noto Serif CJK SC, Source Han Serif SC, STSong and SimSun. Buttons, forms, small metadata and operation feedback use the system UI sans stack. Keep body text at least 14px and secondary text at least 12px, with sufficient contrast and room for English and long Chinese text. The device chooses its available system font; the package does not download or redistribute proprietary fonts.

## Check

Inspect actual generated desktop and 390px layouts, chapter/date switching, a deep stay link, materials and both languages. Confirm that switching chapters and language preserves an unfinished ledger/task form. Ticket PNG zoom and the original PDF link remain available. Keep these browser observations separate from hosted authentication, cross-session synchronization and physical-device evidence.
