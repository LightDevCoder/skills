"""Behavior checks for wayfinding ops on the local markdown tracker."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DecisionMapBehaviorTest(unittest.TestCase):
    def test_local_tracker_ops_are_usable(self) -> None:
        # Simulate the tracker ops described in docs/agents/issue-tracker.md
        # using only the file conventions the Skill declares.
        with tempfile.TemporaryDirectory(prefix="decision-map-behave-") as tmp:
            base = Path(tmp) / ".scratch" / "demo-effort"
            issues = base / "issues"
            issues.mkdir(parents=True)

            # create map.md
            map_md = base / "map.md"
            map_md.write_text(
                """## Destination
Demo destination

## Notes
Test notes

## Decisions so far

## Not yet specified

- Fog patch A

## Out of scope

""",
                encoding="utf-8",
            )

            # create two child tickets, 02 blocked by 01
            t01 = issues / "01-first-decision.md"
            t01.write_text("Type: grilling\nStatus: open\nBlocked by:\n\n## Question\nFirst?\n", encoding="utf-8")
            t02 = issues / "02-second-decision.md"
            t02.write_text("Type: research\nStatus: open\nBlocked by: 01\n\n## Question\nSecond?\n", encoding="utf-8")

            # Frontier = unblocked, unclaimed, open => only 01
            def frontier(base: Path):
                front = []
                for p in sorted((base / "issues").glob("*.md")):
                    text = p.read_text(encoding="utf-8")
                    status = "open" if "Status: open" in text else "claimed" if "Status: claimed" in text else "resolved" if "Status: resolved" in text else "unknown"
                    blocked_line = next((l for l in text.splitlines() if l.startswith("Blocked by:")), "Blocked by:")
                    blocked = [s.strip() for s in blocked_line.replace("Blocked by:", "").split(",") if s.strip()]
                    # check if blocked tickets resolved
                    blocked_resolved = True
                    for bn in blocked:
                        # find file with prefix bn
                        bf = next(issues.glob(f"{bn}-*.md"), None)
                        if bf is None or "Status: resolved" not in bf.read_text(encoding="utf-8"):
                            blocked_resolved = False
                    if status == "open" and blocked_resolved:
                        front.append(p.name)
                return front

            self.assertEqual(frontier(base), ["01-first-decision.md"])

            # Claim 01
            text = t01.read_text(encoding="utf-8").replace("Status: open", "Status: claimed")
            t01.write_text(text, encoding="utf-8")
            self.assertEqual(frontier(base), [])

            # Resolve 01
            text = t01.read_text(encoding="utf-8").replace("Status: claimed", "Status: resolved")
            text += "\n## Answer\nDone.\n"
            t01.write_text(text, encoding="utf-8")
            # append to Decisions so far
            map_text = map_md.read_text(encoding="utf-8")
            map_md.write_text(map_text.replace("## Decisions so far", "## Decisions so far\n\n- [First decision](issues/01-first-decision.md) — done."), encoding="utf-8")

            # Now frontier should be 02
            self.assertEqual(frontier(base), ["02-second-decision.md"])
            self.assertIn("First decision", map_md.read_text(encoding="utf-8"))

    def test_map_contract_describes_decisions_so_far_indexing(self) -> None:
        mc = (ROOT / "references" / "MAP-CONTRACT.md").read_text(encoding="utf-8")
        wf = (ROOT / "references" / "WORKFLOW.md").read_text(encoding="utf-8")

        self.assertIn("Decisions so far", mc)
        self.assertIn("one line per closed ticket", mc)
        self.assertIn("gist", mc.lower())
        self.assertIn("Not yet specified", mc)
        self.assertIn("Out of scope", mc)
        # workflow mentions graduation of fog and scope ruling
        self.assertIn("graduate", wf.lower())
        self.assertIn("Out of scope", wf)

    def test_handoff_material_exists_when_fog_clear(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        wf = (ROOT / "references" / "WORKFLOW.md").read_text(encoding="utf-8")

        self.assertIn("project-spec", skill.lower())
        self.assertIn("fog is empty", wf.lower() if "fog is empty" in wf.lower() else wf.lower() + skill.lower())
        self.assertIn("No open tickets", wf)


if __name__ == "__main__":
    unittest.main(verbosity=2)
