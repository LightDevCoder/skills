from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("light_bootstrap", ROOT / "scripts" / "bootstrap.py")
assert SPEC and SPEC.loader
BOOTSTRAP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOOTSTRAP)


def config(goal: str = "Ship a parser") -> dict:
    return {
        "projectType": "software",
        "goal": goal,
        "outputs": ["parser", "tests"],
        "preset": "software",
        "relevantSkills": ["project-spec", "project-tickets", "implement", "project-review"],
        "issueTracker": {"kind": "local-markdown", "path": ".scratch/<effort>/issues"},
        "domainContext": ["CONTEXT.md", "docs/adr/"],
        "reviewProfile": "software",
        "acceptanceStrategy": "ticket criteria plus project-review",
        "workingArea": ".scratch",
        "collaboration": "solo",
        "constraints": ["preserve API"],
        "instructionFile": "AGENTS.md",
    }


class ProjectInitBehaviorTest(unittest.TestCase):
    def test_empty_repository_bootstraps_all_downstream_contracts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            report = BOOTSTRAP.bootstrap(root, config())
            self.assertEqual(set(report["paths"]), {"AGENTS.md", "docs/agents/light-project.md", "docs/agents/issue-tracker.md"})
            for relative in report["paths"]:
                self.assertTrue((root / relative).is_file())
            project = (root / "docs/agents/light-project.md").read_text(encoding="utf-8")
            tracker = (root / "docs/agents/issue-tracker.md").read_text(encoding="utf-8")
            for value in ("Ship a parser", "local-markdown", "CONTEXT.md", "software", ".scratch"):
                self.assertIn(value, project)
            self.assertIn("Blocked by", tracker)
            self.assertIn("ready-for-agent", tracker)

    def test_preexisting_empty_targets_are_reported_as_updated(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            project = root / "docs/agents/light-project.md"
            tracker = root / "docs/agents/issue-tracker.md"
            project.parent.mkdir(parents=True)
            for path in (root / "AGENTS.md", project, tracker):
                path.touch()

            report = BOOTSTRAP.bootstrap(root, config())

            self.assertEqual(set(report["paths"].values()), {"updated"})

    def test_rerun_updates_only_managed_content_and_preserves_manual_additions(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# Existing rules\n\nKeep this line.\n", encoding="utf-8")
            (root / "CLAUDE.md").write_text("# Keep Claude untouched.\n", encoding="utf-8")
            BOOTSTRAP.bootstrap(root, config())
            project_path = root / "docs/agents/light-project.md"
            project_path.write_text(project_path.read_text(encoding="utf-8") + "\n## Manual Notes\nKeep this note.\n", encoding="utf-8")
            report = BOOTSTRAP.bootstrap(root, config("Ship a streaming parser"))
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            project = project_path.read_text(encoding="utf-8")
            self.assertIn("Keep this line.", agents)
            self.assertEqual((root / "CLAUDE.md").read_text(encoding="utf-8"), "# Keep Claude untouched.\n")
            self.assertEqual(agents.count("## Project Initialization"), 1)
            self.assertEqual(project.count(BOOTSTRAP.START), 1)
            self.assertIn("Ship a streaming parser", project)
            self.assertIn("Keep this note.", project)
            self.assertEqual(report["paths"]["AGENTS.md"], "preserved")

    def test_existing_initialization_section_content_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"
            agents.write_text(
                "# Rules\n\n## Project Initialization\n\nKeep this user-authored setup note.\n\n## Testing\n\nRun tests.\n",
                encoding="utf-8",
            )

            BOOTSTRAP.bootstrap(root, config())
            first = agents.read_text(encoding="utf-8")
            BOOTSTRAP.bootstrap(root, config())
            second = agents.read_text(encoding="utf-8")

            self.assertEqual(first, second)
            self.assertIn("Keep this user-authored setup note.", second)
            self.assertIn("## Testing\n\nRun tests.", second)
            self.assertEqual(second.count(BOOTSTRAP.POINTER_START), 1)

    def test_fenced_initialization_heading_is_not_treated_as_a_live_section(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"
            example = "# Rules\n\n```markdown\n## Project Initialization\n\nExample only.\n```\n"
            agents.write_text(example, encoding="utf-8")

            BOOTSTRAP.bootstrap(root, config())

            updated = agents.read_text(encoding="utf-8")
            self.assertIn(example, updated)
            self.assertEqual(updated.count("## Project Initialization"), 2)
            self.assertGreater(updated.index(BOOTSTRAP.POINTER_START), updated.index("```\n", updated.index("```markdown") + 3))

    def test_windows_paths_are_literal_on_managed_and_instruction_reruns(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"
            agents.write_text(
                "## Project Initialization\n\nUse C:\\src\\tool.\n",
                encoding="utf-8",
            )
            windows = config()
            windows["domainContext"] = [r"C:\src\docs"]

            BOOTSTRAP.bootstrap(root, windows)
            first_agents = agents.read_text(encoding="utf-8")
            first_project = (root / "docs/agents/light-project.md").read_text(encoding="utf-8")
            BOOTSTRAP.bootstrap(root, windows)

            self.assertEqual(agents.read_text(encoding="utf-8"), first_agents)
            self.assertEqual((root / "docs/agents/light-project.md").read_text(encoding="utf-8"), first_project)
            self.assertIn(r"C:\src\tool", first_agents)
            self.assertIn(r"C:\src\docs", first_project)

    def test_partial_rerun_preserves_omitted_optional_decisions(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            BOOTSTRAP.bootstrap(root, config())
            partial = config("Ship a revised parser")
            for key in ("acceptanceStrategy", "collaboration", "constraints"):
                del partial[key]

            BOOTSTRAP.bootstrap(root, partial)

            project = (root / "docs/agents/light-project.md").read_text(encoding="utf-8")
            self.assertIn("Goal: Ship a revised parser", project)
            self.assertIn("Acceptance strategy: ticket criteria plus project-review", project)
            self.assertIn("Collaboration: solo", project)
            self.assertIn("Constraints: preserve API", project)

    def test_invalid_contract_fails_before_writes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            invalid = config()
            invalid["issueTracker"] = {"kind": "local-markdown"}
            with self.assertRaisesRegex(ValueError, "issueTracker requires kind and path"):
                BOOTSTRAP.bootstrap(root, invalid)
            self.assertEqual(list(root.iterdir()), [])

    def test_unsupported_tracker_fails_closed_before_writes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            unsupported = config()
            unsupported["issueTracker"] = {"kind": "github", "path": "owner/repo"}
            with self.assertRaisesRegex(ValueError, "require local-markdown"):
                BOOTSTRAP.bootstrap(root, unsupported)
            self.assertEqual(list(root.iterdir()), [])

    def test_tracker_path_must_stay_under_working_area(self) -> None:
        for path in ("../../outside/issues", "/tmp/issues", "issues"):
            with self.subTest(path=path), tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
                root = Path(tmp)
                unsafe = config()
                unsafe["issueTracker"] = {"kind": "local-markdown", "path": path}
                with self.assertRaisesRegex(ValueError, "stay under"):
                    BOOTSTRAP.bootstrap(root, unsafe)
                self.assertEqual(list(root.iterdir()), [])

    def test_noncanonical_tracker_path_fails_before_writes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            unsupported = config()
            unsupported["issueTracker"] = {"kind": "local-markdown", "path": ".scratch/custom-items"}
            with self.assertRaisesRegex(ValueError, "supported .scratch/<effort>/issues"):
                BOOTSTRAP.bootstrap(root, unsupported)
            self.assertEqual(list(root.iterdir()), [])

    def test_empty_domain_context_is_recorded_without_blocking_bootstrap(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            no_domain = config()
            no_domain["domainContext"] = []
            BOOTSTRAP.bootstrap(root, no_domain)
            project = (root / "docs/agents/light-project.md").read_text(encoding="utf-8")
            self.assertIn("Domain context: none recorded", project)

    def test_instruction_precedence_is_case_insensitive_and_reports_conflict(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            agents = root / "agents.MD"
            claude = root / "CLAUDE.md"
            agents.write_text("# Agent notes\n", encoding="utf-8")
            claude.write_text("# Claude notes\n", encoding="utf-8")

            result = BOOTSTRAP.bootstrap(root, config())

            self.assertEqual(Path(result["instructionTarget"]), agents.resolve())
            self.assertEqual(len(result["conflicts"]), 1)
            self.assertIn("Project Initialization", agents.read_text(encoding="utf-8"))
            self.assertEqual(claude.read_text(encoding="utf-8"), "# Claude notes\n")

    def test_empty_repository_uses_the_inspected_host_instruction_style(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            claude_host = config()
            claude_host["instructionFile"] = "CLAUDE.md"

            result = BOOTSTRAP.bootstrap(root, claude_host)

            self.assertEqual(Path(result["instructionTarget"]), (root / "CLAUDE.md").resolve())
            self.assertTrue((root / "CLAUDE.md").is_file())
            self.assertFalse((root / "AGENTS.md").exists())

    def test_duplicate_late_managed_block_causes_no_partial_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            project = root / "docs/agents/light-project.md"
            tracker = root / "docs/agents/issue-tracker.md"
            project.parent.mkdir(parents=True)
            project.write_text("manual project note\n", encoding="utf-8")
            tracker.write_text(
                f"{BOOTSTRAP.START}\none\n{BOOTSTRAP.END}\n{BOOTSTRAP.START}\ntwo\n{BOOTSTRAP.END}\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "multiple Light managed"):
                BOOTSTRAP.bootstrap(root, config())

            self.assertEqual(project.read_text(encoding="utf-8"), "manual project note\n")
            self.assertFalse((root / "AGENTS.md").exists())

    def test_unbalanced_managed_markers_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            project = root / "docs/agents/light-project.md"
            project.parent.mkdir(parents=True)
            project.write_text(f"{BOOTSTRAP.START}\ninterrupted\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "unbalanced Light managed"):
                BOOTSTRAP.bootstrap(root, config())

            self.assertEqual(project.read_text(encoding="utf-8"), f"{BOOTSTRAP.START}\ninterrupted\n")
            self.assertFalse((root / "AGENTS.md").exists())

    def test_reversed_markers_and_duplicate_instruction_sections_fail_closed(self) -> None:
        fixtures = (
            ("docs/agents/light-project.md", f"{BOOTSTRAP.END}\nreversed\n{BOOTSTRAP.START}\n", "misordered Light managed"),
            ("AGENTS.md", f"## Project Initialization\n\n{BOOTSTRAP.POINTER_END}\nreversed\n{BOOTSTRAP.POINTER_START}\n", "misordered Light project pointer"),
            (
                "AGENTS.md",
                f"## Project Initialization\n\n{BOOTSTRAP.POINTER_START}\npointer\n{BOOTSTRAP.POINTER_END}\n\n## Project Initialization\n\nmanual\n",
                "multiple Project Initialization",
            ),
        )
        for relative, content, error in fixtures:
            with self.subTest(relative=relative, error=error), tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
                root = Path(tmp)
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, error):
                    BOOTSTRAP.bootstrap(root, config())
                self.assertEqual(target.read_text(encoding="utf-8"), content)

    def test_research_fallback_persists_sources_confirmation_and_validation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            fallback = config()
            fallback.update({
                "preset": "research-fallback",
                "sources": ["official-api.md", "project-brief.md"],
                "confirmation": "user confirmed on 2026-08-26",
                "validation": "source and path checks passed",
            })
            BOOTSTRAP.bootstrap(root, fallback)
            project = (root / "docs/agents/light-project.md").read_text(encoding="utf-8")
            for value in ("Sources: official-api.md, project-brief.md", "Confirmation: user confirmed on 2026-08-26", "Validation: source and path checks passed"):
                self.assertIn(value, project)

    def test_research_fallback_missing_evidence_fails_before_writes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            fallback = config()
            fallback["preset"] = "research-fallback"
            with self.assertRaisesRegex(ValueError, "research-fallback requires"):
                BOOTSTRAP.bootstrap(root, fallback)
            self.assertEqual(list(root.iterdir()), [])

    def test_rendered_value_injection_fails_before_any_write(self) -> None:
        injections = (
            ("goal", f"unsafe\n{BOOTSTRAP.START}"),
            ("outputs", ["safe", "unsafe\rvalue"]),
            ("constraints", [BOOTSTRAP.POINTER_END]),
        )
        for key, value in injections:
            with self.subTest(key=key), tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
                root = Path(tmp)
                injected = config()
                injected[key] = value
                with self.assertRaisesRegex(ValueError, "newline or managed marker"):
                    BOOTSTRAP.bootstrap(root, injected)
                self.assertEqual(list(root.iterdir()), [])

    def test_non_file_target_collision_fails_before_any_other_write(self) -> None:
        for relative in ("docs/agents/issue-tracker.md", "AGENTS.md"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
                root = Path(tmp)
                collision = root / relative
                collision.mkdir(parents=True)
                with self.assertRaisesRegex(ValueError, "not a regular file"):
                    BOOTSTRAP.bootstrap(root, config())
                self.assertTrue(collision.is_dir())
                self.assertFalse((root / "docs/agents/light-project.md").exists())
                other = root / ("AGENTS.md" if relative != "AGENTS.md" else "docs/agents/issue-tracker.md")
                self.assertFalse(other.exists())

    def test_unwritable_late_target_fails_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            instruction = root / "AGENTS.md"
            instruction.write_text("manual\n", encoding="utf-8")
            instruction.chmod(0o444)
            try:
                with self.assertRaisesRegex(ValueError, "not writable"):
                    BOOTSTRAP.bootstrap(root, config())
                self.assertEqual(instruction.read_text(encoding="utf-8"), "manual\n")
                self.assertFalse((root / "docs").exists())
            finally:
                instruction.chmod(0o644)

    def test_replace_failure_rolls_back_every_target(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)
            instruction = root / "AGENTS.md"
            instruction.write_text("manual\n", encoding="utf-8")
            real_replace = os.replace
            calls = 0

            def fail_fourth_replace(source, target):
                nonlocal calls
                calls += 1
                if calls == 4:
                    raise OSError("simulated late replace failure")
                return real_replace(source, target)

            with mock.patch.object(BOOTSTRAP.os, "replace", side_effect=fail_fourth_replace):
                with self.assertRaisesRegex(OSError, "simulated late replace failure"):
                    BOOTSTRAP.bootstrap(root, config())

            self.assertEqual(instruction.read_text(encoding="utf-8"), "manual\n")
            self.assertFalse((root / "docs").exists())
            self.assertFalse(any(".light-" in path.name for path in root.rglob("*")))

    def test_staging_write_failure_removes_temp_files_and_created_directories(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
            root = Path(tmp)

            with mock.patch.object(BOOTSTRAP.os, "fdopen", side_effect=OSError("simulated staging write failure")):
                with self.assertRaisesRegex(OSError, "simulated staging write failure"):
                    BOOTSTRAP.bootstrap(root, config())

            self.assertEqual(list(root.iterdir()), [])

    def test_instruction_symlink_alias_fails_before_writes(self) -> None:
        for relative in ("docs/agents/light-project.md", "docs/agents/issue-tracker.md"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
                root = Path(tmp)
                target = root / relative
                target.parent.mkdir(parents=True)
                target.write_text("manual\n", encoding="utf-8")
                (root / "AGENTS.md").symlink_to(target.relative_to(root))

                with self.assertRaisesRegex(ValueError, "resolve to the same file"):
                    BOOTSTRAP.bootstrap(root, config())

                self.assertEqual(target.read_text(encoding="utf-8"), "manual\n")
                other = root / ("docs/agents/issue-tracker.md" if relative.endswith("light-project.md") else "docs/agents/light-project.md")
                self.assertFalse(other.exists())

    def test_managed_contract_symlinks_fail_before_writes(self) -> None:
        for relative in ("docs/agents/light-project.md", "docs/agents/issue-tracker.md"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
                root = Path(tmp)
                readme = root / "README.md"
                readme.write_text("# Existing README\n", encoding="utf-8")
                target = root / relative
                target.parent.mkdir(parents=True)
                target.symlink_to(readme)

                with self.assertRaisesRegex(ValueError, "must not be a symlink"):
                    BOOTSTRAP.bootstrap(root, config())

                self.assertEqual(readme.read_text(encoding="utf-8"), "# Existing README\n")
                self.assertTrue(target.is_symlink())
                self.assertFalse((root / "AGENTS.md").exists())

    def test_capability_availability_is_classified_and_not_promoted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-cap-") as tmp:
            root = Path(tmp)
            capability_root = Path(tmp) / "installed-skills"
            for name in ("project-spec", "project-tickets"):
                (capability_root / name).mkdir(parents=True)
                (capability_root / name / "SKILL.md").write_text(f"---\nname: {name}\ndescription: fixture\n---\n", encoding="utf-8")

            cfg = config()
            report = BOOTSTRAP.bootstrap(root, cfg, capability_roots=[capability_root])
            statuses = {item["skill"]: item["status"] for item in report["capabilities"]}
            for name in cfg["relevantSkills"]:
                self.assertIn(name, statuses)
            self.assertEqual(statuses["project-spec"], "available")
            self.assertEqual(statuses["project-tickets"], "available")
            self.assertEqual(statuses["implement"], "unavailable")
            self.assertEqual(statuses["project-review"], "unavailable")

    def test_capability_availability_is_unknown_without_a_capability_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-unknown-") as tmp:
            root = Path(tmp)
            report = BOOTSTRAP.bootstrap(root, config())
            statuses = {item["skill"]: item["status"] for item in report["capabilities"]}
            self.assertTrue(statuses)
            self.assertTrue(all(status == "unknown" for status in statuses.values()))
            self.assertIn("not verified", report["capabilities"][0]["reason"])

    def test_explicitly_unavailable_capability_is_not_promoted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-unavail-") as tmp:
            root = Path(tmp)
            capability_root = Path(tmp) / "installed-skills"
            (capability_root / "project-spec").mkdir(parents=True)
            (capability_root / "project-spec" / "SKILL.md").write_text("---\nname: project-spec\ndescription: fixture\n---\n", encoding="utf-8")
            report = BOOTSTRAP.bootstrap(
                root,
                config(),
                capability_roots=[capability_root],
                unavailable_capabilities=["project-spec"],
            )
            statuses = {item["skill"]: item["status"] for item in report["capabilities"]}
            self.assertEqual(statuses["project-spec"], "unavailable")

    def test_project_family_declares_consumption_of_bootstrap_fields(self) -> None:
        packages = ROOT.parent
        expected = {
            "project-clarify": ("goal", "domain-context", "tracker"),
            "decision-map": ("issue-tracker", "working-area"),
            "project-spec": ("goal", "domain-context", "working area"),
            "project-tickets": ("tracker", "working area"),
            "implement": ("tracker", "domain-context", "review-profile"),
            "project-review": ("review profile", "acceptance strategy"),
        }
        for name, fields in expected.items():
            text = (packages / name / "SKILL.md").read_text(encoding="utf-8").lower()
            self.assertIn("docs/agents/light-project.md", text)
            for field in fields:
                self.assertIn(field, text, f"{name} does not consume {field}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
