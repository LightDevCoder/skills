# Round 3 Spec report

Captured from completed read-only reviewer `/root/spec_final`.
Candidate: `b4382c65ffa63940cd5bd6b932e9a034d444cc7d`; fixed point: `49e7cbe8be1b978bfbe5f22745b0c0dfefbb89a7`.
Charter: `travel-handbook-2026-10-03-v1`; Round 3.

One Medium finding, `SPEC-R3-001` (Core identity `F-007`): bookings -> native Skip `#main` -> tasks -> actual browser Back restores the URL `#main` but retains `chapter=todo`, hidden stays and visible tasks. This violates AC4. The same boundary was independently reproduced with Happy DOM popstate. Ordinary `#stays` Back and direct Skip still work.

F-001 through F-006 remain fixed. The complete package and cumulative diff were read; 61 package hashes, generated-template equality and both input hashes matched. Nineteen focused tests passed. Real IAB 1440px double pages and 390px single 356px column had no overflow. Task text is 14px, enabled menu 13px, ledger category 14px; no visible text below 12px. Date 08, stay deep link, bilingual behavior, pending materials and amount 127.80/unsent note/task draft preservation were observed. No source edits, remote D1, production or physical-device claims. Temporary tab closed and viewport reset.
