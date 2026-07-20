#!/usr/bin/env python3
"""Run a real-browser fixture through the case collector and rendered validator."""

from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_png(path: Path, width: int = 640, height: int = 360) -> None:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            row.extend(((x * 255) // width, (y * 255) // height, 120))
        rows.append(bytes(row))
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(b"".join(rows), 9))
    data += chunk(b"IEND", b"")
    path.write_bytes(data)


def run(*arguments: str) -> None:
    result = subprocess.run([sys.executable, *arguments], text=True, capture_output=True, check=False)
    if result.returncode:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(arguments)}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="feishu-case-browser-") as temporary:
        output = Path(temporary)
        write_png(output / "proof.png")
        story_hash = "a" * 64
        layout = {
            "version": 8,
            "canvas": {"width": 1920, "height": 1080},
            "page_count_reason": "default-one-page",
            "story_hash": story_hash,
            "token_profile": "case-standard-v2",
            "approved_overrides": [],
            "layout_mode": "classic-case-card",
            "case_grammar": "classic-case-card",
            "layout_recipe": "classic-case-card-v1",
            "selection_reason": "Browser collector contract fixture.",
            "flow_placement": "inside-mechanism",
            "flow_container_id": "mechanism",
            "process_first_exception": "",
            "pages": [{
                "id": "page-1",
                "page_role": "before-mechanism-result",
                "dominant_business_task": "mechanism",
                "dominant_narrative_element": {"type": "evidence", "container_id": "mechanism"},
                "dominant_evidence_id": "proof",
                "title_cjk_equivalent_chars": 8,
                "metric_treatment": "gradient-cards",
                "metric_card_recipe": "blue-result-cards-v1",
                "metric_count": 2,
                "metrics": [
                    {"id": "effect", "metric_role": "measured-effect", "unit_semantics": "percentage", "evidence_status": "measured", "display_text": "80%", "placement": "top-result-band", "prominent": True},
                    {"id": "value", "metric_role": "business-value", "unit_semantics": "currency", "evidence_status": "estimated", "display_text": "预计100万", "placement": "top-result-band", "prominent": True},
                ],
                "flow_evidence_order": ["proof"],
                "evidence_composition": {"ref": "asset-plan"},
                "pain_detail_treatment": {"recipe": "stacked-cards", "point_count": 2, "rationale": "Two independent obstacles."},
                "column_role_weights": {"pain": 22, "mechanism": 48, "result": 30},
                "caption_patterns": ["in-image"],
                "header_row_aligned": True,
                "summary_above_evidence": True,
                "regions": [
                    {"id": "title", "role": "title", "y_pct": 0, "height_pct": 18, "background_strategy": "open-band"},
                    {"id": "metrics", "role": "metrics-context", "y_pct": 18, "height_pct": 10, "background_strategy": "open-band"},
                    {"id": "main", "role": "main", "y_pct": 28, "height_pct": 66, "background_strategy": "card-group"},
                    {"id": "safe", "role": "bottom-safe", "y_pct": 94, "height_pct": 6, "background_strategy": "open-band"},
                ],
                "containers": [
                    {"id": "pain", "owner_region": "main", "story_role": "pain", "evidence_priority": "supporting", "evidence_id": "proof", "source_aspect_ratio": 1.7777777778, "x_pct": 0, "y_pct": 0, "width_pct": 21.5, "height_pct": 100, "background_frame": True},
                    {"id": "mechanism", "owner_region": "main", "story_role": "mechanism", "evidence_priority": "dominant", "evidence_id": "proof", "source_aspect_ratio": 1.7777777778, "x_pct": 22.35, "y_pct": 0, "width_pct": 47.3, "height_pct": 100, "background_frame": True},
                    {"id": "result", "owner_region": "main", "story_role": "result", "evidence_priority": "supporting", "evidence_id": "proof", "source_aspect_ratio": 1.7777777778, "x_pct": 70.5, "y_pct": 0, "width_pct": 29.5, "height_pct": 100, "background_frame": True},
                ],
            }],
        }
        write_json(output / "layout-plan.json", layout)
        write_json(output / "asset-plan.json", {"mechanism_evidence": {"evidence_composition": {"recipe": "single-dominant", "asset_ids_in_visual_order": ["proof"], "node_mapping": [{"asset_id": "proof", "turn_ids": ["verify"], "rationale": "Proof."}]}}})
        html = """<!doctype html><html><head><meta charset="utf-8"><style>
          *{box-sizing:border-box}html,body{margin:0;background:#0b1220}body{font-family:Arial,sans-serif}.case{width:1920px;height:1080px;display:grid;grid-template-rows:18% 10% 66% 6%;color:white;background:#101a2e}.grid{display:contents}.title{padding:40px 72px}.title h1{font-size:48px;line-height:58px;margin:0}.title p{font-size:30px;line-height:38px;margin:10px 0 0}.metrics{display:grid;grid-template-columns:1fr 1fr;gap:15px;padding:10px 72px}.metric{background:linear-gradient(104deg,rgb(47 107 238),rgb(22 61 156));border:0;padding:14px}.metric b{font-size:38px}.metric span{font-size:18px}.main{display:grid;grid-template-columns:21.5fr 47.3fr 29.5fr;gap:15px;padding:0 72px}.block{border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.06);padding:18px;min-width:0}.block h2{font-size:24px;line-height:30px;margin:0 0 10px}.block p[data-case-copy-role="summary"]{font-size:22px}.block p[data-case-copy-role="body"]{font-size:18px}[data-case-copy-role="flow-node"]{font-size:18px}.point{height:70px;margin-top:14px;background:rgba(255,255,255,.12);border:0;outline:1px solid rgba(255,255,255,.35);padding:12px}.evidence{width:100%;height:405px;margin:16px 0 0}.evidence img{display:block;width:100%;height:100%;object-fit:contain}.caption{font-size:18px;line-height:24px;background:rgb(255 255 255 / .85);color:#163d9c;padding:8px 12px}.safe{padding:14px 72px}.lightbox{position:fixed;inset:0;background:rgba(0,0,0,.8);display:grid;place-items:center;z-index:5}.lightbox[hidden]{visibility:hidden;pointer-events:none}.lightbox img{max-width:85%;max-height:85%;object-fit:contain}.trigger{position:absolute;z-index:2}
        </style></head><body><section class="case" data-case-page="page-1"><div class="grid" data-case-top-grid="true">
          <header class="title" data-case-region="title" data-case-role="title"><h1 data-case-title>机制闭环案例</h1><p data-case-subtitle>真实证据验证</p></header>
          <section class="metrics" data-case-region="metrics" data-case-role="metrics-context" data-case-metric-band="blue-result-cards-v1"><div class="metric" data-case-metric-id="effect" data-case-metric-placement="top-result-band" data-case-metric-status="measured"><b data-case-copy-role="metric-value">80%</b><span data-case-copy-role="metric-label">覆盖</span></div><div class="metric" data-case-metric-id="value" data-case-metric-placement="top-result-band" data-case-metric-status="estimated"><b data-case-copy-role="metric-value">100万</b><span data-case-copy-role="metric-label">预计价值</span></div></section>
          <main class="main" data-case-region="main" data-case-role="main" data-case-column-row><article class="block" data-case-block="pain" data-case-pain-treatment="stacked-cards"><h2 data-case-peer-title data-case-copy-role="module-title">过去问题</h2><p data-case-copy-role="summary">两项障碍</p><div class="point" data-case-pain-point>人工</div><div class="point" data-case-pain-point>分散</div></article><article class="block" data-case-block="mechanism" data-case-evidence-composition="single-dominant" data-case-evidence-composition-assets="proof"><h2 data-case-peer-title data-case-copy-role="module-title">当前机制</h2><p data-case-copy-role="summary">系统闭环</p><div data-case-flow data-case-flow-placement="inside-mechanism" data-case-flow-container="mechanism"><span data-case-copy-role="flow-node">验证</span></div><figure class="evidence" data-case-evidence="proof" data-case-display-mode="contain" data-case-source-ratio="1.7777777778" data-case-caption-mode="in-image" data-case-evidence-sequence="1" data-case-proof-task="system-judgement"><button class="trigger" data-case-lightbox-trigger="true">+</button><img src="proof.png"></figure><figcaption class="caption" data-case-copy-role="caption">真实系统判断证据</figcaption></article><article class="block" data-case-block="result"><h2 data-case-peer-title data-case-copy-role="module-title">结果验证</h2><p data-case-copy-role="body">结果可追踪</p></article></main>
          <footer class="safe" data-case-region="safe" data-case-role="bottom-safe">verified</footer></div><div class="lightbox" data-case-lightbox hidden><img src="proof.png"></div></section><script>const overlay=document.querySelector('[data-case-lightbox]');document.querySelector('[data-case-lightbox-trigger]').onclick=()=>{overlay.hidden=false};overlay.onclick=()=>{overlay.hidden=true};</script></body></html>"""
        html_path = output / "index.html"
        html_path.write_text(html, encoding="utf-8")
        run(
            str(ROOT / "collect_case_qa.py"),
            "--html", str(html_path),
            "--layout-plan", str(output / "layout-plan.json"),
            "--rendered-report", str(output / "rendered-layout.json"),
            "--screenshot", str(output / "qa.png"),
            "--interaction-report", str(output / "interaction-check.json"),
        )
        run(
            str(ROOT / "validate_rendered_layout.py"),
            "--layout-plan", str(output / "layout-plan.json"),
            "--html", str(html_path),
            "--report", str(output / "rendered-layout.json"),
            "--output", str(output / "rendered-layout-validation.json"),
        )
    print("PASS: real-browser collector and rendered validator contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
