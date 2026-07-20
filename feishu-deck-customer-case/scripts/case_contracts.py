#!/usr/bin/env python3
"""Strict loaders for the machine-readable customer-case contracts."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
TOKEN_FILE = SKILL_DIR / "assets" / "tokens" / "case-tokens.json"
RECIPE_FILE = SKILL_DIR / "assets" / "contracts" / "layout-recipes.json"


class ContractConfigError(ValueError):
    """Raised when a packaged machine contract is missing or malformed."""


def _read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractConfigError(f"cannot load packaged contract {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractConfigError(f"packaged contract {path} must contain an object")
    return value


def load_token_registry() -> dict[str, Any]:
    registry = _read_object(TOKEN_FILE)
    if registry.get("schema_version") != 1 or not isinstance(registry.get("profiles"), dict):
        raise ContractConfigError("case-tokens.json must use schema_version 1 and define profiles")
    return registry


def load_token_profile(name: str) -> dict[str, Any]:
    registry = load_token_registry()
    profile = registry["profiles"].get(name)
    if not isinstance(profile, dict):
        raise ContractConfigError(f"unknown token_profile {name!r}")
    return copy.deepcopy(profile)


def _set_path(target: dict[str, Any], raw_path: str, value: Any) -> None:
    parts = raw_path.split(".")
    cursor: dict[str, Any] = target
    for part in parts[:-1]:
        child = cursor.get(part)
        if not isinstance(child, dict):
            raise ContractConfigError(f"override path does not resolve to a token: {raw_path}")
        cursor = child
    if parts[-1] not in cursor:
        raise ContractConfigError(f"override path does not resolve to a token: {raw_path}")
    cursor[parts[-1]] = value


def resolve_tokens(profile_name: str, overrides: object) -> dict[str, Any]:
    registry = load_token_registry()
    allowed = set(registry.get("overrideable_paths", []))
    profile = load_token_profile(profile_name)
    if not isinstance(overrides, list):
        raise ContractConfigError("approved_overrides must be an array")
    seen: set[str] = set()
    for index, override in enumerate(overrides):
        if not isinstance(override, dict):
            raise ContractConfigError(f"approved_overrides[{index}] must be an object")
        path = override.get("token")
        if path not in allowed:
            raise ContractConfigError(f"approved_overrides[{index}].token is not overrideable: {path!r}")
        if path in seen:
            raise ContractConfigError(f"approved_overrides repeats path {path!r}")
        seen.add(path)
        if override.get("confirmed_in_story") is not True:
            raise ContractConfigError(f"approved_overrides[{index}] is not confirmed in the story")
        reason = override.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ContractConfigError(f"approved_overrides[{index}].reason is required")
        confirmation = override.get("user_confirmation")
        if not isinstance(confirmation, str) or not confirmation.strip():
            raise ContractConfigError(f"approved_overrides[{index}].user_confirmation is required")
        if "value" not in override:
            raise ContractConfigError(f"approved_overrides[{index}].value is required")
        _set_path(profile, path, override["value"])
    return profile


def load_recipe_registry() -> dict[str, Any]:
    registry = _read_object(RECIPE_FILE)
    if registry.get("schema_version") != 1 or not isinstance(registry.get("recipes"), dict):
        raise ContractConfigError("layout-recipes.json must use schema_version 1 and define recipes")
    return registry["recipes"]


def validate_recipe_selection(
    grammar: object,
    recipe_id: object,
    layout_mode: object | None = None,
    flow_placement: object | None = None,
    exception_reason: object | None = None,
) -> list[str]:
    recipes = load_recipe_registry()
    recipe = recipes.get(recipe_id)
    if not isinstance(recipe, dict):
        return [f"unknown layout_recipe {recipe_id!r}"]
    errors: list[str] = []
    if recipe.get("case_grammar") != grammar:
        errors.append(f"layout_recipe {recipe_id!r} is not permitted for {grammar!r}")
    if layout_mode is not None and recipe.get("layout_mode") != layout_mode:
        errors.append(f"layout_recipe {recipe_id!r} requires layout_mode {recipe.get('layout_mode')!r}")
    if flow_placement is not None:
        allowed = recipe.get("flow_placement")
        allowed_values = allowed if isinstance(allowed, list) else [allowed]
        if flow_placement not in allowed_values:
            errors.append(f"layout_recipe {recipe_id!r} does not allow flow_placement {flow_placement!r}")
    if recipe.get("requires_exception_reason") is True:
        if not isinstance(exception_reason, str) or not exception_reason.strip():
            errors.append(f"layout_recipe {recipe_id!r} requires process_first_exception")
    elif isinstance(exception_reason, str) and exception_reason.strip():
        errors.append(f"layout_recipe {recipe_id!r} cannot carry process_first_exception")
    return errors


def token_runtime_values(tokens: dict[str, Any]) -> dict[str, float]:
    """Expose the scalar values consumed by DOM and layout validators."""
    return {
        "title_px": tokens["typography"]["title_px"],
        "title_max_cjk_chars": tokens["typography"]["title_max_cjk_chars"],
        "subtitle_px": tokens["typography"]["subtitle_px"],
        "title_subtitle_gap_px": tokens["spacing"]["title_subtitle_gap_px"],
        "column_gap_px": tokens["spacing"]["column_gap_px"],
        "image_radius_px": tokens["radii"]["image_px"]["recommended"],
        "panel_radius_px": tokens["radii"]["panel_px"]["recommended"],
        "caption_px": tokens["typography"]["caption_px"]["recommended"],
        "metric_value_px": tokens["typography"]["metric_value_px"]["recommended"],
    }
