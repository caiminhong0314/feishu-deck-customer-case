#!/usr/bin/env python3
"""Validate the complete evidence inventory and selected evidence chain for a case run."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


PROOF_ROLES = {"before", "after", "value", "weak"}
PRIORITIES = {"dominant", "supporting", "optional"}
LAYOUT_CONTEXTS = {
    "single-dominant",
    "paired-comparison",
    "supporting-nonuniform",
    "dominant-plus-supporting",
    "process-sequence",
    "parallel-matrix",
}
EVIDENCE_COMPOSITION_RECIPES = {
    "single-dominant",
    "paired-comparison",
    "dominant-plus-supporting",
    "process-sequence",
    "parallel-matrix",
}
DISPLAY_MODES = {"contain", "scroll", "crop"}
CAPTION_MODES = {"in-image", "above-image"}
PROOF_TASKS = {
    "context",
    "trigger",
    "execution",
    "system-judgement",
    "result-feedback",
    "result-validation",
}
AVAILABILITY = {"downloaded", "inaccessible", "not-image"}


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read plan: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("plan must contain a JSON object")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_error(errors: list[str], index: int, message: str) -> None:
    errors.append(f"assets[{index}]: {message}")


def valid_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_selected_asset(asset: dict, index: int, run_dir: Path, page_count: int, errors: list[str]) -> None:
    page = asset.get("page")
    if not isinstance(page, int) or page < 1 or page > page_count:
        add_error(errors, index, f"page must be between 1 and {page_count}")
    if not isinstance(asset.get("user_required"), bool):
        add_error(errors, index, "user_required must be boolean")
    role = asset.get("proof_role")
    if role not in PROOF_ROLES:
        add_error(errors, index, f"proof_role must be one of {sorted(PROOF_ROLES)}")
    elif role == "weak":
        add_error(errors, index, "weak/decorative evidence cannot be selected")
    proof_task = asset.get("proof_task")
    if proof_task not in PROOF_TASKS:
        add_error(errors, index, f"proof_task must be one of {sorted(PROOF_TASKS)}")
    process_stage = asset.get("process_stage")
    sequence = asset.get("sequence")
    if process_stage in (None, ""):
        if sequence not in (None, ""):
            add_error(errors, index, "sequence must be null when process_stage is empty")
    else:
        if not valid_string(process_stage):
            add_error(errors, index, "process_stage must be a non-empty string or null")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            add_error(errors, index, "process_stage requires a positive integer sequence")
    if not valid_string(asset.get("claim")):
        add_error(errors, index, "claim must state the business conclusion this image proves")
    if asset.get("priority") not in PRIORITIES:
        add_error(errors, index, f"priority must be one of {sorted(PRIORITIES)}")
    context = asset.get("layout_context")
    if context not in LAYOUT_CONTEXTS:
        add_error(errors, index, f"layout_context must be one of {sorted(LAYOUT_CONTEXTS)}")
    mode = asset.get("display_mode")
    if mode not in DISPLAY_MODES:
        add_error(errors, index, f"display_mode must be one of {sorted(DISPLAY_MODES)}")
    elif mode == "crop":
        if not valid_string(asset.get("crop_reason")):
            add_error(errors, index, "crop requires crop_reason")
        if not valid_string(asset.get("focal_region")):
            add_error(errors, index, "crop requires focal_region")
    caption_mode = asset.get("caption_mode")
    if caption_mode not in CAPTION_MODES:
        add_error(errors, index, f"caption_mode must be one of {sorted(CAPTION_MODES)}")
    elif context in {
        "single-dominant",
        "paired-comparison",
        "supporting-nonuniform",
        "dominant-plus-supporting",
        "process-sequence",
    } and caption_mode != "in-image":
        add_error(errors, index, f"{context} evidence must use an in-image bottom caption")
    elif context == "parallel-matrix" and caption_mode != "above-image":
        add_error(errors, index, "parallel-matrix evidence must use an above-image light-blue caption")
    if not valid_string(asset.get("caption")):
        add_error(errors, index, "caption is required")
    raw_path = asset.get("path")
    if not valid_string(raw_path):
        add_error(errors, index, "selected evidence requires path")
    else:
        path = Path(str(raw_path)).expanduser()
        if not path.is_absolute():
            path = run_dir / path
        if not path.resolve().is_file():
            add_error(errors, index, f"file does not exist: {path.resolve()}")


def validate_mechanism(plan: dict, selected: list[dict], all_assets: list[dict], errors: list[str]) -> None:
    mechanism = plan.get("mechanism_evidence")
    if not isinstance(mechanism, dict):
        errors.append("mechanism_evidence must be an object")
        return
    driven = mechanism.get("mechanism_driven")
    if not isinstance(driven, bool):
        errors.append("mechanism_evidence.mechanism_driven must be boolean")
        return
    if not valid_string(mechanism.get("coverage_note")):
        errors.append("mechanism_evidence.coverage_note is required")
    ordered_ids = mechanism.get("selected_asset_ids_in_reading_order")
    if not driven:
        if ordered_ids not in (None, []):
            errors.append("non-mechanism story must not declare mechanism evidence order")
        return
    key_turns = mechanism.get("key_turns")
    if not isinstance(key_turns, list) or not 2 <= len(key_turns) <= 5:
        errors.append("mechanism_evidence.key_turns must list 2-5 causal turns")
        return
    turn_by_id: dict[str, dict] = {}
    for index, turn in enumerate(key_turns):
        if not isinstance(turn, dict) or not valid_string(turn.get("id")) or not valid_string(turn.get("label")):
            errors.append(f"mechanism_evidence.key_turns[{index}] needs id and label")
            continue
        turn_id = turn["id"]
        if turn_id in turn_by_id:
            errors.append(f"mechanism_evidence.key_turns repeats id {turn_id!r}")
        turn_by_id[turn_id] = turn
        if turn.get("evidence_requirement") not in {"visual-if-available", "text-allowed"}:
            errors.append(f"mechanism_evidence.key_turns[{index}].evidence_requirement is invalid")
    if not isinstance(ordered_ids, list) or not 1 <= len(ordered_ids) <= 4 or len(set(ordered_ids)) != len(ordered_ids):
        errors.append("mechanism_evidence.selected_asset_ids_in_reading_order must contain 1-4 unique selected assets")
    selected_by_id = {asset.get("id"): asset for asset in selected}
    listed = [selected_by_id.get(asset_id) for asset_id in ordered_ids or []]
    if any(asset is None for asset in listed):
        errors.append("mechanism_evidence order may reference only selected evidence assets")
    else:
        sequences = [asset.get("sequence") for asset in listed]
        if any(not isinstance(value, int) for value in sequences):
            errors.append("mechanism evidence order requires process_stage and sequence on every selected image")
        elif sequences != sorted(sequences):
            errors.append("mechanism evidence assets must be listed in increasing causal sequence")
    coverage = mechanism.get("turn_coverage")
    if not isinstance(coverage, list) or len(coverage) != len(turn_by_id):
        errors.append("mechanism_evidence.turn_coverage must cover every key turn exactly once")
        return
    coverage_by_turn: dict[str, dict] = {}
    for index, item in enumerate(coverage):
        if not isinstance(item, dict) or not valid_string(item.get("turn_id")):
            errors.append(f"mechanism_evidence.turn_coverage[{index}] needs turn_id")
            continue
        turn_id = item["turn_id"]
        if turn_id in coverage_by_turn or turn_id not in turn_by_id:
            errors.append(f"mechanism_evidence.turn_coverage has invalid or duplicate turn {turn_id!r}")
        coverage_by_turn[turn_id] = item
        mode = item.get("coverage")
        ids = item.get("asset_ids")
        if mode not in {"evidence", "text"} or not isinstance(ids, list):
            errors.append(f"mechanism_evidence.turn_coverage[{index}] needs coverage and asset_ids")
            continue
        if mode == "evidence":
            if not ids or any(asset_id not in selected_by_id for asset_id in ids):
                errors.append(f"mechanism_evidence.turn_coverage[{index}] evidence must reference selected images")
        else:
            if ids:
                errors.append(f"mechanism_evidence.turn_coverage[{index}] text coverage cannot reference images")
            if not valid_string(item.get("rationale")):
                errors.append(f"mechanism_evidence.turn_coverage[{index}] text coverage requires rationale")
    if set(coverage_by_turn) != set(turn_by_id):
        errors.append("mechanism_evidence.turn_coverage turn IDs do not match key_turns")

    composition = mechanism.get("evidence_composition")
    if not isinstance(composition, dict):
        errors.append("mechanism_evidence.evidence_composition must be an object")
    else:
        recipe = composition.get("recipe")
        if recipe not in EVIDENCE_COMPOSITION_RECIPES:
            errors.append(
                "mechanism_evidence.evidence_composition.recipe must be one of "
                f"{sorted(EVIDENCE_COMPOSITION_RECIPES)}"
            )
        visual_ids = composition.get("asset_ids_in_visual_order")
        if not isinstance(visual_ids, list) or visual_ids != ordered_ids:
            errors.append(
                "mechanism_evidence.evidence_composition.asset_ids_in_visual_order "
                "must exactly match selected_asset_ids_in_reading_order"
            )
        if recipe == "single-dominant" and isinstance(visual_ids, list) and len(visual_ids) != 1:
            errors.append("single-dominant evidence composition requires exactly one image")
        if recipe == "paired-comparison" and isinstance(visual_ids, list) and len(visual_ids) != 2:
            errors.append("paired-comparison evidence composition requires exactly two images")
        if recipe in {"dominant-plus-supporting", "process-sequence", "parallel-matrix"} and isinstance(visual_ids, list) and not 2 <= len(visual_ids) <= 4:
            errors.append(f"{recipe} evidence composition requires two to four images")
        mappings = composition.get("node_mapping")
        if not isinstance(mappings, list) or len(mappings) != len(ordered_ids or []):
            errors.append(
                "mechanism_evidence.evidence_composition.node_mapping must map every selected mechanism image exactly once"
            )
        else:
            seen_assets: set[str] = set()
            mapped_turns: set[str] = set()
            for index, mapping in enumerate(mappings):
                prefix = f"mechanism_evidence.evidence_composition.node_mapping[{index}]"
                if not isinstance(mapping, dict):
                    errors.append(f"{prefix} must be an object")
                    continue
                asset_id = mapping.get("asset_id")
                if not isinstance(asset_id, str) or asset_id not in selected_by_id or asset_id in seen_assets:
                    errors.append(f"{prefix}.asset_id must be a unique selected mechanism image")
                else:
                    seen_assets.add(asset_id)
                turn_ids = mapping.get("turn_ids")
                if not isinstance(turn_ids, list) or not turn_ids or any(
                    not isinstance(turn_id, str) or turn_id not in turn_by_id for turn_id in turn_ids
                ):
                    errors.append(f"{prefix}.turn_ids must list one or more approved mechanism turn IDs")
                else:
                    mapped_turns.update(turn_ids)
                if not valid_string(mapping.get("rationale")):
                    errors.append(f"{prefix}.rationale is required")
            evidence_turns = {
                turn_id
                for turn_id, item in coverage_by_turn.items()
                if isinstance(item, dict) and item.get("coverage") == "evidence"
            }
            if not evidence_turns.issubset(mapped_turns):
                errors.append(
                    "mechanism evidence composition must map every visually covered turn to its evidence image"
                )
        if not valid_string(composition.get("rationale")):
            errors.append("mechanism_evidence.evidence_composition.rationale is required")
    selected_stages = {str(asset.get("process_stage")) for asset in selected if valid_string(asset.get("process_stage"))}
    for turn_id, turn in turn_by_id.items():
        item = coverage_by_turn.get(turn_id)
        if not item:
            continue
        if str(turn.get("label")) in selected_stages and item.get("coverage") != "evidence":
            errors.append(f"mechanism turn {turn_id!r} has selected stage evidence but is declared text-only")
    rejected_stages = {
        str(asset.get("process_stage"))
        for asset in all_assets
        if asset.get("candidate_status") == "rejected" and valid_string(asset.get("process_stage"))
    }
    for turn_id, turn in turn_by_id.items():
        item = coverage_by_turn.get(turn_id)
        if item and item.get("coverage") == "text" and str(turn.get("label")) in rejected_stages and not valid_string(item.get("rationale")):
            errors.append(f"mechanism turn {turn_id!r} needs an explicit reason for not using its rejected visual evidence")


def validate_story_contract(plan: dict, run_dir: Path, errors: list[str]) -> None:
    path = run_dir / "output" / "story-contract.json"
    if not path.is_file():
        errors.append("missing output/story-contract.json")
        return
    try:
        contract = load_json(path)
    except ValueError as exc:
        errors.append(str(exc))
        return
    if contract.get("story_hash") != plan.get("story_hash"):
        errors.append("asset plan story_hash differs from story-contract.json")
    expected_turns = contract.get("mechanism_turns", [])
    actual_turns = plan.get("mechanism_evidence", {}).get("key_turns", [])
    if isinstance(expected_turns, list) and expected_turns:
        expected_ids = [turn.get("id") for turn in expected_turns if isinstance(turn, dict)]
        actual_ids = [turn.get("id") for turn in actual_turns if isinstance(turn, dict)]
        if expected_ids != actual_ids:
            errors.append("asset plan mechanism key turns must match story-contract.json in the approved order")


def validate(plan: dict, run_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if plan.get("version") != 4:
        errors.append("version must be 4")
    if plan.get("candidate_inventory_complete") is not True:
        errors.append("candidate_inventory_complete must be true")
    story_hash = plan.get("story_hash")
    if not isinstance(story_hash, str) or len(story_hash) != 64:
        errors.append("story_hash must be the approved 64-character SHA-256")
    page_count = plan.get("page_count")
    if not isinstance(page_count, int) or page_count not in {1, 2}:
        errors.append("page_count must be 1 or 2")
        page_count = 1
    assets = plan.get("assets")
    if not isinstance(assets, list) or not assets:
        return errors + ["assets must be a non-empty array"], warnings
    identifiers: set[str] = set()
    selected: list[dict] = []
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            add_error(errors, index, "must be an object")
            continue
        asset_id = asset.get("id")
        if not valid_string(asset_id):
            add_error(errors, index, "id is required")
        elif asset_id in identifiers:
            add_error(errors, index, f"duplicate id {asset_id!r}")
        else:
            identifiers.add(asset_id)
        selected_flag = asset.get("selected")
        if not isinstance(selected_flag, bool):
            add_error(errors, index, "selected must be boolean")
            continue
        expected_status = "selected" if selected_flag else "rejected"
        if asset.get("candidate_status") != expected_status:
            add_error(errors, index, f"candidate_status must be {expected_status!r}")
        if asset.get("availability") not in AVAILABILITY:
            add_error(errors, index, f"availability must be one of {sorted(AVAILABILITY)}")
        if not valid_string(asset.get("source_ref")):
            add_error(errors, index, "source_ref is required for every candidate")
        if selected_flag:
            if asset.get("availability") != "downloaded":
                add_error(errors, index, "selected evidence must be downloaded")
            if str(asset.get("rejection_reason", "")).strip():
                add_error(errors, index, "selected evidence must not have rejection_reason")
            selected.append(asset)
            validate_selected_asset(asset, index, run_dir, page_count, errors)
        elif not valid_string(asset.get("rejection_reason")):
            add_error(errors, index, "rejected candidate requires a business rejection_reason")
    if not selected:
        errors.append("at least one evidence asset must be selected")
    for page in range(1, page_count + 1):
        page_assets = [asset for asset in selected if asset.get("page") == page]
        dominant = [asset for asset in page_assets if asset.get("priority") == "dominant"]
        if len(dominant) != 1:
            errors.append(f"page {page} must have exactly one dominant visual evidence asset; found {len(dominant)}")
        if not page_assets:
            errors.append(f"page {page} has no selected evidence")
        matrix = [asset for asset in page_assets if asset.get("layout_context") == "parallel-matrix"]
        if len(matrix) == 1:
            errors.append(f"page {page} parallel-matrix context requires at least two peer images")
    roles = Counter(asset.get("proof_role") for asset in selected)
    if roles["before"] == 0:
        warnings.append("no selected Before evidence; confirm that the story can still prove change")
    if roles["after"] == 0:
        warnings.append("no selected After evidence; confirm that the solution is visible")
    validate_mechanism(plan, selected, assets, errors)
    validate_story_contract(plan, run_dir, errors)
    state_file = run_dir / "case-state.json"
    if state_file.is_file() and isinstance(story_hash, str):
        try:
            state = load_json(state_file)
            if state.get("story", {}).get("sha256") != story_hash:
                errors.append("story_hash does not match the approved story in case-state.json")
            if state.get("story", {}).get("status") != "approved":
                errors.append("case-state.json has no current approved story")
        except ValueError as exc:
            errors.append(f"cannot verify case-state.json: {exc}")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--report")
    args = parser.parse_args()
    plan_path = Path(args.plan).expanduser().resolve()
    run_dir = Path(args.run_dir).expanduser().resolve()
    try:
        plan = load_json(plan_path)
        errors, warnings = validate(plan, run_dir)
    except ValueError as exc:
        errors, warnings = [str(exc)], []
    report = {
        "schema_version": 1,
        "pass": not errors,
        "plan_path": str(plan_path),
        "plan_sha256": sha256_file(plan_path) if plan_path.is_file() else None,
        "errors": errors,
        "warnings": warnings,
    }
    report_path = Path(args.report).expanduser().resolve() if args.report else plan_path.parent / "asset-validation.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    print(f"PASS: {len(plan.get('assets', []))} candidate records validated; report={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
