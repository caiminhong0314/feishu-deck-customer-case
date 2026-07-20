#!/usr/bin/env python3
"""Collect rendered case geometry, screenshot, and interaction checks in Chromium."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from case_contracts import resolve_tokens

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        return


def visible_lightbox(page):
    candidates = page.locator("[data-case-lightbox]")
    for index in range(candidates.count()):
        candidate = candidates.nth(index)
        if candidate.is_visible():
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", required=True)
    parser.add_argument("--layout-plan", required=True)
    parser.add_argument("--collector", default=str(Path(__file__).with_name("collect_rendered_layout.js")))
    parser.add_argument("--rendered-report", required=True)
    parser.add_argument("--screenshot", required=True)
    parser.add_argument("--interaction-report", required=True)
    parser.add_argument("--browser")
    args = parser.parse_args()

    html_path = Path(args.html).expanduser().resolve()
    layout_plan_path = Path(args.layout_plan).expanduser().resolve()
    collector_path = Path(args.collector).expanduser().resolve()
    rendered_path = Path(args.rendered_report).expanduser().resolve()
    screenshot_path = Path(args.screenshot).expanduser().resolve()
    interaction_path = Path(args.interaction_report).expanduser().resolve()
    if not html_path.is_file() or not collector_path.is_file():
        raise SystemExit("BLOCKED: final HTML or rendered-layout collector is missing")
    layout_plan = json.loads(layout_plan_path.read_text(encoding="utf-8"))
    tokens = resolve_tokens(layout_plan.get("token_profile"), layout_plan.get("approved_overrides"))

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("BLOCKED: Python Playwright is required for automated case QA") from exc

    handler = partial(QuietHandler, directory=str(html_path.parent))
    server: ThreadingHTTPServer | None = None
    thread: threading.Thread | None = None
    try:
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{server.server_port}/{html_path.name}"
    except PermissionError:
        url = html_path.as_uri()
    console_errors: list[str] = []
    checks = {
        "page_load_nonblank": False,
        "images_loaded": False,
        "lightbox_opens_complete_image": False,
        "lightbox_closes_on_image_or_overlay_click": False,
        "layout_stable_after_close": False,
        "no_console_errors": False,
    }
    scroll_viewports: list[dict] = []
    try:
        with sync_playwright() as playwright:
            launch = {"headless": True}
            if args.browser:
                launch["executable_path"] = str(Path(args.browser).expanduser().resolve())
            browser = playwright.chromium.launch(**launch)
            page = browser.new_page(viewport=tokens["canvas"], device_scale_factor=1)
            page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
            page.on("pageerror", lambda error: console_errors.append(str(error)))
            page.goto(url, wait_until="networkidle")
            page.evaluate("document.fonts && document.fonts.ready")
            page.wait_for_timeout(500)

            checks["page_load_nonblank"] = page.locator("[data-case-page]").count() > 0
            checks["images_loaded"] = page.evaluate(
                """() => [...document.images].every((image) => image.complete && image.naturalWidth > 0)"""
            )
            collector_source = collector_path.read_text(encoding="utf-8")
            rendered = page.evaluate(collector_source)
            atomic_write_json(rendered_path, rendered)
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot_path), full_page=True)

            for index in range(page.locator('[data-case-display-mode="scroll"]').count()):
                viewport = page.locator('[data-case-display-mode="scroll"]').nth(index)
                result = viewport.evaluate(
                    """(node) => {
                      const vertical = node.scrollHeight > node.clientHeight + 1;
                      const horizontal = node.scrollWidth > node.clientWidth + 1;
                      const before = [node.scrollTop, node.scrollLeft];
                      if (vertical) node.scrollTop = Math.min(20, node.scrollHeight - node.clientHeight);
                      if (horizontal) node.scrollLeft = Math.min(20, node.scrollWidth - node.clientWidth);
                      return {
                        id: node.dataset.caseEvidence || `scroll-${node.dataset.caseDisplayMode}`,
                        axes: [...(vertical ? ['vertical'] : []), ...(horizontal ? ['horizontal'] : [])],
                        pass: (vertical || horizontal) && (node.scrollTop !== before[0] || node.scrollLeft !== before[1])
                      };
                    }"""
                )
                scroll_viewports.append(result)

            roots_before = page.locator("[data-case-page]").evaluate_all(
                "nodes => nodes.map((node) => { const r = node.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; })"
            )
            trigger = page.locator("[data-case-lightbox-trigger]").first
            if trigger.count() > 0:
                trigger.click()
                page.wait_for_timeout(150)
                overlay = visible_lightbox(page)
                if overlay is not None:
                    lightbox_image = overlay.locator("img").first
                    checks["lightbox_opens_complete_image"] = (
                        lightbox_image.count() > 0
                        and lightbox_image.is_visible()
                        and lightbox_image.evaluate("image => image.complete && image.naturalWidth > 0")
                    )
                    overlay.click(position={"x": 4, "y": 4})
                    page.wait_for_timeout(150)
                    checks["lightbox_closes_on_image_or_overlay_click"] = visible_lightbox(page) is None
                    roots_after = page.locator("[data-case-page]").evaluate_all(
                        "nodes => nodes.map((node) => { const r = node.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; })"
                    )
                    checks["layout_stable_after_close"] = roots_before == roots_after
            checks["no_console_errors"] = not console_errors
            browser.close()
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None:
            thread.join(timeout=2)

    passed = all(checks.values()) and all(item.get("pass") is True for item in scroll_viewports)
    interaction = {
        "schema_version": 1,
        "target_html_sha256": sha256_file(html_path),
        "pass": passed,
        "checks": checks,
        "scroll_viewports": scroll_viewports,
        "console_errors": console_errors,
    }
    atomic_write_json(interaction_path, interaction)
    if not passed:
        print(f"BLOCKED: automated browser QA failed; report={interaction_path}")
        return 2
    print(f"PASS: browser QA collected; rendered={rendered_path}; screenshot={screenshot_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
