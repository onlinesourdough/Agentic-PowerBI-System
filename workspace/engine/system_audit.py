#!/usr/bin/env python3
"""Strictly read-only accumulated-state audit for Agentic Power BI System."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import urlsplit, urlunsplit


# Loading the shared checker must not create ignored bytecode in the audited
# checkout. The route is read-only even for files Git status would hide.
sys.dont_write_bytecode = True


SCOPES = ("repository", "workspace", "both")
STATUSES = ("PASS", "FAIL", "BLOCKED")
WORKSPACE_TRUTH = (
    "workspace/PROJECT-BRIEF.md",
    "workspace/briefs",
    "workspace/models",
    "workspace/reports",
    "workspace/state",
    "workspace/runs",
    "workspace/history/runs.jsonl",
    "workspace/learning",
)
SSH_USER_RE = re.compile(r"^[A-Za-z0-9._-]+$")
SCP_REMOTE_RE = re.compile(
    r"^(?:(?P<user>[A-Za-z0-9._-]+)@)?"
    r"(?P<host>[A-Za-z0-9.-]+):(?P<path>[^\s]+)$"
)


def _load_checks():
    path = Path(__file__).with_name("checks.py")
    spec = importlib.util.spec_from_file_location("system_audit_checks", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load existing checks from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checks = _load_checks()


@dataclass(frozen=True)
class AuditResult:
    status: str
    scope: str
    evidence: Tuple[str, ...]
    evidence_gaps: Tuple[str, ...]
    next_action: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "scope": self.scope,
            "evidence": list(self.evidence),
            "evidence_gaps": list(self.evidence_gaps),
            "next_action": self.next_action,
        }


@dataclass(frozen=True)
class GitSnapshot:
    refs_digest: str
    index_digest: str
    worktree_digest: str
    status: str


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run_git(
    root: Path,
    args: Sequence[str],
    *,
    git_dir: Optional[Path] = None,
    timeout: int = 30,
) -> subprocess.CompletedProcess[str]:
    command = ["git"]
    if git_dir is not None:
        command.append(f"--git-dir={git_dir}")
    else:
        command.extend(("-C", str(root)))
    command.extend(args)
    environment = os.environ.copy()
    environment.update(
        {
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
            "LC_ALL": "C",
        }
    )
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            env=environment,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(command, 124, "", "Git command timed out")
    except OSError as exc:
        return subprocess.CompletedProcess(
            command, 127, "", f"Git command unavailable: {exc}"
        )


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _normalize_remote_identity(value: str) -> Optional[str]:
    """Return a credential-free Git identity or reject it without disclosure."""

    identity = value.strip()
    if not identity or any(ord(character) < 32 for character in identity):
        return None
    try:
        parsed = urlsplit(identity)
        scheme = parsed.scheme.lower()
        if scheme in {"http", "https"}:
            if (
                parsed.username is not None
                or parsed.password is not None
                or parsed.hostname is None
                or parsed.query
                or parsed.fragment
            ):
                return None
            parsed.port
            return urlunsplit((scheme, parsed.netloc, parsed.path, "", ""))
        if scheme == "ssh":
            if (
                parsed.password is not None
                or parsed.hostname is None
                or parsed.query
                or parsed.fragment
                or (parsed.username and not SSH_USER_RE.fullmatch(parsed.username))
            ):
                return None
            parsed.port
            return urlunsplit((scheme, parsed.netloc, parsed.path, "", ""))
        if scheme == "file":
            if (
                parsed.username is not None
                or parsed.password is not None
                or parsed.hostname not in {None, "", "localhost"}
                or parsed.query
                or parsed.fragment
                or not parsed.path
            ):
                return None
            return urlunsplit((scheme, parsed.netloc, parsed.path, "", ""))
        if scheme:
            return None
    except ValueError:
        return None

    scp_match = SCP_REMOTE_RE.fullmatch(identity)
    if scp_match:
        return identity
    if ":" not in identity and "@" not in identity and "?" not in identity:
        return identity
    return None


def _git_snapshot(root: Path) -> GitSnapshot:
    head = _run_git(root, ("rev-parse", "HEAD"))
    symbolic_head = _run_git(root, ("symbolic-ref", "--quiet", "HEAD"))
    refs = _run_git(root, ("for-each-ref", "--format=%(refname)%00%(objectname)"))
    status = _run_git(
        root,
        ("status", "--porcelain=v2", "-z", "--untracked-files=all"),
    )
    index_path_result = _run_git(root, ("rev-parse", "--git-path", "index"))
    for label, result in (("HEAD", head), ("refs", refs), ("status", status)):
        if result.returncode != 0:
            raise RuntimeError(f"cannot snapshot Git {label}: {result.stderr.strip()}")
    if index_path_result.returncode != 0:
        raise RuntimeError(
            f"cannot locate Git index: {index_path_result.stderr.strip()}"
        )
    index_path = Path(index_path_result.stdout.strip())
    if not index_path.is_absolute():
        index_path = root / index_path
    index_bytes = index_path.read_bytes() if index_path.is_file() else b"<missing>"
    refs_bytes = (head.stdout + symbolic_head.stdout + refs.stdout).encode("utf-8")
    status_bytes = status.stdout.encode("utf-8")
    return GitSnapshot(
        refs_digest=_digest(refs_bytes),
        index_digest=_digest(index_bytes),
        worktree_digest=_digest(status_bytes),
        status=status.stdout,
    )


def _workspace_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in WORKSPACE_TRUTH:
        path = root / relative
        digest.update(relative.encode("utf-8") + b"\0")
        if not path.exists() and not path.is_symlink():
            digest.update(b"missing\0")
            continue
        candidates = [path]
        if path.is_dir():
            candidates = sorted(path.rglob("*"))
        for candidate in candidates:
            item_relative = candidate.relative_to(root).as_posix()
            digest.update(item_relative.encode("utf-8") + b"\0")
            if candidate.is_symlink():
                digest.update(b"link\0" + os.readlink(candidate).encode("utf-8"))
            elif candidate.is_file():
                digest.update(b"file\0" + candidate.read_bytes())
            elif candidate.is_dir():
                digest.update(b"directory\0")
    return digest.hexdigest()


def _repository_contract_paths() -> Tuple[str, ...]:
    paths = []
    for relative in checks.REQUIRED_PATHS:
        if relative.startswith("workspace/") and not relative.startswith(
            "workspace/engine/"
        ):
            continue
        path = Path(relative)
        if path.suffix or path.name == "AGENTS.md":
            paths.append(relative)
    return tuple(paths)


def _record_contract_surface(
    root: Path,
    evidence: List[str],
    gaps: List[str],
    defects: List[str],
) -> None:
    missing = []
    unreadable = []
    for relative in _repository_contract_paths():
        path = root / relative
        if not path.is_file():
            missing.append(relative)
            continue
        try:
            path.read_bytes()
        except OSError:
            unreadable.append(relative)
    if missing:
        defects.append("repository contract paths missing: " + ", ".join(missing))
    if unreadable:
        gaps.append(
            "repository contract paths unreadable: " + ", ".join(unreadable)
        )
    if not missing and not unreadable:
        evidence.append(
            "repository.contract: primary route, Power BI domain audit, "
            "validation, System audit, engine, and tests are readable"
        )


def _live_relation(
    root: Path,
    local_sha: str,
    remote_identity: str,
    merge_ref: str,
) -> Tuple[Optional[str], Optional[str]]:
    live = _run_git(root, ("ls-remote", "--exit-code", remote_identity, merge_ref))
    if live.returncode == 2:
        return None, f"live upstream ref is missing: {merge_ref}"
    if live.returncode != 0:
        return None, (
            "live upstream evidence unavailable "
            "(read access denied or network unavailable)"
        )
    lines = [line.split() for line in live.stdout.splitlines() if line.strip()]
    matches = [parts[0] for parts in lines if len(parts) == 2 and parts[1] == merge_ref]
    if len(matches) != 1:
        return None, f"live upstream returned no unique value for {merge_ref}"
    live_sha = matches[0]
    if live_sha == local_sha:
        return "equal", live_sha

    with tempfile.TemporaryDirectory(prefix="agentic-powerbi-audit-") as temporary:
        comparison = Path(temporary) / "comparison.git"
        initialized = _run_git(
            root,
            ("init", "--bare", "--quiet", str(comparison)),
        )
        if initialized.returncode != 0:
            return None, "temporary comparison database could not be initialized"
        local_fetch = _run_git(
            root,
            (
                "fetch",
                "--quiet",
                "--no-tags",
                "--no-write-fetch-head",
                str(root),
                f"+{local_sha}:refs/audit/local",
            ),
            git_dir=comparison,
        )
        live_fetch = _run_git(
            root,
            (
                "fetch",
                "--quiet",
                "--no-tags",
                "--no-write-fetch-head",
                remote_identity,
                f"+{merge_ref}:refs/audit/live",
            ),
            git_dir=comparison,
        )
        if local_fetch.returncode != 0 or live_fetch.returncode != 0:
            return None, "commit ancestry could not be loaded into temporary storage"
        fetched_live = _run_git(
            root, ("rev-parse", "refs/audit/live"), git_dir=comparison
        )
        if fetched_live.returncode != 0 or fetched_live.stdout.strip() != live_sha:
            return None, "live upstream changed while the audit was running"
        local_ancestor = _run_git(
            root,
            ("merge-base", "--is-ancestor", "refs/audit/local", "refs/audit/live"),
            git_dir=comparison,
        )
        live_ancestor = _run_git(
            root,
            ("merge-base", "--is-ancestor", "refs/audit/live", "refs/audit/local"),
            git_dir=comparison,
        )
        if local_ancestor.returncode == 0:
            return "behind", live_sha
        if live_ancestor.returncode == 0:
            return "ahead", live_sha
        if local_ancestor.returncode == 1 and live_ancestor.returncode == 1:
            return "diverged", live_sha
        return None, "commit ancestry comparison failed"


def _audit_repository(
    root: Path,
    evidence: List[str],
    gaps: List[str],
    defects: List[str],
) -> Optional[GitSnapshot]:
    top = _run_git(root, ("rev-parse", "--show-toplevel"))
    if top.returncode != 0:
        if top.returncode in {124, 127}:
            gaps.append("repository identity evidence unavailable: " + top.stderr)
        else:
            defects.append("selected repository scope is not a Git checkout")
        return None
    actual_top = Path(top.stdout.strip()).resolve()
    if actual_top != root:
        defects.append(f"selected root is not the Git top-level: {actual_top}")
        return None
    try:
        before = _git_snapshot(root)
    except (OSError, RuntimeError) as exc:
        gaps.append(f"repository no-mutation baseline unavailable: {exc}")
        return None

    head = _run_git(root, ("rev-parse", "HEAD"))
    branch = _run_git(root, ("symbolic-ref", "--quiet", "--short", "HEAD"))
    local_sha = head.stdout.strip()
    evidence.append(f"repository.identity: {root} at {local_sha}")
    _record_contract_surface(root, evidence, gaps, defects)

    if before.status:
        defects.append("repository worktree or index is dirty")
    else:
        evidence.append("repository.state: index and worktree are clean")

    if branch.returncode != 0:
        defects.append("repository HEAD is detached")
        return before
    branch_name = branch.stdout.strip()
    remote = _run_git(root, ("config", "--get", f"branch.{branch_name}.remote"))
    merge = _run_git(root, ("config", "--get", f"branch.{branch_name}.merge"))
    if remote.returncode != 0 or merge.returncode != 0:
        defects.append(f"branch {branch_name} has no configured upstream")
        return before
    remote_name = remote.stdout.strip()
    merge_ref = merge.stdout.strip()
    if not remote_name or remote_name == "." or not merge_ref.startswith("refs/heads/"):
        defects.append(f"branch {branch_name} has no live remote branch upstream")
        return before
    remote_url = _run_git(root, ("remote", "get-url", remote_name))
    if remote_url.returncode != 0 or not remote_url.stdout.strip():
        defects.append(f"configured upstream remote {remote_name} is unavailable")
        return before

    remote_identity = _normalize_remote_identity(remote_url.stdout)
    if remote_identity is None:
        gaps.append(
            "live upstream remote identity is unsafe or contains embedded credentials"
        )
        return before

    relation, detail = _live_relation(
        root, local_sha, remote_identity, merge_ref
    )
    if relation is None:
        if detail and detail.startswith("live upstream ref is missing"):
            defects.append(detail)
        else:
            gaps.append(detail or "live upstream relation is unavailable")
        return before
    evidence.append(
        f"repository.upstream: {branch_name} is {relation} to live "
        f"{remote_name}/{merge_ref.removeprefix('refs/heads/')} at {detail}"
    )
    if relation != "equal":
        defects.append(f"repository is {relation} relative to its live upstream")
    return before


def _read_ledger_records(path: Path) -> List[Dict[str, Any]]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if isinstance(value, dict):
            records.append(value)
    return records


def _audit_workspace(
    root: Path, evidence: List[str], gaps: List[str], defects: List[str]
) -> Optional[str]:
    try:
        before = _workspace_digest(root)
    except OSError as exc:
        gaps.append(f"workspace no-mutation baseline unavailable: {exc}")
        return None

    missing = [relative for relative in WORKSPACE_TRUTH if not (root / relative).exists()]
    if missing:
        defects.append("workspace truth paths missing: " + ", ".join(missing))
        return before
    ledger_errors = checks.check_ledger(root)
    for error in ledger_errors:
        target = gaps if "cannot be read" in error else defects
        target.append(f"workspace ledger: {error}")
    ledger = root / "workspace/history/runs.jsonl"
    if ledger_errors:
        return before
    try:
        records = _read_ledger_records(ledger)
    except (OSError, UnicodeError, ValueError) as exc:
        defects.append(f"workspace ledger cannot be inspected: {exc}")
        return before

    run_ids = {record.get("run_id") for record in records}
    run_directories = {
        path.name
        for path in (root / "workspace/runs").iterdir()
        if not path.name.startswith(".") and path.is_dir()
    }
    orphaned = sorted(run_directories.difference(run_ids))
    if orphaned:
        defects.append("workspace run directories lack ledger records: " + ", ".join(orphaned))
    missing_run_directories = sorted(
        str(run_id) for run_id in run_ids if run_id not in run_directories
    )
    if missing_run_directories:
        defects.append(
            "workspace ledger records lack run directories: "
            + ", ".join(missing_run_directories)
        )

    failed = {
        record.get("run_id")
        for record in records
        if record.get("status") == "failed"
    }
    recovered = {
        recovery.get("from_run_id")
        for record in records
        for recovery in [record.get("recovery")]
        if isinstance(recovery, dict)
    }
    unresolved = sorted(str(run_id) for run_id in failed.difference(recovered))
    if unresolved:
        defects.append("workspace has unresolved failed runs: " + ", ".join(unresolved))
    evidence.append(
        "workspace.history: "
        f"{len(records)} ledger record(s), {len(failed)} failed, "
        f"{len(recovered)} recovered, {len(unresolved)} unresolved"
    )
    if not orphaned and not missing_run_directories:
        evidence.append("workspace.proof: run/history references are discoverable")
    return before


def audit_system(root: Path, scope: str) -> AuditResult:
    if scope not in SCOPES:
        raise ValueError(f"scope must be one of: {', '.join(SCOPES)}")
    root = root.resolve()
    evidence: List[str] = []
    gaps: List[str] = []
    defects: List[str] = []

    git_before: Optional[GitSnapshot] = None
    workspace_before: Optional[str] = None
    if scope in {"repository", "both"}:
        git_before = _audit_repository(root, evidence, gaps, defects)
    if scope in {"workspace", "both"}:
        workspace_before = _audit_workspace(root, evidence, gaps, defects)
    if scope == "both":
        defects.extend(
            f"deterministic validation: {error}"
            for error in checks.check_structure(root)
        )

    if git_before is not None:
        try:
            git_after = _git_snapshot(root)
            if git_after != git_before:
                defects.append("audit changed repository refs, index, or worktree state")
            else:
                evidence.append("repository.no-mutation: refs, index, and worktree preserved")
        except (OSError, RuntimeError) as exc:
            gaps.append(f"repository no-mutation proof unavailable after audit: {exc}")
    if workspace_before is not None:
        try:
            workspace_after = _workspace_digest(root)
            if workspace_after != workspace_before:
                defects.append("audit changed accumulated workspace truth")
            else:
                evidence.append("workspace.no-mutation: accumulated truth preserved")
        except OSError as exc:
            gaps.append(f"workspace no-mutation proof unavailable after audit: {exc}")

    if defects:
        status = "FAIL"
        evidence.extend(f"defect: {defect}" for defect in defects)
        next_action = _next_action(defects[0], blocked=False)
    elif gaps:
        status = "BLOCKED"
        next_action = _next_action(gaps[0], blocked=True)
    else:
        status = "PASS"
        next_action = "No repair action; schedule the next periodic System audit."
    assert status in STATUSES
    return AuditResult(
        status=status,
        scope=scope,
        evidence=tuple(evidence),
        evidence_gaps=tuple(gaps),
        next_action=next_action,
    )


def _next_action(finding: str, *, blocked: bool) -> str:
    if blocked:
        if "upstream" in finding or "ancestry" in finding:
            return "Restore read-only upstream access, then rerun this audit."
        return "Restore the missing read-only evidence, then rerun this audit."
    if "dirty" in finding:
        return "Route the pending change through per-change Review or restore a clean checkout, then rerun."
    if any(word in finding for word in ("ahead", "behind", "diverged", "detached", "upstream")):
        return "Route repository synchronization or branch repair through Build/Review, then rerun."
    if "failed runs" in finding:
        return "Route the unresolved run to its owning Build/Review lifecycle, preserve its evidence, then rerun."
    return "Route the smallest cited repair through Build and per-change Review, then rerun."


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the read-only periodic Agentic Power BI System audit."
    )
    parser.add_argument(
        "--root", type=Path, default=None, help="exact repository root to audit"
    )
    parser.add_argument("--scope", choices=SCOPES, required=True)
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parser().parse_args(argv)
    result = audit_system(args.root or repository_root(), args.scope)
    if args.json:
        print(json.dumps(result.as_dict(), indent=2, sort_keys=True))
    else:
        print(result.status)
        print(f"scope: {result.scope}")
        print("evidence:")
        for item in result.evidence:
            print(f"- {item}")
        print("evidence gaps:")
        if result.evidence_gaps:
            for item in result.evidence_gaps:
                print(f"- {item}")
        else:
            print("- none")
        print(f"next action: {result.next_action}")
    return {"PASS": 0, "FAIL": 1, "BLOCKED": 2}[result.status]


if __name__ == "__main__":
    raise SystemExit(main())
