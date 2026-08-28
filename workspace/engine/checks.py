#!/usr/bin/env python3
"""Structural, contract, and stale-route checks for the standalone System."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


PRODUCT_NAME = "Agentic Power BI System"
VISIBLE_FUNCTIONAL_ROOTS = {"workspace", "examples", "docs"}
PUBLIC_ROOT_FILES = {"AGENTS.md", "README.md", "LICENSE"}
TOOLCHAIN_ROOT_FILES = {
    "Cargo.lock",
    "Cargo.toml",
    "Gemfile",
    "GNUmakefile",
    "Makefile",
    "go.mod",
    "go.sum",
    "package-lock.json",
    "package.json",
    "pnpm-lock.yaml",
    "pyproject.toml",
    "pytest.ini",
    "setup.cfg",
    "tox.ini",
    "yarn.lock",
}
REQUIRED_PATHS = (
    "AGENTS.md",
    "README.md",
    ".agents/skills/agentic-powerbi-system/SKILL.md",
    ".agents/skills/powerbi/SKILL.md",
    ".agents/skills/pbip/SKILL.md",
    ".agents/skills/dax/SKILL.md",
    ".agents/skills/report/SKILL.md",
    ".agents/skills/system-audit/SKILL.md",
    ".agents/skills/fabric/SKILL.md",
    ".agents/skills/validation/SKILL.md",
    "workspace/PROJECT-BRIEF.md",
    "workspace/README.md",
    "workspace/briefs",
    "workspace/models",
    "workspace/reports",
    "workspace/state",
    "workspace/runs",
    "workspace/history/runs.jsonl",
    "workspace/learning",
    "workspace/engine/tracer.py",
    "workspace/engine/checks.py",
    "workspace/engine/doctor.mjs",
    "workspace/engine/seed-guard.mjs",
    "workspace/engine/system_audit.py",
    "workspace/engine/validate-pbip.mjs",
    "workspace/engine/tests/test_system_audit.py",
    "workspace/engine/tests/test_template.py",
    "workspace/engine/tests/test-validator.mjs",
    "docs/contract.md",
    "docs/validation.md",
)
STALE_ROOT_NAMES = {
    "assets",
    "engine",
    "ext" + "ensions",
    "prom" + "pts",
    "scripts",
    "tests",
}
CURATED_EXAMPLE_FIELDS = {"curated", "example", "source_run_id", "status"}
LEDGER_FIELDS = {
    "run_id",
    "started_at",
    "finished_at",
    "status",
    "input_ref",
    "output_ref",
    "proof_ref",
    "previous_run_id",
    "previous_run_relation",
    "failure",
    "recovery",
}
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _public_text_files(root: Path) -> Iterable[Path]:
    """Yield source files that form the public or operational contract."""

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pbix"}:
            continue
        yield path


def _contains_stale_language(text: str) -> List[str]:
    """Return forbidden legacy route or unsafe public wording fragments."""

    # Keep legacy fragments assembled so this checker does not become a stale
    # public artifact containing the routes it is designed to catch.
    forbidden = (
        "PowerBI-" + "template",
        "prom" + "pts/",
        "p" + "i" + ".prom" + "pts",
        "." + "p" + "i" + "/",
        "@mario" + "zechner",
        "hand" + "off " + "sche" + "ma",
        "hand" + "off-" + "sche" + "ma",
        "hand" + " " + "off " + "sche" + "ma",
        "hand" + " " + "off-" + "sche" + "ma",
        "shared " + "sche" + "ma",
        "shared-" + "sche" + "ma",
        "cross-" + "system " + "sche" + "ma",
        "cross " + "system " + "sche" + "ma",
        "runtime " + "dependency",
        "runtime-" + "dependency",
        "shared " + "package",
        "central " + "database",
        "raw " + "pr" + "ompt",
        "Agentic " + "Project " + "Template",
    )
    lowered = text.lower()
    return [phrase for phrase in forbidden if phrase.lower() in lowered]


def _relative_reference(root: Path, value: object) -> Optional[Path]:
    if not isinstance(value, str) or not value:
        return None
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def check_structure(root: Path) -> List[str]:
    """Return structural violations; an empty list means the shell is valid."""

    errors: List[str] = []
    if not root.is_dir():
        return [f"repository root is not a directory: {root}"]

    visible_entries = [entry for entry in root.iterdir() if not entry.name.startswith(".")]
    for entry in visible_entries:
        if entry.name in VISIBLE_FUNCTIONAL_ROOTS:
            continue
        if entry.name in PUBLIC_ROOT_FILES or entry.name in TOOLCHAIN_ROOT_FILES:
            continue
        if entry.name in STALE_ROOT_NAMES:
            errors.append(f"legacy root path is present: {entry.name}/")
        elif entry.is_dir() or entry.is_symlink():
            errors.append(f"visible functional root is not allowed: {entry.name}/")
        else:
            errors.append(f"visible root file is not part of the public shell: {entry.name}")

    for stale_name in sorted(STALE_ROOT_NAMES):
        if (root / stale_name).exists():
            errors.append(f"legacy root path is present: {stale_name}/")

    hidden_legacy = {"." + "p" + "i", "p" + "i" + ".prom" + "pts"}
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        if any(part in hidden_legacy for part in path.parts):
            errors.append(f"legacy hidden path is present: {path.relative_to(root)}")

    for relative in REQUIRED_PATHS:
        if not (root / relative).exists():
            errors.append(f"required path is missing: {relative}")

    for path in (root / "workspace", root / "examples", root / "docs"):
        if path.is_symlink():
            errors.append(f"functional root must be a directory, not a symlink: {path.name}/")
        elif not path.is_dir():
            errors.append(f"functional root must be a directory: {path.name}/")

    history = root / "workspace" / "history" / "runs.jsonl"
    if history.exists() and not history.is_file():
        errors.append("workspace/history/runs.jsonl must be a file")
    if history.is_file():
        _check_ledger(history, root, errors)

    for path in _public_text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for phrase in _contains_stale_language(text):
            errors.append(f"stale public wording {phrase!r} in {path.relative_to(root)}")

    examples_root = root / "examples"
    if examples_root.is_dir():
        _check_example_tree(examples_root, errors)

    return errors


def _check_example_tree(directory: Path, errors: List[str]) -> bool:
    """Validate curated leaves while allowing a readable run-name container."""

    visible = sorted(entry for entry in directory.iterdir() if not entry.name.startswith("."))
    if not visible:
        return True

    proof_path = directory / "proof.json"
    readme_path = directory / "README.md"
    if proof_path.exists() or readme_path.exists():
        label = directory.as_posix()
        if not proof_path.is_file() or not readme_path.is_file():
            errors.append(f"example is not a standalone proof: {label}/")
            return True
        allowed_files = {"README.md", "proof.json"}
        extra = [
            entry.name
            for entry in visible
            if not entry.is_dir() and entry.name not in allowed_files
        ]
        if extra:
            errors.append(
                f"example contains uncurated files: {label}/ ({', '.join(extra)})"
            )
        try:
            proof = json.loads(proof_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"example proof is not valid JSON: {label}/ ({exc})")
            return True
        if not isinstance(proof, dict) or not CURATED_EXAMPLE_FIELDS.issubset(proof):
            errors.append(f"example proof lacks curation fields: {label}/")
        elif proof.get("curated") is not True:
            errors.append(f"example is not explicitly curated: {label}/")
        return True

    found_leaf = False
    for entry in visible:
        if entry.is_dir():
            found_leaf = _check_example_tree(entry, errors) or found_leaf
        else:
            errors.append(
                f"example file is outside a curated proof: {entry.relative_to(directory.parent)}"
            )
    if directory != directory.parents[0] and not found_leaf and visible:
        errors.append(f"example container has no curated proof: {directory.as_posix()}/")
    return found_leaf


def _check_ledger(path: Path, root: Path, errors: List[str]) -> None:
    """Validate the local append-only ledger and its artifact references."""

    parsed: List[Tuple[int, Dict[str, object]]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"ledger cannot be read: {path.relative_to(root)} ({exc})")
        return

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"ledger line {line_number} is not valid JSON: {exc.msg}")
            continue
        if not isinstance(record, dict):
            errors.append(f"ledger line {line_number} must be a JSON object")
            continue

        missing = sorted(LEDGER_FIELDS.difference(record))
        if missing:
            errors.append(
                f"ledger line {line_number} is missing fields: {', '.join(missing)}"
            )
        parsed.append((line_number, record))

    seen: Dict[str, Dict[str, object]] = {}
    recovered: Dict[str, int] = {}
    for line_number, record in parsed:
        run_id = record.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            errors.append(f"ledger line {line_number} must have a non-empty run_id")
            continue
        duplicate_run_id = run_id in seen
        if duplicate_run_id:
            errors.append(f"ledger line {line_number} repeats run_id {run_id!r}")

        for timestamp_field in ("started_at", "finished_at"):
            timestamp = record.get(timestamp_field)
            if not isinstance(timestamp, str) or not TIMESTAMP_RE.fullmatch(timestamp):
                errors.append(
                    f"ledger line {line_number} has an invalid {timestamp_field}"
                )

        status = record.get("status")
        if status not in {"succeeded", "failed"}:
            errors.append(f"ledger line {line_number} has an invalid status")

        for ref_field in ("output_ref", "proof_ref"):
            ref_path = _relative_reference(root, record.get(ref_field))
            if ref_path is None or not ref_path.is_file():
                errors.append(
                    f"ledger line {line_number} has an invalid {ref_field}"
                )

        previous_id = record.get("previous_run_id")
        relation = record.get("previous_run_relation")
        if previous_id is None and relation is not None:
            errors.append(
                f"ledger line {line_number} has a relation without a previous run"
            )
        if previous_id is not None and relation not in {"predecessor", "recovery"}:
            errors.append(
                f"ledger line {line_number} has an invalid previous-run relation"
            )
        if previous_id is not None and not isinstance(previous_id, str):
            errors.append(f"ledger line {line_number} has an invalid previous_run_id")
        if isinstance(previous_id, str) and (
            previous_id == run_id or previous_id not in seen
        ):
            errors.append(
                f"ledger line {line_number} points to a run that is not earlier in the ledger"
            )

        recovery = record.get("recovery")
        if relation == "recovery" and recovery is None:
            errors.append(f"ledger line {line_number} lacks recovery evidence")
        if recovery is not None:
            if not isinstance(recovery, dict):
                errors.append(f"ledger line {line_number} has invalid recovery evidence")
                continue
            from_id = recovery.get("from_run_id")
            if relation != "recovery":
                errors.append(
                    f"ledger line {line_number} has recovery evidence without a recovery relation"
                )
            if from_id != previous_id:
                errors.append(
                    f"ledger line {line_number} recovery target disagrees with previous_run_id"
                )
            if not isinstance(from_id, str) or seen.get(from_id, {}).get("status") != "failed":
                errors.append(
                    f"ledger line {line_number} recovery target is not a failed run"
                )
            elif from_id in recovered:
                errors.append(
                    f"ledger line {line_number} recovers failed run {from_id!r} more than once"
                )
            else:
                recovered[from_id] = line_number
            recovery_ref = _relative_reference(root, recovery.get("ref"))
            if recovery_ref is None or not recovery_ref.is_file():
                errors.append(f"ledger line {line_number} lacks a recovery reference")

        failure = record.get("failure")
        if status == "failed" and failure is None:
            errors.append(f"ledger line {line_number} failed without failure evidence")
        if status == "succeeded" and failure is not None:
            errors.append(f"ledger line {line_number} succeeded with failure evidence")
        if failure is not None:
            if not isinstance(failure, dict):
                errors.append(f"ledger line {line_number} has invalid failure evidence")
            else:
                failure_ref = _relative_reference(root, failure.get("ref"))
                if failure_ref is None or not failure_ref.is_file():
                    errors.append(f"ledger line {line_number} lacks a failure reference")

        if not duplicate_run_id:
            seen[run_id] = record


def check_ledger(root: Path) -> List[str]:
    """Return ledger contract violations without inspecting other scopes."""

    root = root.resolve()
    path = root / "workspace" / "history" / "runs.jsonl"
    if not path.is_file():
        return ["workspace/history/runs.jsonl must be a file"]
    errors: List[str] = []
    _check_ledger(path, root, errors)
    return errors


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check the Agentic Power BI System shell.")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root to check (defaults to this checkout)",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parser().parse_args(argv)
    root = (args.root or repository_root()).resolve()
    errors = check_structure(root)
    if errors:
        print("FAIL: Agentic Power BI System checks", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"PASS: structure {root}")
    print(f"PASS: product {PRODUCT_NAME}")
    print("PASS: visible roots workspace/ examples/ docs/")
    print("PASS: stale-route and public-wording scan")
    print("PASS: curated examples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
