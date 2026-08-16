"""Port of skills/ask-light/tests/ask-light-behavior-tests.ps1.

The behavior suite exercises the real `scripts/ask-light.ps1` scanner against
disposable fixture catalogs. It requires PowerShell (pwsh) to execute the
scanner; on hosts without pwsh the suite is skipped, while CI (which ships
pwsh on ubuntu-latest) runs the full scenario.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests"))

from check_helpers import Checks  # noqa: E402

HAS_PWSH = shutil.which("pwsh") is not None


def new_skill(root: Path, name: str, description: str, *, allow_implicit: bool = False, malformed: bool = False, body: str = "", hosts: str = "", block_hosts: bool = False) -> Path:
    path = root / name
    (path / "agents").mkdir(parents=True, exist_ok=True)
    if malformed:
        (path / "SKILL.md").write_text("# no metadata", encoding="utf-8")
    else:
        content = "---\nname: %s\ndescription: %s\n---\n\n%s" % (name, description, body)
        (path / "SKILL.md").write_text(content, encoding="utf-8")
    yaml_lines = [
        "interface:",
        f'  display_name: "{name}"',
        f'  short_description: "{description}"',
        f'  default_prompt: "Use ${name}"',
        "",
        "policy:",
        f"  allow_implicit_invocation: {str(allow_implicit).lower()}",
    ]
    if hosts:
        if block_hosts:
            yaml_lines.append("hosts:")
            for h in hosts.split(","):
                yaml_lines.append(f"  - {h.strip()}")
        else:
            yaml_lines.append(f"hosts: [{hosts}]")
    (path / "agents" / "openai.yaml").write_text("\n".join(yaml_lines), encoding="utf-8")
    return path


def run_scanner(scanner: Path, *, mode: str = "", roots_json: str, context_json: str, host_name: str = "") -> dict:
    cmd = ["pwsh", "-File", str(scanner)]
    if mode:
        cmd += ["-Mode", mode]
    if host_name:
        cmd += ["-HostName", host_name]
    cmd += ["-RootsJson", roots_json, "-ContextJson", context_json]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


@unittest.skipUnless(HAS_PWSH, "pwsh not available; ask-light behavior suite requires PowerShell")
class AskLightBehaviorTest(unittest.TestCase):
    def test_ask_light_behavior(self) -> None:
        c = Checks()
        scanner = ROOT / "skills/ask-light/scripts/ask-light.ps1"
        with tempfile.TemporaryDirectory(prefix="ask-light-") as tmp:
            fixture = Path(tmp)
            categories = ("project", "global", "first-party", "upstream", "modified-third-party", "other")
            roots = []
            for category in categories:
                category_root = fixture / category
                category_root.mkdir(parents=True, exist_ok=True)
                roots.append({"category": category, "path": str(category_root)})

            new_skill(fixture / "project", "local-helper", "A generic local project helper.")
            new_skill(fixture / "global", "global-helper", "A generic global helper.", allow_implicit=True)
            new_skill(fixture / "first-party", "manuscript-review", "Review manuscript documents and source evidence.")
            new_skill(fixture / "upstream", "research", "Research primary sources and synthesize evidence.", allow_implicit=True)
            new_skill(fixture / "modified-third-party", "data-adapter", "Analyze data and repair compatibility issues.")
            new_skill(fixture / "other", "knowledge-notes", "Organize knowledge notes and links.")

            new_skill(fixture / "project", "shared", "A shared project Skill.")
            new_skill(fixture / "upstream", "shared", "A shared upstream Skill.")

            new_skill(fixture / "other", "broken-metadata", "ignored", malformed=True)
            incomplete_path = fixture / "other" / "incomplete-metadata"
            (incomplete_path / "agents").mkdir(parents=True, exist_ok=True)
            (incomplete_path / "SKILL.md").write_text("---\nname: incomplete-metadata\ndescription: Incomplete metadata fixture.\n---\n\nBody", encoding="utf-8")
            (incomplete_path / "agents" / "openai.yaml").write_text("interface:\npolicy:\n  allow_implicit_invocation: false", encoding="utf-8")

            for i in range(1, 26):
                new_skill(fixture / "other", f"catalog-{i}", "A catalog entry with no matching task.", body=f"SENTINEL-BODY-{i}")

            roots_json = json.dumps(roots)
            software_context = json.dumps({
                "goal": "review software source changes", "artifacts": ["src/parser.ts"], "blockers": "",
                "projectType": "software", "taskKind": "review", "availability": "codex", "invocationControl": "explicit-only",
            })
            result = run_scanner(scanner, roots_json=roots_json, context_json=software_context)

            c.check(result.get("status") == "RECOMMEND", "available catalog returns recommendation")
            c.check(result.get("skill") == "manuscript-review", "context selects the best manuscript review fit")
            c.check(bool(re_match(r"^first-party:", result.get("source", ""))), "first-party source is retained in recommendation")
            c.check(result.get("invocation") == "$manuscript-review", "Codex invocation is explicit and host-appropriate")
            c.check(bool(re_match(r"nothing was invoked or installed", result.get("execution", ""))), "recommendation does not execute or install")
            c.check(result.get("reads", {}).get("metadata", 0) >= 30 and result.get("reads", {}).get("bodies", 99) <= 3, "large catalog uses metadata-first bounded body reads")
            for category in categories:
                c.check(any(x.get("sourceCategory") == category for x in result.get("candidates", [])), f"{category} source discovered")
            c.check(len([x for x in result.get("candidates", []) if x.get("name") == "shared"]) == 2, "duplicate names remain distinct records")
            c.check(len([g for g in result.get("gaps", []) if "broken-metadata" in g]) == 1, "unavailable metadata is reported as a gap")
            c.check(len([x for x in result.get("candidates", []) if x.get("name") == "broken-metadata" and x.get("metadataStatus") == "unavailable" and "other" in x.get("packagePath", "")]) == 1, "malformed metadata candidate is retained with source and path")
            c.check(len([x for x in result.get("candidates", []) if x.get("name") == "incomplete-metadata" and x.get("metadataStatus") == "unavailable" and re_match(r"displayName|shortDescription|defaultPrompt", x.get("metadataError", ""))]) == 1, "incomplete metadata fields are explicitly unavailable")

            amb_root = fixture / "ambiguous"
            amb_root.mkdir()
            new_skill(amb_root, "review-code", "Review changes and verify acceptance.")
            new_skill(amb_root, "review-spec", "Review specification requirements and verify acceptance.")
            amb_roots = json.dumps([{"category": "project", "path": str(amb_root)}])
            amb_context = json.dumps({
                "goal": "review and verify acceptance", "artifacts": ["artifact.md"], "blockers": "",
                "projectType": "generic", "taskKind": "review", "availability": "codex", "invocationControl": "explicit-only",
            })
            ambiguous = run_scanner(scanner, roots_json=amb_roots, context_json=amb_context)
            c.check(ambiguous.get("status") == "RECOMMEND" and ambiguous.get("alternative") is not None, "genuine tie returns exactly one alternative")

            equiv_root = fixture / "equivalent"
            equiv_root.mkdir()
            new_skill(equiv_root, "review-one", "Review artifacts and verify acceptance.")
            new_skill(equiv_root, "review-two", "Review artifacts and verify acceptance.")
            equiv_roots = json.dumps([{"category": "project", "path": str(equiv_root)}])
            equiv = run_scanner(scanner, roots_json=equiv_roots, context_json=amb_context)
            c.check(equiv.get("status") == "RECOMMEND" and equiv.get("alternative") is None, "equivalent tied actions suppress alternative")

            host_root = fixture / "host-filter"
            host_root.mkdir()
            new_skill(host_root, "claude-review", "Review software changes and verify acceptance.", hosts="claude")
            new_skill(host_root, "claude-block", "Review software changes and verify acceptance.", hosts="claude", block_hosts=True)
            new_skill(host_root, "codex-review", "Review software changes.", hosts="codex")
            host_roots = json.dumps([{"category": "project", "path": str(host_root)}])
            host_availability = {"host": "codex", "readablePaths": [str(host_root)], "unavailableSkills": []}
            host_context = json.dumps({
                "goal": "review software changes", "artifacts": ["src/parser.ts"], "blockers": "",
                "projectType": "software", "taskKind": "review", "availability": host_availability, "invocationControl": "explicit-only",
            })
            host_result = run_scanner(scanner, host_name="codex", roots_json=host_roots, context_json=host_context)
            c.check(host_result.get("status") == "RECOMMEND" and host_result.get("skill") == "codex-review", "host availability selects compatible Skill")
            c.check(len([x for x in host_result.get("candidates", []) if x.get("name") == "claude-review" and x.get("availabilityStatus") == "unavailable"]) == 1, "host-incompatible Skill is not eligible")
            c.check(len([x for x in host_result.get("candidates", []) if x.get("name") == "claude-block" and x.get("availabilityStatus") == "unavailable"]) == 1, "block-list host incompatibility is not eligible")
            c.check("host 'codex' is not declared" in " ".join(host_result.get("gaps", [])), "host incompatibility has actionable gap")

            # Negative cross-platform path boundary: a package OUTSIDE the host's
            # readable paths must be unavailable (pins the platform-native
            # separator handling in the scanner's Test-PathUnder).
            path_root = fixture / "path-filter"
            outside_dir = fixture / "outside-readable"
            path_root.mkdir()
            outside_dir.mkdir()
            new_skill(path_root, "inside-skill", "Review software changes.")
            new_skill(outside_dir, "outside-skill", "Review software changes.")
            path_roots = json.dumps([
                {"category": "project", "path": str(path_root)},
                {"category": "project", "path": str(outside_dir)},
            ])
            path_availability = {"host": "codex", "readablePaths": [str(path_root)], "unavailableSkills": []}
            path_context = json.dumps({
                "goal": "review software changes", "artifacts": ["src/parser.ts"], "blockers": "",
                "projectType": "software", "taskKind": "review", "availability": path_availability, "invocationControl": "explicit-only",
            })
            path_result = run_scanner(scanner, host_name="codex", roots_json=path_roots, context_json=path_context)
            c.check(path_result.get("status") == "RECOMMEND" and path_result.get("skill") == "inside-skill", "readable-path filter keeps the compatible Skill eligible")
            c.check(len([x for x in path_result.get("candidates", []) if x.get("name") == "outside-skill" and x.get("availabilityStatus") == "unavailable"]) == 1, "package outside host readable paths is not eligible")
            c.check("package path is outside host readable paths" in " ".join(path_result.get("gaps", [])), "outside-readable-path candidate has actionable gap")

            read_fail_root = fixture / "read-failure"
            read_fail_root.mkdir()
            new_skill(read_fail_root, "broken-body", "Review software changes.", body="[missing](references/missing.md)")
            read_fail_roots = json.dumps([{"category": "project", "path": str(read_fail_root)}])
            read_fail = run_scanner(scanner, roots_json=read_fail_roots, context_json=amb_context)
            c.check(read_fail.get("status") == "BLOCKED", "unreadable shortlisted reference blocks recommendation")
            c.check(len([x for x in read_fail.get("candidates", []) if x.get("name") == "broken-body" and x.get("readStatus") == "unavailable"]) == 1, "unreadable shortlisted candidate is marked ineligible")
            c.check(bool(re_match(r"body/reference unreadable|restore", " ".join(read_fail.get("gaps", [])))), "unreadable body/reference has actionable gap")

            clear_context = json.dumps({
                "goal": "review software parser implementation", "artifacts": ["src/parser.ts"], "blockers": "",
                "projectType": "software", "taskKind": "implementation", "availability": "codex", "invocationControl": "explicit-only",
            })
            clear = run_scanner(scanner, roots_json=roots_json, context_json=clear_context)
            c.check(clear.get("alternative") is None, "clear winner has no alternative")

            missing_root = fixture / "missing"
            missing_root.mkdir()
            new_skill(missing_root, "unreadable", "not usable", malformed=True)
            missing_roots = json.dumps([{"category": "global", "path": str(missing_root)}])
            missing_context = json.dumps({
                "goal": "something", "artifacts": [], "blockers": "",
                "projectType": "generic", "taskKind": "implementation", "availability": "codex", "invocationControl": "explicit-only",
            })
            missing = run_scanner(scanner, roots_json=missing_roots, context_json=missing_context)
            c.check(missing.get("status") == "BLOCKED" and bool(re_match(r"Install or restore|unreadable", " ".join(missing.get("gaps", [])))), "missing Skill gives actionable guidance")

            input_context = json.dumps({
                "goal": "", "artifacts": [], "blockers": "",
                "projectType": "generic", "taskKind": "", "availability": "codex", "invocationControl": "explicit-only",
            })
            input_result = run_scanner(scanner, roots_json=roots_json, context_json=input_context)
            c.check(input_result.get("status") == "NEED-INPUT" and bool(re_match(r"goal and taskKind", " ".join(input_result.get("gaps", [])))), "unknown context asks for input instead of guessing")

            recap_root = fixture / "recap-discovery"
            recap_root.mkdir()
            new_skill(recap_root, "recap", "Generate exactly one line summarizing the current Agent session.")
            new_skill(recap_root, "generic-helper", "Perform generic project maintenance.")
            recap_roots = json.dumps([{"category": "first-party", "path": str(recap_root)}])
            recap_context = json.dumps({
                "goal": "summarize the current session in one line", "artifacts": [], "blockers": "",
                "projectType": "generic", "taskKind": "recap", "availability": "codex", "invocationControl": "explicit-only",
            })
            recap_result = run_scanner(scanner, roots_json=recap_roots, context_json=recap_context)
            c.check(recap_result.get("status") == "RECOMMEND" and recap_result.get("skill") == "recap", "direct session-summary request discovers recap")
            c.check(recap_result.get("invocation") == "$recap" and bool(re_match(r"nothing was invoked", recap_result.get("execution", ""))), "recap recommendation preserves explicit-only non-execution boundary")

            workflow_root = fixture / "workflow"
            wf_first = workflow_root / "first-party"
            wf_upstream = workflow_root / "upstream"
            wf_third = workflow_root / "modified-third-party"
            for d in (wf_first, wf_upstream, wf_third):
                d.mkdir(parents=True)
            for name in ("review-loop", "ask-light", "project-init", "learn-anything", "manuscript-ops", "recap"):
                new_skill(wf_first, name, f"First-party {name} capability.")
            for name in ("to-spec", "to-tickets", "implement", "code-review", "handoff", "diagnosing-bugs", "grill-me", "wayfinder", "writing-great-skills"):
                new_skill(wf_upstream, name, f"Upstream {name} capability.", allow_implicit=True)
            new_skill(wf_third, "code-review", "Modified third-party code review capability.", allow_implicit=True)
            wf_roots = json.dumps([
                {"category": "first-party", "path": str(wf_first)},
                {"category": "upstream", "path": str(wf_upstream)},
                {"category": "modified-third-party", "path": str(wf_third)},
            ])
            feature_context = json.dumps({
                "goal": "build a software feature with acceptance criteria", "artifacts": ["brief.md"], "blockers": "",
                "projectType": "software", "taskKind": "feature", "availability": "codex", "invocationControl": "explicit-only",
            })
            feature_workflow = run_scanner(scanner, mode="workflow", roots_json=wf_roots, context_json=feature_context)
            c.check(feature_workflow.get("status") == "RECOMMEND" and feature_workflow.get("workflow") == "software-feature", "software feature workflow is recommended")
            c.check(len(feature_workflow.get("steps", [])) == 7, "software feature workflow exposes all handoff steps")
            c.check(len([s for s in feature_workflow.get("steps", []) if s.get("skill") == "review-loop"]) == 2, "software feature workflow retains both review-loop boundaries")
            c.check(feature_workflow.get("finalAuthority") == "review-loop" and bool(re_match(r"PASS|FAIL|BLOCKED", feature_workflow.get("stoppingBoundary", ""))), "workflow reports final authority and stopping boundary")
            c.check(bool(re_match(r"nothing was invoked|orchestrated", feature_workflow.get("execution", ""))), "workflow recommendation does not execute or orchestrate")
            c.check(len([s for s in feature_workflow.get("steps", []) if s.get("skill") == "to-spec" and s.get("sourceCategory") == "upstream"]) == 1, "workflow preserves third-party source category")
            c.check(len([s for s in feature_workflow.get("steps", []) if s.get("skill") == "code-review" and s.get("sourceCategory") == "upstream" and s.get("availability") == "available"]) == 1, "workflow selects the declared source category when duplicate Skill names exist")
            reads = feature_workflow.get("reads", {})
            c.check(reads.get("metadata") == 16 and reads.get("bodies") == 0 and reads.get("references") == 0, "workflow exposes bounded metadata-only read counts")

            bug_context = json.dumps({
                "goal": "diagnose a software regression and repair the error", "artifacts": ["failing-test.txt"], "blockers": "",
                "projectType": "software", "taskKind": "bug", "availability": "codex", "invocationControl": "explicit-only",
            })
            bug_workflow = run_scanner(scanner, mode="workflow", roots_json=wf_roots, context_json=bug_context)
            c.check(bug_workflow.get("workflow") == "bug-diagnosis" and len([s for s in bug_workflow.get("steps", []) if s.get("skill") == "diagnosing-bugs"]) == 1, "bug diagnosis workflow selects diagnosing-bugs")

            manuscript_context = json.dumps({
                "goal": "start a manuscript project with explicit handoffs", "artifacts": ["brief.md"], "blockers": "",
                "projectType": "manuscript", "taskKind": "initialization", "availability": "codex", "invocationControl": "explicit-only",
            })
            manuscript_workflow = run_scanner(scanner, mode="workflow", roots_json=wf_roots, context_json=manuscript_context)
            c.check(manuscript_workflow.get("status") == "RECOMMEND" and manuscript_workflow.get("workflow") == "manuscript-project", "manuscript workflow is recommended")
            c.check(bool(re_match(r"handoff", manuscript_workflow.get("stoppingBoundary", ""))) and len([s for s in manuscript_workflow.get("steps", []) if s.get("skill") == "project-init" and s.get("invocationType") == "user-invoked"]) == 1, "manuscript workflow preserves explicit handoff and invocation boundary")

            mismatched_context = json.dumps({
                "goal": "write a manuscript and plan chapters", "artifacts": ["brief.md"], "blockers": "",
                "projectType": "generic", "taskKind": "maintenance", "availability": "codex", "invocationControl": "explicit-only",
            })
            mismatched_workflow = run_scanner(scanner, mode="workflow", roots_json=wf_roots, context_json=mismatched_context)
            c.check(mismatched_workflow.get("status") == "NEED-INPUT" and mismatched_workflow.get("workflow") == "", "mismatched project type and task kind do not select a manuscript recipe")

            missing_project_type_context = json.dumps({
                "goal": "build a software feature", "artifacts": ["brief.md"], "blockers": "",
                "projectType": "", "taskKind": "feature", "availability": "codex", "invocationControl": "explicit-only",
            })
            missing_project_type = run_scanner(scanner, mode="workflow", roots_json=wf_roots, context_json=missing_project_type_context)
            c.check(missing_project_type.get("status") == "NEED-INPUT" and bool(re_match(r"projectType", " ".join(missing_project_type.get("gaps", [])))), "workflow requires project type before matching a recipe")

            incomplete_workflow_context = json.dumps({"goal": "build a software feature", "projectType": "software", "taskKind": "feature"})
            incomplete_workflow = run_scanner(scanner, mode="workflow", roots_json=wf_roots, context_json=incomplete_workflow_context)
            c.check(incomplete_workflow.get("status") == "NEED-INPUT" and bool(re_match(r"artifacts.*blockers.*availability.*invocationControl", " ".join(incomplete_workflow.get("gaps", [])))), "workflow requires the remaining context fields instead of assuming them")

            invalid_availability_context = json.dumps({
                "goal": "build a software feature", "artifacts": ["brief.md"], "blockers": "",
                "projectType": "software", "taskKind": "feature", "availability": {}, "invocationControl": "explicit-only",
            })
            invalid_availability = run_scanner(scanner, mode="workflow", roots_json=wf_roots, context_json=invalid_availability_context)
            c.check(invalid_availability.get("status") == "NEED-INPUT" and bool(re_match(r"availability", " ".join(invalid_availability.get("gaps", [])))), "empty availability context is not treated as reliable")

            invalid_invocation_context = json.dumps({
                "goal": "build a software feature", "artifacts": ["brief.md"], "blockers": "",
                "projectType": "software", "taskKind": "feature", "availability": "codex", "invocationControl": "automatic",
            })
            invalid_invocation = run_scanner(scanner, mode="workflow", roots_json=wf_roots, context_json=invalid_invocation_context)
            c.check(invalid_invocation.get("status") == "NEED-INPUT" and bool(re_match(r"invocationControl", " ".join(invalid_invocation.get("gaps", [])))), "unknown invocation control is not accepted as reliable context")

            source_context = json.dumps({
                "goal": "learn a reusable Skill method from source material", "artifacts": ["transcript.md"], "blockers": "",
                "projectType": "skill-development", "taskKind": "skill-development", "availability": "codex", "invocationControl": "explicit-only",
            })
            source_workflow = run_scanner(scanner, mode="workflow", roots_json=wf_roots, context_json=source_context)
            learn_steps = [s for s in source_workflow.get("steps", []) if s.get("skill") == "learn-anything"]
            c.check(source_workflow.get("workflow") == "source-to-skill" and learn_steps and learn_steps[0].get("availability") == "available", "source-to-skill workflow recommends learn-anything")
            c.check(learn_steps[0].get("invocationType") == "user-invoked" and bool(re_match(r"nothing was invoked", source_workflow.get("execution", ""))), "explicit-only mode does not exclude learn-anything and remains non-executing")

            new_project_context = json.dumps({
                "goal": "initialize a new project", "artifacts": [], "blockers": "",
                "projectType": "generic", "taskKind": "initialization", "availability": "codex", "invocationControl": "explicit-only",
            })
            new_project_workflow = run_scanner(scanner, mode="workflow", roots_json=wf_roots, context_json=new_project_context)
            c.check(new_project_workflow.get("workflow") == "new-project-initialization", "new project initialization workflow is recommended")

            final_context = json.dumps({
                "goal": "perform the final acceptance review and issue a verdict", "artifacts": ["evidence.md"], "blockers": "",
                "projectType": "generic", "taskKind": "final-review", "availability": "codex", "invocationControl": "explicit-only",
            })
            final_workflow = run_scanner(scanner, mode="workflow", roots_json=wf_roots, context_json=final_context)
            c.check(final_workflow.get("workflow") == "final-review" and len(final_workflow.get("steps", [])) == 1 and final_workflow.get("finalAuthority") == "review-loop", "final review workflow delegates final authority to review-loop")

            private_root = fixture / "private-third-party"
            private_root.mkdir()
            new_skill(private_root, "review-loop", "First-party final acceptance.")
            private_roots = json.dumps([{"category": "first-party", "path": str(private_root)}])
            private_context = json.dumps({
                "goal": "resolve a private third-party dependency", "artifacts": [], "blockers": "",
                "projectType": "generic", "taskKind": "dependency", "availability": "codex", "invocationControl": "explicit-only",
            })
            private_workflow = run_scanner(scanner, mode="workflow", roots_json=private_roots, context_json=private_context)
            c.check(private_workflow.get("status") == "BLOCKED" and bool(re_match(r"private skills-3rdParty", " ".join(private_workflow.get("gaps", [])))), "missing private third-party dependency is BLOCKED with an availability gap")
            c.check(len([s for s in private_workflow.get("steps", []) if s.get("skill") == "code-review" and s.get("availability") == "unavailable"]) == 1, "missing private dependency step is explicitly unavailable")

            learn_missing_root = fixture / "learn-missing"
            (learn_missing_root / "learn-anything" / "agents").mkdir(parents=True)
            (learn_missing_root / "learn-anything" / "SKILL.md").write_text("---\nname: learn-anything\ndescription: Learn from source.\n---\n\nBody", encoding="utf-8")
            (learn_missing_root / "learn-anything" / "agents" / "openai.yaml").write_text("interface:\npolicy:\n  allow_implicit_invocation: false", encoding="utf-8")
            learn_missing_roots = json.dumps([{"category": "first-party", "path": str(learn_missing_root)}])
            learn_missing = run_scanner(scanner, roots_json=learn_missing_roots, context_json=source_context)
            c.check(learn_missing.get("status") == "BLOCKED" and bool(re_match(r"learn-anything", " ".join(learn_missing.get("gaps", [])))), "missing learn-anything metadata blocks a workflow recommendation")

            ambiguous_context = json.dumps({
                "goal": "unclear work with no reliable route", "artifacts": [], "blockers": "",
                "projectType": "generic", "taskKind": "maintenance", "availability": "codex", "invocationControl": "explicit-only",
            })
            ambiguous_workflow = run_scanner(scanner, mode="workflow", roots_json=wf_roots, context_json=ambiguous_context)
            c.check(ambiguous_workflow.get("status") == "NEED-INPUT" and bool(re_match(r"No reliable workflow recipe", " ".join(ambiguous_workflow.get("gaps", [])))), "ambiguous workflow requests input instead of guessing")

        self.assertGreater(c.assertions, 0)
        self.assertFalse(c.failures, f"ask-light behavior failed: {c.failures}")


def re_match(pattern: str, text: str) -> bool:
    import re

    return bool(re.search(pattern, text, flags=re.IGNORECASE))


if __name__ == "__main__":
    unittest.main(verbosity=2)
