#!/usr/bin/env python3
"""Deterministic filesystem proof tracer for the Agentic Power BI System.

The tracer is a small local workflow, not a framework. It inspects the local
run ledger, writes one run directory, appends one ledger record, and promotes a
standalone example only when explicitly requested.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_TIMESTAMP = "2026-01-01T00:00:00Z"
PRODUCT_NAME = "Agentic Power BI System"
ROUTE = "system-proof"
INPUT_REF = "fixture://agentic-powerbi-system/system-proof"
DECISION_REF = "workspace/PROJECT-BRIEF.md"
RUN_ID_PATTERN = re.compile(r"^run-(\d{4,})$")
SPECIALIST_ROUTES = (
    "powerbi",
    "pbip",
    "dax",
    "report",
    "fabric",
    "validation",
)


class TraceError(RuntimeError):
    """Raised when the local trace cannot preserve its evidence."""


@dataclass(frozen=True)
class TraceResult:
    run_id: str
    status: str
    output_path: Path
    proof_path: Path
    ledger_path: Path
    example_path: Optional[Path]
    previous_run_id: Optional[str]
    previous_run_relation: Optional[str]
    inspected_prior_runs: int
    failure_path: Optional[Path]
    recovery_path: Optional[Path]


def repository_root() -> Path:
    """Return the repository root derived from this file, not the cwd."""

    return Path(__file__).resolve().parents[2]


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _write_json(path: Path, value: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _read_ledger(ledger_path: Path) -> List[Dict[str, Any]]:
    if not ledger_path.exists():
        return []

    records: List[Dict[str, Any]] = []
    for line_number, line in enumerate(
        ledger_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TraceError(
                f"ledger line {line_number} is not valid JSON: {exc.msg}"
            ) from exc
        if not isinstance(record, dict):
            raise TraceError(f"ledger line {line_number} must be an object")
        records.append(record)
    return records


def _next_run_id(records: List[Dict[str, Any]]) -> str:
    numbers = []
    for record in records:
        match = RUN_ID_PATTERN.match(str(record.get("run_id", "")))
        if match:
            numbers.append(int(match.group(1)))
    return f"run-{(max(numbers, default=0) + 1):04d}"


def _append_ledger(ledger_path: Path, record: Dict[str, Any]) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def _promote_example(
    root: Path,
    run_id: str,
    output: Dict[str, Any],
    proof: Dict[str, Any],
) -> Path:
    """Write a self-contained proof only after explicit curation."""

    example_dir = root / "examples" / "powerbi-system-proof" / run_id
    example_proof = {
        "assertions": proof["assertions"],
        "curated": True,
        "example": "powerbi-system-proof",
        "product": PRODUCT_NAME,
        "result": output["result"],
        "route": output["route"],
        "source_proof_ref": proof["proof_ref"],
        "source_run_id": run_id,
        "specialist_routes": output["specialist_routes"],
        "status": output["status"],
    }
    _write_json(example_dir / "proof.json", example_proof)
    (example_dir / "README.md").write_text(
        "# Curated Agentic Power BI System proof\n\n"
        "This directory is an intentionally curated, standalone proof of one "
        "deterministic System route. It contains fixture evidence only; it "
        "does not claim a live Power BI model or service result.\n\n"
        f"- Product: `{PRODUCT_NAME}`\n"
        f"- Run: `{run_id}`\n"
        f"- Route: `{output['route']}`\n"
        f"- Status: `{output['status']}`\n"
        f"- Result: {output['result']}\n\n"
        "The complete assertions are in `proof.json`. This example is a "
        "readable proof artifact; it is not an executable dependency.\n",
        encoding="utf-8",
    )
    return example_dir


def trace_once(
    root: Path,
    *,
    promote_example: bool = False,
    simulate_failure: bool = False,
    recover: bool = False,
    timestamp: str = DEFAULT_TIMESTAMP,
) -> TraceResult:
    """Run one deterministic route and preserve its evidence.

    ``recover`` consumes the latest relevant failed run. The explicit root
    keeps the workflow testable in a fresh temporary copy.
    """

    root = root.resolve()
    if not root.is_dir():
        raise TraceError(f"repository root is not a directory: {root}")
    if simulate_failure and recover:
        raise TraceError("choose either --simulate-failure or --recover")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", timestamp):
        raise TraceError("timestamp must use UTC form YYYY-MM-DDTHH:MM:SSZ")

    ledger_path = root / "workspace" / "history" / "runs.jsonl"
    records = _read_ledger(ledger_path)
    relevant = [
        record for record in records if record.get("input_ref") == INPUT_REF
    ]
    recovered_failures = set()
    for record in relevant:
        recovery = record.get("recovery")
        if isinstance(recovery, dict) and recovery.get("from_run_id"):
            recovered_failures.add(recovery.get("from_run_id"))
    failed_prior = next(
        (
            record
            for record in reversed(relevant)
            if record.get("status") == "failed"
            and record.get("run_id") not in recovered_failures
        ),
        None,
    )
    if recover and failed_prior is None:
        raise TraceError("--recover requires a previous unresolved failed System run")

    if recover:
        previous_run_id = failed_prior.get("run_id")
    else:
        previous = relevant[-1] if relevant else None
        previous_run_id = previous.get("run_id") if previous else None

    if previous_run_id is None:
        previous_run_relation = None
    elif recover:
        previous_run_relation = "recovery"
    else:
        previous_run_relation = "predecessor"

    run_id = _next_run_id(records)
    run_dir = root / "workspace" / "runs" / run_id
    if run_dir.exists():
        raise TraceError(f"run directory already exists: {_relative(run_dir, root)}")
    run_dir.mkdir(parents=True)

    output_path = run_dir / "output.json"
    proof_path = run_dir / "proof.json"
    failure_path: Optional[Path] = None
    recovery_path: Optional[Path] = None

    input_record = {
        "decision_ref": DECISION_REF,
        "input_ref": INPUT_REF,
        "request_kind": "deterministic-system-proof",
        "route": ROUTE,
        "specialist_routes": list(SPECIALIST_ROUTES),
        "system": PRODUCT_NAME,
    }
    _write_json(run_dir / "input.json", input_record)

    if simulate_failure:
        status = "failed"
        output = {
            "audience": "Power BI model and report owners",
            "decision": "Confirm that the decision-first route preserves its evidence.",
            "previous_run_id": previous_run_id,
            "previous_run_relation": previous_run_relation,
            "result": "The deterministic System route stopped at its recoverable fixture.",
            "route": ROUTE,
            "run_id": run_id,
            "specialist_routes": list(SPECIALIST_ROUTES),
            "status": status,
            "system": PRODUCT_NAME,
        }
        failure_path = run_dir / "failure.json"
        failure = {
            "code": "SYSTEM_PROOF_FAILURE",
            "message": "The deterministic recoverable failure fixture was requested.",
            "recoverable": True,
            "run_id": run_id,
        }
        _write_json(failure_path, failure)
        recovery: Optional[Dict[str, Any]] = None
        assertions = [
            "the primary System route selected the deterministic fixture",
            "the run recorded a deterministic recoverable failure artifact",
            "the failed run remained available for a later recovery",
        ]
    else:
        status = "succeeded"
        recovered_from = failed_prior.get("run_id") if recover and failed_prior else None
        output = {
            "audience": "Power BI model and report owners",
            "decision": "Confirm that the decision-first route preserves its evidence.",
            "previous_run_id": previous_run_id,
            "previous_run_relation": previous_run_relation,
            "recovered_from": recovered_from,
            "result": "The Agentic Power BI System route completed deterministically without live-service claims.",
            "route": ROUTE,
            "run_id": run_id,
            "specialist_routes": list(SPECIALIST_ROUTES),
            "status": status,
            "system": PRODUCT_NAME,
        }
        recovery = None
        if recover:
            recovery_path = run_dir / "recovery.json"
            recovery = {
                "action": "reroute the System proof after its recorded failure",
                "from_run_id": failed_prior.get("run_id"),
                "run_id": run_id,
                "status": "recovered",
            }
            _write_json(recovery_path, recovery)
            assertions = [
                "the primary System route inspected a prior failed run",
                "the route completed after the recorded failure",
                "recovery evidence points to the failed predecessor",
            ]
        else:
            assertions = [
                "the primary System route inspected the local run ledger",
                "Power BI specialist route references were recorded",
                "output and proof were written under workspace/runs",
                "the append-only ledger received one run record",
            ]

    _write_json(output_path, output)
    proof = {
        "assertions": assertions,
        "curated_example_ref": (
            f"examples/powerbi-system-proof/{run_id}/" if promote_example else None
        ),
        "decision_ref": DECISION_REF,
        "failure_ref": _relative(failure_path, root) if failure_path else None,
        "input_ref": INPUT_REF,
        "ledger_ref": f"workspace/history/runs.jsonl#{run_id}",
        "output_ref": _relative(output_path, root),
        "previous_run_id": previous_run_id,
        "previous_run_relation": previous_run_relation,
        "proof_ref": _relative(proof_path, root),
        "recovery_ref": _relative(recovery_path, root) if recovery_path else None,
        "route": ROUTE,
        "run_id": run_id,
        "specialist_routes": list(SPECIALIST_ROUTES),
        "status": status,
        "system": PRODUCT_NAME,
    }
    _write_json(proof_path, proof)

    ledger_record = {
        "failure": (
            {
                "code": "SYSTEM_PROOF_FAILURE",
                "ref": _relative(failure_path, root),
            }
            if failure_path
            else None
        ),
        "finished_at": timestamp,
        "input_ref": INPUT_REF,
        "output_ref": _relative(output_path, root),
        "previous_run_id": previous_run_id,
        "previous_run_relation": previous_run_relation,
        "proof_ref": _relative(proof_path, root),
        "recovery": (
            {
                "from_run_id": failed_prior.get("run_id"),
                "ref": _relative(recovery_path, root),
            }
            if recovery_path and failed_prior
            else None
        ),
        "route": ROUTE,
        "run_id": run_id,
        "specialist_routes": list(SPECIALIST_ROUTES),
        "started_at": timestamp,
        "status": status,
        "system": PRODUCT_NAME,
    }
    _append_ledger(ledger_path, ledger_record)

    example_path = None
    if promote_example:
        example_path = _promote_example(root, run_id, output, proof)

    return TraceResult(
        run_id=run_id,
        status=status,
        output_path=output_path,
        proof_path=proof_path,
        ledger_path=ledger_path,
        example_path=example_path,
        previous_run_id=previous_run_id,
        previous_run_relation=previous_run_relation,
        inspected_prior_runs=len(relevant),
        failure_path=failure_path,
        recovery_path=recovery_path,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the deterministic Agentic Power BI System proof."
    )
    parser.add_argument(
        "--promote-example",
        action="store_true",
        help="intentionally curate this run into examples/",
    )
    parser.add_argument(
        "--simulate-failure",
        action="store_true",
        help="record the deterministic recoverable failure path",
    )
    parser.add_argument(
        "--recover",
        action="store_true",
        help="recover the latest failed System proof run",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root to trace (defaults to this checkout)",
    )
    parser.add_argument(
        "--timestamp",
        default=DEFAULT_TIMESTAMP,
        help=f"UTC timestamp (default: {DEFAULT_TIMESTAMP})",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _parser().parse_args(argv)
    root = (args.root or repository_root()).resolve()
    try:
        result = trace_once(
            root,
            promote_example=args.promote_example,
            simulate_failure=args.simulate_failure,
            recover=args.recover,
            timestamp=args.timestamp,
        )
    except TraceError as exc:
        print(f"trace failed: {exc}", file=sys.stderr)
        return 1

    print(f"system: {PRODUCT_NAME}")
    print(f"route: {ROUTE}")
    print(f"inspected_prior_runs: {result.inspected_prior_runs}")
    print(f"run: {result.run_id}")
    print(f"status: {result.status}")
    print(f"output: {_relative(result.output_path, root)}")
    print(f"proof: {_relative(result.proof_path, root)}")
    print(f"ledger: {_relative(result.ledger_path, root)}")
    if result.failure_path:
        print(f"failure: {_relative(result.failure_path, root)}")
    if result.recovery_path:
        print(f"recovery: {_relative(result.recovery_path, root)}")
    if result.example_path:
        print(f"curated_example: {_relative(result.example_path, root)}/")
    else:
        print("curated_example: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
