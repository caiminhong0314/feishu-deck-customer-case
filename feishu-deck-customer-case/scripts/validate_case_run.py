#!/usr/bin/env python3
"""Validate the complete customer-case artifact chain before local delivery."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


REQUIRED_FILES = (
    "case-state.json",
    "input/SOURCE-NOTES.md",
    "output/STORY-REVIEW.md",
    "output/story-contract.json",
    "output/asset-plan.json",
    "output/asset-validation.json",
    "output/DESIGN-PLAN.md",
    "output/layout-plan.json",
    "output/layout-validation.json",
    "output/rendered-layout.json",
    "output/rendered-layout-validation.json",
    "output/outline.json",
    "output/deck.json",
    "output/index.html",
    "output/QA-NOTES.md",
    "output/qa-notes.json",
    "output/interaction-check.json",
    "output/delivery-manifest.json",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    errors: list[str] = []
    checks: dict[str, bool] = {}
    if not run_dir.is_dir():
        errors.append(f"run directory does not exist: {run_dir}")
    for relative in REQUIRED_FILES:
        present = (run_dir / relative).is_file()
        checks[f"exists:{relative}"] = present
        if not present:
            errors.append(f"missing required artifact: {relative}")
    if not errors:
        try:
            state = read_json(run_dir / "case-state.json")
            state_ok = state.get("state") == "VALIDATED"
            checks["state:VALIDATED"] = state_ok
            if not state_ok:
                errors.append("case-state.json must be VALIDATED before final run validation")
            state_contract_ok = state.get("schema_version") == 2 and isinstance(state.get("deck_id"), str)
            checks["state-contract-v2"] = state_contract_ok
            if not state_contract_ok:
                errors.append("case-state.json must use schema_version 2 with a stable deck_id")
            story = run_dir / "output" / "STORY-REVIEW.md"
            contract = read_json(run_dir / "output" / "story-contract.json")
            contract_ok = contract.get("story_hash") == sha256_file(story)
            checks["story-contract-hash"] = contract_ok
            if not contract_ok:
                errors.append("story-contract.json does not match STORY-REVIEW.md")
            if state.get("story", {}).get("sha256") != sha256_file(story):
                errors.append("case-state.json does not match STORY-REVIEW.md")

            asset_plan = run_dir / "output" / "asset-plan.json"
            asset_report = read_json(run_dir / "output" / "asset-validation.json")
            asset_ok = asset_report.get("pass") is True and asset_report.get("plan_sha256") == sha256_file(asset_plan)
            checks["asset-validation"] = asset_ok
            if not asset_ok:
                errors.append("asset validation is missing, failed, or belongs to another asset plan")

            layout_plan = run_dir / "output" / "layout-plan.json"
            layout_report = read_json(run_dir / "output" / "layout-validation.json")
            layout_ok = layout_report.get("pass") is True and layout_report.get("plan_sha256") == sha256_file(layout_plan)
            checks["layout-validation"] = layout_ok
            if not layout_ok:
                errors.append("layout validation is missing, failed, or belongs to another layout plan")

            html = run_dir / "output" / "index.html"
            rendered_report = read_json(run_dir / "output" / "rendered-layout-validation.json")
            rendered_ok = (
                rendered_report.get("pass") is True
                and rendered_report.get("layout_plan_sha256") == sha256_file(layout_plan)
                and rendered_report.get("html_sha256") == sha256_file(html)
            )
            checks["rendered-layout-validation"] = rendered_ok
            if not rendered_ok:
                errors.append("rendered layout validation is missing, failed, or belongs to another HTML/layout plan")

            qa = read_json(run_dir / "output" / "qa-notes.json")
            qa_ok = (
                qa.get("schema_version") == 1
                and qa.get("pass") is True
                and qa.get("base_validator") == "pass"
                and qa.get("unresolved_limitations") == []
                and qa.get("html", {}).get("sha256") == sha256_file(html)
                and Path(qa.get("html", {}).get("path", "")).expanduser().resolve() == html
                and isinstance(qa.get("checks"), dict)
                and all(value == "pass" for value in qa["checks"].values())
            )
            checks["qa-notes-json"] = qa_ok
            if not qa_ok:
                errors.append("qa-notes.json does not pass for the exact final HTML")

            deck = read_json(run_dir / "output" / "deck.json")
            deck_id_ok = deck.get("deck", {}).get("deck_id") == state.get("deck_id")
            checks["deck-id"] = deck_id_ok
            if not deck_id_ok:
                errors.append("deck.json deck.deck_id must match case-state.json deck_id")

            manifest = read_json(run_dir / "output" / "delivery-manifest.json")
            manifest_ok = (
                manifest.get("pass") is True
                and manifest.get("html", {}).get("sha256") == sha256_file(html)
                and Path(manifest.get("html", {}).get("path", "")).expanduser().resolve() == html
            )
            checks["delivery-manifest"] = manifest_ok
            if not manifest_ok:
                errors.append("delivery-manifest.json does not pass for the exact final HTML")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"cannot validate complete artifact chain: {exc}")
    result = {
        "schema_version": 2,
        "pass": not errors,
        "run_dir": str(run_dir),
        "output_dir": str(run_dir / "output"),
        "checks": checks,
        "errors": errors,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    print(f"PASS: complete case run validated; report={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
