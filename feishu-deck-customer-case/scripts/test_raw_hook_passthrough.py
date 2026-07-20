#!/usr/bin/env python3
"""Prove that the base raw renderer preserves customer-case data hooks."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


HOOKS = (
    'data-case-page="page-1"',
    'data-case-top-grid="true"',
    'data-case-evidence="proof"',
    'data-case-evidence-sequence="1"',
    'data-case-proof-task="system-judgement"',
    'data-case-lightbox-trigger="true"',
)


def find_renderer() -> Path:
    candidates = []
    if os.environ.get("FEISHU_DECK_ROOT"):
        candidates.append(Path(os.environ["FEISHU_DECK_ROOT"]))
    candidates.extend(
        [
            Path.home() / ".codex" / "skills" / "Feishu Deck 0613",
            Path.home() / ".codex" / "skills" / "feishu-deck-h5",
            Path.home() / ".agents" / "skills" / "feishu-deck-h5",
        ]
    )
    for root in candidates:
        renderer = root / "deck-json" / "render-deck.py"
        if renderer.is_file():
            return renderer
    raise RuntimeError("installed base Deck renderer was not found")


def main() -> int:
    html = """<div data-case-page="page-1" data-case-top-grid="true">
      <header data-case-region="title" data-case-role="title"><h1 data-case-title>T</h1><p data-case-subtitle>S</p></header>
      <main data-case-region="main" data-case-role="main" data-case-column-row>
        <section data-case-block="mechanism"><p data-case-copy-role="body">Body content with enough words for rendering.</p>
          <figure data-case-evidence="proof" data-case-display-mode="contain" data-case-source-ratio="1.78" data-case-caption-mode="above-image" data-case-evidence-sequence="1" data-case-proof-task="system-judgement">
            <button data-case-lightbox-trigger="true">Open proof</button>
          </figure>
        </section>
      </main>
      <div data-case-flow data-case-flow-placement="inside-mechanism" data-case-flow-container="mechanism"></div>
      <div data-case-lightbox hidden></div>
    </div>"""
    deck = {
        "version": "1.0",
        "deck": {"title": "Hook pass-through", "deck_id": "dk-hookpassthrough", "language": "zh-only", "mode": "rewrite"},
        "slides": [{"key": "case", "layout": "raw", "screen_label": "01 Case", "data": {"html": html}}],
    }
    with tempfile.TemporaryDirectory(prefix="feishu-case-hook-") as temporary:
        root = Path(temporary)
        deck_path = root / "deck.json"
        output = root / "output-a"
        output_b = root / "output-b"
        deck_path.write_text(json.dumps(deck, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        hook_validator = Path(__file__).with_name("validate_deck_hooks.py")
        hook_result = subprocess.run(
            [sys.executable, str(hook_validator), "--deck", str(deck_path)],
            text=True,
            capture_output=True,
            check=False,
        )
        if hook_result.returncode:
            raise AssertionError(f"raw DeckJSON hook validation failed\nstdout: {hook_result.stdout}\nstderr: {hook_result.stderr}")
        result = subprocess.run(
            [sys.executable, str(find_renderer()), str(deck_path), str(output), "--skip-fit-check", "--skip-copy-assets", "--skip-validate-html", "--quick"],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise AssertionError(f"base raw render failed\nstdout: {result.stdout}\nstderr: {result.stderr}")
        rendered = (output / "index.html").read_text(encoding="utf-8")
        missing = [hook for hook in HOOKS if hook not in rendered]
        if missing:
            raise AssertionError(f"base raw renderer removed hooks: {missing}")
        result_b = subprocess.run(
            [sys.executable, str(find_renderer()), str(deck_path), str(output_b), "--skip-fit-check", "--skip-copy-assets", "--skip-validate-html", "--quick"],
            text=True,
            capture_output=True,
            check=False,
        )
        if result_b.returncode:
            raise AssertionError(f"second base raw render failed\nstdout: {result_b.stdout}\nstderr: {result_b.stderr}")
        if (output / "index.html").read_bytes() != (output_b / "index.html").read_bytes():
            raise AssertionError("the same deck.json produced different index.html bytes")
    print("PASS: deck.json raw case hooks survive into index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
