#!/usr/bin/env python3
"""Verify the exact customer-case HTML artifact that will be delivered."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


LOCAL_ATTRIBUTES = {"src", "href", "poster"}
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name.lower() in LOCAL_ATTRIBUTES and value:
                self.references.append(value)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def normalize_reference(raw: str, base: Path) -> Path | None:
    value = raw.strip()
    if not value or value.startswith("#"):
        return None
    parsed = urlsplit(value)
    if parsed.scheme in {"http", "https", "data", "blob", "mailto", "tel", "javascript"}:
        return None
    if parsed.scheme == "file":
        return Path(unquote(parsed.path)).resolve()
    if parsed.scheme:
        return None
    path_text = unquote(parsed.path)
    if not path_text:
        return None
    path = Path(path_text)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def inspect_screenshot(path: Path) -> tuple[bool, dict, list[str]]:
    errors: list[str] = []
    details: dict = {"path": str(path), "sha256": None, "width": None, "height": None}
    if not path.is_file() or path.stat().st_size < 1000:
        return False, details, [f"screenshot is missing or too small: {path}"]
    details["sha256"] = sha256_file(path)
    try:
        from PIL import Image, ImageStat

        with Image.open(path) as image:
            image = image.convert("RGB")
            details["width"], details["height"] = image.size
            if image.width < 320 or image.height < 180:
                errors.append("screenshot dimensions are too small for visual QA")
            sample = image.copy()
            sample.thumbnail((160, 160))
            colors = sample.getcolors(maxcolors=160 * 160)
            details["sample_unique_colors"] = len(colors) if colors else 160 * 160
            deviation = ImageStat.Stat(sample).stddev
            details["sample_stddev"] = [round(value, 2) for value in deviation]
            if colors is not None and len(colors) < 8:
                errors.append("screenshot appears blank or nearly uniform")
            if max(deviation) < 2.0:
                errors.append("screenshot has insufficient pixel variation")
    except ImportError:
        details["pixel_check"] = "Pillow unavailable; structural screenshot check only"
    except Exception as exc:
        errors.append(f"cannot inspect screenshot pixels: {exc}")
    return not errors, details, errors


def inspect_interactions(path: Path, html_hash: str | None) -> tuple[dict, list[str]]:
    errors: list[str] = []
    details: dict = {"path": str(path), "pass": False}
    if not path.is_file():
        return details, [f"interaction report is missing: {path}"]
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return details, [f"cannot read interaction report: {exc}"]
    details = report
    details["path"] = str(path)
    if report.get("schema_version") != 1:
        errors.append("interaction report schema_version must be 1")
    if report.get("target_html_sha256") != html_hash:
        errors.append("interaction report belongs to a different HTML revision")
    if report.get("pass") is not True:
        errors.append("interaction report is not marked passed")
    checks = report.get("checks")
    required = (
        "lightbox_opens_complete_image",
        "lightbox_closes_on_image_or_overlay_click",
        "layout_stable_after_close",
    )
    if not isinstance(checks, dict):
        errors.append("interaction report checks must be an object")
    else:
        for name in required:
            if checks.get(name) is not True:
                errors.append(f"interaction check did not pass: {name}")
    viewports = report.get("scroll_viewports")
    if not isinstance(viewports, list):
        errors.append("interaction report scroll_viewports must be an array")
    else:
        for index, viewport in enumerate(viewports):
            if not isinstance(viewport, dict):
                errors.append(f"scroll_viewports[{index}] must be an object")
                continue
            if not isinstance(viewport.get("id"), str) or not viewport.get("id"):
                errors.append(f"scroll_viewports[{index}] id is required")
            axes = viewport.get("axes")
            if (
                not isinstance(axes, list)
                or not axes
                or any(axis not in {"vertical", "horizontal"} for axis in axes)
            ):
                errors.append(
                    f"scroll_viewports[{index}] axes must contain vertical and/or horizontal"
                )
            if viewport.get("pass") is not True:
                errors.append(f"scroll_viewports[{index}] did not pass")
    return details, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", required=True)
    parser.add_argument("--mode", choices=["linked", "single"], required=True)
    parser.add_argument("--viewer", choices=["local", "in-app", "share"], required=True)
    parser.add_argument("--screenshot", required=True)
    parser.add_argument("--interaction-report", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--allow-large-in-app", action="store_true")
    args = parser.parse_args()

    html_path = Path(args.html).expanduser().resolve()
    screenshot_path = Path(args.screenshot).expanduser().resolve()
    interaction_path = Path(args.interaction_report).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    references: list[str] = []
    missing: list[str] = []

    if not html_path.is_file():
        errors.append(f"HTML does not exist: {html_path}")
        html_text = ""
        size = 0
        html_hash = None
    else:
        size = html_path.stat().st_size
        html_hash = sha256_file(html_path)
        html_text = html_path.read_text(encoding="utf-8", errors="replace")
        lowered = html_text.lower()
        if size < 500:
            errors.append("HTML is suspiciously small")
        for token in ("<html", "<body", "slide-frame", "data-slide-key"):
            if token not in lowered:
                errors.append(f"HTML contract token is missing: {token}")

        parser_impl = ReferenceParser()
        parser_impl.feed(html_text)
        parser_impl.references.extend(match[1] for match in CSS_URL.findall(html_text))
        seen: set[str] = set()
        for raw in parser_impl.references:
            local = normalize_reference(raw, html_path.parent)
            if local is None:
                continue
            key = str(local)
            if key in seen:
                continue
            seen.add(key)
            references.append(key)
            if not local.exists():
                missing.append(key)

        if args.mode == "linked" and missing:
            errors.append(f"linked HTML has {len(missing)} missing local resource(s)")
        if args.mode == "single" and references:
            errors.append(
                f"single-file HTML still references {len(references)} local resource(s)"
            )
        if (
            args.mode == "single"
            and args.viewer == "in-app"
            and size > 5 * 1024 * 1024
            and not args.allow_large_in_app
        ):
            errors.append(
                "self-contained HTML exceeds 5 MB and was not explicitly tested/allowed for the in-app viewer"
            )

    screenshot_ok, screenshot_details, screenshot_errors = inspect_screenshot(screenshot_path)
    if not screenshot_ok:
        errors.extend(screenshot_errors)
    interaction_details, interaction_errors = inspect_interactions(interaction_path, html_hash)
    errors.extend(interaction_errors)
    if args.mode == "linked" and not references:
        warnings.append("linked mode contains no local resource references")

    manifest = {
        "schema_version": 1,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "pass": not errors,
        "html": {
            "path": str(html_path),
            "size_bytes": size,
            "sha256": html_hash,
            "mode": args.mode,
            "viewer": args.viewer,
            "local_references": references,
            "missing_references": missing,
        },
        "screenshot": screenshot_details,
        "interactions": interaction_details,
        "errors": errors,
        "warnings": warnings,
    }
    atomic_write(manifest_path, manifest)
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        print(f"manifest written: {manifest_path}", file=sys.stderr)
        return 2
    print(f"PASS: exact delivery verified; manifest={manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
