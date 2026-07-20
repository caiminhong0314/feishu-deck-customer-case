#!/usr/bin/env python3
"""Compare a generated layout plan with an isolated regression fixture."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def validate(fixture: dict, plan: dict) -> list[str]:
    errors: list[str] = []
    if fixture.get("version") not in {3, 4}:
        errors.append("fixture version must be 3 or 4")
    pages = plan.get("pages")
    page_count = len(pages) if isinstance(pages, list) else None
    if page_count != fixture.get("expected_page_count"):
        errors.append(
            f"page count drift: expected {fixture.get('expected_page_count')}, got {page_count}"
        )
    expected_layout_mode = fixture.get("expected_layout_mode")
    if expected_layout_mode and expected_layout_mode != plan.get("layout_mode"):
        errors.append(
            f"layout mode drift: expected {expected_layout_mode!r}, got {plan.get('layout_mode')!r}"
        )

    expected_case_grammar = fixture.get("expected_case_grammar")
    if expected_case_grammar and expected_case_grammar != plan.get("case_grammar"):
        errors.append(
            f"case grammar drift: expected {expected_case_grammar!r}, got {plan.get('case_grammar')!r}"
        )

    expected_flow_placement = fixture.get("expected_flow_placement")
    if expected_flow_placement and expected_flow_placement != plan.get("flow_placement"):
        errors.append(
            f"flow placement drift: expected {expected_flow_placement!r}, got {plan.get('flow_placement')!r}"
        )

    expected_metric_treatment = fixture.get("expected_metric_treatment")
    if expected_metric_treatment and isinstance(pages, list):
        styles = {page.get("metric_treatment") for page in pages if isinstance(page, dict)}
        if styles != {expected_metric_treatment}:
            errors.append(
                f"metric treatment drift: expected only {expected_metric_treatment!r}, got {sorted(str(item) for item in styles)}"
            )

    if fixture.get("version") == 4 and isinstance(pages, list):
        expected_focus = fixture.get("expected_dominant_business_task")
        if expected_focus:
            actual_focuses = {page.get("dominant_business_task") for page in pages if isinstance(page, dict)}
            if actual_focuses != {expected_focus}:
                errors.append(
                    f"dominant business task drift: expected only {expected_focus!r}, got {sorted(str(item) for item in actual_focuses)}"
                )
        expected_metric_roles = fixture.get("expected_metric_roles", [])
        if expected_metric_roles:
            actual_metric_roles: set[str] = set()
            for page in pages:
                if not isinstance(page, dict):
                    continue
                for metric in page.get("metrics", []):
                    if isinstance(metric, dict) and metric.get("prominent") is True and isinstance(metric.get("metric_role"), str):
                        actual_metric_roles.add(metric["metric_role"])
            if set(expected_metric_roles) != actual_metric_roles:
                errors.append(
                    f"prominent metric role drift: expected {sorted(expected_metric_roles)}, got {sorted(actual_metric_roles)}"
                )
        expected_evidence_order = fixture.get("expected_flow_evidence_order", [])
        if expected_evidence_order:
            first_page = pages[0] if pages else {}
            actual_order = first_page.get("flow_evidence_order") if isinstance(first_page, dict) else None
            if actual_order != expected_evidence_order:
                errors.append(
                    f"flow evidence order drift: expected {expected_evidence_order!r}, got {actual_order!r}"
                )
        expected_weights = fixture.get("expected_column_role_weights")
        if expected_weights:
            first_page = pages[0] if pages else {}
            actual_weights = first_page.get("column_role_weights") if isinstance(first_page, dict) else None
            if actual_weights != expected_weights:
                errors.append(
                    f"column role weight drift: expected {expected_weights!r}, got {actual_weights!r}"
                )

    required_roles = set(fixture.get("required_story_roles", []))
    actual_roles: set[str] = set()
    if isinstance(pages, list):
        for page in pages:
            if not isinstance(page, dict):
                continue
            for container in page.get("containers", []):
                if isinstance(container, dict) and isinstance(container.get("story_role"), str):
                    actual_roles.add(container["story_role"])
    missing = required_roles - actual_roles
    if missing:
        errors.append(f"missing required semantic roles: {sorted(missing)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--layout-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    fixture_path = Path(args.fixture).expanduser().resolve()
    layout_path = Path(args.layout_plan).expanduser().resolve()
    run_dir = Path(args.run_dir).expanduser().resolve()
    skill_dir = Path(__file__).resolve().parents[1]
    try:
        errors: list[str] = []
        if inside(fixture_path, skill_dir) or inside(fixture_path, run_dir):
            errors.append("regression fixture must be physically outside both the skill directory and RUN_DIR")
        fixture = read_json(fixture_path)
        plan = read_json(layout_path)
        errors.extend(validate(fixture, plan))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    print("PASS: page count, grammar, focus, metric treatment, flow evidence, and story roles match fixture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
