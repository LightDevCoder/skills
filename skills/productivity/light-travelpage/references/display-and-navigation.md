# Display and navigation

Read with [data-contract.md](data-contract.md) when generating travel content or updating the display modules.

## Bilingual content

The template updates display text in place. It does not rebuild forms or write language changes to shared state. System translations live in `i18n.js`; trip translations live in `trip-data.json.translations`, keyed by the exact original display string with `en` and/or `zh-CN` values. For example: `"西湖散步":{"en":"West Lake walk"}`. Prepare these translations from supplied facts during generation, not through a browser translation service. Identical original strings share one translation.

The first visit uses Chinese or English browser preference, otherwise `config.language` (default `zh-CN`). An explicit choice is stored in local storage. Missing English authored content remains visible with a `Chinese only` marker; English source content without Chinese retains the source with `暂无中文`. Blank translations are invalid and runtime fallback still preserves the source. Original addresses and local names remain available; runtime traveler names, notes and tasks are deliberately not translated. PDFs remain original. Mark new user-content nodes with `data-no-translate`; register source display content for fallback handling. Translate accessibility labels without translating embedded user names.

Both languages use a fine serif system font stack: Baskerville / Iowan Old Style for Latin, Songti SC / Noto Serif CJK SC / Source Han Serif SC / STSong / SimSun for Chinese. Availability depends on the device; no proprietary font files are redistributed. Retain adequate contrast and readable size for secondary text.

## Cards

Display complete and pending records distinctly. Source data with no flight segments can use a pending journey; do not invent a countdown. Airport endpoints may reference `placeId`; journeys may reference `ticketIds`. Stays appear between flights and the route and can be linked from schedule items using `accommodationId`. Stay nights are computed from local calendar dates, not elapsed UTC hours. Credentials and booking documents remain inside the authenticated deployment. Chromium and WebKit can block PDF `iframe` content inside a modal, so the builder keeps each source PDF unchanged and generates a same-name PNG of its first page. Both files stay behind the same authentication. `#ticket-dialog` displays the PNG directly, offers zoom, and retains a link to open the original PDF in a new window.

## Regional maps

All card, itinerary and schematic-pin navigation uses `TravelMaps`. Each place chooses independently: CN → Amap, KR → Kakao, RU → Yandex; other known region codes → Google. HK/MO/TW are independent codes and use the other-region default. Apple is an alternative everywhere; KR/RU also offer Google. Unknown regions offer explicit service selection and address copy.

Resolution priority is a local preference for the region, an allowed place-specific provider, then the regional default. Reset removes only that region's preference. In a provider, use a supported verified URL first, then a supported provider ID, compatible sourced coordinates, or original-name/address search. Google Maps `query` and Apple Maps `q` use the readable local name and address when present; Apple may also retain compatible coordinates in `ll`. Pure coordinates are a search fallback only when no readable name or address exists. Amap coordinates require GCJ02; other implemented coordinate links require WGS84. No coordinate conversion is performed. Unknown or incompatible systems fall back to address search. Preserve legacy Google fields; supported URLs are used only for the Google choice. A pure latitude/longitude Google search URL is not a verified place URL when the place has a readable name or address; do not bulk-write such URLs into `trip-data.json`. Unsupported links fall back to search without deleting source fields.

Navigation opens an external HTTPS map. No iframe preview or custom App scheme is required. The dialog always offers service choice, reset and original-address copy; clipboard denial leaves selectable address text. Do not send booking numbers, travelers or group credentials to map services. Provider links are allowlisted and unrelated query parameters stripped.

Protocol references checked 2026-09-14: [Amap search](https://lbs.amap.com/api/uri-api/guide/search/search), [Amap markers](https://lbs.amap.com/api/uri-api/guide/mobile-web/point), [Kakao map links](https://apis.map.kakao.com/web/guide/), [Apple map links](https://developer.apple.com/library/archive/featuredarticles/iPhoneURLScheme_Reference/MapLinks/MapLinks.html), [Google Maps URLs](https://developers.google.com/maps/documentation/urls/get-started), [Yandex sharing](https://www.yandex.com/support/maps/en/concept/get-map-reference). Recheck official protocols when extending adapters.

## Verification and demonstrations

Test actual rendered language switching while editing, refresh with a draft, both complete/pending cards, invalid dates/references, regional defaults and reset, unknown coordinate fallback, and protected ticket fallback. On narrow Chromium and WebKit viewports, open a PDF ticket and confirm the PNG image visibly loads inside `#ticket-dialog`, zoom changes its size, no PDF `iframe` is used, and the original PDF link remains available. Separately record real external page loading, correct destination results, and mobile App opening; these are different evidence classes. A network timeout remains unverified.

Only a deliberately fictional demo sets `config.demo: true` and `demoNavigationPlaceIds`. Keep demo navigation examples outside the real itinerary. A fictional hotel's link must be explicitly labelled as a separate real public navigation target. Generated blank projects contain no demo bookings or extra map examples. Use the same template code for demo and real trips.
