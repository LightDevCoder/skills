from __future__ import annotations

import importlib.util
import json
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
        packages = ROOT.parents[1]
        expected = {
            "project-clarify": ("goal", "domain-context", "tracker"),
            "decision-map": ("issue-tracker", "working-area"),
            "project-spec": ("goal", "domain-context", "working area"),
            "project-tickets": ("tracker", "working area"),
            "implement": ("tracker", "domain-context", "review-profile"),
            "project-review": ("review profile", "acceptance strategy"),
        }
        for name, fields in expected.items():
            text = next(packages.glob(f"*/{name}/SKILL.md")).read_text(encoding="utf-8").lower()
            self.assertIn("docs/agents/light-project.md", text)
            for field in fields:
                self.assertIn(field, text, f"{name} does not consume {field}")

    def test_default_invocation_has_no_jev_side_effects(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-no-jev-") as tmp:
            root = Path(tmp)
            report = BOOTSTRAP.bootstrap(root, config())
            project = (root / "docs/agents/light-project.md").read_text(encoding="utf-8")
            self.assertNotIn("typesafe-ai", project)
            self.assertNotIn("TypeSafe Jev", project)
            self.assertFalse((root / ".env").exists())
            self.assertFalse((root / ".gitignore").exists())
            self.assertFalse((root / ".pi").exists())
            self.assertNotIn("jev", report)

    def test_detect_typesafe_key_from_env_and_dotenv(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-key-") as tmp:
            root = Path(tmp)
            # 1. Neither env nor .env
            with mock.patch.dict(os.environ, {}, clear=True):
                found, source = BOOTSTRAP.detect_typesafe_key(root)
                self.assertFalse(found)
                self.assertEqual(source, "missing")

            # 2. From os.environ
            with mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key-12345"}):
                found, source = BOOTSTRAP.detect_typesafe_key(root)
                self.assertTrue(found)
                self.assertEqual(source, "os.environ")

            # 3. From project-level .env
            (root / ".env").write_text("TYPESAFE_API_KEY=dotenv-key-67890\nOTHER=1\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {}, clear=True):
                found, source = BOOTSTRAP.detect_typesafe_key(root)
                self.assertTrue(found)
                self.assertEqual(source, ".env")

    def test_check_global_skill(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-global-") as tmp:
            skill_root = Path(tmp)
            # Missing skill
            self.assertFalse(BOOTSTRAP.check_global_skill("typesafe-ai", search_roots=[skill_root]))

            # Present skill
            skill_dir = skill_root / "typesafe-ai"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("---\nname: typesafe-ai\n---\n", encoding="utf-8")
            self.assertTrue(BOOTSTRAP.check_global_skill("typesafe-ai", search_roots=[skill_root]))

    def test_ensure_gitignored(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-ignore-") as tmp:
            root = Path(tmp)
            # Creates .gitignore if missing
            added = BOOTSTRAP.ensure_gitignored(root, ".env")
            self.assertTrue(added)
            self.assertTrue((root / ".gitignore").is_file())
            self.assertIn(".env\n", (root / ".gitignore").read_text(encoding="utf-8"))

            # Does not duplicate if already present
            added_again = BOOTSTRAP.ensure_gitignored(root, ".env")
            self.assertFalse(added_again)
            self.assertEqual((root / ".gitignore").read_text(encoding="utf-8").count(".env"), 1)

            # Appends to existing .gitignore with other content
            (root / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
            added_to_existing = BOOTSTRAP.ensure_gitignored(root, ".env")
            self.assertTrue(added_to_existing)
            content = (root / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("node_modules/", content)
            self.assertIn(".env", content)

    def test_configure_typesafe_key_enforces_gitignore_and_masks_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-cfg-") as tmp:
            root = Path(tmp)
            secret = "ts-test-secret-abcdef123456"
            BOOTSTRAP.configure_typesafe_key(root, secret)

            # Enforces gitignore
            self.assertTrue((root / ".gitignore").is_file())
            self.assertIn(".env", (root / ".gitignore").read_text(encoding="utf-8"))

            # Writes .env correctly
            self.assertTrue((root / ".env").is_file())
            self.assertIn(f"TYPESAFE_API_KEY={secret}", (root / ".env").read_text(encoding="utf-8"))

            # Masking never leaks secret
            masked = BOOTSTRAP.mask_secret(secret)
            self.assertNotIn(secret, masked)
            self.assertEqual(masked, "[REDACTED]")

    def test_jev_opt_in_with_global_key_and_global_skill_reuses_without_local_duplication(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-jev-global-") as tmp:
            root = Path(tmp)
            global_skills = Path(tmp) / "global_skills"
            (global_skills / "typesafe-ai").mkdir(parents=True)
            (global_skills / "typesafe-ai" / "SKILL.md").write_text("---\nname: typesafe-ai\n---\n", encoding="utf-8")

            with mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key-global"}):
                report = BOOTSTRAP.bootstrap(
                    root,
                    config(),
                    capability_roots=[global_skills],
                    jev=True,
                )

            project = (root / "docs/agents/light-project.md").read_text(encoding="utf-8")
            self.assertIn("typesafe-ai", project)
            self.assertIn("TypeSafe Jev System One semantic acceleration", project)

            # No local skill duplication
            self.assertFalse((root / ".pi" / "skills" / "typesafe-ai").exists())
            self.assertFalse((root / ".agents" / "skills" / "typesafe-ai").exists())

            # Report asserts
            self.assertIn("jev", report)
            self.assertTrue(report["jev"]["enabled"])
            self.assertTrue(report["jev"]["keyDetected"])
            self.assertEqual(report["jev"]["keySource"], "os.environ")
            self.assertEqual(report["jev"]["skillLocation"], "global")

    def test_jev_opt_in_without_global_skill_installs_local_skill(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-jev-local-") as tmp:
            root = Path(tmp)
            target_skill_dir = root / ".pi" / "skills" / "typesafe-ai"

            def fake_installer(project_root: Path, agent_target=None, installer_cmd=None):
                target_skill_dir.mkdir(parents=True, exist_ok=True)
                (target_skill_dir / "SKILL.md").write_text("---\nname: typesafe-ai\ndescription: official\n---\n# TypeSafe\n", encoding="utf-8")
                return True, target_skill_dir, "installed-local"

            with mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key-local"}):
                with mock.patch.object(BOOTSTRAP, "check_global_skill", return_value=False):
                    with mock.patch.object(BOOTSTRAP, "install_official_typesafe_skill", side_effect=fake_installer):
                        report = BOOTSTRAP.bootstrap(root, config(), jev=True)

            local_skill = root / ".pi" / "skills" / "typesafe-ai" / "SKILL.md"
            self.assertTrue(local_skill.is_file())
            self.assertIn("typesafe-ai", local_skill.read_text(encoding="utf-8"))
            self.assertEqual(report["jev"]["skillLocation"], "installed-local")
            project = (root / "docs/agents/light-project.md").read_text(encoding="utf-8")
            self.assertIn("typesafe-ai", project)

    def test_project_init_never_generates_fake_typesafe_ai_skill(self) -> None:
        """Verify that missing official skill never generates a stub DEFAULT_TYPESAFE_SKILL_MD."""
        self.assertFalse(hasattr(BOOTSTRAP, "DEFAULT_TYPESAFE_SKILL_MD"))
        with tempfile.TemporaryDirectory(prefix="project-init-no-fake-") as tmp:
            root = Path(tmp)
            with mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
                with mock.patch.object(BOOTSTRAP, "check_global_skill", return_value=False):
                    with mock.patch.object(BOOTSTRAP, "install_official_typesafe_skill", return_value=(False, None, "JEV_SKILL_SETUP_INCOMPLETE")):
                        report = BOOTSTRAP.bootstrap(root, config(), jev=True)

            self.assertFalse((root / ".pi" / "skills" / "typesafe-ai").exists())
            self.assertFalse((root / ".agents" / "skills" / "typesafe-ai").exists())
            self.assertEqual(report["jev"]["skillLocation"], "JEV_SKILL_SETUP_INCOMPLETE")
            self.assertEqual(report["jev"]["status"], "SKILL_INCOMPLETE")

    def test_official_skill_install_failure_reports_incomplete_setup(self) -> None:
        """Verify official installer failure marks Jev onboarding as incomplete without failing project-init."""
        with tempfile.TemporaryDirectory(prefix="project-init-fail-") as tmp:
            root = Path(tmp)
            with mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
                with mock.patch.object(BOOTSTRAP, "check_global_skill", return_value=False):
                    with mock.patch.object(BOOTSTRAP, "install_official_typesafe_skill", return_value=(False, None, "JEV_SKILL_SETUP_INCOMPLETE")):
                        report = BOOTSTRAP.bootstrap(root, config(), jev=True)

            self.assertEqual(report["jev"]["status"], "SKILL_INCOMPLETE")
            self.assertEqual(report["jev"]["skillLocation"], "JEV_SKILL_SETUP_INCOMPLETE")
            self.assertTrue((root / "docs/agents/light-project.md").is_file())

    def test_relevant_skills_updated_only_after_verified_skill_availability(self) -> None:
        """Verify typesafe-ai is added to Relevant Skills ONLY after verified skill setup."""
        with tempfile.TemporaryDirectory(prefix="project-init-rel-") as tmp:
            root = Path(tmp)
            # Case 1: Skill installation fails -> NOT added to Relevant Skills
            with mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
                with mock.patch.object(BOOTSTRAP, "check_global_skill", return_value=False):
                    with mock.patch.object(BOOTSTRAP, "install_official_typesafe_skill", return_value=(False, None, "JEV_SKILL_SETUP_INCOMPLETE")):
                        report = BOOTSTRAP.bootstrap(root, config(), jev=True)
            project_content = (root / "docs/agents/light-project.md").read_text(encoding="utf-8")
            self.assertNotIn("typesafe-ai", project_content)

            # Case 2: Skill verified globally -> added to Relevant Skills
            global_skills = Path(tmp) / "global_skills"
            (global_skills / "typesafe-ai").mkdir(parents=True)
            (global_skills / "typesafe-ai" / "SKILL.md").write_text("---\nname: typesafe-ai\n---\n# Valid\n", encoding="utf-8")
            report2 = BOOTSTRAP.bootstrap(root, config(), capability_roots=[global_skills], jev=True)
            project_content2 = (root / "docs/agents/light-project.md").read_text(encoding="utf-8")
            self.assertIn("typesafe-ai", project_content2)

    def test_optional_jev_setup_failure_preserves_core_bootstrap_success(self) -> None:
        """Core project-init remains SUCCESS even if optional Jev onboarding fails."""
        with tempfile.TemporaryDirectory(prefix="project-init-core-success-") as tmp:
            root = Path(tmp)
            with mock.patch.object(BOOTSTRAP, "check_global_skill", return_value=False):
                with mock.patch.object(BOOTSTRAP, "install_official_typesafe_skill", return_value=(False, None, "JEV_SKILL_SETUP_INCOMPLETE")):
                    report = BOOTSTRAP.bootstrap(root, config(), jev=True)

            self.assertTrue((root / "docs/agents/light-project.md").is_file())
            self.assertTrue((root / "docs/agents/issue-tracker.md").is_file())
            self.assertTrue((root / "AGENTS.md").is_file())
            self.assertEqual(report["jev"]["status"], "SKILL_INCOMPLETE")

    def test_raw_api_key_never_echoed(self) -> None:
        """Verify raw API key never appears in report, stdout, or contracts."""
        with tempfile.TemporaryDirectory(prefix="project-init-secret-") as tmp:
            root = Path(tmp)
            secret = "ts-live-secret-test-key-998877"
            BOOTSTRAP.configure_typesafe_key(root, secret)

            with mock.patch.object(BOOTSTRAP, "check_global_skill", return_value=True):
                report = BOOTSTRAP.bootstrap(root, config(), jev=True)
            report_str = json.dumps(report)
            self.assertNotIn(secret, report_str)

            project_content = (root / "docs/agents/light-project.md").read_text(encoding="utf-8")
            self.assertNotIn(secret, project_content)

    def test_prompt_typesafe_key_uses_getpass(self) -> None:
        """Verify prompt_typesafe_key uses getpass instead of echoing input."""
        with tempfile.TemporaryDirectory(prefix="project-init-getpass-") as tmp:
            root = Path(tmp)
            with mock.patch("sys.stdin.isatty", return_value=True):
                with mock.patch.dict(os.environ, {}, clear=True):
                    with mock.patch("getpass.getpass", return_value="ts-secret-pass") as mock_getpass:
                        found, source = BOOTSTRAP.prompt_typesafe_key(root)
                        self.assertTrue(found)
                        self.assertEqual(source, ".env")
                        mock_getpass.assert_called_once()
                        self.assertTrue((root / ".env").is_file())
                        self.assertIn("ts-secret-pass", (root / ".env").read_text(encoding="utf-8"))

    def test_non_interactive_fallback_defaults_to_no_jev(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-init-fallback-") as tmp:
            root = Path(tmp)
            with mock.patch("sys.stdin.isatty", return_value=False):
                report = BOOTSTRAP.bootstrap(root, config(), jev=None)
            self.assertNotIn("jev", report)
            project = (root / "docs/agents/light-project.md").read_text(encoding="utf-8")
            self.assertNotIn("typesafe-ai", project)

    def test_cli_flags_jev_and_no_jev(self) -> None:
        parser = BOOTSTRAP.build_argument_parser()
        args_jev = parser.parse_args(["--project-root", ".", "--config-json", "{}", "--jev"])
        self.assertIs(args_jev.jev, True)

        args_no_jev = parser.parse_args(["--project-root", ".", "--config-json", "{}", "--no-jev"])
        self.assertIs(args_no_jev.jev, False)

        args_default = parser.parse_args(["--project-root", ".", "--config-json", "{}"])
        self.assertIsNone(args_default.jev)

    def test_active_agent_target_resolution(self) -> None:
        """Verify host target resolution across Pi, Claude, Cursor, Codex, and fail-closed unknown."""
        # Explicit target
        self.assertEqual(BOOTSTRAP.resolve_active_agent_target(explicit_target="pi"), "pi")
        self.assertEqual(BOOTSTRAP.resolve_active_agent_target(explicit_target="claude"), "claude")

        # Config target
        self.assertEqual(BOOTSTRAP.resolve_active_agent_target(config={"agentTarget": "cursor"}), "cursor")

        # Environment target
        with mock.patch.dict(os.environ, {"SKILLS_AGENT_TARGET": "codex"}, clear=True):
            self.assertEqual(BOOTSTRAP.resolve_active_agent_target(), "codex")

        # Pi environment variable detection
        with mock.patch.dict(os.environ, {"PI_APP_NAME": "pi"}, clear=True):
            self.assertEqual(BOOTSTRAP.resolve_active_agent_target(), "pi")

        # Claude environment variable detection
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_ENTRY": "1"}, clear=True):
            self.assertEqual(BOOTSTRAP.resolve_active_agent_target(), "claude")

        # Unknown environment without evidence fails closed
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.object(Path, "is_dir", return_value=False):
                self.assertIsNone(BOOTSTRAP.resolve_active_agent_target(config={"instructionFile": "OTHER.md"}))

    def test_unknown_agent_target_fails_closed_without_calling_installer(self) -> None:
        """P0 (Section 4): Unknown agent target must fail closed and never run installer."""
        with tempfile.TemporaryDirectory(prefix="project-init-unknown-") as tmp:
            root = Path(tmp)
            cfg = config()

            with mock.patch("subprocess.run") as mock_sub:
                with mock.patch.dict(os.environ, {}, clear=True):
                    with mock.patch.object(BOOTSTRAP, "resolve_active_agent_target", return_value=None):
                        report = BOOTSTRAP.bootstrap(root, cfg, jev=True)

            self.assertEqual(report["jev"]["status"], "TARGET_UNRESOLVED")
            for call_args in mock_sub.call_args_list:
                cmd = call_args[0][0]
                self.assertNotIn("skills", cmd)
                self.assertNotIn("npx", cmd)

    def test_installer_invokes_correct_agent_flags(self) -> None:
        """P0 (Section 3 & 32): Installer commands must include exact --agent and --yes without real execution."""
        with tempfile.TemporaryDirectory(prefix="project-init-cmd-") as tmp:
            root = Path(tmp)

            # Test Pi target
            with mock.patch("subprocess.run") as mock_sub:
                mock_sub.return_value = mock.MagicMock(returncode=0)
                BOOTSTRAP.install_official_typesafe_skill(root, agent_target="pi")
                mock_sub.assert_called_once()
                called_cmd = mock_sub.call_args[0][0]
                self.assertIn("--agent", called_cmd)
                self.assertIn("pi", called_cmd)
                self.assertIn("--yes", called_cmd)

            # Test Claude target
            with mock.patch("subprocess.run") as mock_sub:
                mock_sub.return_value = mock.MagicMock(returncode=0)
                BOOTSTRAP.install_official_typesafe_skill(root, agent_target="claude")
                called_cmd = mock_sub.call_args[0][0]
                self.assertIn("--agent", called_cmd)
                self.assertIn("claude", called_cmd)

    def test_target_scope_verification(self) -> None:
        """P0 (Section 5): Installation must verify expected agent scope only."""
        with tempfile.TemporaryDirectory(prefix="project-init-scope-") as tmp:
            root = Path(tmp)

            # Create skill in Claude directory, but target is Pi
            claude_skill = root / ".claude" / "skills" / "typesafe-ai"
            claude_skill.mkdir(parents=True)
            (claude_skill / "SKILL.md").write_text("---\nname: typesafe-ai\n---\n# TypeSafe\n", encoding="utf-8")

            with mock.patch("subprocess.run", return_value=mock.MagicMock(returncode=0)):
                ok, path, msg = BOOTSTRAP.install_official_typesafe_skill(root, agent_target="pi")
                # Must fail because it was not installed in Pi scope!
                self.assertFalse(ok)
                self.assertIsNone(path)
                self.assertIn("expected agent scope", msg)

            # Now create in Pi directory
            pi_skill = root / ".pi" / "skills" / "typesafe-ai"
            pi_skill.mkdir(parents=True)
            (pi_skill / "SKILL.md").write_text("---\nname: typesafe-ai\n---\n# TypeSafe\n", encoding="utf-8")

            with mock.patch("subprocess.run", return_value=mock.MagicMock(returncode=0)):
                ok, path, msg = BOOTSTRAP.install_official_typesafe_skill(root, agent_target="pi")
                self.assertTrue(ok)
                self.assertEqual(path, pi_skill)

    def test_canonical_credential_resolution_and_cross_process_availability(self) -> None:
        """P0 (Sections 7, 8, 49): Canonical credential resolution across simulated processes."""
        with tempfile.TemporaryDirectory(prefix="project-init-creds-") as tmp:
            root = Path(tmp)
            secret = "ts-test-secret-key-12345"

            # 1. Configured via project-init
            BOOTSTRAP.configure_typesafe_key(root, secret)

            # 2. Re-read without python-dotenv or process env
            with mock.patch.dict(os.environ, {}, clear=True):
                key, source = BOOTSTRAP.resolve_typesafe_credentials(root)
                self.assertEqual(key, secret)
                self.assertEqual(source, ".env")

                # Test ask-light resolver finds the same project key
                al_script = ROOT.parent.parent / "productivity" / "ask-light" / "scripts"
                import sys
                if str(al_script) not in sys.path:
                    sys.path.insert(0, str(al_script))
                from semantic_router import resolve_typesafe_key as ask_light_key_resolver
                al_key, al_src = ask_light_key_resolver(root)
                self.assertEqual(al_key, secret)
                self.assertEqual(al_src, ".env")

                # Test agent-config resolver finds the same project key
                ac_script = ROOT.parent.parent / "engineering" / "agent-config" / "scripts"
                if str(ac_script) not in sys.path:
                    sys.path.insert(0, str(ac_script))
                from abstract_profiler import resolve_typesafe_key as agent_config_key_resolver
                ac_key, ac_src = agent_config_key_resolver(root)
                self.assertEqual(ac_key, secret)
                self.assertEqual(ac_src, ".env")

    def test_end_to_end_local_integration_without_network(self) -> None:
        """Section 49: Full local integration test verifying contracts, credentials, and downstream resolvers."""
        with tempfile.TemporaryDirectory(prefix="project-init-e2e-") as tmp:
            root = Path(tmp)
            pi_skill = root / ".pi" / "skills" / "typesafe-ai"
            pi_skill.mkdir(parents=True)
            (pi_skill / "SKILL.md").write_text("---\nname: typesafe-ai\n---\n# TypeSafe\n", encoding="utf-8")

            secret_key = "ts-mock-e2e-key-7788"
            BOOTSTRAP.configure_typesafe_key(root, secret_key)

            fake_client = mock.MagicMock()
            fake_client.system_one.return_value = mock.MagicMock(
                nouls={"readiness_check": mock.MagicMock(noul=1.0)}
            )

            with mock.patch.object(BOOTSTRAP, "check_global_skill", return_value=False):
                with mock.patch.object(BOOTSTRAP, "verify_typesafe_sdk", return_value=True):
                    with mock.patch.object(BOOTSTRAP, "install_official_typesafe_skill", return_value=(True, pi_skill, "installed-local")):
                        report = BOOTSTRAP.bootstrap(
                            root,
                            config(),
                            jev=True,
                            agent_target="pi",
                            smoke_client=fake_client,
                        )

            # Contract checks
            self.assertEqual(report["jev"]["status"], "READY")
            self.assertEqual(report["jev"]["agentTarget"], "pi")
            self.assertTrue(report["jev"]["keyDetected"])
            self.assertEqual(report["jev"]["keySource"], ".env")

            proj_md = (root / "docs/agents/light-project.md").read_text(encoding="utf-8")
            self.assertIn("typesafe-ai", proj_md)
            self.assertIn("TypeSafe Jev System One semantic acceleration", proj_md)

            # New simulated process without process env
            with mock.patch.dict(os.environ, {}, clear=True):
                al_script = ROOT.parent.parent / "productivity" / "ask-light" / "scripts"
                ac_script = ROOT.parent.parent / "engineering" / "agent-config" / "scripts"
                import sys
                if str(al_script) not in sys.path:
                    sys.path.insert(0, str(al_script))
                if str(ac_script) not in sys.path:
                    sys.path.insert(0, str(ac_script))
                from semantic_router import resolve_typesafe_key as al_res
                from abstract_profiler import resolve_typesafe_key as ac_res
                k1, _ = al_res(root)
                k2, _ = ac_res(root)
                self.assertEqual(k1, secret_key)
                self.assertEqual(k2, secret_key)



if __name__ == "__main__":
    unittest.main(verbosity=2)
