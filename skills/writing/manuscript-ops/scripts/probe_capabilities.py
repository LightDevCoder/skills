#!/usr/bin/env python3
"""Probe local format dependencies without installing or changing anything."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from manuscript_ops_core import (
    ContractError,
    dump_json,
    load_json,
    parse_timestamp,
    sha256_file,
    utc_now,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    assets = Path(__file__).resolve().parents[1] / "assets"
    default_registry = assets / "format-registry.json"
    parser.add_argument("--registry", type=Path, default=default_registry)
    parser.add_argument(
        "--declare",
        action="append",
        default=[],
        help="Legacy unaudited capability declaration; prefer --platform-capabilities",
    )
    parser.add_argument(
        "--platform-capabilities",
        type=Path,
        help="Structured host capability evidence JSON",
    )
    parser.add_argument(
        "--capability-map",
        type=Path,
        default=assets / "platform-capability-map.json",
        help="Known logical host capabilities and required operation coverage",
    )
    parser.add_argument("--compact", action="store_true")
    return parser.parse_args()


def _which(*names: str) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return str(Path(found).resolve())
    return None


def _module(*names: str) -> str | None:
    for name in names:
        if importlib.util.find_spec(name) is None:
            continue
        try:
            importlib.import_module(name)
        except Exception:
            continue
        return name
    return None


def _command_version(executable: str | None) -> str | None:
    if not executable:
        return None
    try:
        result = subprocess.run(
            [executable, "--version"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    text = (result.stdout or result.stderr).strip()
    return text.splitlines()[0][:200] if text else None


def _distribution_version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def _playwright_browser() -> tuple[str | None, str | None]:
    if importlib.util.find_spec("playwright") is None:
        return None, None
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as manager:
            executable = Path(manager.chromium.executable_path)
    except Exception:
        return None, None
    if not executable.is_file():
        return None, None
    version = _command_version(str(executable))
    return (str(executable.resolve()), version) if version else (None, None)


def _windows_app_path(executable: str) -> str | None:
    found = _which(executable)
    if found:
        return found
    if os.name != "nt":
        return None
    try:
        import winreg
    except ImportError:
        return None
    key_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{executable}"
    for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        for view in (0, winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
            try:
                with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ | view) as key:
                    value, _ = winreg.QueryValueEx(key, None)
                    if value and Path(value).exists():
                        return str(Path(value).resolve())
            except OSError:
                continue
    return None


PROCESS_OPERATIONS: dict[str, list[str]] = {
    "jj": ["version_control"],
    "pandoc": ["read", "edit", "generate", "structural_qa"],
    "libreoffice": ["read", "edit", "generate", "render", "round_trip", "structural_qa"],
    "microsoft_word": ["read", "edit", "generate", "render", "round_trip"],
    "microsoft_powerpoint": ["read", "edit", "generate", "render", "round_trip"],
    "microsoft_excel": ["read", "edit", "generate", "render", "round_trip"],
    "poppler": ["read", "render", "structural_qa"],
    "pdfa_validator": ["structural_qa", "standards_validation"],
    "epubcheck": ["standards_validation"],
    "epub_renderer": ["render"],
    "latex_engine": ["generate", "render", "structural_qa"],
    "biber": ["generate", "structural_qa"],
    "html_validator": ["structural_qa"],
    "accessibility_checker": ["accessibility_qa"],
    "docx_library": ["read", "edit", "generate", "structural_qa"],
    "pdf_library": ["read", "edit", "generate", "structural_qa"],
    "epub_library": ["read", "edit", "generate", "structural_qa"],
    "pptx_library": ["read", "edit", "generate", "structural_qa"],
    "xlsx_library": ["read", "edit", "generate", "structural_qa"],
    "odf_library": ["read", "edit", "generate", "structural_qa"],
    "pillow": ["read", "edit", "generate"],
    "browser": ["render", "runtime_qa"],
}

DERIVED_ALIAS_PARENTS: dict[str, tuple[str, ...]] = {
    "rtf_capable_editor": ("microsoft_word", "libreoffice"),
    "spreadsheet_application": ("microsoft_excel", "libreoffice"),
}


def load_capability_map(path: Path) -> dict[str, set[str]]:
    value = load_json(path)
    if (
        not isinstance(value, dict)
        or value.get("schema_version") != "1"
        or not isinstance(value.get("capabilities"), dict)
    ):
        raise ContractError("platform capability map is invalid")
    result: dict[str, set[str]] = {}
    for name, item in value["capabilities"].items():
        if (
            not isinstance(name, str)
            or not name
            or not isinstance(item, dict)
            or not isinstance(item.get("operations"), list)
            or not item["operations"]
            or not all(isinstance(operation, str) and operation for operation in item["operations"])
        ):
            raise ContractError(f"invalid platform capability map entry: {name!r}")
        result[name] = set(item["operations"])
    return result


def load_platform_capabilities(
    path: Path | None,
    capability_map_path: Path | None = None,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any] | None]:
    if path is None:
        return {}, None
    if capability_map_path is None:
        capability_map_path = (
            Path(__file__).resolve().parents[1]
            / "assets"
            / "platform-capability-map.json"
        )
    capability_map = load_capability_map(capability_map_path)
    value = load_json(path)
    if not isinstance(value, dict) or not isinstance(value.get("capabilities"), list):
        raise ContractError("platform capability snapshot must contain a capabilities array")
    if value.get("schema_version") != "1":
        raise ContractError("platform capability snapshot schema_version must be 1")
    captured_at = value.get("captured_at")
    platform = value.get("platform")
    if not isinstance(captured_at, str) or not captured_at:
        raise ContractError("platform capability snapshot requires captured_at")
    try:
        parse_timestamp(captured_at)
    except (ContractError, ValueError) as exc:
        raise ContractError(f"platform capability snapshot has invalid captured_at: {exc}") from exc
    if not isinstance(platform, str) or not platform:
        raise ContractError("platform capability snapshot requires platform")
    observed: dict[str, dict[str, Any]] = {}
    for item in value["capabilities"]:
        if not isinstance(item, dict):
            raise ContractError("platform capability entries must be objects")
        name = item.get("name")
        provider = item.get("provider")
        version = item.get("version")
        evidence = item.get("evidence")
        operations = item.get("operations")
        if not all(isinstance(field, str) and field for field in (name, provider, version, evidence)):
            raise ContractError("platform capability entries require name, provider, version, and evidence")
        if not isinstance(operations, list) or not operations or not all(
            isinstance(operation, str) and operation for operation in operations
        ):
            raise ContractError(f"platform capability {name!r} requires operations")
        if name not in capability_map:
            raise ContractError(f"unknown platform capability: {name}")
        missing_operations = sorted(capability_map[name] - set(operations))
        if missing_operations:
            raise ContractError(
                f"platform capability {name!r} omits required operations: "
                f"{missing_operations}"
            )
        if name in observed:
            raise ContractError(f"duplicate platform capability: {name}")
        observed[name] = {
            "available": True,
            "evidence": evidence,
            "provider": provider,
            "version": version,
            "operations": operations,
            "source": "platform_snapshot",
        }
    return observed, {
        "path": str(path.resolve()),
        "sha256": sha256_file(path.resolve()),
        "platform": platform,
        "captured_at": captured_at,
        "capability_map": {
            "path": str(capability_map_path.resolve()),
            "sha256": sha256_file(capability_map_path.resolve()),
        },
    }


def observe(
    declared: set[str],
    platform_observed: dict[str, dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    browser_path, browser_version = _playwright_browser()
    raw: dict[str, str | None] = {
        "jj": _which("jj"),
        "pandoc": _which("pandoc"),
        "libreoffice": _which("soffice", "libreoffice"),
        "microsoft_word": _windows_app_path("WINWORD.EXE"),
        "microsoft_powerpoint": _windows_app_path("POWERPNT.EXE"),
        "microsoft_excel": _windows_app_path("EXCEL.EXE"),
        "poppler": _which("pdftoppm", "mutool"),
        "pdfa_validator": _which("verapdf"),
        "epubcheck": _which("epubcheck"),
        "epub_renderer": _which("ebook-viewer"),
        "latex_engine": _which("lualatex", "xelatex", "pdflatex"),
        "biber": _which("biber"),
        "html_validator": _which("html-validate", "vnu"),
        "accessibility_checker": _which("axe", "pa11y"),
        "docx_library": _module("docx"),
        "pdf_library": _module("pypdf", "fitz"),
        "epub_library": _module("ebooklib"),
        "pptx_library": _module("pptx"),
        "xlsx_library": _module("openpyxl"),
        "odf_library": _module("odf"),
        "pillow": _module("PIL"),
        "browser": browser_path,
    }
    versions = {
        "jj": _command_version(raw["jj"]),
        "pandoc": _command_version(raw["pandoc"]),
        "libreoffice": _command_version(raw["libreoffice"]),
        "poppler": _command_version(raw["poppler"]),
        "pdfa_validator": _command_version(raw["pdfa_validator"]),
        "epubcheck": _command_version(raw["epubcheck"]),
        "epub_renderer": _command_version(raw["epub_renderer"]),
        "latex_engine": _command_version(raw["latex_engine"]),
        "biber": _command_version(raw["biber"]),
        "html_validator": _command_version(raw["html_validator"]),
        "accessibility_checker": _command_version(raw["accessibility_checker"]),
        "docx_library": _distribution_version("python-docx"),
        "pdf_library": _distribution_version("pypdf") or _distribution_version("PyMuPDF"),
        "epub_library": _distribution_version("EbookLib"),
        "pptx_library": _distribution_version("python-pptx"),
        "xlsx_library": _distribution_version("openpyxl"),
        "odf_library": _distribution_version("odfpy"),
        "pillow": _distribution_version("Pillow"),
        "browser": browser_version,
    }
    cli_capabilities = {
        "jj",
        "pandoc",
        "libreoffice",
        "poppler",
        "pdfa_validator",
        "epubcheck",
        "epub_renderer",
        "latex_engine",
        "biber",
        "html_validator",
        "accessibility_checker",
    }
    installed_apps = {
        "microsoft_word",
        "microsoft_powerpoint",
        "microsoft_excel",
    }
    observed: dict[str, dict[str, Any]] = {}
    for name, evidence in raw.items():
        if name in cli_capabilities:
            available = bool(evidence and versions.get(name))
        elif name in installed_apps:
            # Installation discovery is not evidence that automation, rendering,
            # or round-trip control is available to this host session.
            available = False
        else:
            available = bool(evidence)
        source = (
            "process_probe"
            if available
            else ("installed_unproven" if evidence else None)
        )
        provider = (
            "local-process-probe"
            if available
            else ("path-detected-unproven" if evidence else None)
        )
        version = versions.get(name) if available else ("probe-failed" if evidence else None)
        operations = PROCESS_OPERATIONS.get(name, []) if available else []
        if name in declared and not available:
            available = True
            evidence = evidence or "legacy declaration by caller"
            provider = "legacy-declare"
            version = "unreported"
            operations = []
            source = "legacy_declare"
        observed[name] = {
            "available": available,
            "evidence": evidence,
            "provider": provider,
            "version": version,
            "operations": operations,
            "source": source,
        }
    observed.update(platform_observed or {})

    unavailable = {
        "available": False,
        "evidence": None,
        "provider": None,
        "version": None,
        "operations": [],
        "source": None,
    }
    aliases = {
        "image_inspector": dict(unavailable),
        "rtf_capable_editor": dict(unavailable),
        "spreadsheet_application": dict(unavailable),
        "microsoft_365_connector": dict(unavailable),
        "google_workspace_connector": dict(unavailable),
        "apple_iwork_application": dict(unavailable),
    }
    for name in (
        "image_inspector",
        "microsoft_365_connector",
        "google_workspace_connector",
        "apple_iwork_application",
    ):
        if name in observed and observed[name].get("available"):
            aliases[name] = observed[name]
        elif name in declared:
            aliases[name] = {
                "available": True,
                "evidence": "legacy declaration by caller",
                "provider": "legacy-declare",
                "version": "unreported",
                "operations": [],
                "source": "legacy_declare",
            }
    def derived_alias(*names: str) -> dict[str, Any]:
        for source_name in names:
            source = observed[source_name]
            if source.get("available"):
                return {
                    **source,
                    "source": f"derived_alias:{source_name}",
                }
        return dict(unavailable)

    for alias_name, parent_names in DERIVED_ALIAS_PARENTS.items():
        aliases[alias_name] = derived_alias(*parent_names)
    observed.update(aliases)
    for name in declared:
        observed.setdefault(
            name,
            {
                "available": True,
                "evidence": "legacy declaration by caller",
                "provider": "legacy-declare",
                "version": "unreported",
                "operations": [],
                "source": "legacy_declare",
            },
        )
    return observed


RENDER_GROUPS: dict[str, tuple[tuple[tuple[str, ...], str], ...]] = {
    "markdown": ((("browser",), "render"), (("image_inspector",), "visual_qa")),
    "docx": (
        (("microsoft_word", "libreoffice", "docx_renderer"), "render"),
        (("image_inspector",), "visual_qa"),
    ),
    "pdf": ((("poppler", "pdf_renderer"), "render"), (("image_inspector",), "visual_qa")),
    "html": ((("browser",), "render"), (("image_inspector",), "visual_qa")),
    "epub": ((("epub_renderer",), "render"), (("image_inspector",), "visual_qa")),
    "pptx": (
        (("microsoft_powerpoint", "libreoffice", "presentation_renderer"), "render"),
        (("image_inspector",), "visual_qa"),
    ),
    "odt": ((("libreoffice",), "render"), (("image_inspector",), "visual_qa")),
    "rtf": ((("rtf_capable_editor",), "render"), (("image_inspector",), "visual_qa")),
    "latex": (
        (("latex_engine",), "render"),
        (("poppler",), "render"),
        (("image_inspector",), "visual_qa"),
    ),
    "odp": ((("libreoffice",), "render"), (("image_inspector",), "visual_qa")),
    "xlsx": (
        (("microsoft_excel", "libreoffice", "spreadsheet_renderer"), "render"),
        (("image_inspector",), "visual_qa"),
    ),
    "ods": ((("libreoffice",), "render"), (("image_inspector",), "visual_qa")),
    "google-workspace": (
        (("google_workspace_connector",), "render"),
        (("image_inspector",), "visual_qa"),
    ),
    "microsoft-365": (
        (("microsoft_365_connector",), "render"),
        (("image_inspector",), "visual_qa"),
    ),
    "apple-iwork": (
        (("apple_iwork_application",), "render"),
        (("image_inspector",), "visual_qa"),
    ),
}

PROVIDER_ALTERNATIVES = {
    "docx_provider": ("docx_provider", "docx_library", "document_provider"),
    "pdf_provider": ("pdf_provider", "pdf_library", "pdf_tool"),
    "epub_provider": ("epub_provider", "epub_library", "epub_tool"),
    "presentation_provider": ("presentation_provider", "pptx_library"),
    "spreadsheet_provider": ("spreadsheet_provider", "xlsx_library"),
}

DEPENDENCY_OPERATIONS: dict[str, set[str]] = {
    "docx_provider": {"read", "edit", "generate"},
    "pdf_provider": {"read", "generate"},
    "epub_provider": {"read", "edit", "generate"},
    "presentation_provider": {"read", "edit", "generate"},
    "spreadsheet_provider": {"read", "edit", "generate"},
    "libreoffice": {"read", "edit", "generate"},
    "rtf_capable_editor": {"read", "edit", "generate"},
    "google_workspace_connector": {"read", "edit", "generate"},
    "microsoft_365_connector": {"read", "edit", "generate"},
    "apple_iwork_application": {"read", "edit", "generate"},
}


def capability_available(
    name: str,
    observed: dict[str, dict[str, Any]],
    required_operations: set[str] | None = None,
) -> bool:
    alternatives = PROVIDER_ALTERNATIVES.get(name, (name,))
    required_operations = required_operations or set()
    for candidate in alternatives:
        evidence = observed.get(candidate, {})
        if not evidence.get("available", False):
            continue
        if evidence.get("source") == "legacy_declare":
            continue
        operations = set(evidence.get("operations", []))
        if required_operations.issubset(operations):
            return True
    return False


def adapter_status(adapter: dict[str, Any], observed: dict[str, dict[str, Any]]) -> dict[str, Any]:
    missing_required = [
        name
        for name in adapter.get("required_dependencies", [])
        if not capability_available(
            name,
            observed,
            DEPENDENCY_OPERATIONS.get(name, set()),
        )
    ]
    missing_render_groups = []
    for group, operation in RENDER_GROUPS.get(adapter["id"], ()):
        if not any(
            capability_available(name, observed, {operation})
            for name in group
        ):
            missing_render_groups.append(list(group))
    missing_validation_groups = []
    for requirement in adapter.get("validation_dependencies", []):
        group = tuple(requirement.get("alternatives", []))
        operation = requirement.get("operation")
        if not any(
            capability_available(name, observed, {operation})
            for name in group
        ):
            missing_validation_groups.append(list(group))

    if missing_required:
        status = "BLOCKED"
    elif missing_render_groups or missing_validation_groups:
        status = "BLOCKED" if adapter.get("blocking_qa_gaps", False) else "DEGRADED"
    else:
        status = "READY"
    return {
        "id": adapter["id"],
        "format": adapter["format"],
        "tier": adapter["tier"],
        "status": status,
        "missing_required": missing_required,
        "missing_render_or_visual_groups": missing_render_groups,
        "missing_validation_groups": missing_validation_groups,
        "claim_limit": adapter["degradation"] if status != "READY" else None,
    }


def main() -> int:
    args = parse_args()
    try:
        registry = load_json(args.registry)
        if not isinstance(registry, dict) or not isinstance(registry.get("adapters"), list):
            raise ContractError("registry must contain an adapters array")
        declared = set(args.declare)
        platform_observed, platform_snapshot = load_platform_capabilities(
            args.platform_capabilities,
            args.capability_map,
        )
        observed = observe(declared, platform_observed)
        result = {
            "schema_version": "1",
            "captured_at": utc_now(),
            "registry": str(args.registry.resolve()),
            "declared_capabilities": sorted(declared),
            "platform_snapshot": platform_snapshot,
            "observed": observed,
            "adapters": [adapter_status(item, observed) for item in registry["adapters"]],
            "claim_warning": "A process probe cannot prove host-tool access or visual inspection. Prefer a structured, evidence-backed platform snapshot; legacy --declare evidence cannot establish final acceptance.",
        }
    except (ContractError, OSError, json.JSONDecodeError) as exc:
        print(f"capability probe error: {exc}", file=sys.stderr)
        return 2
    print(dump_json(result, pretty=not args.compact))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
