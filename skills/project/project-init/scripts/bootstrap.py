#!/usr/bin/env python3
"""Idempotently write the repository contract consumed by Light Project Skills."""

from __future__ import annotations

import argparse
import getpass
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Optional

PROJECT_PATH = Path("docs/agents/light-project.md")
TRACKER_PATH = Path("docs/agents/issue-tracker.md")
START = "<!-- light-project:managed:start -->"
END = "<!-- light-project:managed:end -->"
POINTER_START = "<!-- light-project:pointer:start -->"
POINTER_END = "<!-- light-project:pointer:end -->"

REQUIRED = (
    "projectType", "goal", "outputs", "preset", "relevantSkills",
    "issueTracker", "domainContext", "reviewProfile", "workingArea",
    "instructionFile",
)
PRESETS = {
    "generic", "software", "manuscript", "skill-development", "research",
    "knowledge-base", "data-analysis", "research-fallback",
}
MARKER_TOKENS = (START, END, POINTER_START, POINTER_END)

JEV_SKILL_NAME = "typesafe-ai"
JEV_CONSTRAINT = "TypeSafe Jev System One semantic acceleration"

# ==============================================================================
# Canonical Agent Mappings for official Skills CLI (npx skills add ...)
# Source: official vercel-labs/skills agent registry / README.md / cli.mjs
# Verified revision: vercel-labs/skills v1.7.0 (2026-09-20)
#
# Core distinction:
#   internal_host_id (e.g., "claude", "cursor", "agy", "grok-build", "hermes")
#   ≠
#   skills_cli_agent_id (e.g., "claude-code", "cursor", "antigravity", "grok", "hermes-agent")
#
# DeepSeek Harness (DSH):
#   Unsupported by official skills CLI. Fails closed (TARGET_UNRESOLVED).
#   No installer calls, no guessed CLI IDs.
# ==============================================================================

AGENT_TARGETS: dict[str, dict[str, Any]] = {
    "pi": {
        "cli_agent": "pi",
        "canonical_project_paths": [Path(".pi/skills")],
        "canonical_global_subpaths": [Path(".pi/agent/skills")],
        "legacy_global_subpaths": [Path(".pi/skills"), Path(".agents/skills")],
    },
    "claude": {
        "cli_agent": "claude-code",
        "canonical_project_paths": [Path(".claude/skills")],
        "canonical_global_subpaths": [Path(".claude/skills")],
        "legacy_global_subpaths": [Path(".agents/skills")],
    },
    "cursor": {
        "cli_agent": "cursor",
        "canonical_project_paths": [Path(".agents/skills")],
        "canonical_global_subpaths": [Path(".cursor/skills")],
        "legacy_global_subpaths": [Path(".agents/skills")],
    },
    "codex": {
        "cli_agent": "codex",
        "canonical_project_paths": [Path(".agents/skills")],
        "canonical_global_subpaths": [Path(".codex/skills")],
        "legacy_global_subpaths": [Path(".agents/skills")],
    },
    "agy": {
        "cli_agent": "antigravity",
        "canonical_project_paths": [Path(".agents/skills")],
        "canonical_global_subpaths": [Path(".gemini/antigravity/skills")],
        "legacy_global_subpaths": [Path(".agents/skills")],
    },
    "grok-build": {
        "cli_agent": "grok",
        "canonical_project_paths": [Path(".grok/skills")],
        "canonical_global_subpaths": [Path(".grok/skills")],
        "legacy_global_subpaths": [Path(".agents/skills")],
    },
    "hermes": {
        "cli_agent": "hermes-agent",
        "canonical_project_paths": [Path(".hermes/skills")],
        "canonical_global_subpaths": [Path(".hermes/skills")],
        "legacy_global_subpaths": [Path(".agents/skills")],
    },
}

AGENT_TARGET_ALIASES: dict[str, str] = {
    "claude-code": "claude",
    "antigravity": "agy",
    "grok": "grok-build",
    "hermes-agent": "hermes",
}

# Compatibility alias for existing callers
SUPPORTED_AGENT_TARGETS = AGENT_TARGETS


def normalize_agent_target(target: Optional[str]) -> Optional[str]:
    """Normalize agent target to internal canonical key or None if unsupported."""
    if not target:
        return None
    cleaned = str(target).strip().lower()
    if cleaned in AGENT_TARGET_ALIASES:
        cleaned = AGENT_TARGET_ALIASES[cleaned]
    if cleaned in AGENT_TARGETS:
        return cleaned
    return None


def get_agent_canonical_global_paths(agent_target: Optional[str] = None, home: Optional[Path] = None) -> list[Path]:
    """Dynamically resolve official canonical global skill search roots for active Agent."""
    h = home or Path.home()
    norm = normalize_agent_target(agent_target)
    if norm and norm in AGENT_TARGETS:
        # Check official environment variable overrides
        if norm == "claude" and os.environ.get("CLAUDE_CONFIG_DIR"):
            return [Path(os.environ["CLAUDE_CONFIG_DIR"].strip()) / "skills"]
        elif norm == "codex" and os.environ.get("CODEX_HOME"):
            return [Path(os.environ["CODEX_HOME"].strip()) / "skills"]
        elif norm == "grok-build" and os.environ.get("GROK_HOME"):
            return [Path(os.environ["GROK_HOME"].strip()) / "skills"]
        elif norm == "hermes" and os.environ.get("HERMES_HOME"):
            return [Path(os.environ["HERMES_HOME"].strip()) / "skills"]
        return [h / p for p in AGENT_TARGETS[norm]["canonical_global_subpaths"]]
    return [
        h / ".pi" / "agent" / "skills",
        h / ".claude" / "skills",
        h / ".cursor" / "skills",
        h / ".codex" / "skills",
    ]


def get_agent_legacy_global_paths(agent_target: Optional[str] = None, home: Optional[Path] = None) -> list[Path]:
    """Resolve legacy-discoverable global skill paths for backward-compatible reuse."""
    h = home or Path.home()
    norm = normalize_agent_target(agent_target)
    if norm and norm in AGENT_TARGETS:
        return [h / p for p in AGENT_TARGETS[norm]["legacy_global_subpaths"]]
    return [
        h / ".agents" / "skills",
        h / ".pi" / "skills",
    ]


def get_agent_global_paths(agent_target: Optional[str] = None, home: Optional[Path] = None, include_legacy: bool = True) -> list[Path]:
    """Dynamically resolve global skill search roots relative to current or specified home."""
    canonical = get_agent_canonical_global_paths(agent_target, home=home)
    if include_legacy:
        legacy = get_agent_legacy_global_paths(agent_target, home=home)
        combined: list[Path] = []
        for p in canonical + legacy:
            if p not in combined:
                combined.append(p)
        return combined
    return canonical


def resolve_active_agent_target(
    root: Optional[Path] = None,
    config: Optional[dict[str, Any]] = None,
    explicit_target: Optional[str] = None,
) -> Optional[str]:
    """Resolve canonical active-Agent target for skills installer.

    Order:
      1. explicit_target argument (normalized; unsupported like 'dsh' fails closed)
      2. config.get("agentTarget") or config.get("hostAgent") (normalized)
      3. os.environ["SKILLS_AGENT_TARGET"] (normalized)
      4. Evidenced host environment:
         - PI_* env vars -> "pi"
         - CLAUDE_CODE_ENTRY or CLAUDE_PROJECT_DIR -> "claude"
         - CURSOR_AGENT or CURSOR_PROJECT_DIR -> "cursor"
         - CODEX_AGENT or CODEX_DIR -> "codex"
         - ANTIGRAVITY_AGENT or GEMINI_AGENT -> "agy"
         - GROK_AGENT or GROK_BUILD -> "grok-build"
         - HERMES_AGENT -> "hermes"
      5. Evidenced instruction file:
         - CLAUDE.md -> "claude"
         - AGENTS.md with evidenced Pi environment -> "pi"
      6. Fails closed (returns None) if agent is unknown or unverified (e.g. DSH).
    """
    candidates = [
        explicit_target,
        config.get("agentTarget") if config else None,
        config.get("hostAgent") if config else None,
        os.environ.get("SKILLS_AGENT_TARGET"),
    ]
    for cand in candidates:
        if cand and str(cand).strip().lower() in ("dsh", "deepseek", "deepseek-harness"):
            # Explicitly unsupported agent fails closed immediately
            return None
        norm = normalize_agent_target(cand)
        if norm:
            return norm

    if any(k.startswith("PI_") for k in os.environ):
        return "pi"
    if os.environ.get("CLAUDE_CODE_ENTRY") or os.environ.get("CLAUDE_PROJECT_DIR"):
        return "claude"
    if os.environ.get("CURSOR_AGENT") or os.environ.get("CURSOR_PROJECT_DIR"):
        return "cursor"
    if os.environ.get("CODEX_AGENT") or os.environ.get("CODEX_DIR"):
        return "codex"
    if os.environ.get("ANTIGRAVITY_AGENT") or os.environ.get("GEMINI_AGENT"):
        return "agy"
    if os.environ.get("GROK_AGENT") or os.environ.get("GROK_BUILD"):
        return "grok-build"
    if os.environ.get("HERMES_AGENT"):
        return "hermes"

    if config:
        inst_file = str(config.get("instructionFile", "")).lower()
        if inst_file == "claude.md":
            return "claude"
        if inst_file == "agents.md":
            if (Path.home() / ".pi").is_dir() or (root and (root / ".pi").is_dir()):
                return "pi"

    return None


def mask_secret(value: str) -> str:
    """Mask sensitive keys or tokens. Never print or store raw secrets in plaintext."""
    if not value:
        return ""
    return "[REDACTED]"


def resolve_typesafe_credentials(project_root: Optional[Path] = None) -> tuple[Optional[str], str]:
    """Canonical credential resolution for TypeSafe API key.

    Order:
      1. Current process environment: os.environ["TYPESAFE_API_KEY"]
      2. Explicit active project .env (parsed line-by-line, no dotenv dependency)
      3. Unavailable (None, "missing")

    Never scans arbitrary parents or unrelated directories.
    """
    env_key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if env_key:
        return env_key, "os.environ"

    if project_root is not None:
        env_path = project_root / ".env"
        if env_path.is_file():
            try:
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    if k.strip() == "TYPESAFE_API_KEY":
                        clean_v = v.strip().strip("'\"")
                        if clean_v:
                            return clean_v, ".env"
            except Exception:
                pass

    return None, "missing"


def detect_typesafe_key(project_root: Optional[Path] = None) -> tuple[bool, str]:
    """Inspect os.environ and explicit project .env for TYPESAFE_API_KEY.

    Returns (found, source). Never returns raw key value.
    """
    key, source = resolve_typesafe_credentials(project_root)
    return bool(key), source


def is_valid_typesafe_skill(skill_dir: Path) -> bool:
    """Verify that a directory contains a valid official typesafe-ai skill.

    Rejects missing files, empty stubs, and skills without proper frontmatter name.
    """
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return False
    try:
        content = skill_file.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return False
        parts = content.split("---", 2)
        if len(parts) < 3:
            return False
        frontmatter = parts[1]
        name_match = re.search(r"^name:\s*([^\s\n\r]+)", frontmatter, re.MULTILINE)
        if not name_match or name_match.group(1).strip() != JEV_SKILL_NAME:
            return False
        if len(content.strip()) < 15:
            return False
        return True
    except Exception:
        return False


def find_global_skill(
    skill_name: str = JEV_SKILL_NAME,
    agent_target: Optional[str] = None,
    search_roots: Optional[list[Path]] = None,
    home: Optional[Path] = None,
    include_scope: bool = False,
    canonical_only: bool = False,
) -> Any:
    """Locate official typesafe-ai skill in global agent skill directories matching target.

    If include_scope is True: returns (path, scope_type) where scope_type is
    "canonical-global", "legacy-global", or "none".
    If include_scope is False: returns path or None.
    """
    if search_roots is not None:
        for root in search_roots:
            skill_dir = root / skill_name
            if is_valid_typesafe_skill(skill_dir):
                return (skill_dir, "canonical-global") if include_scope else skill_dir
        return (None, "none") if include_scope else None

    # 1. Check canonical global paths first
    canonical_roots = get_agent_canonical_global_paths(agent_target, home=home)
    for root in canonical_roots:
        skill_dir = root / skill_name
        if is_valid_typesafe_skill(skill_dir):
            return (skill_dir, "canonical-global") if include_scope else skill_dir

    # 2. Check legacy discoverable paths
    if not canonical_only:
        legacy_roots = get_agent_legacy_global_paths(agent_target, home=home)
        for root in legacy_roots:
            skill_dir = root / skill_name
            if is_valid_typesafe_skill(skill_dir):
                return (skill_dir, "legacy-global") if include_scope else skill_dir

    return (None, "none") if include_scope else None


def check_global_skill(
    skill_name: str = JEV_SKILL_NAME,
    agent_target: Optional[str] = None,
    search_roots: Optional[list[Path]] = None,
    canonical_only: bool = False,
) -> bool:
    """Check if valid official skill is present in global skills directories for agent target."""
    return find_global_skill(
        skill_name=skill_name,
        agent_target=agent_target,
        search_roots=search_roots,
        canonical_only=canonical_only,
    ) is not None


def ensure_gitignored(project_root: Path, entry: str = ".env") -> bool:
    """Ensure entry is present in project .gitignore. Return True if added."""
    clean_entry = entry.strip()
    gitignore_path = project_root / ".gitignore"
    if gitignore_path.is_file():
        content = gitignore_path.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines()]
        if clean_entry in lines or f"/{clean_entry}" in lines or f"{clean_entry}/" in lines:
            return False
        new_content = content
        if new_content and not new_content.endswith("\n"):
            new_content += "\n"
        new_content += f"{clean_entry}\n"
        gitignore_path.write_text(new_content, encoding="utf-8")
        return True
    else:
        gitignore_path.write_text(f"{clean_entry}\n", encoding="utf-8")
        return True


def configure_typesafe_key(project_root: Path, api_key: str) -> bool:
    """Safely configure TYPESAFE_API_KEY in local .env, enforcing .gitignore first."""
    clean_key = api_key.strip()
    if not clean_key:
        return False
    ensure_gitignored(project_root, ".env")
    env_file = project_root / ".env"
    existing_lines: list[str] = []
    found = False
    if env_file.is_file():
        try:
            for line in env_file.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped.startswith("#") and "=" in stripped:
                    k, _ = stripped.split("=", 1)
                    if k.strip() == "TYPESAFE_API_KEY":
                        existing_lines.append(f"TYPESAFE_API_KEY={clean_key}")
                        found = True
                        continue
                existing_lines.append(line)
        except Exception:
            existing_lines = []
    if not found:
        existing_lines.append(f"TYPESAFE_API_KEY={clean_key}")
    env_file.write_text("\n".join(existing_lines) + "\n", encoding="utf-8")
    return True


def prompt_jev_opt_in() -> bool:
    """Interactively ask user if they want to initialize TypeSafe Jev."""
    try:
        response = input("是否为此项目初始化 TypeSafe Jev 语义增强？[y/N] ").strip().lower()
        return response in ("y", "yes")
    except (EOFError, KeyboardInterrupt, OSError):
        return False


def prompt_typesafe_key(project_root: Path) -> tuple[bool, str]:
    """Interactively prompt user for TYPESAFE_API_KEY if missing.

    Uses non-echoing password input to prevent raw key exposure in terminal/logs.
    """
    found, source = detect_typesafe_key(project_root)
    if found:
        return True, source
    if not sys.stdin.isatty():
        return False, "missing"
    try:
        raw_key = getpass.getpass("未检测到 TYPESAFE_API_KEY。请输入您的 TypeSafe API Key（留空跳过）: ").strip()
        if raw_key:
            configure_typesafe_key(project_root, raw_key)
            return True, ".env"
    except (EOFError, KeyboardInterrupt, OSError):
        pass
    return False, "missing"


def prompt_install_sdk() -> bool:
    """Interactively ask user if they want to install typesafe-sdk in active Python."""
    try:
        response = input("typesafe-sdk 未安装。是否立即在当前 Python 环境中安装？[y/N] ").strip().lower()
        return response in ("y", "yes")
    except (EOFError, KeyboardInterrupt, OSError):
        return False


def install_official_typesafe_skill(
    project_root: Path,
    agent_target: Optional[str] = None,
    installer_cmd: Optional[list[str]] = None,
) -> tuple[bool, Optional[Path], str]:
    """Install official typesafe-ai skill via official package installer targeting active Agent.

    Uses canonical cli_agent for --agent flag, NOT internal host key.
    Fails closed if agent_target is unknown or unsupported (e.g. DSH).
    Never calls installer without --agent.
    """
    norm = normalize_agent_target(agent_target)
    if not norm or norm not in AGENT_TARGETS:
        return False, None, "JEV_SKILL_TARGET_UNRESOLVED: unable to determine active Agent target for skills installer"

    target_info = AGENT_TARGETS[norm]
    cli_agent_id = target_info["cli_agent"]

    cmd = installer_cmd or [
        "npx", "skills", "add", "typesafe-ai/skills",
        "--skill", JEV_SKILL_NAME,
        "--agent", cli_agent_id,
        "--yes",
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
        )
        if proc.returncode != 0:
            return False, None, f"JEV_SKILL_SETUP_INCOMPLETE: installer failed with code {proc.returncode}"
    except Exception as exc:
        return False, None, f"JEV_SKILL_SETUP_INCOMPLETE: installer execution failed ({type(exc).__name__})"

    # Verify strictly in CANONICAL project scope of the target agent
    for rel_path in target_info["canonical_project_paths"]:
        candidate = project_root / rel_path / JEV_SKILL_NAME
        if is_valid_typesafe_skill(candidate):
            return True, candidate, "installed-local"

    return False, None, "JEV_SKILL_SETUP_INCOMPLETE: installed skill missing or invalid in expected agent scope"


def verify_typesafe_sdk(python_bin: Optional[str] = None) -> bool:
    """Verify that typesafe_sdk is importable by the Python runtime executing the scripts."""
    py_exec = python_bin or sys.executable
    try:
        res = subprocess.run(
            [py_exec, "-c", "import typesafe_sdk"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
        return res.returncode == 0
    except Exception:
        return False


def install_typesafe_sdk(python_bin: Optional[str] = None) -> tuple[bool, str]:
    """Attempt to install typesafe-sdk using the active Python interpreter.

    Does NOT install python-dotenv unless explicitly required.
    """
    py_exec = python_bin or sys.executable
    try:
        res = subprocess.run(
            [py_exec, "-m", "pip", "install", "typesafe-sdk"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
        )
        if res.returncode == 0:
            return True, "installed"
        return False, f"pip install failed with code {res.returncode}"
    except Exception as exc:
        return False, f"pip install error: {type(exc).__name__}"


def verify_jev_runtime(
    project_root: Optional[Path] = None,
    client: Optional[Any] = None,
    api_key: Optional[str] = None,
) -> tuple[bool, str]:
    """Perform a minimal smoke test verifying TypeSafe Jev System One readiness.

    Verifies authentication, basic System One request, and typed response.
    Never exposes raw API keys in exceptions or returned diagnostics.
    If client is injected, avoids importing typesafe_sdk so offline tests are hermetic.
    """
    if client is not None:
        try:
            resp = client.system_one(
                state="Project initialization Jev runtime smoke test.",
                questions={"readiness_check": "readiness verification check"},
            )
            if resp and hasattr(resp, "nouls") and "readiness_check" in resp.nouls:
                return True, "verified"
            return False, "JEV_RUNTIME_UNVERIFIED: unexpected response structure"
        except Exception as exc:
            return False, f"JEV_RUNTIME_UNVERIFIED: {type(exc).__name__}"

    try:
        from typesafe_sdk import Noul, TypeSafeClient
    except ImportError:
        return False, "JEV_RUNTIME_UNVERIFIED: typesafe-sdk not importable"

    resolved_key = api_key
    if not resolved_key:
        resolved_key, _ = resolve_typesafe_credentials(project_root)

    if not resolved_key:
        return False, "JEV_RUNTIME_UNVERIFIED: TYPESAFE_API_KEY missing"

    try:
        ts_client = TypeSafeClient(api_key=resolved_key)
        resp = ts_client.system_one(
            state="Project initialization Jev runtime smoke test.",
            questions={"readiness_check": Noul(instructions="Is this a readiness verification check?")},
        )
        if resp and hasattr(resp, "nouls") and "readiness_check" in resp.nouls:
            return True, "verified"
        return False, "JEV_RUNTIME_UNVERIFIED: unexpected response structure"
    except Exception as exc:
        return False, f"JEV_RUNTIME_UNVERIFIED: {type(exc).__name__}"


def detect_project_stack(project_root: Path) -> list[str]:
    """Detect stack and provide Jev installation advice without extraneous packages."""
    recommendations: list[str] = []
    is_python = any((
        (project_root / "requirements.txt").is_file(),
        (project_root / "pyproject.toml").is_file(),
        (project_root / "setup.py").is_file(),
        (project_root / "Pipfile").is_file(),
    ))
    is_node = any((
        (project_root / "package.json").is_file(),
        (project_root / "node_modules").is_dir(),
    ))
    if is_python:
        recommendations.append("pip install typesafe-sdk")
    if is_node:
        recommendations.append("npm install @typesafe/sdk")
    if not recommendations:
        recommendations.append("pip install typesafe-sdk (Python) or npm install @typesafe/sdk (Node)")
    return recommendations


def validate_render_text(label: str, value: Any) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    if "\n" in value or "\r" in value or any(marker in value for marker in MARKER_TOKENS):
        raise ValueError(f"{label} contains a newline or managed marker")


def validate_config(config: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED if key not in config or config[key] in (None, "")]
    if missing:
        raise ValueError(f"missing bootstrap fields: {', '.join(missing)}")
    if not isinstance(config["issueTracker"], dict) or not config["issueTracker"].get("kind") or not config["issueTracker"].get("path"):
        raise ValueError("issueTracker requires kind and path")
    if config["issueTracker"]["kind"] != "local-markdown":
        raise ValueError("unsupported issueTracker kind; current Light Project Skills require local-markdown")
    if config["workingArea"] != ".scratch":
        raise ValueError("unsupported workingArea; current Light Project Skills require .scratch")
    if str(config["instructionFile"]).lower() not in {"agents.md", "claude.md"}:
        raise ValueError("instructionFile must be AGENTS.md or CLAUDE.md based on inspected host evidence")
    if config["preset"] not in PRESETS:
        raise ValueError(f"unsupported preset: {config['preset']}")
    if config["preset"] == "research-fallback":
        fallback_missing = [
            key for key in ("sources", "confirmation", "validation")
            if key not in config or config[key] in (None, "", [])
        ]
        if fallback_missing:
            raise ValueError(f"research-fallback requires: {', '.join(fallback_missing)}")
        if not isinstance(config["sources"], list):
            raise ValueError("research-fallback sources must be a list")
    tracker_path = Path(str(config["issueTracker"]["path"]))
    if tracker_path.is_absolute() or ".." in tracker_path.parts or not tracker_path.parts or tracker_path.parts[0] != config["workingArea"]:
        raise ValueError("issueTracker path must stay under the configured .scratch working area")
    if tracker_path.as_posix() != ".scratch/<effort>/issues":
        raise ValueError("issueTracker path must use the supported .scratch/<effort>/issues contract")
    for key in ("outputs", "relevantSkills", "domainContext"):
        if not isinstance(config[key], list):
            raise ValueError(f"{key} must be a list")
    if not config["outputs"] or not config["relevantSkills"]:
        raise ValueError("outputs and relevantSkills must not be empty")
    scalar_keys = ("projectType", "goal", "preset", "reviewProfile", "workingArea", "instructionFile")
    optional_scalars = ("acceptanceStrategy", "collaboration", "confirmation", "validation")
    for key in scalar_keys:
        validate_render_text(key, config[key])
    for key in optional_scalars:
        if key in config:
            validate_render_text(key, config[key])
    for key in ("kind", "path"):
        validate_render_text(f"issueTracker.{key}", config["issueTracker"][key])
    for key in ("outputs", "relevantSkills", "domainContext", "constraints", "sources"):
        if key in config:
            if not isinstance(config[key], list):
                raise ValueError(f"{key} must be a list")
            for index, value in enumerate(config[key]):
                validate_render_text(f"{key}[{index}]", value)


def inspect_capabilities(
    relevant_skills: list[str],
    roots: Optional[list[Path]] = None,
    unavailable: Optional[list[str]] = None,
) -> list[dict[str, Any]]:
    """Classify declared relevant Light capabilities without over-claiming.

    Statuses are available, unavailable, or unknown. A missing root means
    unknown, never a silent promotion to available.
    """
    unavailable = unavailable or []
    results: list[dict[str, Any]] = []
    for name in relevant_skills:
        status = "unknown"
        reason = "no capability root supplied; availability not verified"
        if roots:
            matches = [root / name / "SKILL.md" for root in roots if (root / name / "SKILL.md").is_file()]
            if name in unavailable:
                status, reason = "unavailable", "declared unavailable by the active host"
            elif matches:
                status, reason = "available", "readable SKILL.md found in supplied capability root"
            else:
                status, reason = "unavailable", "no readable SKILL.md found in supplied capability root"
        results.append({"skill": name, "status": status, "reason": reason})
    return results


def csv(values: list[Any]) -> str:
    return ", ".join(str(value) for value in values)


def existing_managed_value(existing: str, label: str) -> Optional[str]:
    """Read one generated field without interpreting its rendered value."""
    block_pattern = re.compile(re.escape(START) + r"(.*?)" + re.escape(END), re.S)
    block = block_pattern.search(existing)
    if block is None:
        return None
    matches = re.findall(rf"^- {re.escape(label)}: (.*)$", block.group(1), re.M)
    if len(matches) > 1:
        raise ValueError(f"multiple {label} fields in the Light managed block require manual reconciliation")
    return matches[0] if matches and matches[0] else None


def render_project(config: dict[str, Any], existing: str = "") -> str:
    if "constraints" in config:
        constraints = csv(config["constraints"]) if config["constraints"] else "none recorded"
    else:
        constraints = existing_managed_value(existing, "Constraints") or "none recorded"
    collaboration = config.get("collaboration") or existing_managed_value(existing, "Collaboration") or "default"
    acceptance = (
        config.get("acceptanceStrategy")
        or existing_managed_value(existing, "Acceptance strategy")
        or f"{config['reviewProfile']} profile via project-review"
    )
    lines = [
        START,
        "# Light Project Configuration",
        "",
        f"- Project type: {config['projectType']}",
        f"- Goal: {config['goal']}",
        f"- Outputs: {csv(config['outputs'])}",
        f"- Preset: {config['preset']}",
        f"- Relevant Skills: {csv(config['relevantSkills'])}",
        f"- Issue tracker: {config['issueTracker']['kind']} at {config['issueTracker']['path']}",
        f"- Domain context: {csv(config['domainContext']) if config['domainContext'] else 'none recorded'}",
        f"- Review profile: {config['reviewProfile']}",
        f"- Acceptance strategy: {acceptance}",
        f"- Working area: {config['workingArea']}",
        f"- Collaboration: {collaboration}",
        f"- Constraints: {constraints}",
    ]
    if config["preset"] == "research-fallback":
        lines.extend((
            f"- Sources: {csv(config['sources'])}",
            f"- Confirmation: {config['confirmation']}",
            f"- Validation: {config['validation']}",
        ))
    lines.append(END)
    return "\n".join(lines) + "\n"


def render_tracker(config: dict[str, Any]) -> str:
    tracker = config["issueTracker"]
    return "\n".join((
        START,
        "# Issue Tracker Contract",
        "",
        f"- Kind: {tracker['kind']}",
        f"- Work item location: {tracker['path']}",
        "- SPEC location: <working-area>/<effort>/spec.md",
        "- Ticket location: <working-area>/<effort>/issues/NN-<slug>.md",
        "- Edge field: Blocked by: NN, NN",
        "- Statuses: open | ready-for-agent | claimed | resolved",
        "- Frontier: unblocked open/ready-for-agent items, first by number",
        END,
    )) + "\n"


def merge_managed(existing: str, rendered: str) -> str:
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)
    starts, ends = existing.count(START), existing.count(END)
    if starts != ends:
        raise ValueError("unbalanced Light managed block markers require manual reconciliation")
    if starts > 1 or len(pattern.findall(existing)) > 1:
        raise ValueError("multiple Light managed blocks require manual reconciliation")
    match = pattern.search(existing)
    if starts == 1 and match is None:
        raise ValueError("misordered Light managed block markers require manual reconciliation")
    if match:
        return pattern.sub(lambda _match: rendered, existing, count=1)
    if not existing.strip():
        return rendered
    return existing.rstrip() + "\n\n" + rendered


def mask_markdown_fences(text: str) -> str:
    """Mask fenced code while preserving byte offsets and line endings."""
    masked: list[str] = []
    fence_character = ""
    fence_length = 0
    for line in text.splitlines(keepends=True):
        candidate = line.lstrip(" ")
        indent = len(line) - len(candidate)
        marker = re.match(r"(`{3,}|~{3,})", candidate) if indent <= 3 else None
        if not fence_character and marker:
            token = marker.group(1)
            fence_character, fence_length = token[0], len(token)
            masked.append("".join(character if character in "\r\n" else " " for character in line))
            continue
        if fence_character:
            closing = re.match(rf"{re.escape(fence_character)}{{{fence_length},}}[ \t]*(?:\r?\n)?$", candidate) if indent <= 3 else None
            masked.append("".join(character if character in "\r\n" else " " for character in line))
            if closing:
                fence_character, fence_length = "", 0
            continue
        masked.append(line)
    return "".join(masked)


def merge_instruction(existing: str) -> str:
    pointer = "\n".join((
        POINTER_START,
        "Read `docs/agents/light-project.md` before Light Project workflows. Its managed block is the stable project contract; preserve manual notes outside it.",
        POINTER_END,
    ))
    visible = mask_markdown_fences(existing)
    pointer_pattern = re.compile(re.escape(POINTER_START) + r".*?" + re.escape(POINTER_END), re.S)
    section_pattern = re.compile(r"(?ms)^## Project Initialization\s*$.*?(?=^## (?!#)|\Z)")
    sections = list(section_pattern.finditer(visible))
    if len(sections) > 1:
        raise ValueError("multiple Project Initialization sections require manual reconciliation")
    pointer_starts, pointer_ends = visible.count(POINTER_START), visible.count(POINTER_END)
    if pointer_starts != pointer_ends:
        raise ValueError("unbalanced Light project pointer markers require manual reconciliation")
    if pointer_starts > 1 or len(pointer_pattern.findall(existing)) > 1:
        raise ValueError("multiple Light project pointers require manual reconciliation")
    pointer_match = pointer_pattern.search(visible)
    if pointer_starts == 1 and pointer_match is None:
        raise ValueError("misordered Light project pointer markers require manual reconciliation")
    if pointer_match:
        if not sections or not (sections[0].start() <= pointer_match.start() and pointer_match.end() <= sections[0].end()):
            raise ValueError("Light project pointer must be inside one Project Initialization section")
        return existing[:pointer_match.start()] + pointer + existing[pointer_match.end():]
    if sections:
        section_match = sections[0]
        section = existing[section_match.start():section_match.end()].rstrip()
        updated = section + "\n\n" + pointer + "\n"
        return existing[:section_match.start()] + updated + existing[section_match.end():]
    block = "## Project Initialization\n\n" + pointer + "\n"
    if not existing.strip():
        return block
    return existing.rstrip() + "\n\n" + block


def named_file(root: Path, name: str) -> Optional[Path]:
    matches = sorted(
        (path for path in root.iterdir() if path.is_file() and path.name.lower() == name.lower()),
        key=lambda path: path.name,
    )
    if len(matches) > 1:
        raise ValueError(f"multiple case variants of {name} require manual reconciliation")
    return matches[0] if matches else None


def instruction_target(root: Path, preferred_name: str) -> tuple[Path, bool]:
    agents = named_file(root, "AGENTS.md")
    claude = named_file(root, "CLAUDE.md")
    preferred = agents if preferred_name.lower() == "agents.md" else claude
    other = claude if preferred_name.lower() == "agents.md" else agents
    return (preferred or root / preferred_name), bool(other)


def safe_target(root: Path, relative: Path, *, reject_symlink: bool = False) -> Path:
    unresolved = root / relative
    if reject_symlink and unresolved.is_symlink():
        raise ValueError(f"managed bootstrap target must not be a symlink: {relative}")
    target = unresolved.resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"bootstrap target escapes project root: {relative}") from exc
    return target


def preflight_file_target(path: Path) -> None:
    if path.exists() and not path.is_file():
        raise ValueError(f"bootstrap target exists but is not a regular file: {path}")
    if path.is_file() and not (path.stat().st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)):
        raise ValueError(f"bootstrap target is not writable: {path}")


def prepare_merged(path: Path, rendered: str, *, instruction: bool = False) -> tuple[str, str]:
    existed = path.is_file()
    existing = path.read_text(encoding="utf-8") if existed else ""
    updated = merge_instruction(existing) if instruction else merge_managed(existing, rendered)
    if updated == existing:
        return updated, "preserved"
    return updated, "updated" if existed else "created"


def commit_prepared(root: Path, prepared: dict[Path, tuple[str, str]]) -> None:
    """Stage every changed file, then replace targets with rollback on failure."""
    changed = {path: content for path, (content, status) in prepared.items() if status != "preserved"}
    staged: dict[Path, Path] = {}
    records: list[dict[str, Any]] = []
    created_dirs: list[Path] = []
    try:
        for path, content in changed.items():
            missing: list[Path] = []
            parent = path.parent
            while not parent.exists() and parent != root:
                missing.append(parent)
                parent = parent.parent
            for directory in reversed(missing):
                directory.mkdir()
                created_dirs.append(directory)
            descriptor, staged_name = tempfile.mkstemp(prefix=f".{path.name}.light-stage-", dir=path.parent)
            staged_path = Path(staged_name)
            staged[path] = staged_path
            try:
                handle = os.fdopen(descriptor, "w", encoding="utf-8")
                descriptor = -1
                with handle:
                    handle.write(content)
                    handle.flush()
                    os.fsync(handle.fileno())
            except Exception:
                if descriptor >= 0:
                    os.close(descriptor)
                raise
            if path.exists():
                os.chmod(staged_path, stat.S_IMODE(path.stat().st_mode))
        for path, staged_path in staged.items():
            record: dict[str, Any] = {"target": path, "backup": None, "installed": False}
            records.append(record)
            if path.exists():
                descriptor, backup_name = tempfile.mkstemp(prefix=f".{path.name}.light-backup-", dir=path.parent)
                os.close(descriptor)
                os.remove(backup_name)
                backup = Path(backup_name)
                os.replace(path, backup)
                record["backup"] = backup
            os.replace(staged_path, path)
            record["installed"] = True

        for record in records:
            backup = record["backup"]
            if backup is not None and backup.exists():
                try:
                    os.remove(backup)
                except OSError:
                    pass
    except Exception:
        for record in reversed(records):
            target, backup = record["target"], record["backup"]
            if record["installed"] and target.exists():
                os.remove(target)
            if backup is not None and backup.exists():
                os.replace(backup, target)
        for staged_path in staged.values():
            if staged_path.exists():
                os.remove(staged_path)
        for directory in reversed(created_dirs):
            try:
                os.rmdir(directory)
            except OSError:
                pass
        raise


def bootstrap(
    root: Path,
    config: dict[str, Any],
    capability_roots: Optional[list[Path]] = None,
    unavailable_capabilities: Optional[list[str]] = None,
    jev: Optional[bool] = None,
    agent_target: Optional[str] = None,
    installer_cmd: Optional[list[str]] = None,
    smoke_client: Optional[Any] = None,
    auto_install_sdk: bool = False,
    python_bin: Optional[str] = None,
) -> dict[str, Any]:
    """Bootstrap Light Project contracts with explicit transaction phases.

    Phases:
      Phase A: Preflight validation
      Phase B: Core project-init transaction (writes baseline contracts)
      Phase C: Jev onboarding (official skill check/install, key detection, SDK verify)
      Phase D: Jev verification (minimal System One smoke test)
      Phase E: Contract registration (relevantSkills/constraints updated ONLY if verified)
    """
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"project root does not exist: {root}")
    validate_config(config)

    # Resolve Jev opt-in
    if jev is None:
        if "jev" in config:
            jev = bool(config["jev"])
        elif os.environ.get("CI") or not sys.stdin.isatty():
            jev = False
        else:
            jev = prompt_jev_opt_in()

    # Phase A: Target resolution and preflight checks
    project = safe_target(root, PROJECT_PATH, reject_symlink=True)
    tracker = safe_target(root, TRACKER_PATH, reject_symlink=True)
    instruction, instruction_conflict = instruction_target(root, config["instructionFile"])
    instruction = instruction.resolve()
    instruction.relative_to(root)
    if len({project, tracker, instruction}) != 3:
        raise ValueError("bootstrap targets resolve to the same file; reconcile instruction symlinks before retrying")
    for path in (project, tracker, instruction):
        preflight_file_target(path)

    # Phase B: Core project-init transaction (without unverified Jev additions)
    existing_project = project.read_text(encoding="utf-8") if project.is_file() else ""
    prepared = {
        project: prepare_merged(project, render_project(config, existing_project)),
        tracker: prepare_merged(tracker, render_tracker(config)),
        instruction: prepare_merged(instruction, "", instruction=True),
    }
    commit_prepared(root, prepared)

    statuses = {
        str(path.relative_to(root)): status
        for path, (_, status) in prepared.items()
    }
    conflicts = [f"Both instruction styles exist; only inspected host target {config['instructionFile']} was updated"] if instruction_conflict else []

    # If user opted out of Jev, complete immediately
    if not jev:
        capabilities = inspect_capabilities(config["relevantSkills"], capability_roots, unavailable_capabilities)
        return {
            "projectRoot": str(root),
            "instructionTarget": str(instruction),
            "paths": statuses,
            "conflicts": conflicts,
            "capabilities": capabilities,
        }

    # Phase C: Jev onboarding
    skill_verified = False
    installed_skill_path: Optional[Path] = None
    jev_skill_status = "none"

    active_agent = resolve_active_agent_target(root, config, explicit_target=agent_target)
    if not active_agent:
        jev_skill_status = "TARGET_UNRESOLVED"
    else:
        global_path, global_scope = find_global_skill(
            JEV_SKILL_NAME,
            agent_target=active_agent,
            search_roots=capability_roots,
            include_scope=True,
        )
        if global_path is not None:
            skill_verified = True
            jev_skill_status = global_scope
        else:
            installed, local_path, install_msg = install_official_typesafe_skill(
                project_root=root,
                agent_target=active_agent,
                installer_cmd=installer_cmd,
            )
            if installed and local_path is not None:
                skill_verified = True
                jev_skill_status = "installed-local"
                installed_skill_path = local_path
                if capability_roots is not None:
                    local_root = local_path.parent
                    if local_root not in capability_roots:
                        capability_roots = list(capability_roots) + [local_root]
            else:
                skill_verified = False
                jev_skill_status = install_msg or "SKILL_INCOMPLETE"

    key, key_source = resolve_typesafe_credentials(project_root=root)
    if not key and sys.stdin.isatty():
        key_prompted, key_source = prompt_typesafe_key(project_root=root)
        if key_prompted:
            key, key_source = resolve_typesafe_credentials(project_root=root)
    key_found = bool(key)

    sdk_ok = verify_typesafe_sdk(python_bin=python_bin)
    sdk_declined = False
    if not sdk_ok:
        if auto_install_sdk or (sys.stdin.isatty() and prompt_install_sdk()):
            installed_sdk, _ = install_typesafe_sdk(python_bin=python_bin)
            sdk_ok = verify_typesafe_sdk(python_bin=python_bin)
        elif sys.stdin.isatty():
            sdk_declined = True

    stack_recommendations = detect_project_stack(root)

    # Phase D: Smoke verification & precise setup states
    smoke_ok = False
    smoke_msg = "skipped: prerequisites not met"

    if not active_agent:
        jev_status = "TARGET_UNRESOLVED"
        smoke_msg = "skipped: active agent target unresolved"
    elif not skill_verified:
        jev_status = "SKILL_INCOMPLETE"
        smoke_msg = f"skipped: {jev_skill_status}"
    elif not key_found:
        jev_status = "KEY_MISSING"
        smoke_msg = "skipped: TYPESAFE_API_KEY unavailable"
    elif not sdk_ok:
        jev_status = "SDK_INSTALL_DECLINED" if sdk_declined else "SDK_MISSING"
        smoke_msg = "skipped: typesafe-sdk unavailable"
    else:
        smoke_ok, smoke_msg = verify_jev_runtime(project_root=root, client=smoke_client, api_key=key)
        jev_status = "READY" if smoke_ok else "RUNTIME_UNVERIFIED"

    # Phase E: Contract registration (ONLY if skill verified)
    effective_skills = list(config["relevantSkills"])
    if skill_verified:
        if JEV_SKILL_NAME not in effective_skills:
            effective_skills.append(JEV_SKILL_NAME)

        config_jev = dict(config)
        config_jev["relevantSkills"] = effective_skills
        if "constraints" in config_jev:
            if JEV_CONSTRAINT not in config_jev["constraints"]:
                config_jev["constraints"] = list(config_jev["constraints"]) + [JEV_CONSTRAINT]
        else:
            existing_p = project.read_text(encoding="utf-8") if project.is_file() else ""
            existing_c = existing_managed_value(existing_p, "Constraints")
            if existing_c and existing_c != "none recorded":
                c_list = [c.strip() for c in existing_c.split(",")]
                if JEV_CONSTRAINT not in c_list:
                    c_list.append(JEV_CONSTRAINT)
                config_jev["constraints"] = c_list
            else:
                config_jev["constraints"] = [JEV_CONSTRAINT]

        cur_proj = project.read_text(encoding="utf-8")
        prepared_update = {
            project: prepare_merged(project, render_project(config_jev, cur_proj)),
        }
        commit_prepared(root, prepared_update)
        statuses[str(project.relative_to(root))] = prepared_update[project][1]

    capabilities = inspect_capabilities(effective_skills, capability_roots, unavailable_capabilities)

    report: dict[str, Any] = {
        "projectRoot": str(root),
        "instructionTarget": str(instruction),
        "paths": statuses,
        "conflicts": conflicts,
        "capabilities": capabilities,
        "jev": {
            "enabled": True,
            "status": jev_status,
            "agentTarget": active_agent or "unknown",
            "keyDetected": key_found,
            "keySource": key_source,
            "skillLocation": jev_skill_status,
            "sdkAvailable": sdk_ok,
            "runtimeVerification": smoke_msg,
            "recommendations": stack_recommendations,
        },
    }
    if installed_skill_path is not None:
        try:
            report["jev"]["installedSkillPath"] = str(installed_skill_path.relative_to(root))
        except ValueError:
            report["jev"]["installedSkillPath"] = str(installed_skill_path)

    return report


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap Light Project contracts.")
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--config-json", required=True)
    parser.add_argument("--capability-roots-json", default="[]")
    parser.add_argument("--unavailable-capabilities-json", default="[]")
    parser.add_argument("--agent-target", default=None, help="Target Agent identifier for skills installation (pi, claude, cursor, codex, agy, grok-build, hermes)")
    parser.add_argument("--auto-install-sdk", action="store_true", default=False, help="Automatically install typesafe-sdk into active python runtime if missing")
    parser.add_argument("--jev", dest="jev", action="store_true", default=None, help="Enable TypeSafe Jev semantic acceleration")
    parser.add_argument("--no-jev", dest="jev", action="store_false", help="Disable TypeSafe Jev semantic acceleration")
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()
    roots = [Path(value) for value in json.loads(args.capability_roots_json)]
    unavailable = json.loads(args.unavailable_capabilities_json)
    print(json.dumps(bootstrap(
        args.project_root,
        json.loads(args.config_json),
        roots,
        unavailable,
        jev=args.jev,
        agent_target=args.agent_target,
        auto_install_sdk=args.auto_install_sdk,
    ), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
