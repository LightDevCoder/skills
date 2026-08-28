#!/usr/bin/env python3
"""Pre-fix reproductions A-H against baseline 38f4f9b.

Demonstrates that without durable review transaction coherence in ask-light:
- Active non-terminal states (READY, CRITIC, REPAIR, EVALUATE) with old PASS verdicts incorrectly returned accepted.
- Missing state.md incorrectly returned accepted.
- Changed Charter revision with old review revision incorrectly returned accepted.
- Profile mismatch (Charter generic vs State software) incorrectly returned accepted.
- State FAIL with old Verdict PASS incorrectly returned accepted.
"""

from __future__ import annotations

import sys
import tempfile
import subprocess
from pathlib import Path

# Add ask-light to sys.path
ASK_LIGHT_DIR = Path(__file__).resolve().parents[3] / "skills" / "ask-light" / "scripts"
sys.path.insert(0, str(ASK_LIGHT_DIR))
import ask_light


def setup_base():
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name) / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "test"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "test@test.com"], check=True)
    (root / "docs" / "agents").mkdir(parents=True)
    (root / "docs" / "agents" / "light-project.md").write_text("# Contract\n- Goal: test\n- Outputs: test\n")
    (root / "SPEC.md").write_text("# SPEC\n- Status: approved\n")
    (root / ".scratch" / "e1" / "issues").mkdir(parents=True)
    (root / ".scratch" / "e1" / "spec.md").write_text("# SPEC\n- Status: approved\n")
    (root / ".scratch" / "e1" / "issues" / "01.md").write_text("# Ticket 1\n- Status: done\n")
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("print(1)\n")
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "c1"], check=True)
    c1 = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    return temp, root, c1


def main():
    print("=== Pre-fix Reproduction Matrix (Baseline 38f4f9b) ===")
    
    # Test A: State READY, Verdict PASS
    temp, root, c1 = setup_base()
    rdir = root / ".project-review"
    rdir.mkdir()
    (rdir / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Source: .scratch/e1/spec.md\n- Source revision or identity: commit {c1}\n- Profile: generic\n")
    (rdir / "state.md").write_text("# State\n- Status: READY\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    (rdir / "verdict.md").write_text("# Verdict\n- Verdict: **PASS**\n")
    res = ask_light.inspect_project_state(root)
    print("A (READY + PASS):", res["stage"], "| skill:", res["skill"])

    # Test B: State CRITIC, Verdict PASS
    (rdir / "state.md").write_text("# State\n- Status: CRITIC\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    res = ask_light.inspect_project_state(root)
    print("B (CRITIC + PASS):", res["stage"], "| skill:", res["skill"])

    # Test C: State REPAIR, Verdict PASS
    (rdir / "state.md").write_text("# State\n- Status: REPAIR\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    res = ask_light.inspect_project_state(root)
    print("C (REPAIR + PASS):", res["stage"], "| skill:", res["skill"])

    # Test D: State EVALUATE, Verdict PASS
    (rdir / "state.md").write_text("# State\n- Status: EVALUATE\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    res = ask_light.inspect_project_state(root)
    print("D (EVALUATE + PASS):", res["stage"], "| skill:", res["skill"])

    # Test E: state.md missing, Verdict PASS
    (rdir / "state.md").unlink()
    res = ask_light.inspect_project_state(root)
    print("E (missing state.md + PASS):", res["stage"], "| skill:", res["skill"])

    # Test F: Charter rev 2, State rev 1, Verdict PASS
    (rdir / "charter.md").write_text(f"# Charter\n- Charter revision: 2\n- Source: .scratch/e1/spec.md\n- Source revision or identity: commit {c1}\n- Profile: generic\n")
    (rdir / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    res = ask_light.inspect_project_state(root)
    print("F (Charter rev 2, State rev 1 + PASS):", res["stage"], "| skill:", res["skill"])

    # Test G: State Profile != Charter Profile
    (rdir / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Source: .scratch/e1/spec.md\n- Source revision or identity: commit {c1}\n- Profile: generic\n")
    (rdir / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: software\n- Round: 1\n")
    res = ask_light.inspect_project_state(root)
    print("G (Profile mismatch generic vs software):", res["stage"], "| skill:", res["skill"])

    # Test H: State FAIL, Verdict PASS
    (rdir / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Source: .scratch/e1/spec.md\n- Source revision or identity: commit {c1}\n- Profile: generic\n")
    (rdir / "state.md").write_text("# State\n- Status: FAIL\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    res = ask_light.inspect_project_state(root)
    print("H (State FAIL + Verdict PASS):", res["stage"], "| skill:", res["skill"])


if __name__ == "__main__":
    main()
