"""Port of skills/language-learning/tests/language-learning-contract-tests.ps1."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tests"))

from check_helpers import Checks  # noqa: E402


def phrase_pattern(phrase: str) -> str:
    parts = [re.escape(p) for p in phrase.split(" ")]
    return r"\s+".join(parts)


def test_phrase(text: str, phrase: str) -> bool:
    return bool(re.search(phrase_pattern(phrase), text))


def test_context_reuse(text: str) -> bool:
    return (
        test_phrase(text, "Reuse information already known from the current conversation")
        and test_phrase(text, "default to beginner")
        and test_phrase(text, "infer it only when obvious from the conversation")
    )


def test_selective_correction(text: str) -> bool:
    return (
        test_phrase(text, "Do not correct every mistake")
        and test_phrase(text, "Do not enumerate every mistake")
        and test_phrase(text, "fell off the mountain")
    )


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    skill = (root / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    metadata = (root / "agents" / "openai.yaml").read_text(encoding="utf-8", errors="replace")
    ref_dir = root / "references"
    conversation = (ref_dir / "CONVERSATION.md").read_text(encoding="utf-8", errors="replace")
    lesson = (ref_dir / "DAILY-LESSON.md").read_text(encoding="utf-8", errors="replace")
    flashcards = (ref_dir / "FLASHCARDS.md").read_text(encoding="utf-8", errors="replace")
    grammar = (ref_dir / "GRAMMAR-DECODER.md").read_text(encoding="utf-8", errors="replace")
    evaluator = (ref_dir / "PROGRESS-EVALUATOR.md").read_text(encoding="utf-8", errors="replace")
    immersion = (ref_dir / "IMMERSION.md").read_text(encoding="utf-8", errors="replace")

    c.check(bool(re.search(r"(?m)^name:\s*language-learning\s*$", skill)), "frontmatter name is language-learning")
    c.check(bool(re.search(r"(?m)^disable-model-invocation:\s*true\s*$", skill)), "Claude metadata disables model invocation")
    c.check(bool(re.search(r"(?ms)^description:.*", skill)), "frontmatter has a description")
    c.check(test_context_reuse(skill), "Start section reuses context and defaults instead of re-asking")
    c.check(test_phrase(skill, "Keep the learner producing the language"), "Teaching Behavior keeps the learner producing")
    c.check(test_phrase(skill, "Reuse useful vocabulary, phrases, and corrections from earlier in the session"), "Teaching Behavior reuses session vocabulary and corrections")
    c.check(test_phrase(skill, "unnecessary meta commentary"), "Teaching Behavior forbids meta commentary")
    c.check(test_phrase(skill, "Retrieval before reveal"), "Conventions preserve retrieval before reveal")
    c.check(bool(re.search(r'display_name:\s*"Language Learning"', metadata)), "metadata has display name")
    c.check(bool(re.search(r'short_description:\s*"[^"]{25,64}"', metadata)), "metadata has bounded short description")
    c.check(test_phrase(metadata, "Use $language-learning to get a lesson"), "metadata default prompt invokes language-learning explicitly")
    c.check(bool(re.search(r"allow_implicit_invocation:\s*false", metadata)), "Codex metadata disables implicit invocation")

    for ref in ("DAILY-LESSON.md", "FLASHCARDS.md", "CONVERSATION.md", "GRAMMAR-DECODER.md", "PROGRESS-EVALUATOR.md", "IMMERSION.md"):
        c.check((ref_dir / ref).is_file(), f"references/{ref} exists")

    c.check(test_selective_correction(conversation), "Conversation mode corrects selectively without enumerating every mistake")
    c.check(test_phrase(conversation, "Prioritize mistakes that affect meaning, naturalness"), "Conversation mode prioritizes meaning-affecting mistakes")
    c.check(test_phrase(lesson, "Use the 10/10/5/5 split as a guideline rather than a rigid requirement"), "Daily lesson treats time split as a guideline")
    c.check(test_phrase(lesson, "explanation") and test_phrase(lesson, "exercises") and test_phrase(lesson, "quiz"), "Daily lesson still covers explanation, examples, exercises, quiz")
    c.check(test_phrase(flashcards, "most common everyday meaning first"), "Flashcards lead with the everyday meaning")
    c.check(test_phrase(flashcards, "stress or IPA only when pronunciation is non-obvious"), "Flashcards gate English IPA behind non-obvious pronunciation")
    c.check(test_phrase(grammar, "closest form learners commonly confuse"), "Grammar Decoder offers confusable contrasts when useful")
    c.check(test_phrase(grammar, "be used to") and test_phrase(grammar, "used to + verb"), "Grammar Decoder shows the used to / be used to contrast")
    c.check(test_phrase(evaluator, "concise evaluation"), "Progress Evaluator gives a concise evaluation after question 10")
    c.check(test_phrase(evaluator, "highest-priority areas to practice next"), "Progress Evaluator names next practice priorities")
    c.check(test_phrase(immersion, "Adapt or translate"), "Immersion Engine adapts content, not just translates")
    c.check(test_phrase(immersion, "Stay in the target language as much as the learner can reasonably handle"), "Immersion Engine keeps the follow-up in the target language")
    c.check(test_phrase(immersion, "Beginner") and test_phrase(immersion, "Intermediate") and test_phrase(immersion, "Advanced"), "Immersion Engine scales native-language support by level")

    mutated = re.sub(r"(?is)Reuse information already known from the current conversation", "Ask the learner to restate everything", skill)
    c.check(not test_context_reuse(mutated), "opposite-polarity context-reuse mutation is rejected")
    over_correct = conversation.replace("Do not correct every mistake.", "Correct every mistake you hear.")
    c.check(not test_selective_correction(over_correct), "opposite-polarity selective-correction mutation is rejected")

    return c.assertions, c.failures


class LanguageLearningContractTest(unittest.TestCase):
    def test_language_learning_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"LANGUAGE_LEARNING_CONTRACT=FAIL: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
