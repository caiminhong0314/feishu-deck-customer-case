#!/usr/bin/env python3
"""Validate deterministic customer-case DOM hooks in raw DeckJSON slides."""

from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path


REQUIRED_ATTRIBUTES = {
    "data-case-page",
    "data-case-top-grid",
    "data-case-region",
    "data-case-role",
    "data-case-title",
    "data-case-subtitle",
    "data-case-column-row",
    "data-case-block",
    "data-case-copy-role",
    "data-case-evidence",
    "data-case-display-mode",
    "data-case-source-ratio",
    "data-case-caption-mode",
    "data-case-flow",
    "data-case-flow-placement",
    "data-case-flow-container",
    "data-case-lightbox-trigger",
    "data-case-lightbox",
}


class HookParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.attributes: set[str] = set()
        self.values: dict[str, list[str]] = {}

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.attributes.update(name for name, _value in attrs)
        for name, value in attrs:
            if value is not None:
                self.values.setdefault(name, []).append(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deck", required=True)
    parser.add_argument("--layout-plan")
    args = parser.parse_args()
    deck_path = Path(args.deck).expanduser().resolve()
    errors: list[str] = []
    try:
        deck = json.loads(deck_path.read_text(encoding="utf-8"))
        layout_pages: dict[str, dict] = {}
        if args.layout_plan:
            layout = json.loads(Path(args.layout_plan).expanduser().resolve().read_text(encoding="utf-8"))
            layout_pages = {
                page.get("id"): page
                for page in layout.get("pages", [])
                if isinstance(page, dict) and isinstance(page.get("id"), str)
            }
        slides = deck.get("slides")
        if not isinstance(slides, list):
            raise ValueError("slides must be an array")
        case_slides = 0
        for index, slide in enumerate(slides, start=1):
            if not isinstance(slide, dict) or slide.get("layout") != "raw":
                continue
            data = slide.get("data")
            html = data.get("html") if isinstance(data, dict) else None
            if not isinstance(html, str) or "data-case-page" not in html:
                continue
            case_slides += 1
            hooks = HookParser()
            hooks.feed(html)
            missing = sorted(REQUIRED_ATTRIBUTES - hooks.attributes)
            if missing:
                errors.append(f"slide {index} is missing case hooks: {', '.join(missing)}")
            if "data-case-evidence-sequence" not in hooks.attributes or "data-case-proof-task" not in hooks.attributes:
                errors.append(f"slide {index} must expose sequence and proof task for mechanism evidence")
            page_id = (hooks.values.get("data-case-page") or [None])[0]
            plan_page = layout_pages.get(page_id)
            if plan_page:
                if plan_page.get("metric_count", 0) > 0:
                    for attribute in ("data-case-metric-id", "data-case-metric-placement", "data-case-metric-status"):
                        if attribute not in hooks.attributes:
                            errors.append(f"slide {index} must expose {attribute} for planned metrics")
                if plan_page.get("metric_treatment") == "gradient-cards" and "data-case-metric-band" not in hooks.attributes:
                    errors.append(f"slide {index} must expose the planned metric band hook")
                if plan_page.get("evidence_composition") == {"ref": "asset-plan"}:
                    for attribute in ("data-case-evidence-composition", "data-case-evidence-composition-assets"):
                        if attribute not in hooks.attributes:
                            errors.append(f"slide {index} must expose {attribute}")
                pain = plan_page.get("pain_detail_treatment")
                if isinstance(pain, dict) and pain.get("recipe") != "none":
                    if "data-case-pain-treatment" not in hooks.attributes:
                        errors.append(f"slide {index} must expose data-case-pain-treatment")
                    if pain.get("recipe") == "stacked-cards" and "data-case-pain-point" not in hooks.attributes:
                        errors.append(f"slide {index} must expose data-case-pain-point")
        if case_slides == 0:
            errors.append("deck.json contains no raw customer-case slide with data-case-page")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors = [f"cannot validate deck hooks: {exc}"]
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    print("PASS: raw DeckJSON exposes deterministic customer-case hooks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
