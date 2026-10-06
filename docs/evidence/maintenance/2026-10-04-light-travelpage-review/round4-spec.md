# Round 4 Spec specialist report

- Evidence label: review
- Independent read-only context: /root/spec_round4_resume
- Reviewed revision: 06b0e64c0d99c5bce5de2dd1bf776e82d3c9df72
- Fixed point: 49e7cbe8be1b978bfbe5f22745b0c0dfefbb89a7
- Charter revision: travel-handbook-2026-10-03-v2; unchanged nine criteria
- Findings: []

Per-ID rechecks, all Medium and fixed:
- F-002: handbook.css ledger category/feedback measured 14px/12px; AC2 (Charter line13).
- F-003: site-navigation.js direct Skip #main preserves bookings; AC4 (line15).
- F-004: travel-cards.js demo insertion uses materials/main, actual-template assertion passes; AC3/AC5 (lines14/16).
- F-005: .todo-text and menu measured 14px/13px at390; AC2 (line13).
- F-006: ledger change notifications and pocket snapshot integration retain drafts and refresh source-derived content; AC1/AC4 (lines12/15), integration assertions pass.
- F-007: actual Back to #main restores bookings, Forward to #prep restores todo, matching new assertion; AC4 (line15).

The reviewer independently verified all61 package hashes, frozen manifest and local installed copy; installed generator/template equality; current generated source and retained original D1 input. Independently ran node --test tests/handbook.test.mjs tests/ledger-dom.test.mjs:17 passing, no failures/skips. Complete49-test and successful-build receipts were inspected, not relabeled as independent full reruns.

Actual IAB ID2 observations completed before a platform interruption:1440x900 two pages,390x844 stacking; date08,deep link,pending materials,place navigation entry,bilingual behavior and task/ledger draft preservation. Width=scrollWidth=390. Titles/large dates use system serif; forms use UI font. Existing13px form inputs were not treated as a newly invented minimum; AC2 specifies readable UI forms and14px body/12px secondary text.

Extra PDF-ticket re-observation was not completed: after interruption CUA inventory was browsers:[],old IAB ID2 disappeared and the iab alias could not create a tab. Chinese restoration,viewport reset and closing prior tabs could not be confirmed and are not counted as success. Ticket judgment is limited to the preserved historical fixture,current byte-identical app.js/handbook.js paths and assertion evidence. The historical ticket fixture as a whole is not the current package; several shell/navigation/style files differ. No current-round actual PDF,remoteD1,production,physicalphone or host-reload conclusion is claimed.

No source,Charter,fixture,evidence or state was edited by the reviewer. Core captures this report and owns project acceptance.
