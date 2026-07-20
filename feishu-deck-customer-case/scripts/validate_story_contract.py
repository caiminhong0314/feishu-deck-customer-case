#!/usr/bin/env python3
"""Validate the approved structured story decisions used by later case stages."""

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

CASE_GRAMMARS = {
    "classic-case-card",
    "adaptive-evidence",
    "process-first-exception",
    "other",
}
DISPLAY_REQUIREMENTS = {"top-band", "headline", "inline", "detail", "omitted"}
METRIC_LEVELS = {"L1", "L2", "L3"}
METRIC_BAND_DECISIONS = {"required", "optional", "not-used"}
EVIDENCE_REQUIREMENTS = {"visual-if-available", "text-allowed"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("contract must contain a JSON object")
    return value


def text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(contract: dict, story_path: Path) -> list[str]:
    errors: list[str] = []
    if contract.get("version") != 2:
        errors.append("version must be 2")
    story_hash = contract.get("story_hash")
    actual_story_hash = sha256_file(story_path) if story_path.is_file() else None
    if not text(story_hash) or story_hash != actual_story_hash:
        errors.append("story_hash must match the exact STORY-REVIEW.md revision")
    page_count = contract.get("page_count")
    if page_count not in {1, 2}:
        errors.append("page_count must be 1 or 2")
    grammar = contract.get("case_grammar")
    if grammar not in CASE_GRAMMARS:
        errors.append(f"case_grammar must be one of {sorted(CASE_GRAMMARS)}")
    recipe = contract.get("layout_recipe")
    try:
        errors.extend(validate_recipe_selection(grammar, recipe))
        resolve_tokens(
            contract.get("token_profile"),
            contract.get("approved_overrides"),
        )
    except ContractConfigError as exc:
        errors.append(str(exc))
    if contract.get("dominant_business_task") not in {"pain", "mechanism", "result"}:
        errors.append("dominant_business_task must be pain, mechanism, or result")
    ledger = contract.get("metrics")
    if not isinstance(ledger, list):
        errors.append("metrics must be an array")
        ledger = []
    metric_by_id: dict[str, dict] = {}
    for index, metric in enumerate(ledger):
        if not isinstance(metric, dict) or not text(metric.get("id")):
            errors.append(f"metrics[{index}] needs id")
            continue
        metric_id = metric["id"]
        if metric_id in metric_by_id:
            errors.append(f"metrics repeats id {metric_id!r}")
        metric_by_id[metric_id] = metric
        if metric.get("level") not in METRIC_LEVELS:
            errors.append(f"metrics[{index}].level must be L1, L2, or L3")
        if metric.get("display_requirement") not in DISPLAY_REQUIREMENTS:
            errors.append(f"metrics[{index}].display_requirement is invalid")
        if metric.get("level") == "L1" and metric.get("display_requirement") == "omitted":
            errors.append(f"metrics[{index}] L1 cannot be omitted")
    band = contract.get("metric_band")
    if not isinstance(band, dict):
        errors.append("metric_band must be an object")
    else:
        decision = band.get("decision")
        ids = band.get("metric_ids")
        if decision not in METRIC_BAND_DECISIONS:
            errors.append("metric_band.decision is invalid")
        if not text(band.get("reason")):
            errors.append("metric_band.reason is required")
        if not isinstance(ids, list) or len(ids) != len(set(ids)):
            errors.append("metric_band.metric_ids must be a unique array")
            ids = []
        if decision == "required" and not 2 <= len(ids) <= 4:
            errors.append("required metric band must contain 2-4 L1 metrics")
        if decision != "required" and ids:
            errors.append("optional or not-used metric band must not pre-reserve top-band metrics")
        for metric_id in ids:
            metric = metric_by_id.get(metric_id)
            if not metric or metric.get("level") != "L1" or metric.get("display_requirement") != "top-band":
                errors.append(f"metric_band ID {metric_id!r} must be an L1 top-band metric")
    turns = contract.get("mechanism_turns")
    if not isinstance(turns, list):
        errors.append("mechanism_turns must be an array")
    elif contract.get("dominant_business_task") == "mechanism" and not 2 <= len(turns) <= 5:
        errors.append("mechanism-focused story needs 2-5 mechanism_turns")
    else:
        seen: set[str] = set()
        for index, turn in enumerate(turns):
            if not isinstance(turn, dict) or not text(turn.get("id")) or not text(turn.get("label")):
                errors.append(f"mechanism_turns[{index}] needs id and label")
                continue
            if turn["id"] in seen:
                errors.append(f"mechanism_turns repeats id {turn['id']!r}")
            seen.add(turn["id"])
            if turn.get("evidence_requirement") not in EVIDENCE_REQUIREMENTS:
                errors.append(f"mechanism_turns[{index}].evidence_requirement is invalid")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--story", required=True)
    parser.add_argument("--report")
    args = parser.parse_args()
    contract_path = Path(args.contract).expanduser().resolve()
    story_path = Path(args.story).expanduser().resolve()
    try:
        contract = read_json(contract_path)
        errors = validate(contract, story_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors = [f"cannot validate story contract: {exc}"]
    result = {
        "schema_version": 2,
        "pass": not errors,
        "contract_path": str(contract_path),
        "contract_sha256": sha256_file(contract_path) if contract_path.is_file() else None,
        "story_path": str(story_path),
        "story_sha256": sha256_file(story_path) if story_path.is_file() else None,
        "errors": errors,
    }
    report_path = Path(args.report).expanduser().resolve() if args.report else contract_path.parent / "story-contract-validation.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    print(f"PASS: structured story contract validated; report={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
