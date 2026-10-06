# F-007 concrete repair, pending independent validation

The Round 3 reports are preserved against candidate `b4382c65ffa63940cd5bd6b932e9a034d444cc7d`. Core is BLOCKED because the frozen maximum is three rounds. No extra independent review has been run and no remote push has been performed.

Producer repair: `site-navigation.js` saves `handbookChapter` on each current history entry without adding an entry or discarding other state. Generic `#main`/`#top` restores that recorded chapter; known chapter hashes retain their deterministic mapping. One assertion-bearing test covers bookings -> content anchor -> tasks -> simulated popstate, checking actual bookings and task visibility. The scope is these two package files only.

Behavioral evidence: `history-repair-tests.txt` has 49 passing tests, zero failures/skips; `history-repair-build.txt` completes the generated-project build. `history-repair-equality.json` verifies all 49 runtime source files against the source template and separately verifies the retained authored input. `package-hashes-history-repair.json` freezes all 61 package file hashes.

Runtime evidence: on 2026-10-04, Node v26.7.0/npm 12.2.0/macOS, a fresh actual IAB ID3 tab opened `http://127.0.0.1:4176/#stays`. Native Skip Enter retained bookings at `#main`; the Tasks link showed `#prep`; actual `tab.back()` restored `#main` with `chapter=bookings`, `staysHidden=false`, `tasksHidden=true`. Width=scrollWidth=1280. An earlier isolated identical-source repair preview at port 4180 also verified actual Forward returned to tasks. Generated source retains the original D1 input; only built dist overrides persistence to local. No production or remote D1 claim.

Independent acceptance remains pending. The smallest approval is one additional independent final review round under unchanged acceptance criteria and implementation scope; only after acceptance should the previously authorized main push proceed.
