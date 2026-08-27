from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("clarify_session", ROOT / "scripts" / "session_state.py")
assert SPEC and SPEC.loader
SESSION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SESSION)


class ClarifyPublicContractTest(unittest.TestCase):
    def test_one_invocation_continues_through_normal_answers_to_confirmation(self) -> None:
        state = SESSION.Session()
        state = SESSION.transition(state, "invoke")
        self.assertEqual(state.status, "active")
        state = SESSION.transition(state, "answer")
        state = SESSION.transition(state, "answer")
        self.assertEqual(state.status, "active")
        state = SESSION.transition(state, "synthesize")
        self.assertEqual(state.status, "awaiting-confirmation")
        state = SESSION.transition(state, "confirm")
        self.assertEqual(state.status, "done")

    def test_correction_reopens_the_session_and_invalid_transitions_fail(self) -> None:
        state = SESSION.transition(SESSION.Session(), "invoke")
        state = SESSION.transition(state, "synthesize")
        self.assertEqual(SESSION.transition(state, "correct").status, "active")
        with self.assertRaises(ValueError):
            SESSION.transition(SESSION.Session(), "answer")

    def test_wrapper_composes_engine_without_deep_reference(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "references" / "WORKFLOW.md").read_text(encoding="utf-8")
        self.assertEqual(SESSION.POLICY["compositionTarget"], "socratic")
        self.assertTrue(SESSION.POLICY["ordinaryRepliesContinue"])
        self.assertTrue(SESSION.POLICY["completionRequiresConfirmation"])
        self.assertFalse((ROOT / "references" / "ROUTING.md").exists())
        self.assertNotIn("../../socratic/references", skill + workflow)

    def test_fact_gap_and_auto_chain_boundaries_remain(self) -> None:
        self.assertFalse(SESSION.POLICY["autoChainUserInvokedSkills"])
        self.assertEqual(SESSION.POLICY["factWork"], "report-only")


if __name__ == "__main__":
    unittest.main(verbosity=2)
