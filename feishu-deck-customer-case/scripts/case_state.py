#!/usr/bin/env python3
"""Deterministic workflow state for Feishu customer-case generation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


STATES = [
    "NEW",
    "SOURCE_FETCHED",
    "STORY_DRAFTED",
    "STORY_APPROVED",
    "ASSET_PLANNED",
    "RENDERED",
    "VALIDATED",
    "DELIVERED",
]
STATE_INDEX = {state: index for index, state in enumerate(STATES)}
NEXT_STATE = {
    "ASSET_PLANNED": "STORY_APPROVED",
    "RENDERED": "ASSET_PLANNED",
    "VALIDATED": "RENDERED",
    "DELIVERED": "VALIDATED",
}


class ContractError(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def state_path(run_dir: Path) -> Path:
    return run_dir / "case-state.json"


def require_run_dir(raw: str) -> Path:
    run_dir = Path(raw).expanduser().resolve()
    if not run_dir.is_dir():
        raise ContractError(f"run directory does not exist: {run_dir}")
    return run_dir


def load_state(run_dir: Path) -> dict:
    path = state_path(run_dir)
    if not path.is_file():
        raise ContractError(f"missing state file: {path}; run init first")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read state file: {exc}") from exc
    if data.get("state") not in STATE_INDEX:
        raise ContractError(f"invalid workflow state: {data.get('state')!r}")
    if data.get("schema_version") != 2 or not isinstance(data.get("deck_id"), str):
        raise ContractError("case-state.json must use schema_version 2 and contain deck_id")
    recorded = Path(data.get("run_dir", "")).expanduser().resolve()
    if recorded != run_dir:
        raise ContractError(
            f"state belongs to a different run: {recorded}; requested {run_dir}"
        )
    recorded_output = Path(data.get("output_dir", run_dir / "output")).expanduser().resolve()
    expected_output = (run_dir / "output").resolve()
    if recorded_output != expected_output:
        raise ContractError(
            f"state output_dir must be {expected_output}; recorded {recorded_output}"
        )
    return data


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def add_history(data: dict, event: str, details: dict | None = None) -> None:
    data.setdefault("history", []).append(
        {"at": now_iso(), "event": event, "details": details or {}}
    )
    data["updated_at"] = now_iso()


def invalidate_story(data: dict, reason: str) -> None:
    story = data.setdefault("story", {})
    story.update(
        {
            "status": "missing",
            "path": None,
            "sha256": None,
            "approved_at": None,
            "confirmed_by": None,
            "confirmation_text": None,
        }
    )
    data["artifacts"] = {}
    add_history(data, "approval_invalidated", {"reason": reason})


def require_evaluation_marker(run_dir: Path) -> None:
    if (
        run_dir.parent.name != "runs"
        or run_dir.parent.parent.name != "data"
        or run_dir.parent.parent.parent.name != "技能实验室"
        or not run_dir.name.startswith("run-")
    ):
        raise ContractError("evaluation-harness approval requires a canonical run-<id> directory")
    output_dir = run_dir / "output"
    marker_path = run_dir / "evaluation-mode.json"
    if not marker_path.is_file():
        raise ContractError(f"evaluation-harness approval requires marker {marker_path}")
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read evaluation marker: {exc}") from exc
    if (
        marker.get("schema_version") != 1
        or marker.get("created_by") != "feishu-case-evaluation-workbench"
        or marker.get("mode") != "unattended"
        or marker.get("run_id") != run_dir.name.removeprefix("run-")
        or not isinstance(marker.get("created_at"), str)
        or not marker["created_at"].strip()
        or Path(marker.get("output_dir", "")).expanduser().resolve() != output_dir.resolve()
    ):
        raise ContractError("evaluation marker does not match this unattended run")


def require_story_contract(run_dir: Path, story_hash: str) -> None:
    path = run_dir / "output" / "story-contract.json"
    if not path.is_file():
        raise ContractError(f"missing structured story contract: {path}")
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read structured story contract: {exc}") from exc
    if contract.get("version") != 2:
        raise ContractError("story-contract.json must use version 2")
    if contract.get("story_hash") != story_hash:
        raise ContractError("story-contract.json must match the exact STORY-REVIEW.md revision")


def verify_story_integrity(data: dict, run_dir: Path) -> None:
    if data.get("source", {}).get("status") != "fetched":
        raise ContractError("source is not fully fetched")
    story = data.get("story", {})
    raw_path = story.get("path")
    expected = story.get("sha256")
    if not raw_path or not expected:
        raise ContractError("current story draft is missing")
    path = Path(raw_path)
    if not path.is_absolute():
        path = run_dir / path
    path = path.resolve()
    if not path.is_file():
        raise ContractError(f"story file is missing: {path}")
    actual = sha256_file(path)
    if actual != expected:
        raise ContractError(
            "story file changed after it was recorded; run story-draft and obtain approval again"
        )
    require_story_contract(run_dir, actual)


def normalize_artifact(run_dir: Path, raw: str) -> tuple[Path, str]:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = run_dir / path
    path = path.resolve()
    if not path.exists():
        raise ContractError(f"artifact does not exist: {path}")
    try:
        stored = str(path.relative_to(run_dir))
    except ValueError:
        stored = str(path)
    return path, stored


def artifact_record(run_dir: Path, path: Path, stored: str, dependencies: tuple[str, ...] = ()) -> dict:
    record = {"path": stored, "sha256": sha256_file(path), "dependencies": {}}
    for relative in dependencies:
        dependency = run_dir / relative
        if not dependency.is_file():
            raise ContractError(f"missing stage dependency: {dependency}")
        record["dependencies"][relative] = sha256_file(dependency)
    return record


def require_validation_report(report_path: Path, artifact_path: Path, label: str) -> None:
    if not report_path.is_file():
        raise ContractError(f"missing {label} validation report: {report_path}")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read {label} validation report: {exc}") from exc
    if report.get("pass") is not True:
        raise ContractError(f"{label} validation report did not pass")
    if report.get("plan_sha256") != sha256_file(artifact_path):
        raise ContractError(f"{label} validation report belongs to a different plan revision")


def require_layout_validation(run_dir: Path) -> None:
    plan = run_dir / "output" / "layout-plan.json"
    report = run_dir / "output" / "layout-validation.json"
    if not plan.is_file():
        raise ContractError(f"missing layout plan: {plan}")
    require_validation_report(report, plan, "layout")


def require_qa_notes(notes_path: Path) -> None:
    try:
        notes = json.loads(notes_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read QA notes: {exc}") from exc
    if notes.get("schema_version") != 1 or notes.get("pass") is not True:
        raise ContractError("qa-notes.json must use schema_version 1 and pass")
    if notes.get("base_validator") != "pass":
        raise ContractError("qa-notes.json must record base_validator=pass")
    if notes.get("unresolved_limitations") != []:
        raise ContractError("qa-notes.json must contain no unresolved limitations")
    checks = notes.get("checks")
    required_checks = {
        "page_count_and_keys",
        "source_story_asset_layout",
        "rendered_layout_alignment",
        "overlap_and_dead_space",
        "evidence_readability_and_captions",
        "browser_and_interaction",
    }
    if not isinstance(checks, dict) or any(checks.get(name) != "pass" for name in required_checks):
        raise ContractError("qa-notes.json must mark every required human and browser check as pass")

    html = notes.get("html")
    if not isinstance(html, dict):
        raise ContractError("qa-notes.json must record the exact HTML object")
    html_value = html.get("path")
    html_hash = html.get("sha256")
    if not isinstance(html_value, str) or not isinstance(html_hash, str) or len(html_hash) != 64:
        raise ContractError("qa-notes.json must record an absolute HTML path and SHA256")
    html_path = Path(html_value).expanduser().resolve()
    if not html_path.is_file() or sha256_file(html_path) != html_hash:
        raise ContractError("qa-notes.json belongs to a missing or different HTML revision")

    rendered_value = notes.get("rendered_layout_validation_path")
    if not isinstance(rendered_value, str):
        raise ContractError("qa-notes.json must record rendered_layout_validation_path")
    rendered_path = Path(rendered_value).expanduser().resolve()
    if not rendered_path.is_file():
        raise ContractError("rendered layout validation report is missing")
    try:
        rendered = json.loads(rendered_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read rendered layout validation report: {exc}") from exc
    if rendered.get("pass") is not True:
        raise ContractError("rendered layout validation report did not pass")
    plan_path = notes_path.parent / "layout-plan.json"
    if not plan_path.is_file() or rendered.get("layout_plan_sha256") != sha256_file(plan_path):
        raise ContractError("rendered layout validation belongs to a different layout plan")
    if rendered.get("html_sha256") != html_hash:
        raise ContractError("rendered layout validation belongs to a different HTML revision")

    screenshots = notes.get("screenshot_paths")
    if not isinstance(screenshots, list) or not screenshots:
        raise ContractError("qa-notes.json must record at least one screenshot")
    for value in screenshots:
        if not isinstance(value, str) or not Path(value).expanduser().resolve().is_file():
            raise ContractError("qa-notes.json has a missing screenshot")
    interaction_value = notes.get("interaction_report_path")
    interaction_path = Path(interaction_value).expanduser().resolve() if isinstance(interaction_value, str) else None
    if interaction_path is None or not interaction_path.is_file():
        raise ContractError("qa-notes.json has a missing interaction report")
    try:
        interaction = json.loads(interaction_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read interaction report: {exc}") from exc
    if interaction.get("pass") is not True or interaction.get("target_html_sha256") != html_hash:
        raise ContractError("interaction report did not pass for the exact HTML revision")


def require_run_validation(run_dir: Path) -> None:
    path = run_dir / "output" / "run-validation.json"
    if not path.is_file():
        raise ContractError(f"missing final run validation report: {path}")
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read final run validation report: {exc}") from exc
    if report.get("pass") is not True:
        raise ContractError("final run validation report did not pass")
    if Path(report.get("run_dir", "")).expanduser().resolve() != run_dir:
        raise ContractError("final run validation report belongs to a different run")


def command_init(args: argparse.Namespace) -> None:
    run_dir = require_run_dir(args.run_dir)
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else (run_dir / "output").resolve()
    )
    expected_output = (run_dir / "output").resolve()
    if output_dir != expected_output:
        raise ContractError(
            f"output directory must be exactly {expected_output}; got {output_dir}"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "input" / "assets").mkdir(parents=True, exist_ok=True)
    path = state_path(run_dir)
    if path.exists() and not args.force:
        raise ContractError(f"state already exists: {path}; omit init or use --force")
    created = now_iso()
    data = {
        "schema_version": 2,
        "deck_id": "dk-" + hashlib.sha256(f"feishu-case:{run_dir}".encode("utf-8")).hexdigest()[:20],
        "run_dir": str(run_dir),
        "output_dir": str(output_dir),
        "state": "NEW",
        "source": {
            "url": args.source_url,
            "status": "unknown",
            "revision": None,
        },
        "story": {
            "status": "missing",
            "path": None,
            "sha256": None,
            "approved_at": None,
            "confirmed_by": None,
            "confirmation_text": None,
        },
        "artifacts": {},
        "created_at": created,
        "updated_at": created,
        "history": [{"at": created, "event": "initialized", "details": {}}],
    }
    atomic_write_json(path, data)
    print(f"initialized {path} in state NEW")


def command_source(args: argparse.Namespace) -> None:
    run_dir = require_run_dir(args.run_dir)
    data = load_state(run_dir)
    source = data.setdefault("source", {})
    changed = (
        source.get("status") != args.status
        or source.get("revision") != args.revision
    )
    source.update({"status": args.status, "revision": args.revision})
    if args.source_url:
        changed = changed or source.get("url") != args.source_url
        source["url"] = args.source_url
    if changed and STATE_INDEX[data["state"]] >= STATE_INDEX["STORY_DRAFTED"]:
        invalidate_story(data, "source status, URL, or revision changed")
    if args.status == "fetched":
        if STATE_INDEX[data["state"]] < STATE_INDEX["SOURCE_FETCHED"] or changed:
            data["state"] = "SOURCE_FETCHED"
    else:
        data["state"] = "NEW"
    add_history(
        data,
        "source_recorded",
        {"status": args.status, "revision": args.revision},
    )
    atomic_write_json(state_path(run_dir), data)
    print(f"source={args.status}; state={data['state']}")


def command_story_draft(args: argparse.Namespace) -> None:
    run_dir = require_run_dir(args.run_dir)
    data = load_state(run_dir)
    if data.get("source", {}).get("status") != "fetched":
        raise ContractError("cannot draft story until the exact source is fetched")
    path, stored = normalize_artifact(run_dir, args.story_file)
    digest = sha256_file(path)
    require_story_contract(run_dir, digest)
    previous = data.get("story", {})
    changed = previous.get("sha256") != digest or previous.get("path") != stored
    data["story"] = {
        "status": "drafted",
        "path": stored,
        "sha256": digest,
        "approved_at": None,
        "confirmed_by": None,
        "confirmation_text": None,
    }
    data["state"] = "STORY_DRAFTED"
    data["artifacts"] = {}
    add_history(data, "story_drafted", {"path": stored, "sha256": digest, "changed": changed})
    atomic_write_json(state_path(run_dir), data)
    print(f"story drafted; sha256={digest}; state=STORY_DRAFTED")


def command_story_approve(args: argparse.Namespace) -> None:
    run_dir = require_run_dir(args.run_dir)
    data = load_state(run_dir)
    if data["state"] != "STORY_DRAFTED":
        raise ContractError(
            f"approval requires STORY_DRAFTED, current state is {data['state']}"
        )
    if not args.confirmation_text.strip():
        raise ContractError("confirmation text cannot be empty")
    if args.confirmed_by == "evaluation-harness":
        evaluation_mode = args.evaluation_mode or os.environ.get("EVALUATION_MODE")
        if evaluation_mode != "unattended":
            raise ContractError("evaluation-harness approval requires EVALUATION_MODE=unattended")
        if args.confirmation_text.strip() != "unattended evaluation run":
            raise ContractError("evaluation-harness approval requires the canonical confirmation text")
        require_evaluation_marker(run_dir)
    path, stored = normalize_artifact(run_dir, args.story_file)
    expected = data.get("story", {}).get("sha256")
    actual = sha256_file(path)
    if stored != data.get("story", {}).get("path") or actual != expected:
        raise ContractError("story differs from the draft shown to the user")
    approved_at = now_iso()
    data["story"].update(
        {
            "status": "approved",
            "approved_at": approved_at,
            "confirmed_by": args.confirmed_by,
            "confirmation_text": args.confirmation_text.strip(),
        }
    )
    data["state"] = "STORY_APPROVED"
    add_history(
        data,
        "story_approved",
        {
            "confirmed_by": args.confirmed_by,
            "confirmation_text": args.confirmation_text.strip(),
        },
    )
    atomic_write_json(state_path(run_dir), data)
    print("story approved for this run; state=STORY_APPROVED")


def command_gate(args: argparse.Namespace) -> None:
    run_dir = require_run_dir(args.run_dir)
    data = load_state(run_dir)
    required = {
        "design": "STORY_APPROVED",
        "render": "ASSET_PLANNED",
        "delivery": "VALIDATED",
    }[args.for_stage]
    if STATE_INDEX[data["state"]] < STATE_INDEX[required]:
        raise ContractError(
            f"{args.for_stage} gate requires {required}; current state is {data['state']}"
        )
    if args.for_stage in {"design", "render"}:
        verify_story_integrity(data, run_dir)
        if data.get("story", {}).get("status") != "approved":
            raise ContractError("current story has no valid user approval")
    if args.for_stage == "render" and "ASSET_PLANNED" not in data.get("artifacts", {}):
        raise ContractError("asset plan artifact is not recorded")
    if args.for_stage == "render":
        require_layout_validation(run_dir)
    if args.for_stage == "delivery" and "VALIDATED" not in data.get("artifacts", {}):
        raise ContractError("validation artifact is not recorded")
    if args.for_stage == "delivery":
        qa_record = data.get("artifacts", {}).get("VALIDATED")
        if not isinstance(qa_record, dict):
            raise ContractError("validation artifact record is invalid")
        qa_path = run_dir / qa_record.get("path", "")
        if not qa_path.is_file() or qa_record.get("sha256") != sha256_file(qa_path):
            raise ContractError("validation artifact changed after it was recorded")
        require_qa_notes(qa_path)
    print(f"PASS: {args.for_stage} gate at state {data['state']}")


def command_advance(args: argparse.Namespace) -> None:
    run_dir = require_run_dir(args.run_dir)
    data = load_state(run_dir)
    expected = NEXT_STATE[args.to]
    if data["state"] not in {expected, args.to}:
        raise ContractError(
            f"cannot advance to {args.to} from {data['state']}; expected {expected}"
        )
    if args.to in {"ASSET_PLANNED", "RENDERED"}:
        verify_story_integrity(data, run_dir)
        if data.get("story", {}).get("status") != "approved":
            raise ContractError("current story approval is invalid")
    artifact_path, stored = normalize_artifact(run_dir, args.artifact)
    if args.to == "ASSET_PLANNED":
        require_validation_report(
            artifact_path.parent / "asset-validation.json",
            artifact_path,
            "asset",
        )
    if args.to == "RENDERED":
        require_layout_validation(run_dir)
    if args.to == "VALIDATED":
        require_qa_notes(artifact_path)
    if args.to == "DELIVERED":
        try:
            manifest = json.loads(artifact_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ContractError(f"cannot read delivery manifest: {exc}") from exc
        if manifest.get("pass") is not True:
            raise ContractError("delivery manifest did not pass")
        require_run_validation(run_dir)
    dependencies = {
        "ASSET_PLANNED": ("output/story-contract.json", "output/asset-validation.json"),
        "RENDERED": ("output/layout-plan.json", "output/layout-validation.json", "output/deck.json"),
        "VALIDATED": (
            "output/rendered-layout.json",
            "output/rendered-layout-validation.json",
            "output/interaction-check.json",
        ),
        "DELIVERED": ("output/run-validation.json",),
    }[args.to]
    data.setdefault("artifacts", {})[args.to] = artifact_record(
        run_dir,
        artifact_path,
        stored,
        dependencies,
    )
    data["state"] = args.to
    add_history(data, "state_advanced", {"to": args.to, "artifact": stored})
    atomic_write_json(state_path(run_dir), data)
    print(f"state={args.to}; artifact={stored}")


def command_rewind(args: argparse.Namespace) -> None:
    run_dir = require_run_dir(args.run_dir)
    data = load_state(run_dir)
    if args.to not in {"STORY_APPROVED", "ASSET_PLANNED", "RENDERED", "VALIDATED"}:
        raise ContractError("rewind target is not supported")
    if STATE_INDEX[args.to] >= STATE_INDEX[data["state"]]:
        raise ContractError(f"rewind target {args.to} must precede current state {data['state']}")
    if STATE_INDEX[args.to] >= STATE_INDEX["STORY_APPROVED"]:
        verify_story_integrity(data, run_dir)
    artifacts = data.setdefault("artifacts", {})
    for state in list(artifacts):
        if state in STATE_INDEX and STATE_INDEX[state] > STATE_INDEX[args.to]:
            del artifacts[state]
    data["state"] = args.to
    add_history(data, "state_rewound", {"to": args.to, "reason": args.reason})
    atomic_write_json(state_path(run_dir), data)
    print(f"state={args.to}; reason={args.reason}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init")
    init.add_argument("--run-dir", required=True)
    init.add_argument("--output-dir")
    init.add_argument("--source-url", required=True)
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=command_init)

    source = subparsers.add_parser("source")
    source.add_argument("--run-dir", required=True)
    source.add_argument("--status", choices=["fetched", "partial", "blocked"], required=True)
    source.add_argument("--revision", required=True)
    source.add_argument("--source-url")
    source.set_defaults(func=command_source)

    draft = subparsers.add_parser("story-draft")
    draft.add_argument("--run-dir", required=True)
    draft.add_argument("--story-file", required=True)
    draft.set_defaults(func=command_story_draft)

    approve = subparsers.add_parser("story-approve")
    approve.add_argument("--run-dir", required=True)
    approve.add_argument("--story-file", required=True)
    approve.add_argument("--confirmed-by", required=True)
    approve.add_argument("--confirmation-text", required=True)
    approve.add_argument("--evaluation-mode", choices=["unattended"])
    approve.set_defaults(func=command_story_approve)

    gate = subparsers.add_parser("gate")
    gate.add_argument("--run-dir", required=True)
    gate.add_argument("--for-stage", choices=["design", "render", "delivery"], required=True)
    gate.set_defaults(func=command_gate)

    advance = subparsers.add_parser("advance")
    advance.add_argument("--run-dir", required=True)
    advance.add_argument("--to", choices=list(NEXT_STATE), required=True)
    advance.add_argument("--artifact", required=True)
    advance.set_defaults(func=command_advance)

    rewind = subparsers.add_parser("rewind")
    rewind.add_argument("--run-dir", required=True)
    rewind.add_argument("--to", choices=["STORY_APPROVED", "ASSET_PLANNED", "RENDERED", "VALIDATED"], required=True)
    rewind.add_argument("--reason", required=True)
    rewind.set_defaults(func=command_rewind)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
        return 0
    except ContractError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        if getattr(args, "run_dir", None):
            print(
                f"FIX: {sys.executable} {Path(__file__).with_name('case_pipeline.py')} status --run-dir {Path(args.run_dir).expanduser().resolve()}",
                file=sys.stderr,
            )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
