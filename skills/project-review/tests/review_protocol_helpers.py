"""Python port of skills/review-loop/tests/protocol-test-helpers.ps1.

Disposable-fixture and state-machine helpers for the review-loop protocol
behavior suites. Mirrors the PowerShell semantics exactly: state transitions
are validated, round directories and evidence files are written to a temp
case root.
"""

from __future__ import annotations

import re
from pathlib import Path

STATUSES = ("INIT", "READY", "CRITIC", "REPAIR", "EVALUATE", "PASS", "FAIL", "BLOCKED")
ALLOWED_TRANSITIONS = {
    "INIT": ("READY", "BLOCKED"),
    "READY": ("CRITIC", "BLOCKED"),
    "CRITIC": ("REPAIR", "EVALUATE", "BLOCKED"),
    "REPAIR": ("EVALUATE", "FAIL", "BLOCKED"),
    "EVALUATE": ("PASS", "FAIL", "BLOCKED"),
    "FAIL": ("CRITIC", "BLOCKED"),
    "BLOCKED": ("READY", "CRITIC"),
    "PASS": (),
}


class ReviewState:
    def __init__(self, status: str, round_no: int, next_action: str, charter_revision: str, profile: str, owner: str, raw: str) -> None:
        self.status = status
        self.round = round_no
        self.next = next_action
        self.charter_revision = charter_revision
        self.profile = profile
        self.owner = owner
        self.raw = raw


def _first_group(pattern: str, text: str, default: str = "") -> str:
    m = re.search(pattern, text)
    return m.group(1).strip() if m else default


def get_review_state(case_root: Path) -> ReviewState:
    path = case_root / ".project-review" / "state.md"
    raw = path.read_text(encoding="utf-8", errors="replace")
    status = _first_group(r"(?m)^Status: ([^\r\n]+)", raw)
    round_no = int(_first_group(r"(?m)^Round: (\d+)", raw, "0") or "0")
    next_action = _first_group(r"(?m)^Next action: ([^\r\n]+)", raw)
    charter_revision = _first_group(r"(?m)^Charter revision: ([^\r\n]+)", raw)
    profile = _first_group(r"(?m)^Profile: ([^\r\n]+)", raw)
    owner = _first_group(r"(?m)^Verdict owner: ([^\r\n]+)", raw)
    return ReviewState(status, round_no, next_action, charter_revision, profile, owner, raw)


def set_review_state(
    case_root: Path,
    status: str,
    round_no: int,
    next_action: str,
    profile: str = "generic",
    charter_revision: str = "fixture-1",
    verdict_owner: str = "",
    last_completed_action: str = "protocol transition",
    blocker: str = "none",
) -> None:
    if status not in STATUSES:
        raise ValueError(f"invalid status {status}")
    current = get_review_state(case_root)
    if status not in ALLOWED_TRANSITIONS[current.status]:
        raise ValueError(f"Invalid transition {current.status} -> {status}")
    if status == "CRITIC" and round_no < current.round:
        raise ValueError("Round cannot move backwards")
    records = [
        f"Status: {status}",
        f"Round: {round_no}",
        f"Next action: {next_action}",
        f"Charter revision: {charter_revision}",
        f"Profile: {profile}",
        "Maximum rounds: 3",
        "Independence declaration: fresh read-only Evaluator required",
    ]
    if verdict_owner:
        records.append(f"Verdict owner: {verdict_owner}")
    records += [
        f"Last completed action: {last_completed_action}",
        f"Blocker: {blocker}",
        "Evidence label: executable protocol scenario",
    ]
    path = case_root / ".project-review" / "state.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(records) + "\n", encoding="utf-8")


def new_review_case(root: Path, name: str, profile: str = "generic") -> Path:
    case_root = root / name
    (case_root / ".project-review").mkdir(parents=True, exist_ok=True)
    (case_root / ".project-review" / "state.md").write_text(
        "\n".join([
            "Status: INIT",
            "Round: 0",
            "Next action: resolve acceptance source",
            f"Profile: {profile}",
        ]) + "\n",
        encoding="utf-8",
    )
    return case_root


def new_review_round(case_root: Path, profile: str, next_action: str, producer_evidence: list[str]) -> Path:
    state = get_review_state(case_root)
    if state.status != "READY":
        raise ValueError("Review round requires READY state")
    if not state.charter_revision:
        raise ValueError("Review round requires a frozen Charter revision")
    next_round = max(1, state.round)
    verdict_owner = "project-review Core" if profile in ("software", "manuscript") else ""
    set_review_state(case_root, "CRITIC", next_round, next_action, profile, state.charter_revision, verdict_owner, "executable protocol scenario")
    round_path = case_root / f".project-review/rounds/round-{next_round:02d}"
    round_path.mkdir(parents=True, exist_ok=True)
    (round_path / "producer-evidence.md").write_text("\n".join(producer_evidence) + "\n", encoding="utf-8")
    return round_path


def new_review_next_round(case_root: Path, profile: str, next_action: str, producer_evidence: list[str]) -> Path:
    state = get_review_state(case_root)
    if state.status != "FAIL":
        raise ValueError("Next round requires FAIL state")
    if not state.charter_revision:
        raise ValueError("Next round requires the existing Charter revision")
    round_no = state.round + 1
    verdict_owner = "project-review Core" if profile in ("software", "manuscript") else ""
    set_review_state(case_root, "CRITIC", round_no, next_action, profile, state.charter_revision, verdict_owner, "executable protocol scenario")
    round_path = case_root / f".project-review/rounds/round-{round_no:02d}"
    round_path.mkdir(parents=True, exist_ok=True)
    (round_path / "producer-evidence.md").write_text("\n".join(producer_evidence) + "\n", encoding="utf-8")
    return round_path


def get_review_finding_ids(case_root: Path) -> list[str]:
    path = case_root / ".project-review" / "findings.md"
    if not path.is_file():
        return []
    ids: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^(?:Finding|Re-observed) (F-\d{3})(?:\s|$)", line)
        if m and m.group(1) not in ids:
            ids.append(m.group(1))
    return ids


def get_confirmed_review_finding_ids(case_root: Path) -> list[str]:
    path = case_root / ".project-review" / "findings.md"
    if not path.is_file():
        return []
    latest: dict[str, str] = {}
    current = ""
    disposition = ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^(?:Finding|Re-observed) (F-\d{3})(?:\s|$)", line)
        if m:
            if current:
                latest[current] = disposition
            current = m.group(1)
            disposition = ""
            continue
        disp = re.match(r"^Disposition: (confirmed|rejected)", line)
        if disp:
            disposition = disp.group(1)
    if current:
        latest[current] = disposition
    return [fid for fid in get_review_finding_ids(case_root) if latest.get(fid) == "confirmed"]


def add_review_finding(
    case_root: Path,
    finding_id: str,
    source: str,
    axis: str,
    source_finding_reference: str,
    severity: str,
    disposition: str,
    evidence_label: str = "review",
) -> None:
    if severity not in ("Critical", "High", "Medium", "Low"):
        raise ValueError(f"invalid severity {severity}")
    if disposition not in ("confirmed", "rejected", "duplicate", "out-of-scope"):
        raise ValueError(f"invalid disposition {disposition}")
    path = case_root / ".project-review" / "findings.md"
    prefix = "Re-observed" if path.is_file() else "Finding"
    records = [
        f"{prefix} {finding_id}",
        f"Source: {source}; Axis: {axis}; Source finding reference: {source_finding_reference}",
        f"Severity: {severity}",
        f"Disposition: {disposition}",
        f"Evidence label: {evidence_label}",
    ]
    if prefix == "Finding":
        records = ["# Finding Registry"] + records + ["Resolution evidence: pending fresh Evaluator"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(records) + "\n", encoding="utf-8")
    else:
        with path.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(records) + "\n")


def write_review_repair_evidence(case_root: Path, round_no: int, finding_ids: list[str], evidence_lines: list[str]) -> None:
    round_path = case_root / f".project-review/rounds/round-{round_no:02d}"
    round_path.mkdir(parents=True, exist_ok=True)
    for finding_id in finding_ids:
        lines = [f"Finding: {finding_id}", f"Stable finding ID: {finding_id}"] + evidence_lines
        (round_path / f"repair-evidence-{finding_id}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
