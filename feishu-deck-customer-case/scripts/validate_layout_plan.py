#!/usr/bin/env python3
"""Validate adaptive customer-case geometry and readability constraints."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from case_contracts import (
    ContractConfigError,
    resolve_tokens,
    validate_recipe_selection,
)

BASE_TOKENS = resolve_tokens("case-standard-v2", [])
ROLE_RANGES = {
    role: (limits["min"], limits["max"])
    for role, limits in BASE_TOKENS["regions_pct"].items()
}
REQUIRED_ROLES = {"title", "main", "bottom-safe"}
BACKGROUND_STRATEGIES = {"region-frame", "card-group", "open-band"}
PAGE_COUNT_REASONS = {
    "default-one-page",
    "user-requested-two-page",
    "approved-evidence-split",
    "approved-parallel-stories",
}
METRIC_TREATMENTS = {
    "none",
    "title",
    "subtitle",
    "title-or-inline",
    "inline-metrics",
    "gradient-cards",
    "context-strip",
}
METRIC_CARD_RECIPES = {"blue-result-cards-v1"}
CAPTION_PATTERNS = {"in-image", "above-image"}
EVIDENCE_COMPOSITION_RECIPES = {
    "single-dominant",
    "paired-comparison",
    "dominant-plus-supporting",
    "process-sequence",
    "parallel-matrix",
}
PAIN_DETAIL_RECIPES = {"stacked-cards", "concise-list", "none"}
EVIDENCE_PRIORITIES = {"dominant", "supporting", "optional", "text-only"}
NARRATIVE_ELEMENT_TYPES = {"evidence", "process", "metric"}
CASE_GRAMMARS = {
    "classic-case-card",
    "adaptive-evidence",
    "process-first-exception",
    "other",
}
FLOW_PLACEMENTS = {"inside-mechanism", "absent", "top-level-exception"}
MECHANISM_ROLES = {"mechanism", "solution", "after"}
BUSINESS_TASKS = {"pain", "mechanism", "result"}
METRIC_ROLES_V5 = {
    "measured-effect",
    "business-value",
    "efficiency-value",
    "scale",
    "operating-cadence",
    "baseline",
}
UNIT_SEMANTICS = {"percentage", "percentage-point", "currency", "time", "count", "other"}
EVIDENCE_STATUSES = {"measured", "estimated", "contextual"}
METRIC_PLACEMENTS = {
    "top-result-band",
    "title",
    "subtitle",
    "pain-detail",
    "mechanism-detail",
    "result-detail",
    "inline",
}
CLASSIC_ROLE_GROUPS = {
    "pain": {"pain", "before", "problem"},
    "mechanism": MECHANISM_ROLES,
    "result": {"result", "validation", "value"},
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def overlaps(a: dict, b: dict) -> bool:
    return not (
        a["x_pct"] + a["width_pct"] <= b["x_pct"]
        or b["x_pct"] + b["width_pct"] <= a["x_pct"]
        or a["y_pct"] + a["height_pct"] <= b["y_pct"]
        or b["y_pct"] + b["height_pct"] <= a["y_pct"]
    )


def validate_tokens(plan: dict, errors: list[str]) -> dict | None:
    if "tokens" in plan:
        errors.append("layout plan version 8 must reference token_profile instead of copying tokens")
    try:
        return resolve_tokens(plan.get("token_profile"), plan.get("approved_overrides"))
    except ContractConfigError as exc:
        errors.append(str(exc))
        return None


def validate_page_count(plan: dict, pages: list, errors: list[str]) -> None:
    reason = plan.get("page_count_reason")
    if reason not in PAGE_COUNT_REASONS:
        errors.append(f"page_count_reason must be one of {sorted(PAGE_COUNT_REASONS)}")
    if len(pages) == 2 and reason == "default-one-page":
        errors.append("two-page plan cannot use default-one-page reason")
    if reason == "user-requested-two-page" and len(pages) != 2:
        errors.append("user-requested-two-page requires exactly two pages")


def validate_regions(page: dict, prefix: str, errors: list[str]) -> dict[str, dict]:
    regions = page.get("regions")
    if not isinstance(regions, list):
        errors.append(f"{prefix}: regions must be an array")
        return {}
    by_id: dict[str, dict] = {}
    by_role: dict[str, dict] = {}
    for region in regions:
        if not isinstance(region, dict):
            errors.append(f"{prefix}: each region must be an object")
            continue
        region_id = region.get("id")
        role = region.get("role")
        if not isinstance(region_id, str) or not region_id:
            errors.append(f"{prefix}: region id is required")
            continue
        if region_id in by_id:
            errors.append(f"{prefix}: duplicate region id {region_id!r}")
        by_id[region_id] = region
        if role not in ROLE_RANGES:
            errors.append(f"{prefix}/{region_id}: invalid role {role!r}")
            continue
        if role in by_role:
            errors.append(f"{prefix}: duplicate role {role!r}")
        by_role[role] = region
        for field in ("y_pct", "height_pct"):
            if not isinstance(region.get(field), (int, float)):
                errors.append(f"{prefix}/{region_id}: {field} must be numeric")
        if region.get("background_strategy") not in BACKGROUND_STRATEGIES:
            errors.append(
                f"{prefix}/{region_id}: background_strategy must be one of {sorted(BACKGROUND_STRATEGIES)}"
            )

    for role in REQUIRED_ROLES:
        if role not in by_role:
            errors.append(f"{prefix}: missing required role {role!r}")
    for role, region in by_role.items():
        height = region.get("height_pct")
        limits = ROLE_RANGES[role]
        if isinstance(height, (int, float)) and not limits[0] <= height <= limits[1]:
            errors.append(
                f"{prefix}/{region['id']}: height {height}% is outside {limits[0]}%-{limits[1]}%"
            )

    numeric_regions = [
        region
        for region in regions
        if isinstance(region, dict)
        and isinstance(region.get("y_pct"), (int, float))
        and isinstance(region.get("height_pct"), (int, float))
    ]
    numeric_regions.sort(key=lambda item: item["y_pct"])
    cursor = 0.0
    for region in numeric_regions:
        start = float(region["y_pct"])
        end = start + float(region["height_pct"])
        if start < 0 or end > 100:
            errors.append(f"{prefix}/{region.get('id')}: region falls outside 0%-100%")
        if abs(start - cursor) > 0.01:
            relation = "gap" if start > cursor else "overlap"
            errors.append(
                f"{prefix}/{region.get('id')}: vertical {relation}; expected y={cursor:g}%, got {start:g}%"
            )
        cursor = max(cursor, end)
    if abs(cursor - 100.0) > 0.01:
        errors.append(f"{prefix}: top-level tracks close at {cursor:g}%, not 100%")
    return by_id


def validate_containers(
    page: dict,
    prefix: str,
    by_region_id: dict[str, dict],
    errors: list[str],
    warnings: list[str],
    narrative_type: str | None,
) -> None:
    containers = page.get("containers")
    if not isinstance(containers, list) or not containers:
        errors.append(f"{prefix}: containers must be a non-empty array")
        return
    framed_by_region: dict[str, list[dict]] = {}
    dominant: list[dict] = []
    for container in containers:
        if not isinstance(container, dict):
            errors.append(f"{prefix}: each container must be an object")
            continue
        container_id = container.get("id", "unnamed")
        owner = container.get("owner_region")
        region = by_region_id.get(owner)
        if region is None:
            errors.append(f"{prefix}/{container_id}: unknown owner_region {owner!r}")
            continue
        if not isinstance(container.get("story_role"), str) or not container["story_role"].strip():
            errors.append(f"{prefix}/{container_id}: story_role is required")
        priority = container.get("evidence_priority")
        if priority not in EVIDENCE_PRIORITIES:
            errors.append(f"{prefix}/{container_id}: invalid evidence_priority {priority!r}")
        if priority == "dominant":
            dominant.append(container)
        if priority != "text-only":
            if not isinstance(container.get("evidence_id"), str) or not container["evidence_id"].strip():
                errors.append(f"{prefix}/{container_id}: evidence_id is required for visual evidence")
            ratio = container.get("source_aspect_ratio")
            if not isinstance(ratio, (int, float)) or ratio <= 0:
                errors.append(f"{prefix}/{container_id}: source_aspect_ratio must be positive")
        for field in ("x_pct", "y_pct", "width_pct", "height_pct"):
            if not isinstance(container.get(field), (int, float)):
                errors.append(f"{prefix}/{container_id}: {field} must be numeric")
        if not all(
            isinstance(container.get(field), (int, float))
            for field in ("x_pct", "y_pct", "width_pct", "height_pct")
        ):
            continue
        if (
            container["x_pct"] < 0
            or container["y_pct"] < 0
            or container["width_pct"] <= 0
            or container["height_pct"] <= 0
            or container["x_pct"] + container["width_pct"] > 100
            or container["y_pct"] + container["height_pct"] > 100
        ):
            errors.append(f"{prefix}/{container_id}: container exceeds its owner region")
        framed = container.get("background_frame")
        if not isinstance(framed, bool):
            errors.append(f"{prefix}/{container_id}: background_frame must be boolean")
        if framed:
            if region.get("background_strategy") != "card-group":
                errors.append(f"{prefix}/{container_id}: module frame requires owner strategy card-group")
            framed_by_region.setdefault(owner, []).append(container)

        ratio = container.get("source_aspect_ratio")
        width = container.get("width_pct")
        if isinstance(ratio, (int, float)) and isinstance(width, (int, float)):
            readability = BASE_TOKENS["readability"]
            if priority == "dominant" and narrative_type == "evidence" and width < readability["dominant_evidence_min_width_pct"]:
                errors.append(
                    f"{prefix}/{container_id}: evidence-first dominant visual receives only {width}% width"
                )
            if ratio >= readability["wide_evidence_ratio_min"] and width < readability["wide_evidence_min_width_pct"]:
                errors.append(f"{prefix}/{container_id}: wide evidence is unreadable at {width}% width")
            if ratio <= readability["tall_evidence_ratio_max"] and width > readability["tall_evidence_max_width_pct"]:
                warnings.append(f"{prefix}/{container_id}: tall evidence may waste horizontal space at {width}% width")

    if len(dominant) != 1:
        errors.append(f"{prefix}: exactly one container must have evidence_priority 'dominant'")
    for owner, framed in framed_by_region.items():
        for left_index, left in enumerate(framed):
            for right in framed[left_index + 1 :]:
                if overlaps(left, right):
                    errors.append(
                        f"{prefix}/{owner}: background frames {left.get('id')!r} and {right.get('id')!r} overlap"
                    )


def validate_case_grammar(plan: dict, pages: list, errors: list[str]) -> None:
    grammar = plan.get("case_grammar")
    if grammar not in CASE_GRAMMARS:
        errors.append(f"case_grammar must be one of {sorted(CASE_GRAMMARS)}")
        return
    recipe = plan.get("layout_recipe")

    flow_placement = plan.get("flow_placement")
    if flow_placement not in FLOW_PLACEMENTS:
        errors.append(f"flow_placement must be one of {sorted(FLOW_PLACEMENTS)}")
        return
    flow_container_id = plan.get("flow_container_id")
    exception = plan.get("process_first_exception")
    if not isinstance(exception, str):
        errors.append("process_first_exception must be a string")
        return

    errors.extend(
        validate_recipe_selection(
            grammar,
            recipe,
            plan.get("layout_mode"),
            flow_placement,
            exception,
        )
    )

    if grammar == "classic-case-card":
        if plan.get("layout_mode") != "classic-case-card":
            errors.append("classic-case-card grammar requires layout_mode 'classic-case-card'")
        if flow_placement != "inside-mechanism":
            errors.append("classic-case-card requires flow_placement 'inside-mechanism'")
        if exception.strip():
            errors.append("classic-case-card cannot carry a process_first_exception")
    elif grammar == "process-first-exception":
        if plan.get("layout_mode") != "process-first-exception":
            errors.append("process-first-exception grammar requires matching layout_mode")
        if flow_placement != "top-level-exception":
            errors.append("process-first-exception requires flow_placement 'top-level-exception'")
        if not exception.strip():
            errors.append("process-first-exception requires a non-empty process_first_exception")
    elif flow_placement == "top-level-exception":
        errors.append("top-level-exception flow requires process-first-exception grammar")

    for page_index, page in enumerate(pages, start=1):
        if not isinstance(page, dict):
            continue
        prefix = f"page {page_index}"
        containers = page.get("containers")
        if not isinstance(containers, list):
            continue
        by_id = {
            item.get("id"): item
            for item in containers
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        narrative = page.get("dominant_narrative_element")
        narrative_type = narrative.get("type") if isinstance(narrative, dict) else None
        if grammar == "classic-case-card":
            roles = {
                item.get("story_role")
                for item in containers
                if isinstance(item, dict) and isinstance(item.get("story_role"), str)
            }
            for role_name, accepted in CLASSIC_ROLE_GROUPS.items():
                if not roles.intersection(accepted):
                    errors.append(
                        f"{prefix}: classic-case-card requires a {role_name} story role"
                    )
            if narrative_type == "process":
                errors.append(
                    f"{prefix}: classic-case-card cannot promote process to the dominant narrative element"
                )
            flow_container = by_id.get(flow_container_id)
            if flow_container is None:
                errors.append(f"{prefix}: flow_container_id {flow_container_id!r} does not exist")
            elif flow_container.get("story_role") not in MECHANISM_ROLES:
                errors.append(
                    f"{prefix}: classic flow must live in a mechanism/solution region"
                )
        elif grammar == "process-first-exception" and narrative_type != "process":
            errors.append(
                f"{prefix}: process-first-exception requires process as dominant_narrative_element"
            )


def validate_metrics(page: dict, prefix: str, errors: list[str]) -> None:
    count = page.get("metric_count")
    metrics = page.get("metrics")
    if not isinstance(metrics, list):
        errors.append(f"{prefix}: metrics must be an array for layout plan version 8")
        return
    if len(metrics) > 6:
        errors.append(f"{prefix}: metrics may contain at most six entries including local baseline data")
    identifiers: set[str] = set()
    prominent: list[dict] = []
    prominent_roles: set[str] = set()
    display_texts: set[str] = set()
    for index, metric in enumerate(metrics):
        metric_prefix = f"{prefix}/metrics[{index}]"
        if not isinstance(metric, dict):
            errors.append(f"{metric_prefix}: must be an object")
            continue
        metric_id = metric.get("id")
        if not isinstance(metric_id, str) or not metric_id.strip():
            errors.append(f"{metric_prefix}: id is required")
        elif metric_id in identifiers:
            errors.append(f"{metric_prefix}: duplicate metric id {metric_id!r}")
        else:
            identifiers.add(metric_id)
        role = metric.get("metric_role")
        if role not in METRIC_ROLES_V5:
            errors.append(f"{metric_prefix}: metric_role must be one of {sorted(METRIC_ROLES_V5)}")
        unit = metric.get("unit_semantics")
        if unit not in UNIT_SEMANTICS:
            errors.append(f"{metric_prefix}: unit_semantics must be one of {sorted(UNIT_SEMANTICS)}")
        status = metric.get("evidence_status")
        if status not in EVIDENCE_STATUSES:
            errors.append(f"{metric_prefix}: evidence_status must be one of {sorted(EVIDENCE_STATUSES)}")
        placement = metric.get("placement")
        if placement not in METRIC_PLACEMENTS:
            errors.append(f"{metric_prefix}: placement must be one of {sorted(METRIC_PLACEMENTS)}")
        display_text = metric.get("display_text")
        if not isinstance(display_text, str) or not display_text.strip():
            errors.append(f"{metric_prefix}: display_text is required")
        else:
            normalized_display = display_text.strip()
            if normalized_display in display_texts:
                errors.append(f"{metric_prefix}: display_text duplicates another metric fact")
            display_texts.add(normalized_display)
            if unit == "percentage-point" and "百分点" not in normalized_display:
                errors.append(f"{metric_prefix}: percentage-point display_text must use '百分点'")
            if status == "estimated" and "预计" not in normalized_display and "测算" not in normalized_display:
                errors.append(f"{metric_prefix}: estimated display_text must state '预计' or '测算'")
        is_prominent = metric.get("prominent")
        if not isinstance(is_prominent, bool):
            errors.append(f"{metric_prefix}: prominent must be boolean")
            continue
        if role == "baseline" and (is_prominent or placement == "top-result-band"):
            errors.append(f"{metric_prefix}: baseline data cannot occupy a top L1 result metric")
        if is_prominent:
            prominent.append(metric)
            if isinstance(role, str):
                if role in prominent_roles:
                    errors.append(f"{metric_prefix}: prominent metric roles must be distinct")
                prominent_roles.add(role)
            if placement not in {"top-result-band", "title", "subtitle", "inline"}:
                errors.append(f"{metric_prefix}: prominent metrics require a headline, result band, or inline placement")
    if len(prominent) != count:
        errors.append(f"{prefix}: metric_count must equal the number of prominent metrics")


def validate_story_focus(
    plan: dict,
    page: dict,
    prefix: str,
    errors: list[str],
) -> None:
    focus = page.get("dominant_business_task")
    if focus not in BUSINESS_TASKS:
        errors.append(f"{prefix}: dominant_business_task must be one of {sorted(BUSINESS_TASKS)}")
        return
    weights = page.get("column_role_weights")
    flow_order = page.get("flow_evidence_order")
    if not isinstance(flow_order, list):
        errors.append(f"{prefix}: flow_evidence_order must be an array")
    elif len(set(flow_order)) != len(flow_order) or any(not isinstance(item, str) or not item.strip() for item in flow_order):
        errors.append(f"{prefix}: flow_evidence_order must contain unique, non-empty evidence IDs")
    elif len(flow_order) > 4:
        errors.append(f"{prefix}: flow_evidence_order may contain at most four key mechanism images")
    if plan.get("case_grammar") != "classic-case-card":
        return
    if not isinstance(weights, dict):
        errors.append(f"{prefix}: classic-case-card requires column_role_weights")
        return
    expected_roles = {"pain", "mechanism", "result"}
    if set(weights) != expected_roles:
        errors.append(f"{prefix}: column_role_weights must contain exactly {sorted(expected_roles)}")
        return
    if any(not isinstance(weights.get(role), (int, float)) for role in expected_roles):
        errors.append(f"{prefix}: column_role_weights must be numeric")
        return
    total_weight = sum(float(weights[role]) for role in expected_roles)
    if abs(total_weight - 100.0) > 0.01:
        errors.append(f"{prefix}: column_role_weights must sum to 100")
    containers = [item for item in page.get("containers", []) if isinstance(item, dict)]
    role_containers: dict[str, dict] = {}
    for semantic_role, accepted_roles in CLASSIC_ROLE_GROUPS.items():
        matched = [item for item in containers if item.get("story_role") in accepted_roles]
        if len(matched) == 1:
            role_containers[semantic_role] = matched[0]
    if len(role_containers) != 3:
        return
    actual_total = sum(float(role_containers[role].get("width_pct", 0)) for role in expected_roles)
    if actual_total <= 0:
        errors.append(f"{prefix}: classic-case-card column widths are invalid")
        return
    for role in expected_roles:
        actual_weight = float(role_containers[role]["width_pct"]) / actual_total * 100
        classic_tokens = BASE_TOKENS["horizontal_pct"]["classic_mechanism_led"]
        if abs(actual_weight - float(weights[role])) > classic_tokens["declared_to_geometry_tolerance"]:
            errors.append(
                f"{prefix}: {role} column geometry {actual_weight:.1f}% differs from column_role_weights {weights[role]}%"
            )
    narrative = page.get("dominant_narrative_element")
    narrative_id = narrative.get("container_id") if isinstance(narrative, dict) else None
    if focus == "mechanism":
        if any(
            not classic_tokens[role]["min"] <= float(weights[role]) <= classic_tokens[role]["max"]
            for role in expected_roles
        ):
            targets = "/".join(str(classic_tokens[role]["target"]) for role in ("pain", "mechanism", "result"))
            errors.append(f"{prefix}: mechanism-led classic case must use the registered pain/mechanism/result target {targets}")
        if not float(weights["mechanism"]) > max(float(weights["pain"]), float(weights["result"])):
            errors.append(f"{prefix}: mechanism-led classic case requires the mechanism column to be widest")
        if narrative_id != role_containers["mechanism"].get("id"):
            errors.append(f"{prefix}: mechanism-led classic case must place dominant narrative element in mechanism column")
        if not isinstance(flow_order, list) or not flow_order:
            errors.append(f"{prefix}: mechanism-led classic case requires at least one key flow evidence image")
    elif float(weights[focus]) < max(float(weights[role]) for role in expected_roles):
        errors.append(f"{prefix}: {focus}-led classic case must give its declared focus the widest semantic column")


def validate_pain_detail_treatment(page: dict, prefix: str, errors: list[str]) -> None:
    treatment = page.get("pain_detail_treatment")
    if not isinstance(treatment, dict):
        errors.append(f"{prefix}: pain_detail_treatment must be an object")
        return
    recipe = treatment.get("recipe")
    if recipe not in PAIN_DETAIL_RECIPES:
        errors.append(
            f"{prefix}: pain_detail_treatment.recipe must be one of {sorted(PAIN_DETAIL_RECIPES)}"
        )
        return
    count = treatment.get("point_count")
    if not isinstance(count, int) or isinstance(count, bool) or not 0 <= count <= 4:
        errors.append(f"{prefix}: pain_detail_treatment.point_count must be an integer from 0 to 4")
    elif recipe == "stacked-cards" and not 2 <= count <= 4:
        errors.append(f"{prefix}: stacked-cards pain treatment requires two to four independent points")
    elif recipe == "concise-list" and not 1 <= count <= 4:
        errors.append(f"{prefix}: concise-list pain treatment requires one to four points")
    elif recipe == "none" and count != 0:
        errors.append(f"{prefix}: none pain treatment requires point_count 0")
    if not isinstance(treatment.get("rationale"), str) or not treatment["rationale"].strip():
        errors.append(f"{prefix}: pain_detail_treatment.rationale is required")


def validate_evidence_composition_ref(page: dict, prefix: str, errors: list[str]) -> None:
    composition = page.get("evidence_composition")
    if composition != {"ref": "asset-plan"}:
        errors.append(f"{prefix}: evidence_composition must be the reference {{'ref': 'asset-plan'}}")


def validate_resolved_evidence_composition(page: dict, composition: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(composition, dict):
        errors.append(f"{prefix}: referenced asset-plan evidence_composition must be an object")
        return
    recipe = composition.get("recipe")
    if recipe not in EVIDENCE_COMPOSITION_RECIPES:
        errors.append(
            f"{prefix}: evidence_composition.recipe must be one of {sorted(EVIDENCE_COMPOSITION_RECIPES)}"
        )
        return
    visual_ids = composition.get("asset_ids_in_visual_order")
    if not isinstance(visual_ids, list) or not 1 <= len(visual_ids) <= 4:
        errors.append(f"{prefix}: evidence_composition.asset_ids_in_visual_order must contain one to four evidence IDs")
        return
    if len(set(visual_ids)) != len(visual_ids) or any(not isinstance(item, str) or not item.strip() for item in visual_ids):
        errors.append(f"{prefix}: evidence_composition.asset_ids_in_visual_order must contain unique, non-empty IDs")
    if recipe == "single-dominant" and len(visual_ids) != 1:
        errors.append(f"{prefix}: single-dominant evidence composition requires exactly one image")
    if recipe == "paired-comparison" and len(visual_ids) != 2:
        errors.append(f"{prefix}: paired-comparison evidence composition requires exactly two images")
    if recipe in {"dominant-plus-supporting", "process-sequence", "parallel-matrix"} and not 2 <= len(visual_ids) <= 4:
        errors.append(f"{prefix}: {recipe} evidence composition requires two to four images")
    if page.get("dominant_business_task") == "mechanism":
        flow_order = page.get("flow_evidence_order")
        if visual_ids != flow_order:
            errors.append(
                f"{prefix}: mechanism evidence composition visual order must exactly match flow_evidence_order"
            )
        mappings = composition.get("node_mapping")
        if not isinstance(mappings, list) or len(mappings) != len(visual_ids):
            errors.append(f"{prefix}: mechanism evidence composition must map every visual evidence image once")
        else:
            mapped_ids: set[str] = set()
            for index, mapping in enumerate(mappings):
                mapping_prefix = f"{prefix}/evidence_composition.node_mapping[{index}]"
                if not isinstance(mapping, dict):
                    errors.append(f"{mapping_prefix} must be an object")
                    continue
                asset_id = mapping.get("asset_id")
                if asset_id not in visual_ids or asset_id in mapped_ids:
                    errors.append(f"{mapping_prefix}.asset_id must be a unique item in visual order")
                else:
                    mapped_ids.add(asset_id)
                turn_ids = mapping.get("turn_ids")
                if not isinstance(turn_ids, list) or not turn_ids or any(
                    not isinstance(turn_id, str) or not turn_id.strip() for turn_id in turn_ids
                ):
                    errors.append(f"{mapping_prefix}.turn_ids must list one or more mechanism turns")
                if not isinstance(mapping.get("rationale"), str) or not mapping["rationale"].strip():
                    errors.append(f"{mapping_prefix}.rationale is required")
    elif composition.get("node_mapping") not in (None, []):
        errors.append(f"{prefix}: non-mechanism evidence composition must not declare mechanism node_mapping")


def validate_layout(plan: dict, version: int) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    canvas = plan.get("canvas")
    expected_canvas = BASE_TOKENS["canvas"]
    if not isinstance(canvas, dict) or canvas != expected_canvas:
        errors.append(f"canvas must be {expected_canvas['width']}x{expected_canvas['height']}")
    story_hash = plan.get("story_hash")
    if not isinstance(story_hash, str) or len(story_hash) != 64:
        errors.append("story_hash must be the approved 64-character SHA-256")
    pages = plan.get("pages")
    if not isinstance(pages, list) or not 1 <= len(pages) <= 2:
        return errors + ["pages must contain one or two page plans"], warnings
    validate_page_count(plan, pages, errors)
    if not isinstance(plan.get("layout_mode"), str) or not plan["layout_mode"].strip():
        errors.append("layout_mode is required")
    if not isinstance(plan.get("selection_reason"), str) or not plan["selection_reason"].strip():
        errors.append("selection_reason is required")
    resolved_tokens = validate_tokens(plan, errors)
    plan["_resolved_tokens"] = resolved_tokens
    validate_case_grammar(plan, pages, errors)

    for page_index, page in enumerate(pages, start=1):
        prefix = f"page {page_index}"
        if not isinstance(page, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        if not isinstance(page.get("page_role"), str) or not page["page_role"].strip():
            errors.append(f"{prefix}: page_role is required")
        narrative = page.get("dominant_narrative_element")
        narrative_type: str | None = None
        narrative_container_id: str | None = None
        if not isinstance(narrative, dict):
            errors.append(f"{prefix}: dominant_narrative_element must be an object")
        else:
            narrative_type = narrative.get("type")
            narrative_container_id = narrative.get("container_id")
            if narrative_type not in NARRATIVE_ELEMENT_TYPES:
                errors.append(
                    f"{prefix}: dominant_narrative_element.type must be one of "
                    f"{sorted(NARRATIVE_ELEMENT_TYPES)}"
                )
            if not isinstance(narrative_container_id, str) or not narrative_container_id.strip():
                errors.append(
                    f"{prefix}: dominant_narrative_element.container_id is required"
                )
        dominant_evidence_id = page.get("dominant_evidence_id")
        if not isinstance(dominant_evidence_id, str) or not dominant_evidence_id.strip():
            errors.append(f"{prefix}: dominant_evidence_id is required")
        title_length = page.get("title_cjk_equivalent_chars")
        title_limit = BASE_TOKENS["typography"]["title_max_cjk_chars"]
        if not isinstance(title_length, (int, float)) or isinstance(title_length, bool) or not 1 <= title_length <= title_limit:
            errors.append(f"{prefix}: title_cjk_equivalent_chars must be within 1-{title_limit}")
        treatment = page.get("metric_treatment")
        count = page.get("metric_count")
        if treatment not in METRIC_TREATMENTS:
            errors.append(f"{prefix}: metric_treatment must be one of {sorted(METRIC_TREATMENTS)}")
        if not isinstance(count, int) or isinstance(count, bool) or not 0 <= count <= 4:
            errors.append(f"{prefix}: metric_count must be an integer from 0 to 4")
        card_recipe = page.get("metric_card_recipe")
        if treatment == "gradient-cards":
            if card_recipe not in METRIC_CARD_RECIPES:
                errors.append(f"{prefix}: gradient-cards must use metric_card_recipe 'blue-result-cards-v1'")
        elif card_recipe not in (None, ""):
            errors.append(f"{prefix}: metric_card_recipe is only allowed with gradient-cards")
        validate_metrics(page, prefix, errors)
        if plan.get("case_grammar") == "classic-case-card" and count >= 3:
            if treatment != "gradient-cards":
                errors.append(
                    f"{prefix}: classic-case-card with 3-4 L1 metrics requires gradient-cards"
                )
        captions = page.get("caption_patterns")
        if not isinstance(captions, list) or not captions:
            errors.append(f"{prefix}: caption_patterns must contain at least one pattern")
        elif any(item not in CAPTION_PATTERNS for item in captions):
            errors.append(f"{prefix}: caption_patterns may only use {sorted(CAPTION_PATTERNS)}")
        if page.get("header_row_aligned") is not True:
            errors.append(f"{prefix}: header_row_aligned must be true")
        if page.get("summary_above_evidence") is not True:
            errors.append(f"{prefix}: summary_above_evidence must be true")
        by_region_id = validate_regions(page, prefix, errors)
        containers = page.get("containers")
        if isinstance(containers, list):
            by_container_id = {
                item.get("id"): item
                for item in containers
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
            narrative_container = by_container_id.get(narrative_container_id)
            if narrative_container_id and narrative_container is None:
                errors.append(
                    f"{prefix}: dominant narrative container "
                    f"{narrative_container_id!r} does not exist"
                )
            elif narrative_type == "evidence" and narrative_container is not None:
                if narrative_container.get("evidence_priority") != "dominant":
                    errors.append(
                        f"{prefix}: evidence-first narrative container must own the "
                        "dominant visual evidence"
                    )
            dominant_evidence_containers = [
                item
                for item in containers
                if isinstance(item, dict)
                and item.get("evidence_priority") == "dominant"
                and item.get("evidence_id") == dominant_evidence_id
            ]
            if len(dominant_evidence_containers) != 1:
                errors.append(
                    f"{prefix}: dominant_evidence_id must match the one container "
                    "with evidence_priority 'dominant'"
                )
        validate_containers(
            page,
            prefix,
            by_region_id,
            errors,
            warnings,
            narrative_type,
        )
        if version == 8:
            validate_story_focus(plan, page, prefix, errors)
            validate_pain_detail_treatment(page, prefix, errors)
            validate_evidence_composition_ref(page, prefix, errors)
    return errors, warnings


def validate(plan: dict) -> tuple[list[str], list[str]]:
    version = plan.get("version")
    if version == 8:
        return validate_layout(plan, version)
    return ["version must be 8"], []


def validate_asset_plan_alignment(plan: dict, run_dir: Path, errors: list[str]) -> None:
    asset_plan_path = run_dir / "output" / "asset-plan.json"
    if not asset_plan_path.is_file():
        errors.append(f"missing approved asset plan: {asset_plan_path}")
        return
    try:
        asset_plan = json.loads(asset_plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read approved asset plan: {exc}")
        return

    selected = [
        asset
        for asset in asset_plan.get("assets", [])
        if isinstance(asset, dict) and asset.get("selected") is True
    ]
    selected_by_id = {
        asset.get("id"): asset
        for asset in selected
        if isinstance(asset.get("id"), str)
    }
    if plan.get("version") == 8 and asset_plan.get("version") != 4:
        errors.append("layout plan version 8 requires asset plan version 4")
    selected_by_page = {
        page_number: {
            asset.get("id"): asset
            for asset in selected
            if asset.get("page") == page_number
            and isinstance(asset.get("id"), str)
        }
        for page_number in range(1, len(plan.get("pages", [])) + 1)
    }

    for page_number, page in enumerate(plan.get("pages", []), start=1):
        if not isinstance(page, dict):
            continue
        page_assets = selected_by_page.get(page_number, {})
        dominant_id = page.get("dominant_evidence_id")
        dominant_asset = page_assets.get(dominant_id)
        if dominant_asset is None:
            errors.append(
                f"page {page_number}: dominant_evidence_id {dominant_id!r} is not "
                "a selected asset assigned to this page"
            )
        elif dominant_asset.get("priority") != "dominant":
            errors.append(
                f"page {page_number}: dominant_evidence_id must reference the asset "
                "with priority 'dominant'"
            )

        for container in page.get("containers", []):
            if not isinstance(container, dict):
                continue
            if container.get("evidence_priority") == "text-only":
                continue
            evidence_id = container.get("evidence_id")
            if evidence_id not in page_assets:
                errors.append(
                    f"page {page_number}/{container.get('id', 'unnamed')}: evidence_id "
                    f"{evidence_id!r} is not a selected asset assigned to this page"
                )
        if plan.get("version") == 8:
            flow_order = page.get("flow_evidence_order", [])
            if not isinstance(flow_order, list):
                continue
            sequence_values: list[int] = []
            for evidence_id in flow_order:
                asset = selected_by_id.get(evidence_id)
                if asset is None or asset.get("page") != page_number:
                    errors.append(
                        f"page {page_number}: flow_evidence_order item {evidence_id!r} is not selected on this page"
                    )
                    continue
                sequence = asset.get("sequence")
                if not isinstance(sequence, int) or sequence < 1:
                    errors.append(
                        f"page {page_number}: flow evidence {evidence_id!r} needs a positive sequence in asset plan"
                    )
                    continue
                sequence_values.append(sequence)
            if sequence_values and sequence_values != sorted(sequence_values):
                errors.append(
                    f"page {page_number}: flow_evidence_order must follow the asset plan causal sequence"
                )
            if page.get("dominant_business_task") == "mechanism":
                layout_composition = page.get("evidence_composition")
                asset_composition = asset_plan.get("mechanism_evidence", {}).get("evidence_composition")
                if layout_composition != {"ref": "asset-plan"}:
                    errors.append(f"page {page_number}: layout evidence composition must reference asset-plan")
                validate_resolved_evidence_composition(page, asset_composition, f"page {page_number}", errors)


def validate_story_contract_alignment(plan: dict, run_dir: Path, errors: list[str]) -> None:
    contract_path = run_dir / "output" / "story-contract.json"
    if not contract_path.is_file():
        errors.append(f"missing structured story contract: {contract_path}")
        return
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read structured story contract: {exc}")
        return
    if plan.get("story_hash") != contract.get("story_hash"):
        errors.append("layout plan story_hash differs from story-contract.json")
    if plan.get("case_grammar") != contract.get("case_grammar"):
        errors.append("layout plan case_grammar differs from story-contract.json")
    if plan.get("layout_recipe") != contract.get("layout_recipe"):
        errors.append("layout plan layout_recipe differs from story-contract.json")
    if plan.get("token_profile") != contract.get("token_profile"):
        errors.append("layout plan token_profile differs from story-contract.json")
    if plan.get("approved_overrides") != contract.get("approved_overrides"):
        errors.append("layout plan approved_overrides differ from story-contract.json")
    pages = plan.get("pages", [])
    if plan.get("page_count_reason") == "user-requested-two-page" and contract.get("page_count") != 2:
        errors.append("layout plan page count differs from story-contract.json")
    if isinstance(pages, list) and contract.get("page_count") != len(pages):
        errors.append("layout plan page count differs from story-contract.json")
    ledger = {
        metric.get("id"): metric
        for metric in contract.get("metrics", [])
        if isinstance(metric, dict) and isinstance(metric.get("id"), str)
    }
    band = contract.get("metric_band", {})
    approved_top_ids = set(band.get("metric_ids", [])) if isinstance(band, dict) else set()
    for page_index, page in enumerate(pages, start=1):
        if not isinstance(page, dict):
            continue
        if page.get("dominant_business_task") != contract.get("dominant_business_task"):
            errors.append(f"page {page_index}: dominant_business_task differs from story-contract.json")
        metrics = page.get("metrics", [])
        if not isinstance(metrics, list):
            continue
        prominent_top_ids: set[str] = set()
        for metric in metrics:
            if not isinstance(metric, dict):
                continue
            metric_id = metric.get("id")
            approved = ledger.get(metric_id)
            if approved is None:
                errors.append(f"page {page_index}: metric {metric_id!r} was not approved in story-contract.json")
                continue
            for field in ("metric_role", "unit_semantics", "evidence_status"):
                if metric.get(field) != approved.get(field):
                    errors.append(f"page {page_index}: metric {metric_id!r} {field} differs from story contract")
            if metric.get("placement") == "top-result-band" and metric.get("prominent") is True:
                prominent_top_ids.add(metric_id)
        decision = band.get("decision") if isinstance(band, dict) else None
        if decision == "required":
            if page.get("metric_treatment") != "gradient-cards":
                errors.append(f"page {page_index}: required metric band must use gradient-cards")
            if prominent_top_ids != approved_top_ids:
                errors.append(f"page {page_index}: top result band differs from approved L1 metric set")
        elif prominent_top_ids:
            errors.append(f"page {page_index}: unapproved top result band metrics are present")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--report")
    args = parser.parse_args()
    plan_path = Path(args.plan).expanduser().resolve()
    run_dir = Path(args.run_dir).expanduser().resolve()
    plan: dict = {}
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        errors, warnings = validate(plan)
        validate_asset_plan_alignment(plan, run_dir, errors)
        validate_story_contract_alignment(plan, run_dir, errors)
    except (OSError, json.JSONDecodeError) as exc:
        errors, warnings = [f"cannot read plan: {exc}"], []
    report_path = (
        Path(args.report).expanduser().resolve()
        if args.report
        else run_dir / "output" / "layout-validation.json"
    )
    report = {
        "schema_version": 7,
        "pass": not errors,
        "plan_path": str(plan_path),
        "plan_sha256": sha256_file(plan_path) if plan_path.is_file() else None,
        "approved_overrides": plan.get("approved_overrides", []) if isinstance(plan, dict) else [],
        "errors": errors,
        "warnings": warnings,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    print(f"PASS: layout geometry, case grammar, and readability validated; report={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
