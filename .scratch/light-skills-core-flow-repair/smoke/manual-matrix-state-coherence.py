#!/usr/bin/env python3
"""Manual smoke test suite covering the 24 required review state coherence scenarios."""

from __future__ import annotations

import sys
import tempfile
import subprocess
from pathlib import Path

ASK_LIGHT_DIR = Path(__file__).resolve().parents[3] / "skills" / "ask-light" / "scripts"
sys.path.insert(0, str(ASK_LIGHT_DIR))
import ask_light


def run_smoke():
    results = []
    
    def make_base():
        t = tempfile.TemporaryDirectory()
        r = Path(t.name) / "repo"
        r.mkdir()
        subprocess.run(["git", "init", "-q", str(r)], check=True)
        subprocess.run(["git", "-C", str(r), "config", "user.name", "smoke"], check=True)
        subprocess.run(["git", "-C", str(r), "config", "user.email", "smoke@example.com"], check=True)
        (r / "docs" / "agents").mkdir(parents=True)
        (r / "docs" / "agents" / "light-project.md").write_text("# Contract\n- Goal: smoke\n- Outputs: smoke\n")
        (r / "SPEC.md").write_text("# SPEC\n- Status: approved\n")
        (r / ".scratch" / "cur" / "issues").mkdir(parents=True)
        (r / ".scratch" / "cur" / "spec.md").write_text("# SPEC\n- Status: approved\n")
        (r / ".scratch" / "cur" / "issues" / "01.md").write_text("# Ticket 1\n- Status: done\n")
        (r / "src").mkdir()
        (r / "src" / "app.py").write_text("print(1)\n")
        subprocess.run(["git", "-C", str(r), "add", "."], check=True)
        subprocess.run(["git", "-C", str(r), "commit", "-qm", "base"], check=True)
        base_sha = subprocess.check_output(["git", "-C", str(r), "rev-parse", "HEAD"], text=True).strip()
        (r / "src" / "app.py").write_text("print(2)\n")
        subprocess.run(["git", "-C", str(r), "add", "."], check=True)
        subprocess.run(["git", "-C", str(r), "commit", "-qm", "candidate"], check=True)
        cand_sha = subprocess.check_output(["git", "-C", str(r), "rev-parse", "HEAD"], text=True).strip()
        return t, r, base_sha, cand_sha

    # 1. coherent PASS transaction -> accepted
    t, r, b, c = make_base()
    rd = r / ".project-review"
    rd.mkdir()
    (rd / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Source: .scratch/cur/spec.md\n- Source revision or identity: commit {b}\n- Profile: generic\n")
    (rd / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    (rd / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n")
    res = ask_light.inspect_project_state(r)
    results.append(("1. coherent PASS transaction", res["stage"], res["skill"], res["stage"] == "accepted"))

    # 2. READY + old PASS -> project-review
    (rd / "state.md").write_text("# State\n- Status: READY\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    res = ask_light.inspect_project_state(r)
    results.append(("2. READY + old PASS", res["stage"], res["skill"], res["stage"] == "project-review" and res["skill"] == "project-review"))

    # 3. CRITIC + old PASS -> project-review
    (rd / "state.md").write_text("# State\n- Status: CRITIC\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    res = ask_light.inspect_project_state(r)
    results.append(("3. CRITIC + old PASS", res["stage"], res["skill"], res["stage"] == "project-review" and res["skill"] == "project-review"))

    # 4. REPAIR + old PASS -> project-review
    (rd / "state.md").write_text("# State\n- Status: REPAIR\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    res = ask_light.inspect_project_state(r)
    results.append(("4. REPAIR + old PASS", res["stage"], res["skill"], res["stage"] == "project-review" and res["skill"] == "project-review"))

    # 5. EVALUATE + old PASS -> project-review
    (rd / "state.md").write_text("# State\n- Status: EVALUATE\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    res = ask_light.inspect_project_state(r)
    results.append(("5. EVALUATE + old PASS", res["stage"], res["skill"], res["stage"] == "project-review" and res["skill"] == "project-review"))

    # 6. missing state.md -> not accepted
    (rd / "state.md").unlink()
    res = ask_light.inspect_project_state(r)
    results.append(("6. missing state.md", res["stage"], res["skill"], res["stage"] == "review-state-unknown"))

    # 7. missing Status -> not accepted
    (rd / "state.md").write_text("# State\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    res = ask_light.inspect_project_state(r)
    results.append(("7. missing Status", res["stage"], res["skill"], res["stage"] == "review-state-unknown"))

    # 8. duplicate Status -> not accepted
    (rd / "state.md").write_text("# State\n- Status: PASS\n- Status: READY\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    res = ask_light.inspect_project_state(r)
    results.append(("8. duplicate Status", res["stage"], res["skill"], res["stage"] == "review-state-unknown"))

    # 9. unknown Status -> not accepted
    (rd / "state.md").write_text("# State\n- Status: UNKNOWN-STAGE\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    res = ask_light.inspect_project_state(r)
    results.append(("9. unknown Status", res["stage"], res["skill"], res["stage"] == "review-state-unknown"))

    # 10. State FAIL + Verdict PASS -> not accepted
    (rd / "state.md").write_text("# State\n- Status: FAIL\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    res = ask_light.inspect_project_state(r)
    results.append(("10. State FAIL + Verdict PASS", res["stage"], res["skill"], res["stage"] == "acceptance-unknown"))

    # 11. State PASS + Verdict FAIL -> not accepted
    (rd / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    (rd / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **FAIL**\n")
    res = ask_light.inspect_project_state(r)
    results.append(("11. State PASS + Verdict FAIL", res["stage"], res["skill"], res["stage"] == "acceptance-unknown"))

    # 12. State BLOCKED + Verdict PASS -> not accepted
    (rd / "state.md").write_text("# State\n- Status: BLOCKED\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    (rd / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n")
    res = ask_light.inspect_project_state(r)
    results.append(("12. State BLOCKED + Verdict PASS", res["stage"], res["skill"], res["stage"] == "acceptance-unknown"))

    # 13. Charter revision mismatch -> not accepted
    (rd / "charter.md").write_text(f"# Charter\n- Charter revision: 2\n- Source: .scratch/cur/spec.md\n- Source revision or identity: commit {b}\n- Profile: generic\n")
    (rd / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    (rd / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n")
    res = ask_light.inspect_project_state(r)
    results.append(("13. Charter revision mismatch", res["stage"], res["skill"], res["stage"] == "review-state-unknown"))

    # 14. Profile mismatch -> not accepted
    (rd / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Source: .scratch/cur/spec.md\n- Source revision or identity: commit {b}\n- Profile: generic\n")
    (rd / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: software\n- Round: 1\n")
    res = ask_light.inspect_project_state(r)
    results.append(("14. Profile mismatch", res["stage"], res["skill"], res["stage"] == "review-state-unknown"))

    # 15. rev1 PASS -> accepted
    (rd / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Source: .scratch/cur/spec.md\n- Source revision or identity: commit {b}\n- Profile: generic\n")
    (rd / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    (rd / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n")
    res = ask_light.inspect_project_state(r)
    results.append(("15. rev1 PASS", res["stage"], res["skill"], res["stage"] == "accepted"))

    # 16. Charter changes to rev2 -> old review not accepted
    (rd / "charter.md").write_text(f"# Charter\n- Charter revision: 2\n- Source: .scratch/cur/spec.md\n- Source revision or identity: commit {b}\n- Profile: generic\n")
    res = ask_light.inspect_project_state(r)
    results.append(("16. Charter changes to rev2", res["stage"], res["skill"], res["stage"] == "review-state-unknown"))

    # 17. READY rev2 -> project-review
    (rd / "state.md").write_text("# State\n- Status: READY\n- Charter revision: 2\n- Profile: generic\n- Round: 1\n")
    res = ask_light.inspect_project_state(r)
    results.append(("17. READY rev2", res["stage"], res["skill"], res["stage"] == "project-review" and res["skill"] == "project-review"))

    # 18. PASS rev2 + fresh PASS -> accepted
    (rd / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 2\n- Profile: generic\n- Round: 1\n")
    (rd / "verdict.md").write_text("# Verdict\n- Charter revision: 2\n- Profile: generic\n- Verdict: **PASS**\n")
    res = ask_light.inspect_project_state(r)
    results.append(("18. PASS rev2 + fresh PASS", res["stage"], res["skill"], res["stage"] == "accepted"))

    # 19. C1->repair->C2 PASS -> accepted
    t2, r2, b2, c2_1 = make_base()
    (r2 / "src" / "app.py").write_text("print(3)\n")
    subprocess.run(["git", "-C", str(r2), "add", "."], check=True)
    subprocess.run(["git", "-C", str(r2), "commit", "-qm", "c2"], check=True)
    c2_2 = subprocess.check_output(["git", "-C", str(r2), "rev-parse", "HEAD"], text=True).strip()
    rd2 = r2 / ".project-review"
    rd2.mkdir()
    (rd2 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Source: .scratch/cur/spec.md\n- Source revision or identity: commit {b2}\n- Profile: software\n- Fixed point: {b2}\n- Implementation scope: src/\n")
    (rd2 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: software\n- Round: 2\n")
    (rd2 / "verdict.md").write_text(f"# Verdict\n- Charter revision: 1\n- Profile: software\n- Verdict: **PASS**\n- Reviewed implementation revision: {c2_2}\n")
    res = ask_light.inspect_project_state(r2)
    results.append(("19. C1->repair->C2 PASS", res["stage"], res["skill"], res["stage"] == "accepted"))

    # 20. reopen C2 review -> old PASS not accepted
    (rd2 / "state.md").write_text("# State\n- Status: READY\n- Charter revision: 1\n- Profile: software\n- Round: 3\n")
    res = ask_light.inspect_project_state(r2)
    results.append(("20. reopen C2 review", res["stage"], res["skill"], res["stage"] == "project-review"))

    # 21. post-C2 in-scope drift -> stale when terminal PASS is current
    (rd2 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: software\n- Round: 3\n")
    (r2 / "src" / "app.py").write_text("print(4)\n")
    res = ask_light.inspect_project_state(r2)
    results.append(("21. post-C2 in-scope drift", res["stage"], res["skill"], res["stage"] == "review-stale"))

    # 22. out-of-scope README -> accepted when terminal PASS is current
    subprocess.run(["git", "-C", str(r2), "checkout", "-q", "--", "src/app.py"], check=True)
    (r2 / "README.md").write_text("# Update README\n")
    res = ask_light.inspect_project_state(r2)
    results.append(("22. out-of-scope README", res["stage"], res["skill"], res["stage"] == "accepted"))

    # 23. ignored in-scope implementation file -> stale
    (r2 / ".gitignore").write_text("src/extra.py\n")
    (r2 / "src" / "extra.py").write_text("extra\n")
    res = ask_light.inspect_project_state(r2)
    results.append(("23. ignored in-scope implementation file", res["stage"], res["skill"], res["stage"] == "review-stale"))

    # 24. ignored directory Source child -> stale
    t3, r3, b3, c3 = make_base()
    rd3 = r3 / ".project-review"
    rd3.mkdir()
    (rd3 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Source: .scratch/cur\n- Source revision or identity: commit {b3}\n- Profile: generic\n")
    (rd3 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n")
    (rd3 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n")
    (r3 / ".gitignore").write_text(".scratch/cur/notes.tmp\n")
    (r3 / ".scratch" / "cur" / "notes.tmp").write_text("temp note\n")
    res = ask_light.inspect_project_state(r3)
    results.append(("24. ignored directory Source child", res["stage"], res["skill"], res["stage"] == "review-stale"))

    all_pass = True
    print(f"{'Scenario':<45} | {'ProjectStage':<22} | {'Skill':<15} | {'Verdict'}")
    print("-" * 95)
    for name, stage, skill, ok in results:
        status_sym = "PASS" if ok else "FAIL"
        if not ok:
            all_pass = False
        print(f"{name:<45} | {stage:<22} | {skill:<15} | [{status_sym}]")
    print("-" * 95)
    print("ALL 24 SCENARIOS PASSED:", all_pass)
    return all_pass


if __name__ == "__main__":
    success = run_smoke()
    sys.exit(0 if success else 1)
