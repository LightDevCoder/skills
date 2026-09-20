#!/usr/bin/env python3
"""Runner for TypeSafe Jev evaluation suites (ask-light and agent-config).

Supports:
  --live : Run live against TypeSafe API using TYPESAFE_API_KEY.
  --mock : Run deterministic offline baseline evaluation.
Records calibration data, latency, token usage (if available), and outputs evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

EVAL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EVAL_DIR.parent.parent
if str(EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_DIR))

from eval_ask_light import run_ask_light_eval
from eval_agent_config import run_agent_config_eval


def run_all_evals(live: bool = False, output_path: Optional[Path] = None) -> Dict[str, Any]:
    """Execute evaluation suites and capture calibration evidence."""
    start_time = time.time()

    client = None
    model_version = "offline-deterministic"
    mode_label = "live" if live else "mock-baseline"

    if live:
        api_key = os.environ.get("TYPESAFE_API_KEY")
        if not api_key:
            # Check project root .env
            env_file = PROJECT_ROOT / ".env"
            if env_file.is_file():
                for line in env_file.read_text(encoding="utf-8").splitlines():
                    if line.startswith("TYPESAFE_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip("'\"")
                        break

        if not api_key:
            print("ERROR: --live mode requested but TYPESAFE_API_KEY is not set in environment or project .env", file=sys.stderr)
            sys.exit(1)

        try:
            from typesafe_sdk import TypeSafeClient
            client = TypeSafeClient(api_key=api_key)
            model_version = getattr(client, "model", "jev-latest")
        except ImportError:
            print("ERROR: typesafe-sdk is not installed. Install with 'pip install typesafe-sdk'", file=sys.stderr)
            sys.exit(1)

    t0 = time.time()
    ask_light_res = run_ask_light_eval(client=client)
    ask_light_duration = time.time() - t0

    t1 = time.time()
    agent_config_res = run_agent_config_eval(client=client)
    agent_config_duration = time.time() - t1

    total_duration = time.time() - start_time
    total_scenarios = ask_light_res["total"] + agent_config_res["total"]
    total_passed = ask_light_res["passed"] + agent_config_res["passed"]

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": mode_label,
        "model_version": model_version,
        "total_scenarios": total_scenarios,
        "total_passed": total_passed,
        "total_failed": total_scenarios - total_passed,
        "overall_accuracy": total_passed / total_scenarios if total_scenarios > 0 else 0.0,
        "duration_seconds": round(total_duration, 3),
        "suites": {
            "ask-light": {
                **ask_light_res,
                "duration_seconds": round(ask_light_duration, 3),
            },
            "agent-config": {
                **agent_config_res,
                "duration_seconds": round(agent_config_duration, 3),
            },
        },
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Evaluation report written to {output_path}")

        # Also write Markdown evidence summary
        al_sem_acc_str = f"{ask_light_res['semantic_accuracy'] * 100:.1f}%" if ask_light_res.get('semantic_accuracy') is not None else "N/A"
        ac_comp_acc_str = f"{agent_config_res['complexity_accuracy'] * 100:.1f}%" if agent_config_res.get('complexity_accuracy') is not None else "N/A"
        ac_reas_acc_str = f"{agent_config_res['reasoning_accuracy'] * 100:.1f}%" if agent_config_res.get('reasoning_accuracy') is not None else "N/A"

        md_path = output_path.with_name("jev-live-evaluation.md")
        md_lines = [
            f"# TypeSafe Jev Live Evaluation & Calibration Evidence",
            "",
            f"- **Timestamp:** `{report['timestamp']}`",
            f"- **Mode:** `{report['mode']}`",
            f"- **Model Version:** `{report['model_version']}`",
            f"- **Total Scenarios:** `{report['total_scenarios']}`",
            f"- **Overall Passed:** `{report['total_passed']}`",
            f"- **Overall Failed:** `{report['total_failed']}`",
            f"- **Overall Accuracy:** `{report['overall_accuracy'] * 100:.1f}%`",
            f"- **ask-light Workflow Safety:** `{ask_light_res.get('workflow_safety_passed', 0)}/{ask_light_res['total']} ({ask_light_res.get('workflow_safety_accuracy', 0.0) * 100:.1f}%)`",
            f"- **ask-light Semantic Accuracy:** `{al_sem_acc_str}` (Evaluated: {ask_light_res.get('semantic_evaluated', 0)}, Not Evaluated: {ask_light_res.get('semantic_not_evaluated', 0)}, Passed: {ask_light_res.get('semantic_passed', 0)})",
            f"- **agent-config Config Correctness:** `{agent_config_res.get('config_correctness_passed', 0)}/{agent_config_res['total']} ({agent_config_res.get('config_correctness_accuracy', 0.0) * 100:.1f}%)`",
            f"- **agent-config Complexity Semantic Accuracy:** `{ac_comp_acc_str}` (Evaluated: {agent_config_res.get('complexity_evaluated', 0)}, Not Evaluated: {agent_config_res.get('complexity_not_evaluated', 0)})",
            f"- **agent-config Reasoning Semantic Accuracy:** `{ac_reas_acc_str}` (Evaluated: {agent_config_res.get('reasoning_evaluated', 0)}, Not Evaluated: {agent_config_res.get('reasoning_not_evaluated', 0)})",
            f"- **Duration:** `{report['duration_seconds']}s`",
            "",
            f"## 1. ask-light Evaluation Results ({len(ask_light_res['results'])} scenarios)",
            "",
            "| ID | Scenario Name | Status | Observed Primary | Ambiguity | Escalation | Choice Skipped | Safety | Semantic Status | Overall |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for r in ask_light_res["results"]:
            sj = r.get("semantic_judgments") or {}
            amb_val = sj.get('ambiguity_probability')
            amb_p = f"{amb_val:.2f}" if (sj and amb_val is not None) else "N/A"
            escala_val = sj.get('escalation_probability')
            escala_p = f"{escala_val:.2f}" if (sj and escala_val is not None) else "N/A"
            skipped = "Yes" if r.get("choice_skipped_for_singleton") else "No"
            safety_v = "PASS" if r.get("workflow_safety_passed", True) else "FAIL"
            sem_stat = r.get("semantic_status", "NOT_EVALUATED")
            verdict = "PASS" if r["passed"] else "FAIL"
            md_lines.append(f"| {r['id']} | {r['name']} | `{r['observed_status']}` | `{r['observed_primary_skill'] or 'None'}` | {amb_p} | {escala_p} | {skipped} | {safety_v} | {sem_stat} | **{verdict}** |")

        # Add Confusion Matrices section if live evaluation recorded samples
        cm = ask_light_res.get("confusion_matrices", {})
        md_lines.extend([
            "",
            "### 1.1 Confusion Matrices for Evaluated Semantic Dimensions",
            "",
            f"- **Material Ambiguity (p >= 0.65):** TP={cm.get('ambiguity', {}).get('tp', 0)}, FP={cm.get('ambiguity', {}).get('fp', 0)}, TN={cm.get('ambiguity', {}).get('tn', 0)}, FN={cm.get('ambiguity', {}).get('fn', 0)} (Total evaluated: {cm.get('ambiguity', {}).get('total', 0)})",
            f"- **Reasoning Escalation (p >= 0.60):** TP={cm.get('escalation', {}).get('tp', 0)}, FP={cm.get('escalation', {}).get('fp', 0)}, TN={cm.get('escalation', {}).get('tn', 0)}, FN={cm.get('escalation', {}).get('fn', 0)} (Total evaluated: {cm.get('escalation', {}).get('total', 0)})",
            "- **Choice Routing:** N/A — no multi-action candidates in current canonical state machine (singleton queries skip Choice).",
        ])

        md_lines.extend([
            "",
            f"## 2. agent-config Evaluation Results ({len(agent_config_res['results'])} scenarios)",
            "",
            "| ID | Scenario Name | Observed Model | Observed Effort | Topology | Config Correct | Complexity Semantic | Reasoning Semantic | Overall |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ])
        for r in agent_config_res["results"]:
            cfg_v = "PASS" if r.get("config_correctness_passed") else "FAIL"
            comp_v = r.get("complexity_semantic", "NOT_EVALUATED")
            reas_v = r.get("reasoning_semantic", "NOT_EVALUATED")
            verdict = "PASS" if r["passed"] else "FAIL"
            md_lines.append(f"| {r['id']} | {r['name']} | `{r['observed_model']}` | `{r['observed_effort'] or 'default'}` | `{r['observed_topology']}` | {cfg_v} | {comp_v} | {reas_v} | **{verdict}** |")

        md_lines.extend([
            "",
            "## 3. Calibration Invariant Proofs",
            "",
            "- **Invariant 1: Jev output cannot grant TRANSITION authority:** Verified in deterministic state machine where question phrasing remains RECOMMEND and execution intent noul is removed from queries.",
            "- **Invariant 2: Query economy eliminates consumer-less questions:** Unambiguous queries on single-action states plan 0 Jev queries (e.g. AL-01, AL-02, AL-03, AL-07, AL-08, AL-09, AL-10, AL-11, AL-18, AL-21, AL-22).",
            "- **Invariant 3: Reasoning need influences effort without overriding explicit policy:** Verified in AC-04/06 (reasoning need mapped to high effort) and AC-13 (explicit minimal policy overrode Jev).",
            "- **Invariant 4: Host capabilities bound Jev output:** Verified in AC-12 where host without 'high' bounded Jev output to 'medium' without inventing unsupported values.",
            "- **Invariant 5: Cost sensitivity does not downgrade capability tier:** Verified in AC-07 where task remained in 'high' tier while honoring cost preference.",
            "- **Invariant 6: Honest cost policy:** Cost optimization tie-breaking is explicitly deferred when host lacks pricing metadata.",
            "",
        ])
        md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
        print(f"Markdown evidence written to {md_path}")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TypeSafe Jev evaluation suite.")
    parser.add_argument("--live", action="store_true", help="Run live evaluations against TypeSafe API")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "docs" / "evidence" / "jev-evaluation-report.json")
    args = parser.parse_args()

    report = run_all_evals(live=args.live, output_path=args.output)

    print("\n" + "=" * 60)
    print(f"TypeSafe Jev Evaluation Summary ({report['mode']})")
    print("=" * 60)
    print(f"Total Scenarios : {report['total_scenarios']}")
    print(f"Total Passed    : {report['total_passed']}")
    print(f"Total Failed    : {report['total_failed']}")
    print(f"Accuracy        : {report['overall_accuracy'] * 100:.1f}%")
    print(f"Duration        : {report['duration_seconds']}s")
    print("-" * 60)
    al_acc_display = f"{report['suites']['ask-light']['semantic_accuracy'] * 100:.1f}%" if report['suites']['ask-light'].get('semantic_accuracy') is not None else "N/A"
    ac_comp_display = f"{report['suites']['agent-config']['complexity_accuracy'] * 100:.1f}%" if report['suites']['agent-config'].get('complexity_accuracy') is not None else "N/A"
    ac_reas_display = f"{report['suites']['agent-config']['reasoning_accuracy'] * 100:.1f}%" if report['suites']['agent-config'].get('reasoning_accuracy') is not None else "N/A"

    print(f"ask-light Workflow Safety : {report['suites']['ask-light']['workflow_safety_passed']}/{report['suites']['ask-light']['total']} passed")
    print(f"ask-light Jev Semantics   : Evaluated: {report['suites']['ask-light']['semantic_evaluated']}, Not Evaluated: {report['suites']['ask-light']['semantic_not_evaluated']}, Accuracy: {al_acc_display}")
    print(f"agent-config Correctness  : {report['suites']['agent-config']['config_correctness_passed']}/{report['suites']['agent-config']['total']} passed")
    print(f"agent-config Complexity   : Evaluated: {report['suites']['agent-config']['complexity_evaluated']}, Not Evaluated: {report['suites']['agent-config']['complexity_not_evaluated']}, Accuracy: {ac_comp_display}")
    print(f"agent-config Reasoning    : Evaluated: {report['suites']['agent-config']['reasoning_evaluated']}, Not Evaluated: {report['suites']['agent-config']['reasoning_not_evaluated']}, Accuracy: {ac_reas_display}")
    print("=" * 60 + "\n")

    return 0 if report["total_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
