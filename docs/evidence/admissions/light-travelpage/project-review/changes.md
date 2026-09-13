# Review continuation and repair record

Original Charter and rounds 1–3 preserved. See resume-01.md for the user-directed continuation after the limit was explained.

Follow-up check 1: Standards found no issues; Spec found SPEC-RESUME-01, where a second ordinary save rejected by the pending guard replaced original recovery metadata. Accepted and repaired in `6bee388`: capture whether a request was pending before this save, and only attach generation/afterSuccess when this attempt newly entered pending. A rejected save cannot change the original recovery callback.

Producer validation:24/24 Node tests. Updated test double now transitions to pending during a failing save, matching the real adapter; added the exact rejected-second-save regression. Follow-up check 2 is independent revalidation of this small fix.
