#!/usr/bin/env python3
"""Inspect, stamp, and requalify a customer-case run without skipping manual gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STATE_ORDER = ["NEW", "SOURCE_FETCHED", "STORY_DRAFTED", "STORY_APPROVED", "ASSET_PLANNED", "RENDERED", "VALIDATED", "DELIVERED"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def atomic_write_json(path: Path, value: dict) -> None:
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


def run_checked(*arguments: str) -> None:
    result = subprocess.run([sys.executable, *arguments], text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(arguments)}")


def load_run(run_dir: Path) -> dict:
    state = read_json(run_dir / "case-state.json")
    if Path(state.get("run_dir", "")).expanduser().resolve() != run_dir:
        raise ValueError("case-state.json belongs to another run")
    return state


def stale_stages(run_dir: Path, state: dict) -> list[str]:
    stale: list[str] = []
    for stage, record in state.get("artifacts", {}).items():
        if not isinstance(record, dict):
            stale.append(stage)
            continue
        path = Path(record.get("path", ""))
        if not path.is_absolute():
            path = run_dir / path
        if not path.is_file() or record.get("sha256") != sha256_file(path):
            stale.append(stage)
            continue
        dependencies = record.get("dependencies")
        if not isinstance(dependencies, dict):
            stale.append(stage)
            continue
        for relative, expected in dependencies.items():
            dependency = run_dir / relative
            if not dependency.is_file() or sha256_file(dependency) != expected:
                stale.append(stage)
                break
    required = {
        "SOURCE_FETCHED": ("input/SOURCE-NOTES.md",),
        "STORY_DRAFTED": ("output/STORY-REVIEW.md", "output/story-contract.json"),
        "ASSET_PLANNED": ("output/asset-plan.json", "output/asset-validation.json"),
        "RENDERED": (
            "output/DESIGN-PLAN.md",
            "output/layout-plan.json",
            "output/layout-validation.json",
            "output/outline.json",
            "output/deck.json",
            "output/index.html",
        ),
        "VALIDATED": (
            "output/rendered-layout.json",
            "output/rendered-layout-validation.json",
            "output/interaction-check.json",
            "output/QA-NOTES.md",
            "output/qa-notes.json",
        ),
        "DELIVERED": ("output/delivery-manifest.json", "output/run-validation.json"),
    }
    current_index = STATE_ORDER.index(state["state"])
    for stage, paths in required.items():
        if current_index < STATE_ORDER.index(stage):
            continue
        if any(not (run_dir / relative).is_file() for relative in paths):
            stale.append(stage)
    qa_path = run_dir / "output" / "qa-notes.json"
    if current_index >= STATE_ORDER.index("VALIDATED") and qa_path.is_file():
        try:
            qa = read_json(qa_path)
            screenshots = qa.get("screenshot_paths")
            if not isinstance(screenshots, list) or not screenshots or any(
                not isinstance(path, str) or not Path(path).expanduser().resolve().is_file()
                for path in screenshots
            ):
                stale.append("VALIDATED")
        except (OSError, ValueError, json.JSONDecodeError):
            stale.append("VALIDATED")
    return sorted(set(stale), key=STATE_ORDER.index)


def status_payload(run_dir: Path) -> dict:
    state = load_run(run_dir)
    stale = stale_stages(run_dir, state)
    next_steps = {
        "NEW": "fetch exact source and record it",
        "SOURCE_FETCHED": "draft STORY-REVIEW.md and story-contract.json",
        "STORY_DRAFTED": "manual stop: obtain explicit current-run story approval",
        "STORY_APPROVED": "plan and validate assets, layout, and DeckJSON",
        "ASSET_PLANNED": "stamp deck_id, render through the base Deck, then run requalify",
        "RENDERED": "run automated browser/layout/interaction QA",
        "VALIDATED": "verify delivery and run the final chain validator",
        "DELIVERED": "no action; rerun requalify only after an input changes",
    }
    commands = {
        "NEW": f'{sys.executable} {ROOT / "case_state.py"} source --run-dir {run_dir} --status fetched --revision <source-revision>',
        "SOURCE_FETCHED": f'{sys.executable} {ROOT / "validate_story_contract.py"} --contract {run_dir / "output/story-contract.json"} --story {run_dir / "output/STORY-REVIEW.md"}',
        "STORY_DRAFTED": f'{sys.executable} {ROOT / "case_state.py"} story-approve --run-dir {run_dir} --story-file {run_dir / "output/STORY-REVIEW.md"} --confirmed-by user --confirmation-text "<exact user confirmation>"',
        "STORY_APPROVED": f'{sys.executable} {ROOT / "validate_asset_plan.py"} --plan {run_dir / "output/asset-plan.json"} --run-dir {run_dir}',
        "ASSET_PLANNED": f'{sys.executable} {ROOT / "case_pipeline.py"} stamp-deck --run-dir {run_dir}',
        "RENDERED": f'{sys.executable} {ROOT / "case_pipeline.py"} requalify --run-dir {run_dir}',
        "VALIDATED": f'{sys.executable} {ROOT / "case_pipeline.py"} requalify --run-dir {run_dir}',
        "DELIVERED": f'{sys.executable} {ROOT / "case_pipeline.py"} status --run-dir {run_dir}',
    }
    current = state.get("state")
    return {
        "schema_version": 1,
        "run_dir": str(run_dir),
        "deck_id": state.get("deck_id"),
        "state": state.get("state"),
        "stale_stages": stale,
        "first_breakpoint": stale[0] if stale else None,
        "next": "rewind and requalify stale artifacts" if stale else next_steps.get(current),
        "next_command": f'{sys.executable} {ROOT / "case_pipeline.py"} requalify --run-dir {run_dir}' if stale else commands.get(current),
    }


def command_status(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).expanduser().resolve()
    print(json.dumps(status_payload(run_dir), ensure_ascii=False, indent=2))


def command_next(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).expanduser().resolve()
    print(status_payload(run_dir)["next_command"])


def stamp_deck(run_dir: Path, state: dict) -> bool:
    deck_path = run_dir / "output" / "deck.json"
    deck = read_json(deck_path)
    metadata = deck.get("deck")
    if not isinstance(metadata, dict):
        raise ValueError("deck.json must contain deck metadata before stamping")
    current = metadata.get("deck_id")
    expected = state["deck_id"]
    if current == expected:
        return False
    if current not in {None, ""}:
        raise ValueError(f"deck.json belongs to another deck_id: {current}")
    metadata["deck_id"] = expected
    atomic_write_json(deck_path, deck)
    return True


def command_stamp(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).expanduser().resolve()
    changed = stamp_deck(run_dir, load_run(run_dir))
    print("deck_id stamped; rerender required" if changed else "deck_id already matches")


def find_base_validator() -> Path:
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
        validator = root / "deck-json" / "validate-deck.py"
        if validator.is_file():
            return validator
    raise ValueError("cannot locate the installed base Deck validate-deck.py")


def rewind_for_stale(run_dir: Path, state: dict, stale: list[str]) -> None:
    if not stale:
        return
    earliest = min(stale, key=STATE_ORDER.index)
    target = {
        "ASSET_PLANNED": "STORY_APPROVED",
        "RENDERED": "ASSET_PLANNED",
        "VALIDATED": "RENDERED",
        "DELIVERED": "VALIDATED",
    }[earliest]
    if STATE_ORDER.index(state["state"]) > STATE_ORDER.index(target):
        run_checked(str(ROOT / "case_state.py"), "rewind", "--run-dir", str(run_dir), "--to", target, "--reason", f"stale {earliest} artifact or dependency")


def command_requalify(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).expanduser().resolve()
    output = run_dir / "output"
    state = load_run(run_dir)
    if STATE_ORDER.index(state["state"]) < STATE_ORDER.index("STORY_APPROVED"):
        raise RuntimeError("manual stop: the exact current story must be explicitly approved first")
    stale = stale_stages(run_dir, state)
    if state["state"] == "DELIVERED" and not stale:
        print("PASS: run is already delivered and every recorded dependency is fresh")
        return
    rewind_for_stale(run_dir, state, stale)
    state = load_run(run_dir)

    story = output / "STORY-REVIEW.md"
    story_contract = output / "story-contract.json"
    asset_plan = output / "asset-plan.json"
    layout_plan = output / "layout-plan.json"
    deck_path = output / "deck.json"
    html = output / "index.html"
    run_checked(str(ROOT / "validate_story_contract.py"), "--contract", str(story_contract), "--story", str(story))
    run_checked(str(ROOT / "validate_asset_plan.py"), "--plan", str(asset_plan), "--run-dir", str(run_dir))
    if state["state"] == "STORY_APPROVED":
        run_checked(str(ROOT / "case_state.py"), "advance", "--run-dir", str(run_dir), "--to", "ASSET_PLANNED", "--artifact", str(asset_plan))
        state = load_run(run_dir)
    run_checked(str(ROOT / "validate_layout_plan.py"), "--plan", str(layout_plan), "--run-dir", str(run_dir))

    stamped = stamp_deck(run_dir, state)
    if stamped:
        raise RuntimeError("deck_id was stamped into deck.json; rerender with the base Deck before requalifying")
    run_checked(str(ROOT / "validate_deck_hooks.py"), "--deck", str(deck_path), "--layout-plan", str(layout_plan))
    run_checked(str(find_base_validator()), "--strict", str(deck_path))
    if not html.is_file() or state["deck_id"] not in html.read_text(encoding="utf-8", errors="replace"):
        raise RuntimeError("final HTML is missing or does not carry the stable deck_id; rerender with the base Deck")

    rendered = output / "rendered-layout.json"
    screenshot = output / "qa-page.png"
    interaction = output / "interaction-check.json"
    collector_args = [
        str(ROOT / "collect_case_qa.py"),
        "--html", str(html),
        "--layout-plan", str(layout_plan),
        "--rendered-report", str(rendered),
        "--screenshot", str(screenshot),
        "--interaction-report", str(interaction),
    ]
    if args.browser:
        collector_args.extend(["--browser", args.browser])
    run_checked(*collector_args)
    rendered_validation = output / "rendered-layout-validation.json"
    run_checked(
        str(ROOT / "validate_rendered_layout.py"),
        "--layout-plan", str(layout_plan),
        "--html", str(html),
        "--report", str(rendered),
        "--output", str(rendered_validation),
    )
    state = load_run(run_dir)
    if state["state"] == "ASSET_PLANNED":
        run_checked(str(ROOT / "case_state.py"), "advance", "--run-dir", str(run_dir), "--to", "RENDERED", "--artifact", str(html))

    html_hash = sha256_file(html)
    qa_json = output / "qa-notes.json"
    if not qa_json.is_file():
        atomic_write_json(
            qa_json,
            {
            "schema_version": 1,
            "pass": False,
            "html": {"path": str(html), "sha256": html_hash},
            "base_validator": "pass",
            "unresolved_limitations": [],
            "screenshot_paths": [str(screenshot)],
            "interaction_report_path": str(interaction),
            "rendered_layout_validation_path": str(rendered_validation),
            "checks": {
                "page_count_and_keys": "pending-human-review",
                "source_story_asset_layout": "pending-human-review",
                "rendered_layout_alignment": "pending-human-review",
                "overlap_and_dead_space": "pending-human-review",
                "evidence_readability_and_captions": "pending-human-review",
                "browser_and_interaction": "pass",
            },
            "notes": [],
            },
        )
    if not (output / "QA-NOTES.md").is_file():
        (output / "QA-NOTES.md").write_text(
            "# QA Notes\n\nMachine result: `qa-notes.json`\n\nHuman visual review is pending. Record observations here, then set every pending check and `pass` in `qa-notes.json`.\n",
            encoding="utf-8",
        )
    qa_data = read_json(qa_json)
    if qa_data.get("pass") is not True:
        raise RuntimeError(
            "manual stop: review page count/keys, story fidelity, overlap/dead space, and evidence readability; "
            f"record the conclusion in {output / 'QA-NOTES.md'} and update pending fields plus pass in {qa_json}"
        )
    state = load_run(run_dir)
    if state["state"] == "RENDERED":
        run_checked(str(ROOT / "case_state.py"), "advance", "--run-dir", str(run_dir), "--to", "VALIDATED", "--artifact", str(qa_json))

    manifest = output / "delivery-manifest.json"
    run_checked(
        str(ROOT / "verify_delivery.py"),
        "--html", str(html),
        "--mode", args.mode,
        "--viewer", args.viewer,
        "--screenshot", str(screenshot),
        "--interaction-report", str(interaction),
        "--manifest", str(manifest),
    )
    run_checked(str(ROOT / "validate_case_run.py"), "--run-dir", str(run_dir), "--output", str(output / "run-validation.json"))
    state = load_run(run_dir)
    if state["state"] == "VALIDATED":
        run_checked(str(ROOT / "case_state.py"), "advance", "--run-dir", str(run_dir), "--to", "DELIVERED", "--artifact", str(manifest))
    print("PASS: run requalified through browser QA, delivery verification, and final validation")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    status = subparsers.add_parser("status")
    status.add_argument("--run-dir", required=True)
    status.set_defaults(func=command_status)
    next_command = subparsers.add_parser("next")
    next_command.add_argument("--run-dir", required=True)
    next_command.set_defaults(func=command_next)
    stamp = subparsers.add_parser("stamp-deck")
    stamp.add_argument("--run-dir", required=True)
    stamp.set_defaults(func=command_stamp)
    requalify = subparsers.add_parser("requalify")
    requalify.add_argument("--run-dir", required=True)
    requalify.add_argument("--mode", choices=["linked", "single"], default="linked")
    requalify.add_argument("--viewer", choices=["local", "in-app", "share"], default="local")
    requalify.add_argument("--browser")
    requalify.set_defaults(func=command_requalify)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        args.func(args)
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
