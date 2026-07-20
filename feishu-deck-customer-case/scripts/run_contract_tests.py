#!/usr/bin/env python3
"""Smoke-test the current customer-case contracts as one complete case run."""

from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STATE = ROOT / "case_state.py"
STORY = ROOT / "validate_story_contract.py"
ASSETS = ROOT / "validate_asset_plan.py"
LAYOUT = ROOT / "validate_layout_plan.py"
RENDERED = ROOT / "validate_rendered_layout.py"
DELIVERY = ROOT / "verify_delivery.py"
RUN = ROOT / "validate_case_run.py"
HOOK_TEST = ROOT / "test_raw_hook_passthrough.py"
PIPELINE = ROOT / "case_pipeline.py"
REGRESSION = ROOT / "validate_regression_contract.py"


def run(*arguments: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([sys.executable, *arguments], text=True, capture_output=True, check=False)
    if result.returncode != expect:
        raise AssertionError(
            f"expected exit {expect}, got {result.returncode}\n"
            f"command: {' '.join(arguments)}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return result


def write_gradient_png(path: Path, width: int = 640, height: int = 360) -> None:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            row.extend(((x * 255) // width, (y * 255) // height, ((x + y) * 255) // (width + height)))
        rows.append(bytes(row))
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(b"".join(rows), 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    skill_root = ROOT.parent
    token_registry = json.loads((skill_root / "assets" / "tokens" / "case-tokens.json").read_text(encoding="utf-8"))
    token_profile = token_registry["profiles"]["case-standard-v2"]
    expected_tokens = {
        "title": token_profile["typography"]["title_px"] == 48,
        "column-gap": token_profile["spacing"]["column_gap_px"] == 15,
        "gradient": token_profile["surfaces"]["result_gradient"]["start_hex"] == "#2F6BEE",
        "caption-alpha": token_profile["surfaces"]["caption_alpha"]["recommended"] == 0.85,
        "dominant-coverage": token_profile["readability"]["fit_coverage_min"]["dominant"] == 0.6,
    }
    if not all(expected_tokens.values()):
        raise AssertionError(f"case token contract drifted: {expected_tokens}")
    collector_source = (ROOT / "collect_rendered_layout.js").read_text(encoding="utf-8")
    for forbidden in ("hasWhite85Surface", "hasVisibleCardSurface", "caption_has_white_85_surface", "visible_card_surface"):
        if forbidden in collector_source:
            raise AssertionError(f"collector must not make style judgement: {forbidden}")
    for path in (
        skill_root / "assets" / "templates" / "story-contract.template.json",
        ROOT / "validate_case_run.py",
        ROOT / "validate_story_contract.py",
    ):
        if not path.is_file():
            raise AssertionError(f"missing required current contract artifact: {path}")
    for rules, required in (
        (skill_root / "references" / "run-state-and-artifacts.md", "validate_case_run.py"),
        (skill_root / "references" / "layout-archetypes.md", "classic-case-card-v1"),
        (skill_root / "references" / "qa-and-delivery.md", "data-case-evidence-composition"),
    ):
        if required not in rules.read_text(encoding="utf-8"):
            raise AssertionError(f"{rules.name} must mention {required}")

    with tempfile.TemporaryDirectory(prefix="feishu-case-contract-") as temporary:
        run_dir = Path(temporary)
        output = run_dir / "output"
        assets_dir = run_dir / "input" / "assets"
        output.mkdir(parents=True)
        assets_dir.mkdir(parents=True)
        (run_dir / "input" / "SOURCE-NOTES.md").write_text("# source\n", encoding="utf-8")
        story = output / "STORY-REVIEW.md"
        story.write_text("# Approved story\n\nA source-backed mechanism case.\n", encoding="utf-8")
        story_hash = hashlib.sha256(story.read_bytes()).hexdigest()
        contract = output / "story-contract.json"
        story_contract = {
            "version": 2,
            "story_hash": story_hash,
            "token_profile": "case-standard-v2",
            "approved_overrides": [],
            "page_count": 1,
            "case_grammar": "classic-case-card",
            "dominant_business_task": "mechanism",
            "layout_recipe": "classic-case-card-v1",
            "metric_band": {"decision": "required", "reason": "Four different L1 outcomes are source-backed.", "metric_ids": ["effect", "value", "efficiency", "cadence"]},
            "metrics": [
                {"id": "effect", "level": "L1", "metric_role": "measured-effect", "unit_semantics": "percentage-point", "evidence_status": "measured", "display_requirement": "top-band"},
                {"id": "value", "level": "L1", "metric_role": "business-value", "unit_semantics": "currency", "evidence_status": "estimated", "display_requirement": "top-band"},
                {"id": "efficiency", "level": "L1", "metric_role": "efficiency-value", "unit_semantics": "currency", "evidence_status": "estimated", "display_requirement": "top-band"},
                {"id": "cadence", "level": "L1", "metric_role": "operating-cadence", "unit_semantics": "count", "evidence_status": "measured", "display_requirement": "top-band"},
            ],
            "mechanism_turns": [
                {"id": "identify", "label": "Identify", "evidence_requirement": "text-allowed"},
                {"id": "feedback", "label": "Feedback", "evidence_requirement": "visual-if-available"},
                {"id": "verify", "label": "Verify", "evidence_requirement": "visual-if-available"},
            ],
        }
        write_json(contract, story_contract)
        run(str(STORY), "--contract", str(contract), "--story", str(story))
        unconfirmed_override = json.loads(json.dumps(story_contract))
        unconfirmed_override["approved_overrides"] = [{"token": "spacing.column_gap_px", "value": 18, "reason": "Source proof needs more separation.", "user_confirmation": "Confirmed in the story review.", "confirmed_in_story": False}]
        write_json(contract, unconfirmed_override)
        run(str(STORY), "--contract", str(contract), "--story", str(story), expect=2)
        missing_confirmation = json.loads(json.dumps(story_contract))
        missing_confirmation["approved_overrides"] = [{"token": "typography.title_px", "value": 44, "reason": "The confirmed reference uses a smaller title.", "user_confirmation": "", "confirmed_in_story": True}]
        write_json(contract, missing_confirmation)
        run(str(STORY), "--contract", str(contract), "--story", str(story), expect=2)
        write_json(contract, story_contract)
        run(str(STATE), "init", "--run-dir", str(run_dir), "--output-dir", str(output), "--source-url", "https://example.com/doc")
        run(str(STATE), "source", "--run-dir", str(run_dir), "--status", "fetched", "--revision", "r1")
        run(str(STATE), "story-draft", "--run-dir", str(run_dir), "--story-file", str(story))
        run(str(STATE), "story-approve", "--run-dir", str(run_dir), "--story-file", str(story), "--confirmed-by", "user", "--confirmation-text", "确认故事方向")

        evidence = assets_dir / "proof.png"
        write_gradient_png(evidence)
        asset_plan = output / "asset-plan.json"
        assets = {
            "version": 4,
            "story_hash": story_hash,
            "page_count": 1,
            "candidate_inventory_complete": True,
            "mechanism_evidence": {
                "mechanism_driven": True,
                "key_turns": story_contract["mechanism_turns"],
                "selected_asset_ids_in_reading_order": ["proof"],
                "evidence_composition": {
                    "recipe": "single-dominant",
                    "asset_ids_in_visual_order": ["proof"],
                    "node_mapping": [
                        {"asset_id": "proof", "turn_ids": ["verify"], "rationale": "The screenshot directly proves AI validation."},
                    ],
                    "rationale": "One readable screenshot proves the decisive system-judgement turn.",
                },
                "turn_coverage": [
                    {"turn_id": "identify", "coverage": "text", "asset_ids": [], "rationale": "No direct source screenshot."},
                    {"turn_id": "feedback", "coverage": "text", "asset_ids": [], "rationale": "The feedback screenshot is unreadable at presentation size."},
                    {"turn_id": "verify", "coverage": "evidence", "asset_ids": ["proof"], "rationale": "The proof shows AI validation."},
                ],
                "coverage_note": "Images cover only decisive turns; remaining turns stay as concise flow text.",
            },
            "assets": [
                {"id": "proof", "path": "input/assets/proof.png", "page": 1, "selected": True, "candidate_status": "selected", "availability": "downloaded", "source_ref": "source-image-1", "rejection_reason": "", "user_required": True, "proof_role": "after", "proof_task": "system-judgement", "process_stage": "Verify", "sequence": 1, "claim": "AI returns a traceable validation result", "priority": "dominant", "layout_context": "single-dominant", "display_mode": "contain", "crop_reason": "", "focal_region": "", "caption_mode": "in-image", "caption": "AI validates the returned store evidence."},
                {"id": "feedback-candidate", "selected": False, "candidate_status": "rejected", "availability": "downloaded", "source_ref": "source-image-2", "rejection_reason": "Unreadable at the required presentation size; concise flow text is clearer.", "process_stage": "Feedback"},
            ],
        }
        write_json(asset_plan, assets)
        run(str(ASSETS), "--plan", str(asset_plan), "--run-dir", str(run_dir))
        invalid_composition_assets = json.loads(json.dumps(assets))
        invalid_composition_assets["mechanism_evidence"].pop("evidence_composition")
        write_json(asset_plan, invalid_composition_assets)
        run(str(ASSETS), "--plan", str(asset_plan), "--run-dir", str(run_dir), expect=2)
        invalid_assets = json.loads(json.dumps(assets))
        invalid_assets["assets"][1]["rejection_reason"] = ""
        write_json(asset_plan, invalid_assets)
        run(str(ASSETS), "--plan", str(asset_plan), "--run-dir", str(run_dir), expect=2)
        write_json(asset_plan, assets)
        run(str(ASSETS), "--plan", str(asset_plan), "--run-dir", str(run_dir))
        run(str(STATE), "advance", "--run-dir", str(run_dir), "--to", "ASSET_PLANNED", "--artifact", str(asset_plan))

        layout_plan = output / "layout-plan.json"
        metrics = [
            {"id": "effect", "metric_role": "measured-effect", "unit_semantics": "percentage-point", "evidence_status": "measured", "display_text": "约+10个百分点", "placement": "top-result-band", "prominent": True},
            {"id": "value", "metric_role": "business-value", "unit_semantics": "currency", "evidence_status": "estimated", "display_text": "预计3000万+/年", "placement": "top-result-band", "prominent": True},
            {"id": "efficiency", "metric_role": "efficiency-value", "unit_semantics": "currency", "evidence_status": "estimated", "display_text": "测算594万/年", "placement": "top-result-band", "prominent": True},
            {"id": "cadence", "metric_role": "operating-cadence", "unit_semantics": "count", "evidence_status": "measured", "display_text": "3次/日", "placement": "top-result-band", "prominent": True},
        ]
        layout = {
            "version": 8, "canvas": {"width": 1920, "height": 1080}, "page_count_reason": "default-one-page", "story_hash": story_hash,
            "token_profile": "case-standard-v2", "approved_overrides": [],
            "layout_mode": "classic-case-card", "case_grammar": "classic-case-card", "layout_recipe": "classic-case-card-v1", "selection_reason": "The approved story has a meaningful past, mechanism, and verified result.",
            "flow_placement": "inside-mechanism", "flow_container_id": "mechanism", "process_first_exception": "",
            "pages": [{
                "id": "page-1", "page_role": "before-mechanism-result", "dominant_business_task": "mechanism", "dominant_narrative_element": {"type": "evidence", "container_id": "mechanism"}, "dominant_evidence_id": "proof", "title_cjk_equivalent_chars": 24,
                "metric_treatment": "gradient-cards", "metric_card_recipe": "blue-result-cards-v1", "metric_count": 4, "metrics": metrics, "flow_evidence_order": ["proof"], "evidence_composition": {"ref": "asset-plan"}, "pain_detail_treatment": {"recipe": "stacked-cards", "point_count": 3, "rationale": "Three independent manual obstacles need separate scanable cards."}, "column_role_weights": {"pain": 22, "mechanism": 48, "result": 30}, "caption_patterns": ["in-image"], "header_row_aligned": True, "summary_above_evidence": True,
                "regions": [
                    {"id": "title", "role": "title", "y_pct": 0, "height_pct": 18, "background_strategy": "open-band"},
                    {"id": "metrics", "role": "metrics-context", "y_pct": 18, "height_pct": 10, "background_strategy": "open-band"},
                    {"id": "main", "role": "main", "y_pct": 28, "height_pct": 66, "background_strategy": "card-group"},
                    {"id": "safe", "role": "bottom-safe", "y_pct": 94, "height_pct": 6, "background_strategy": "open-band"},
                ],
                "containers": [
                    {"id": "pain", "owner_region": "main", "story_role": "pain", "evidence_priority": "supporting", "evidence_id": "proof", "source_aspect_ratio": 1.2, "x_pct": 0, "y_pct": 0, "width_pct": 21.5, "height_pct": 100, "background_frame": True},
                    {"id": "mechanism", "owner_region": "main", "story_role": "mechanism", "evidence_priority": "dominant", "evidence_id": "proof", "source_aspect_ratio": 1.78, "x_pct": 22.35, "y_pct": 0, "width_pct": 47.3, "height_pct": 100, "background_frame": True},
                    {"id": "result", "owner_region": "main", "story_role": "result", "evidence_priority": "supporting", "evidence_id": "proof", "source_aspect_ratio": 1.42, "x_pct": 70.5, "y_pct": 0, "width_pct": 29.5, "height_pct": 100, "background_frame": True},
                ],
            }],
        }
        write_json(layout_plan, layout)
        run(str(LAYOUT), "--plan", str(layout_plan), "--run-dir", str(run_dir))
        warning_layout = json.loads(json.dumps(layout))
        warning_layout["pages"][0]["containers"][1]["source_aspect_ratio"] = 0.7
        write_json(layout_plan, warning_layout)
        run(str(LAYOUT), "--plan", str(layout_plan), "--run-dir", str(run_dir))
        warning_report = json.loads((output / "layout-validation.json").read_text(encoding="utf-8"))
        if warning_report.get("pass") is not True or not warning_report.get("warnings"):
            raise AssertionError("non-blocking layout warning must be recorded while pass remains true")
        override_contract = json.loads(json.dumps(story_contract))
        override_contract["approved_overrides"] = [{"token": "typography.title_px", "value": 44, "reason": "The confirmed source reference uses a smaller title.", "user_confirmation": "User confirmed the 44px reference treatment.", "confirmed_in_story": True}]
        write_json(contract, override_contract)
        run(str(STORY), "--contract", str(contract), "--story", str(story))
        override_layout = json.loads(json.dumps(layout))
        override_layout["approved_overrides"] = override_contract["approved_overrides"]
        write_json(layout_plan, override_layout)
        run(str(LAYOUT), "--plan", str(layout_plan), "--run-dir", str(run_dir))
        write_json(contract, story_contract)
        write_json(layout_plan, layout)
        run(str(LAYOUT), "--plan", str(layout_plan), "--run-dir", str(run_dir))
        invalid_layout = json.loads(json.dumps(layout))
        invalid_layout["pages"][0]["metric_treatment"] = "inline-metrics"
        write_json(layout_plan, invalid_layout)
        run(str(LAYOUT), "--plan", str(layout_plan), "--run-dir", str(run_dir), expect=2)
        invalid_layout = json.loads(json.dumps(layout))
        invalid_layout["pages"][0]["pain_detail_treatment"]["recipe"] = "none"
        write_json(layout_plan, invalid_layout)
        run(str(LAYOUT), "--plan", str(layout_plan), "--run-dir", str(run_dir), expect=2)
        write_json(layout_plan, layout)
        run(str(LAYOUT), "--plan", str(layout_plan), "--run-dir", str(run_dir))

        (output / "DESIGN-PLAN.md").write_text("# design\n", encoding="utf-8")
        write_json(output / "outline.json", {"pages": [{"id": "page-1"}]})
        state_data = json.loads((run_dir / "case-state.json").read_text(encoding="utf-8"))
        write_json(output / "deck.json", {"deck": {"title": "Case", "deck_id": state_data["deck_id"]}, "slides": [{"id": "page-1"}]})
        html = output / "index.html"
        html.write_text("<!doctype html><html><body><section class='slide-frame' data-slide-key='case-1'>" + "x" * 600 + "</section></body></html>", encoding="utf-8")
        rendered_layout = output / "rendered-layout.json"
        rendered = {
            "schema_version": 2,
            "pages": [{
                "id": "page-1", "canvas": {"width": 1920, "height": 1080}, "top_grid": True,
                "regions": [{"id": "title", "role": "title", "x": 0, "y": 0, "width": 1920, "height": 194.4}, {"id": "metrics", "role": "metrics-context", "x": 0, "y": 194.4, "width": 1920, "height": 108}, {"id": "main", "role": "main", "x": 0, "y": 302.4, "width": 1920, "height": 712.8}, {"id": "safe", "role": "bottom-safe", "x": 0, "y": 1015.2, "width": 1920, "height": 64.8}],
                "tokens": {"title_px": 48, "subtitle_px": 30, "title_subtitle_gap_px": 10, "column_gap_px": 15, "peer_title_baseline_delta_px": 0},
                "blocks": [{"id": "pain", "x": 0, "y": 302.4, "width": 412.8, "height": 712.8}, {"id": "mechanism", "x": 429.12, "y": 302.4, "width": 908.16, "height": 712.8}, {"id": "result", "x": 1353.6, "y": 302.4, "width": 566.4, "height": 712.8}],
                "copy": [{"role": "module-title", "font_px": 24}, {"role": "summary", "font_px": 22}, {"role": "body", "font_px": 18}, {"role": "flow-node", "font_px": 18}, {"role": "metric-value", "font_px": 38}, {"role": "metric-label", "font_px": 18}, {"role": "caption", "font_px": 18}],
                "metrics": [{"id": metric["id"], "placement": metric["placement"], "status": metric["evidence_status"], "background_image": "linear-gradient(104deg, rgb(47, 107, 238), rgb(22, 61, 156))"} for metric in metrics], "metric_band_recipe": "blue-result-cards-v1", "metric_band": {"gap_px": 15, "background_image": "none", "border_width_px": 0},
                "evidence": [{"id": "proof", "sequence": 1, "proof_task": "system-judgement", "display_mode": "contain", "rendered_fit": "contain", "overflow_x": "hidden", "overflow_y": "hidden", "declared_source_aspect_ratio": 1.7777777778, "intrinsic_width_px": 1440, "intrinsic_height_px": 810, "image_box_width_px": 720, "image_box_height_px": 405, "x": 500, "y": 420, "width": 720, "height": 405, "caption_mode": "in-image", "caption_background_color": "rgb(255 255 255 / 0.85)", "caption_background_image": "none"}],
                "evidence_composition": {"recipe": "single-dominant", "asset_ids_in_visual_order": ["proof"]},
                "pain_detail": {"recipe": "stacked-cards", "points": [{"index": 1, "x": 24, "y": 410, "width": 360, "height": 70, "background_color": "rgba(255,255,255,0.12)", "background_image": "none", "border_width_px": 1, "outline_width_px": 0, "box_shadow": "none"}, {"index": 2, "x": 24, "y": 494, "width": 360, "height": 70, "background_color": "rgba(255,255,255,0.12)", "background_image": "none", "border_width_px": 1, "outline_width_px": 0, "box_shadow": "none"}, {"index": 3, "x": 24, "y": 578, "width": 360, "height": 70, "background_color": "rgba(255,255,255,0.12)", "background_image": "none", "border_width_px": 1, "outline_width_px": 0, "box_shadow": "none"}]},
                "flow": {"placement": "inside-mechanism", "container_id": "mechanism"},
            }],
        }
        write_json(rendered_layout, rendered)
        rendered_validation = output / "rendered-layout-validation.json"
        run(str(RENDERED), "--layout-plan", str(layout_plan), "--html", str(html), "--report", str(rendered_layout), "--output", str(rendered_validation))
        drift = json.loads(json.dumps(rendered))
        drift["pages"][0]["metrics"][0]["status"] = "estimated"
        write_json(rendered_layout, drift)
        run(str(RENDERED), "--layout-plan", str(layout_plan), "--html", str(html), "--report", str(rendered_layout), "--output", str(rendered_validation), expect=2)
        drift = json.loads(json.dumps(rendered))
        drift["pages"][0]["pain_detail"]["points"][0]["background_color"] = "rgba(255,255,255,0)"
        drift["pages"][0]["evidence"][0]["caption_background_color"] = "rgb(255 255 255 / 0.5)"
        write_json(rendered_layout, drift)
        run(str(RENDERED), "--layout-plan", str(layout_plan), "--html", str(html), "--report", str(rendered_layout), "--output", str(rendered_validation), expect=2)
        write_json(rendered_layout, rendered)
        run(str(RENDERED), "--layout-plan", str(layout_plan), "--html", str(html), "--report", str(rendered_layout), "--output", str(rendered_validation))
        legal_outline = json.loads(json.dumps(rendered))
        legal_outline["pages"][0]["pain_detail"]["points"][0]["border_width_px"] = 0
        legal_outline["pages"][0]["pain_detail"]["points"][0]["outline_width_px"] = 1
        write_json(rendered_layout, legal_outline)
        run(str(RENDERED), "--layout-plan", str(layout_plan), "--html", str(html), "--report", str(rendered_layout), "--output", str(rendered_validation))
        ratio_drift = json.loads(json.dumps(rendered))
        ratio_drift["pages"][0]["evidence"][0]["declared_source_aspect_ratio"] = 1.2
        write_json(rendered_layout, ratio_drift)
        run(str(RENDERED), "--layout-plan", str(layout_plan), "--html", str(html), "--report", str(rendered_layout), "--output", str(rendered_validation), expect=2)
        write_json(rendered_layout, rendered)
        run(str(RENDERED), "--layout-plan", str(layout_plan), "--html", str(html), "--report", str(rendered_layout), "--output", str(rendered_validation))
        run(str(STATE), "advance", "--run-dir", str(run_dir), "--to", "RENDERED", "--artifact", str(html))

        screenshot = output / "qa.png"
        write_gradient_png(screenshot)
        interaction = output / "interaction-check.json"
        write_json(interaction, {"schema_version": 1, "target_html_sha256": hashlib.sha256(html.read_bytes()).hexdigest(), "pass": True, "checks": {"lightbox_opens_complete_image": True, "lightbox_closes_on_image_or_overlay_click": True, "layout_stable_after_close": True}, "scroll_viewports": []})
        qa_md = output / "QA-NOTES.md"
        qa_md.write_text("# QA Notes\n\nMachine result: `qa-notes.json`\n", encoding="utf-8")
        qa = output / "qa-notes.json"
        write_json(qa, {"schema_version": 1, "pass": True, "html": {"path": str(html.resolve()), "sha256": hashlib.sha256(html.read_bytes()).hexdigest()}, "base_validator": "pass", "unresolved_limitations": [], "screenshot_paths": [str(screenshot.resolve())], "interaction_report_path": str(interaction.resolve()), "rendered_layout_validation_path": str(rendered_validation.resolve()), "checks": {"page_count_and_keys": "pass", "source_story_asset_layout": "pass", "rendered_layout_alignment": "pass", "overlap_and_dead_space": "pass", "evidence_readability_and_captions": "pass", "browser_and_interaction": "pass"}, "notes": []})
        run(str(STATE), "advance", "--run-dir", str(run_dir), "--to", "VALIDATED", "--artifact", str(qa))
        manifest = output / "delivery-manifest.json"
        run(str(DELIVERY), "--html", str(html), "--mode", "linked", "--viewer", "local", "--screenshot", str(screenshot), "--interaction-report", str(interaction), "--manifest", str(manifest))
        run(str(RUN), "--run-dir", str(run_dir), "--output", str(output / "run-validation.json"))
        run(str(STATE), "advance", "--run-dir", str(run_dir), "--to", "DELIVERED", "--artifact", str(manifest))
        pipeline_status = run(str(PIPELINE), "status", "--run-dir", str(run_dir))
        if json.loads(pipeline_status.stdout)["stale_stages"]:
            raise AssertionError("fresh delivered run must not report stale artifacts")
        original_html = html.read_text(encoding="utf-8")
        html.write_text(original_html + "\n<!-- drift -->\n", encoding="utf-8")
        stale_status = json.loads(run(str(PIPELINE), "status", "--run-dir", str(run_dir)).stdout)
        if stale_status.get("first_breakpoint") != "RENDERED" or "requalify" not in stale_status.get("next_command", ""):
            raise AssertionError(f"pipeline did not identify rendered drift: {stale_status}")
        html.write_text(original_html, encoding="utf-8")

        fixture = {
            "version": 4,
            "expected_page_count": 1,
            "expected_layout_mode": "classic-case-card",
            "expected_case_grammar": "classic-case-card",
            "expected_flow_placement": "inside-mechanism",
            "expected_metric_treatment": "gradient-cards",
            "expected_dominant_business_task": "mechanism",
            "expected_metric_roles": ["measured-effect", "business-value", "efficiency-value", "operating-cadence"],
            "expected_flow_evidence_order": ["proof"],
            "expected_column_role_weights": {"pain": 22, "mechanism": 48, "result": 30},
            "required_story_roles": ["pain", "mechanism", "result"],
        }
        internal_fixture = run_dir / "hidden-fixture.json"
        write_json(internal_fixture, fixture)
        run(str(REGRESSION), "--fixture", str(internal_fixture), "--layout-plan", str(layout_plan), "--run-dir", str(run_dir), expect=2)
        with tempfile.TemporaryDirectory(prefix="feishu-case-fixtures-") as fixture_dir:
            external_fixture = Path(fixture_dir) / "case.json"
            write_json(external_fixture, fixture)
            run(str(REGRESSION), "--fixture", str(external_fixture), "--layout-plan", str(layout_plan), "--run-dir", str(run_dir))
        run(str(STATE), "source", "--run-dir", str(run_dir), "--status", "fetched", "--revision", "r2")
        blocked_gate = run(str(STATE), "gate", "--run-dir", str(run_dir), "--for-stage", "design", expect=2)
        if "FIX:" not in blocked_gate.stderr or "case_pipeline.py" not in blocked_gate.stderr:
            raise AssertionError("ContractError must include a pipeline status repair command")

        eval_run = run_dir / "技能实验室" / "data" / "runs" / "run-eval"
        eval_output = eval_run / "output"
        (eval_run / "input" / "assets").mkdir(parents=True)
        eval_output.mkdir(parents=True)
        eval_story = eval_output / "STORY-REVIEW.md"
        eval_story.write_text(story.read_text(encoding="utf-8"), encoding="utf-8")
        eval_contract = json.loads(json.dumps(story_contract))
        eval_contract["story_hash"] = hashlib.sha256(eval_story.read_bytes()).hexdigest()
        write_json(eval_output / "story-contract.json", eval_contract)
        run(str(STATE), "init", "--run-dir", str(eval_run), "--output-dir", str(eval_output), "--source-url", "https://example.com/eval")
        run(str(STATE), "source", "--run-dir", str(eval_run), "--status", "fetched", "--revision", "eval-r1")
        run(str(STATE), "story-draft", "--run-dir", str(eval_run), "--story-file", str(eval_story))
        run(str(STATE), "story-approve", "--run-dir", str(eval_run), "--story-file", str(eval_story), "--confirmed-by", "evaluation-harness", "--confirmation-text", "unattended evaluation run", "--evaluation-mode", "unattended", expect=2)
        write_json(eval_run / "evaluation-mode.json", {"schema_version": 1, "created_by": "feishu-case-evaluation-workbench", "mode": "unattended", "run_id": "eval", "created_at": "2026-07-20T00:00:00Z", "output_dir": str(eval_output.resolve())})
        run(str(STATE), "story-approve", "--run-dir", str(eval_run), "--story-file", str(eval_story), "--confirmed-by", "evaluation-harness", "--confirmation-text", "unattended evaluation run", "--evaluation-mode", "unattended")

    run(str(HOOK_TEST))

    print("PASS: current customer-case story, asset, layout, render, and delivery contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
