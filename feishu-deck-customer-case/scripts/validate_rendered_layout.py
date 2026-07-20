#!/usr/bin/env python3
"""Validate browser-collected case geometry against the approved layout plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from functools import cmp_to_key
from pathlib import Path

from case_contracts import ContractConfigError, resolve_tokens, token_runtime_values


COLOR_PATTERN = re.compile(r"rgba?\(([^)]+)\)", re.IGNORECASE)


def _channel(raw: str) -> float:
    raw = raw.strip()
    if raw.endswith("%"):
        return float(raw[:-1]) * 2.55
    return float(raw)


def _alpha(raw: str) -> float:
    raw = raw.strip()
    if raw.endswith("%"):
        return float(raw[:-1]) / 100
    return float(raw)


def parse_css_colors(value: object) -> list[list[float]]:
    colors: list[list[float]] = []
    for match in COLOR_PATTERN.finditer(str(value or "")):
        body = match.group(1).replace(",", " ")
        if "/" in body:
            rgb_text, alpha_text = body.split("/", 1)
            rgb_parts = rgb_text.split()
            alpha_value = _alpha(alpha_text)
        else:
            parts = body.split()
            rgb_parts = parts[:3]
            alpha_value = _alpha(parts[3]) if len(parts) >= 4 else 1.0
        if len(rgb_parts) != 3:
            continue
        try:
            colors.append([*(_channel(part) for part in rgb_parts), alpha_value])
        except ValueError:
            continue
    return colors


def color_matches(actual: list[float], expected: list[float], channel_tolerance: float) -> bool:
    return (
        len(actual) == len(expected) == 4
        and all(abs(actual[index] - expected[index]) <= channel_tolerance for index in range(3))
        and abs(actual[3] - expected[3]) <= 0.01
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def rect(value: object) -> dict | None:
    if not isinstance(value, dict):
        return None
    fields = ("x", "y", "width", "height")
    if any(not isinstance(value.get(field), (int, float)) for field in fields):
        return None
    if value["width"] < 0 or value["height"] < 0:
        return None
    return value


def rects_overlap(left: dict, right: dict) -> bool:
    return not (
        left["x"] + left["width"] <= right["x"]
        or right["x"] + right["width"] <= left["x"]
        or left["y"] + left["height"] <= right["y"]
        or right["y"] + right["height"] <= left["y"]
    )


def allowed_overlap(left: dict, right: dict) -> bool:
    left_allowed = left.get("allow_overlap_with", [])
    right_allowed = right.get("allow_overlap_with", [])
    return (
        isinstance(left_allowed, list)
        and right.get("id") in left_allowed
        or isinstance(right_allowed, list)
        and left.get("id") in right_allowed
    )


def validate_copy_roles(page_id: str, rendered_page: dict, contract_tokens: dict, errors: list[str]) -> None:
    copy = rendered_page.get("copy")
    if not isinstance(copy, list):
        errors.append(f"{page_id}: rendered copy metadata is missing")
        return
    for index, item in enumerate(copy):
        if not isinstance(item, dict):
            errors.append(f"{page_id}: copy[{index}] is invalid")
            continue
        role = item.get("role")
        size = item.get("font_px")
        limits = contract_tokens["typography"]["copy_roles_px"].get(role)
        tolerance = contract_tokens["tolerance"]["pixels"]
        if not isinstance(limits, dict):
            errors.append(f"{page_id}: copy[{index}] has invalid role {role!r}")
        elif not isinstance(size, (int, float)) or not limits["min"] - tolerance <= size <= limits["max"] + tolerance:
            errors.append(f"{page_id}: copy role {role!r} must use {limits['min']}-{limits['max']}px, got {size!r}")


def validate_rendered_metrics(page_id: str, plan_page: dict, rendered_page: dict, errors: list[str]) -> None:
    contract_tokens = plan_page["_contract_tokens"]
    tolerance = contract_tokens["tolerance"]["pixels"]
    rendered = rendered_page.get("metrics")
    if not isinstance(rendered, list):
        errors.append(f"{page_id}: rendered metric metadata is missing")
        return
    if plan_page.get("metric_treatment") == "gradient-cards":
        if rendered_page.get("metric_band_recipe") != plan_page.get("metric_card_recipe"):
            errors.append(f"{page_id}: rendered metric band recipe differs from layout plan")
        band = rendered_page.get("metric_band")
        expected_gap = plan_page.get("_plan_tokens", {}).get("column_gap_px")
        if not isinstance(band, dict):
            errors.append(f"{page_id}: rendered blue metric band geometry is missing")
        else:
            gap = band.get("gap_px")
            border = band.get("border_width_px")
            if not isinstance(gap, (int, float)) or not isinstance(expected_gap, (int, float)) or abs(gap - expected_gap) > tolerance:
                errors.append(f"{page_id}: blue metric cards must use the standard column gap")
            if band.get("background_image") not in {"", "none"} or not isinstance(border, (int, float)) or border > tolerance:
                errors.append(f"{page_id}: blue metric band outer container must remain transparent and unframed")
    actual_by_id: dict[str, list[dict]] = {}
    for item in rendered:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            actual_by_id.setdefault(item["id"], []).append(item)
    for metric in plan_page.get("metrics", []):
        if not isinstance(metric, dict) or metric.get("prominent") is not True:
            continue
        metric_id = metric.get("id")
        actual = actual_by_id.get(metric_id, [])
        if len(actual) != 1:
            errors.append(f"{page_id}: prominent metric {metric_id!r} must appear exactly once in rendered metadata")
            continue
        item = actual[0]
        if item.get("placement") != metric.get("placement"):
            errors.append(f"{page_id}: metric {metric_id!r} rendered placement differs from plan")
        if item.get("status") != metric.get("evidence_status"):
            errors.append(f"{page_id}: metric {metric_id!r} rendered status differs from plan")
        if plan_page.get("metric_treatment") == "gradient-cards" and metric.get("placement") == "top-result-band":
            colors = parse_css_colors(item.get("background_image"))
            approved = contract_tokens["surfaces"]["result_gradient"]
            color_tolerance = contract_tokens["tolerance"]["color_channel"]
            if not any(color_matches(color, approved["start_rgba"], color_tolerance) for color in colors) or not any(color_matches(color, approved["end_rgba"], color_tolerance) for color in colors):
                errors.append(f"{page_id}: metric {metric_id!r} does not use the approved blue result-card gradient")
            if any(
                color_matches(color, forbidden, color_tolerance)
                for color in colors
                for forbidden in approved["forbidden_rgba"]
            ):
                errors.append(f"{page_id}: metric {metric_id!r} contains an unapproved violet result-card gradient")


def validate_rendered_pain_detail(page_id: str, plan_page: dict, rendered_page: dict, errors: list[str]) -> None:
    expected = plan_page.get("pain_detail_treatment")
    if not isinstance(expected, dict):
        return
    actual = rendered_page.get("pain_detail")
    if not isinstance(actual, dict):
        errors.append(f"{page_id}: rendered pain detail metadata is missing")
        return
    recipe = expected.get("recipe")
    if actual.get("recipe") != recipe:
        errors.append(f"{page_id}: rendered pain detail recipe differs from layout plan")
        return
    points = actual.get("points")
    if not isinstance(points, list):
        errors.append(f"{page_id}: rendered pain detail points are missing")
        return
    expected_count = expected.get("point_count")
    if recipe == "stacked-cards":
        if len(points) != expected_count:
            errors.append(f"{page_id}: stacked pain cards count differs from layout plan")
            return
        previous: dict | None = None
        for index, point in enumerate(points):
            point_rect = rect(point)
            if point_rect is None:
                errors.append(f"{page_id}: pain point {index + 1} needs a valid rectangle")
                continue
            background_colors = parse_css_colors(point.get("background_color"))
            minimum_alpha = plan_page["_contract_tokens"]["surfaces"]["pain_card_min_alpha"]
            border = point.get("border_width_px")
            minimum_border = plan_page["_contract_tokens"]["spacing"]["pain_card_min_border_px"]
            outline = point.get("outline_width_px")
            shadow = str(point.get("box_shadow", ""))
            visible_background = (
                str(point.get("background_image", "")) not in {"", "none"}
                or bool(background_colors and background_colors[0][3] > minimum_alpha)
            )
            visible_boundary = (
                isinstance(border, (int, float)) and border >= minimum_border
                or isinstance(outline, (int, float)) and outline >= minimum_border
                or shadow not in {"", "none"}
            )
            if (
                not visible_background
                or not visible_boundary
            ):
                errors.append(
                    f"{page_id}: pain point {index + 1} must render as a visible card, not a transparent outline list"
                )
            if previous is not None:
                if point_rect["y"] < previous["y"]:
                    errors.append(f"{page_id}: stacked pain cards must keep top-to-bottom reading order")
                minimum_gap = plan_page["_contract_tokens"]["spacing"]["pain_card_min_gap_px"]
                if rects_overlap(previous, point_rect) or point_rect["y"] - (previous["y"] + previous["height"]) < minimum_gap:
                    errors.append(f"{page_id}: stacked pain cards overlap or lack visible separation")
            previous = point_rect
    elif points:
        errors.append(f"{page_id}: {recipe} pain treatment must not expose stacked card points")


def validate_rendered_evidence_composition(
    page_id: str,
    plan_page: dict,
    rendered_page: dict,
    rendered_evidence: dict[str, dict],
    errors: list[str],
) -> None:
    expected = plan_page.get("_resolved_evidence_composition")
    if not isinstance(expected, dict):
        return
    actual = rendered_page.get("evidence_composition")
    if not isinstance(actual, dict):
        errors.append(f"{page_id}: rendered evidence composition metadata is missing")
        return
    if actual.get("recipe") != expected.get("recipe"):
        errors.append(f"{page_id}: rendered evidence composition recipe differs from layout plan")
    expected_ids = expected.get("asset_ids_in_visual_order")
    if actual.get("asset_ids_in_visual_order") != expected_ids:
        errors.append(f"{page_id}: rendered evidence composition visual order differs from layout plan")
        return
    if not isinstance(expected_ids, list):
        return
    visual_reading_order: list[int] = []
    for evidence_id in expected_ids:
        evidence = rendered_evidence.get(evidence_id)
        if evidence is None:
            errors.append(f"{page_id}: composition evidence {evidence_id!r} is missing from rendered DOM")
            continue
        reading_order = evidence.get("reading_order")
        if not isinstance(reading_order, int):
            errors.append(f"{page_id}/{evidence_id}: composition evidence needs a visual reading order")
        else:
            visual_reading_order.append(reading_order)
        caption_mode = evidence.get("caption_mode")
        if caption_mode not in plan_page.get("caption_patterns", []):
            errors.append(f"{page_id}/{evidence_id}: caption mode differs from approved layout pattern")
        if caption_mode == "in-image":
            colors = parse_css_colors(evidence.get("caption_background_color"))
            surface = colors[0] if colors else None
            caption_alpha = plan_page["_contract_tokens"]["surfaces"]["caption_alpha"]
            rgb_min = plan_page["_contract_tokens"]["surfaces"]["caption_rgb_min"]
            if (
                surface is None
                or min(surface[:3]) < rgb_min
                or not caption_alpha["min"] <= surface[3] <= caption_alpha["max"]
            ):
                errors.append(f"{page_id}/{evidence_id}: in-image caption needs the approved white 85% attached surface")
    if visual_reading_order and visual_reading_order != sorted(visual_reading_order):
        errors.append(f"{page_id}: evidence composition does not follow declared visual reading order")


def enrich_evidence_measurements(
    page_id: str,
    evidence: list[dict],
    contract_tokens: dict,
    errors: list[str],
    warnings: list[str],
) -> None:
    tolerance = contract_tokens["tolerance"]["reading_order_y_px"]
    band = contract_tokens["tolerance"]["reading_order_ambiguous_band_pct"] / 100
    for left_index, left in enumerate(evidence):
        for right in evidence[left_index + 1 :]:
            if not all(isinstance(item.get("y"), (int, float)) for item in (left, right)):
                continue
            delta = abs(left["y"] - right["y"])
            if tolerance * (1 - band) <= delta <= tolerance * (1 + band):
                warnings.append(
                    f"{page_id}: evidence reading order is ambiguous near the {tolerance}px row tolerance"
                )

    def compare(left: dict, right: dict) -> int:
        if not all(isinstance(item.get(field), (int, float)) for item in (left, right) for field in ("x", "y")):
            left_id = str(left.get("id", ""))
            right_id = str(right.get("id", ""))
            return -1 if left_id < right_id else 1 if left_id > right_id else 0
        if abs(left["y"] - right["y"]) > tolerance:
            return -1 if left["y"] < right["y"] else 1
        if left["x"] != right["x"]:
            return -1 if left["x"] < right["x"] else 1
        left_id = str(left.get("id", ""))
        right_id = str(right.get("id", ""))
        return -1 if left_id < right_id else 1 if left_id > right_id else 0

    for index, item in enumerate(sorted(evidence, key=cmp_to_key(compare)), start=1):
        item["reading_order"] = index

    ratio_tolerance = contract_tokens["tolerance"]["source_ratio_relative"]
    for item in evidence:
        natural_width = item.get("intrinsic_width_px")
        natural_height = item.get("intrinsic_height_px")
        declared_ratio = item.get("declared_source_aspect_ratio")
        box_width = item.get("image_box_width_px")
        box_height = item.get("image_box_height_px")
        frame_width = item.get("width")
        frame_height = item.get("height")
        values = (natural_width, natural_height, box_width, box_height, frame_width, frame_height)
        if any(not isinstance(value, (int, float)) or value <= 0 for value in values):
            errors.append(f"{page_id}/{item.get('id')}: image intrinsic and rendered geometry must be positive")
            continue
        actual_ratio = natural_width / natural_height
        item["actual_source_aspect_ratio"] = actual_ratio
        if (
            not isinstance(declared_ratio, (int, float))
            or declared_ratio <= 0
            or abs(declared_ratio - actual_ratio) / actual_ratio > ratio_tolerance
        ):
            errors.append(f"{page_id}/{item.get('id')}: declared source ratio differs from the actual image ratio")
        content_width = box_width
        content_height = box_height
        if item.get("rendered_fit") == "contain":
            box_ratio = box_width / box_height
            if actual_ratio >= box_ratio:
                content_height = box_width / actual_ratio
            else:
                content_width = box_height * actual_ratio
        item["rendered_content_width_px"] = content_width
        item["rendered_content_height_px"] = content_height
        item["fit_coverage"] = min(1.0, (content_width * content_height) / (frame_width * frame_height))
        item["scroll_enabled"] = (
            item.get("display_mode") == "scroll"
            or item.get("overflow_x") in {"auto", "scroll"}
            or item.get("overflow_y") in {"auto", "scroll"}
        )


def validate_page(plan_page: dict, rendered_page: dict, errors: list[str], warnings: list[str]) -> None:
    page_id = plan_page.get("id", "page")
    prefix = f"{page_id}"
    canvas = rendered_page.get("canvas")
    if not isinstance(canvas, dict):
        errors.append(f"{prefix}: rendered canvas is missing")
        return
    contract_tokens = plan_page["_contract_tokens"]
    tolerance_px = contract_tokens["tolerance"]["pixels"]
    tolerance_pct = contract_tokens["tolerance"]["geometry_pct"]
    plan_canvas = contract_tokens["canvas"]
    for field in ("width", "height"):
        if not isinstance(canvas.get(field), (int, float)) or abs(canvas[field] - plan_canvas[field]) > tolerance_px:
            errors.append(f"{prefix}: rendered canvas.{field} must be {plan_canvas[field]}")
    canvas_height = canvas.get("height")
    if not isinstance(canvas_height, (int, float)) or canvas_height <= 0:
        return
    if rendered_page.get("top_grid") is not True:
        errors.append(f"{prefix}: page must expose one data-case-top-grid=true root")
    validate_copy_roles(prefix, rendered_page, contract_tokens, errors)
    validate_rendered_metrics(prefix, plan_page, rendered_page, errors)

    rendered_regions = rendered_page.get("regions")
    if not isinstance(rendered_regions, list):
        errors.append(f"{prefix}: rendered regions must be an array")
        return
    rendered_by_id = {
        item.get("id"): item
        for item in rendered_regions
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for planned in plan_page.get("regions", []):
        if not isinstance(planned, dict):
            continue
        region_id = planned.get("id")
        actual = rendered_by_id.get(region_id)
        if actual is None:
            errors.append(f"{prefix}: missing rendered region {region_id!r}")
            continue
        if actual.get("role") != planned.get("role"):
            errors.append(f"{prefix}/{region_id}: rendered role differs from layout plan")
        actual_rect = rect(actual)
        if actual_rect is None:
            errors.append(f"{prefix}/{region_id}: rendered region rectangle is invalid")
            continue
        actual_y = actual_rect["y"] / canvas_height * 100
        actual_height = actual_rect["height"] / canvas_height * 100
        if abs(actual_y - planned.get("y_pct", -999)) > tolerance_pct:
            errors.append(
                f"{prefix}/{region_id}: rendered y={actual_y:.2f}% differs from plan {planned.get('y_pct')}%"
            )
        if abs(actual_height - planned.get("height_pct", -999)) > tolerance_pct:
            errors.append(
                f"{prefix}/{region_id}: rendered height={actual_height:.2f}% differs from plan {planned.get('height_pct')}%"
            )

    tokens = rendered_page.get("tokens")
    plan_tokens = plan_page.get("_plan_tokens", {})
    if not isinstance(tokens, dict):
        errors.append(f"{prefix}: rendered tokens are missing")
    else:
        for field in ("title_px", "subtitle_px", "title_subtitle_gap_px", "column_gap_px"):
            actual = tokens.get(field)
            expected = plan_tokens.get(field)
            if not isinstance(actual, (int, float)) or abs(actual - expected) > tolerance_px:
                errors.append(f"{prefix}: rendered {field}={actual!r} differs from plan {expected!r}")
        peer_delta = tokens.get("peer_title_baseline_delta_px")
        peer_limit = contract_tokens["tolerance"]["peer_title_baseline_px"]
        if not isinstance(peer_delta, (int, float)) or peer_delta > peer_limit:
            errors.append(f"{prefix}: peer title baseline delta must be at most {peer_limit}px")

    blocks = rendered_page.get("blocks", [])
    if not isinstance(blocks, list):
        errors.append(f"{prefix}: rendered blocks must be an array")
        blocks = []
    valid_blocks = [block for block in blocks if isinstance(block, dict) and rect(block) is not None]
    if len(valid_blocks) != len(blocks):
        errors.append(f"{prefix}: every rendered block needs a valid rectangle")
    for index, left in enumerate(valid_blocks):
        for right in valid_blocks[index + 1 :]:
            if rects_overlap(left, right) and not allowed_overlap(left, right):
                errors.append(
                    f"{prefix}: rendered blocks {left.get('id')!r} and {right.get('id')!r} overlap"
                )

    expected_evidence = {
        container.get("evidence_id"): container.get("evidence_priority")
        for container in plan_page.get("containers", [])
        if isinstance(container, dict) and container.get("evidence_priority") != "text-only"
    }
    evidence = rendered_page.get("evidence", [])
    if not isinstance(evidence, list):
        errors.append(f"{prefix}: rendered evidence must be an array")
        evidence = []
    rendered_evidence = {
        item.get("id"): item
        for item in evidence
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    enrich_evidence_measurements(prefix, list(rendered_evidence.values()), contract_tokens, errors, warnings)
    for evidence_id, priority in expected_evidence.items():
        actual = rendered_evidence.get(evidence_id)
        if actual is None:
            errors.append(f"{prefix}: missing rendered evidence {evidence_id!r}")
            continue
        mode = actual.get("display_mode")
        fit = str(actual.get("rendered_fit", ""))
        if mode not in {"contain", "scroll", "crop"}:
            errors.append(f"{prefix}/{evidence_id}: invalid rendered display mode")
        if mode != "crop" and "cover" in fit:
            errors.append(f"{prefix}/{evidence_id}: screenshot evidence cannot render with cover")
        if mode == "contain" and actual.get("scroll_enabled") is not True:
            coverage = actual.get("fit_coverage")
            minimum = contract_tokens["readability"]["fit_coverage_min"].get(priority)
            if not isinstance(minimum, (int, float)):
                errors.append(f"{prefix}/{evidence_id}: no readability token exists for priority {priority!r}")
            elif not isinstance(coverage, (int, float)) or coverage < minimum:
                errors.append(f"{prefix}/{evidence_id}: contain evidence wastes too much of its frame")
        minimum_width = contract_tokens["readability"]["evidence_min_rendered_content_width_px"]
        if not isinstance(actual.get("rendered_content_width_px"), (int, float)) or actual.get("rendered_content_width_px") < minimum_width:
            errors.append(f"{prefix}/{evidence_id}: computed evidence width is below the readability threshold")

    if plan_page.get("_layout_version") == 8:
        validate_rendered_pain_detail(prefix, plan_page, rendered_page, errors)
        validate_rendered_evidence_composition(prefix, plan_page, rendered_page, rendered_evidence, errors)

    if plan_page.get("_layout_version") == 8:
        expected_flow_order = plan_page.get("flow_evidence_order", [])
        if isinstance(expected_flow_order, list):
            reading_orders: list[int] = []
            for sequence, evidence_id in enumerate(expected_flow_order, start=1):
                actual = rendered_evidence.get(evidence_id)
                if actual is None:
                    errors.append(f"{prefix}: missing rendered flow evidence {evidence_id!r}")
                    continue
                if actual.get("sequence") != sequence:
                    errors.append(
                        f"{prefix}/{evidence_id}: data-case-evidence-sequence must be {sequence}"
                    )
                if not isinstance(actual.get("proof_task"), str) or not actual["proof_task"].strip():
                    errors.append(f"{prefix}/{evidence_id}: data-case-proof-task is required")
                reading_order = actual.get("reading_order")
                if not isinstance(reading_order, int):
                    errors.append(f"{prefix}/{evidence_id}: rendered evidence reading order is missing")
                else:
                    reading_orders.append(reading_order)
            if reading_orders and reading_orders != sorted(reading_orders):
                errors.append(f"{prefix}: mechanism evidence does not follow declared visual reading order")

        if plan_page.get("dominant_business_task") == "mechanism":
            rendered_blocks = {
                block.get("id"): block
                for block in valid_blocks
                if isinstance(block.get("id"), str)
            }
            mechanism = rendered_blocks.get("mechanism")
            pain = rendered_blocks.get("pain")
            result = rendered_blocks.get("result")
            if all(item is not None for item in (mechanism, pain, result)):
                if not mechanism["width"] > max(pain["width"], result["width"]):
                    errors.append(f"{prefix}: rendered mechanism-led classic case must keep mechanism block widest")

    flow = rendered_page.get("flow")
    expected_flow = plan_page.get("_flow", {})
    if not isinstance(flow, dict):
        errors.append(f"{prefix}: rendered flow metadata is missing")
    else:
        if flow.get("placement") != expected_flow.get("placement"):
            errors.append(f"{prefix}: rendered flow placement differs from layout plan")
        if flow.get("container_id") != expected_flow.get("container_id"):
            errors.append(f"{prefix}: rendered flow container differs from layout plan")


def validate(plan: dict, report: dict, asset_plan: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if report.get("schema_version") != 2:
        errors.append("rendered-layout report schema_version must be 2")
        return errors, warnings
    try:
        contract_tokens = resolve_tokens(plan.get("token_profile"), plan.get("approved_overrides"))
    except ContractConfigError as exc:
        return [str(exc)], warnings
    pages = plan.get("pages")
    rendered_pages = report.get("pages")
    if not isinstance(pages, list) or not isinstance(rendered_pages, list):
        return ["layout plan and rendered report must contain pages arrays"], warnings
    rendered_by_id = {
        page.get("id"): page
        for page in rendered_pages
        if isinstance(page, dict) and isinstance(page.get("id"), str)
    }
    resolved_composition = asset_plan.get("mechanism_evidence", {}).get("evidence_composition")
    if not isinstance(resolved_composition, dict):
        errors.append("asset-plan mechanism evidence composition is missing")
    for plan_page in pages:
        if not isinstance(plan_page, dict):
            continue
        actual = rendered_by_id.get(plan_page.get("id"))
        if actual is None:
            errors.append(f"missing rendered page {plan_page.get('id')!r}")
            continue
        merged = dict(plan_page)
        merged["_contract_tokens"] = contract_tokens
        merged["_plan_tokens"] = token_runtime_values(contract_tokens)
        merged["_layout_version"] = plan.get("version")
        merged["_flow"] = {
            "placement": plan.get("flow_placement"),
            "container_id": plan.get("flow_container_id"),
        }
        merged["_resolved_evidence_composition"] = resolved_composition
        validate_page(merged, actual, errors, warnings)
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layout-plan", required=True)
    parser.add_argument("--html", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    plan_path = Path(args.layout_plan).expanduser().resolve()
    html_path = Path(args.html).expanduser().resolve()
    report_path = Path(args.report).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    try:
        plan = read_json(plan_path)
        report = read_json(report_path)
        asset_plan = read_json(plan_path.parent / "asset-plan.json")
        errors, warnings = validate(plan, report, asset_plan)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors, warnings = [f"cannot validate rendered layout: {exc}"], []
    result = {
        "schema_version": 2,
        "pass": not errors,
        "layout_plan_path": str(plan_path),
        "layout_plan_sha256": sha256_file(plan_path) if plan_path.is_file() else None,
        "html_path": str(html_path),
        "html_sha256": sha256_file(html_path) if html_path.is_file() else None,
        "rendered_layout_path": str(report_path),
        "errors": errors,
        "warnings": warnings,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    print(f"PASS: rendered layout matches plan; report={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
