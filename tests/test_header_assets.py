"""Port of tests/header-asset-tests.ps1."""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_helpers import Checks  # noqa: E402


def read_uint32_be(data: bytes, offset: int) -> int:
    return (data[offset] << 24) | (data[offset + 1] << 16) | (data[offset + 2] << 8) | data[offset + 3]


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    svg_path = root / "skills/docs/assets/skills-header.svg"
    png_path = root / "skills/docs/assets/skills-header.png"
    manifest_path = root / "skills/docs/assets/skills-header.json"

    c.check(svg_path.is_file(), "Editable SVG is missing.")
    c.check(png_path.is_file(), "PNG header is missing.")
    c.check(manifest_path.is_file(), "Header asset manifest is missing.")

    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        c.check(
            manifest.get("source_svg") == "skills-header.svg"
            and manifest.get("rendered_png") == "skills-header.png"
            and manifest.get("width") == 1536
            and manifest.get("height") == 1024,
            "Header asset manifest does not describe the current 1536x1024 PNG.",
        )

    if svg_path.is_file():
        svg = svg_path.read_text(encoding="utf-8")
        c.check(
            bool(re.search(r"<svg\b", svg))
            and 'width="1600"' in svg
            and 'height="480"' in svg
            and 'viewBox="0 0 1600 480"' in svg,
            "SVG dimensions/viewBox are not 1600x480.",
        )
        c.check(
            "LightDevCoder" in svg and "/skills" in svg and "Personal Skills Collection" in svg,
            "SVG does not contain the requested wordmark and slogan.",
        )
        c.check('fill="#72a0a3"' in svg and "translate(6 8)" in svg, "SVG does not contain the flat under-layer typography.")

    if png_path.is_file():
        png = png_path.read_bytes()
        c.check(
            len(png) > 100 and png[0] == 137 and png[1] == 80 and png[2] == 78 and png[3] == 71,
            "PNG signature is invalid.",
        )
        if len(png) >= 24 and manifest_path.is_file():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            c.check(
                read_uint32_be(png, 16) == manifest.get("width") and read_uint32_be(png, 20) == manifest.get("height"),
                "PNG IHDR dimensions do not match the header asset manifest.",
            )

    if manifest_path.is_file() and svg_path.is_file() and png_path.is_file():
        import hashlib

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        svg_hash = hashlib.sha256(svg_path.read_bytes()).hexdigest()
        png_hash = hashlib.sha256(png_path.read_bytes()).hexdigest()
        c.check(svg_hash == manifest.get("svg_sha256"), "SVG does not match the checked-in header asset manifest.")
        c.check(png_hash == manifest.get("png_sha256"), "PNG does not match the checked-in header asset manifest.")

    return c.assertions, c.failures


class HeaderAssetsTest(unittest.TestCase):
    def test_header_assets(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"HEADER_ASSETS=FAIL: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
