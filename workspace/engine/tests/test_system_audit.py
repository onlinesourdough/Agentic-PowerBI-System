from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from shutil import copytree
from typing import Callable, Tuple
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT / "workspace" / "engine"


def _load_audit():
    spec = importlib.util.spec_from_file_location(
        "agentic_powerbi_system_audit", ENGINE / "system_audit.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError("cannot load System audit")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


audit = _load_audit()


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.update(
        {"GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C"}
    )
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} failed in {root}:\n{result.stdout}{result.stderr}"
        )
    return result


def _commit_file(root: Path, relative: str, content: str, message: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _git(root, "add", relative)
    _git(root, "commit", "-m", message)


def _fixture() -> Tuple[tempfile.TemporaryDirectory, Path, Path, Path]:
    temporary = tempfile.TemporaryDirectory()
    base = Path(temporary.name)
    publisher = base / "publisher"
    copytree(
        ROOT,
        publisher,
        ignore=lambda _path, names: {
            ".git",
            "__pycache__",
            "node_modules",
        }.intersection(names),
    )
    _git(publisher, "init", "--initial-branch=main")
    _git(publisher, "config", "user.name", "System Audit Test")
    _git(publisher, "config", "user.email", "audit@example.invalid")
    _git(publisher, "add", ".")
    _git(publisher, "commit", "-m", "fixture seed")

    upstream = base / "upstream.git"
    subprocess.run(
        ["git", "init", "--bare", "--initial-branch=main", str(upstream)],
        capture_output=True,
        text=True,
        check=True,
    )
    _git(publisher, "remote", "add", "origin", str(upstream))
    _git(publisher, "push", "--set-upstream", "origin", "main")
    checkout = base / "checkout"
    subprocess.run(
        ["git", "clone", "--branch", "main", str(upstream), str(checkout)],
        capture_output=True,
        text=True,
        check=True,
    )
    _git(checkout, "config", "user.name", "System Audit Test")
    _git(checkout, "config", "user.email", "audit@example.invalid")
    return temporary, publisher, upstream, checkout


def _full_snapshot(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8") + b"\0")
        if path.is_symlink():
            digest.update(b"link\0" + os.readlink(path).encode("utf-8"))
        elif path.is_file():
            digest.update(b"file\0" + path.read_bytes())
        elif path.is_dir():
            digest.update(b"directory\0")
    return digest.hexdigest()


class _CredentialDenied(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="audit"')
        self.end_headers()

    def log_message(self, _format: str, *args: object) -> None:
        del args


class SystemAuditTests(unittest.TestCase):
    def _assert_repository_state(
        self, mutate: Callable[[Path, Path], None], expected: str
    ) -> None:
        temporary, publisher, _upstream, checkout = _fixture()
        self.addCleanup(temporary.cleanup)
        mutate(publisher, checkout)

        result = audit.audit_system(checkout, "repository")

        self.assertEqual(result.status, "FAIL", result.as_dict())
        self.assertTrue(
            any(expected in item for item in result.evidence), result.as_dict()
        )

    def test_committed_clean_clone_passes_both_scopes(self) -> None:
        temporary, _publisher, _upstream, checkout = _fixture()
        self.addCleanup(temporary.cleanup)

        result = audit.audit_system(checkout, "both")

        self.assertEqual(result.status, "PASS", result.as_dict())
        self.assertEqual(result.evidence_gaps, ())
        self.assertTrue(any("upstream" in item for item in result.evidence))
        self.assertTrue(any("workspace.history" in item for item in result.evidence))

    def test_dirty_repository_fails(self) -> None:
        self._assert_repository_state(
            lambda _publisher, checkout: (checkout / "README.md").write_text(
                "dirty fixture\n", encoding="utf-8"
            ),
            "dirty",
        )

    def test_ahead_repository_fails(self) -> None:
        self._assert_repository_state(
            lambda _publisher, checkout: _commit_file(
                checkout, "ahead.txt", "ahead\n", "ahead"
            ),
            "ahead",
        )

    def test_behind_repository_fails(self) -> None:
        def mutate(publisher: Path, _checkout: Path) -> None:
            _commit_file(publisher, "behind.txt", "behind\n", "behind")
            _git(publisher, "push", "origin", "main")

        self._assert_repository_state(mutate, "behind")

    def test_diverged_repository_fails(self) -> None:
        def mutate(publisher: Path, checkout: Path) -> None:
            _commit_file(publisher, "remote.txt", "remote\n", "remote")
            _git(publisher, "push", "origin", "main")
            _commit_file(checkout, "local.txt", "local\n", "local")

        self._assert_repository_state(mutate, "diverged")

    def test_detached_repository_fails(self) -> None:
        self._assert_repository_state(
            lambda _publisher, checkout: _git(checkout, "checkout", "--detach"),
            "detached",
        )

    def test_missing_upstream_fails(self) -> None:
        self._assert_repository_state(
            lambda _publisher, checkout: _git(
                checkout, "config", "--unset", "branch.main.remote"
            ),
            "no configured upstream",
        )

    def test_credential_denial_is_blocked(self) -> None:
        temporary, _publisher, _upstream, checkout = _fixture()
        self.addCleanup(temporary.cleanup)
        server = ThreadingHTTPServer(("127.0.0.1", 0), _CredentialDenied)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        port = server.server_address[1]
        _git(
            checkout,
            "remote",
            "set-url",
            "origin",
            f"http://127.0.0.1:{port}/private.git",
        )

        result = audit.audit_system(checkout, "repository")

        self.assertEqual(result.status, "BLOCKED", result.as_dict())
        self.assertTrue(any("upstream" in gap for gap in result.evidence_gaps))

    def test_safe_remote_identities_are_normalized(self) -> None:
        temporary, _publisher, upstream, _checkout = _fixture()
        self.addCleanup(temporary.cleanup)
        identities = (
            "https://github.com/onlinesourdough/Agentic-PowerBI-System.git",
            "ssh://git@github.com/onlinesourdough/Agentic-PowerBI-System.git",
            "git@github.com:onlinesourdough/Agentic-PowerBI-System.git",
            str(upstream),
            upstream.as_uri(),
        )

        for identity in identities:
            with self.subTest(identity=identity):
                self.assertEqual(audit._normalize_remote_identity(identity), identity)

    def test_embedded_remote_secret_never_reaches_git_arguments_or_output(self) -> None:
        temporary, _publisher, upstream, checkout = _fixture()
        self.addCleanup(temporary.cleanup)
        sentinel = "SYSTEM_AUDIT_SENTINEL_SECRET_7A4E"
        config_path = checkout / ".git/config"
        original_config = config_path.read_text(encoding="utf-8")
        unsafe_identity = f"https://audit:{sentinel}@example.invalid/private.git"
        unsafe_config = original_config.replace(str(upstream), unsafe_identity)
        self.assertTrue(unsafe_config != original_config)
        config_path.write_text(unsafe_config, encoding="utf-8")

        calls = []
        secret_reached_arguments = False
        original_runner = audit._run_git

        def recording_runner(root, args, *, git_dir=None, timeout=30):
            nonlocal secret_reached_arguments
            argument_values = [str(root), *(str(value) for value in args)]
            if git_dir is not None:
                argument_values.append(str(git_dir))
            secret_reached_arguments = secret_reached_arguments or any(
                sentinel in value for value in argument_values
            )
            calls.append(tuple(args))
            return original_runner(root, args, git_dir=git_dir, timeout=timeout)

        output = io.StringIO()
        with mock.patch.object(audit, "_run_git", side_effect=recording_runner):
            with redirect_stdout(output):
                exit_code = audit.main(
                    ["--root", str(checkout), "--scope", "repository", "--json"]
                )

        serialized = output.getvalue()
        payload = json.loads(serialized)
        network_command_ran = any(
            call and call[0] in {"ls-remote", "fetch"} for call in calls
        )
        self.assertEqual(exit_code, 2, payload)
        self.assertEqual(payload["status"], "BLOCKED", payload)
        self.assertFalse(secret_reached_arguments)
        self.assertFalse(network_command_ran)
        self.assertTrue(sentinel not in serialized)

    def test_workspace_defect_fails_and_recovery_is_discoverable(self) -> None:
        temporary, _publisher, _upstream, checkout = _fixture()
        self.addCleanup(temporary.cleanup)
        tracer = checkout / "workspace/engine/tracer.py"
        failed = subprocess.run(
            [sys.executable, str(tracer), "--root", str(checkout), "--simulate-failure"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(failed.returncode, 0, failed.stdout + failed.stderr)

        failed_audit = audit.audit_system(checkout, "workspace")

        self.assertEqual(failed_audit.status, "FAIL", failed_audit.as_dict())
        self.assertTrue(
            any("unresolved failed runs" in item for item in failed_audit.evidence)
        )

        recovered = subprocess.run(
            [sys.executable, str(tracer), "--root", str(checkout), "--recover"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
        recovered_audit = audit.audit_system(checkout, "workspace")
        self.assertEqual(recovered_audit.status, "PASS", recovered_audit.as_dict())

    def test_invalid_workspace_evidence_fails(self) -> None:
        temporary, _publisher, _upstream, checkout = _fixture()
        self.addCleanup(temporary.cleanup)
        (checkout / "workspace/history/runs.jsonl").write_text(
            "not-json\n", encoding="utf-8"
        )

        result = audit.audit_system(checkout, "workspace")

        self.assertEqual(result.status, "FAIL", result.as_dict())
        self.assertTrue(any("ledger" in item for item in result.evidence))

    def test_audit_preserves_every_audited_byte(self) -> None:
        temporary, _publisher, _upstream, checkout = _fixture()
        self.addCleanup(temporary.cleanup)
        before = _full_snapshot(checkout)

        result = subprocess.run(
            [
                sys.executable,
                str(checkout / "workspace/engine/system_audit.py"),
                "--root",
                str(checkout),
                "--scope",
                "both",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")
        self.assertEqual(_full_snapshot(checkout), before)

    def test_cli_returns_exact_status_and_structured_fields(self) -> None:
        temporary, _publisher, _upstream, checkout = _fixture()
        self.addCleanup(temporary.cleanup)
        result = subprocess.run(
            [
                sys.executable,
                str(checkout / "workspace/engine/system_audit.py"),
                "--root",
                str(checkout),
                "--scope",
                "both",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines()[0], "PASS")
        self.assertIn("evidence gaps:", result.stdout)
        self.assertIn("next action:", result.stdout)


if __name__ == "__main__":
    unittest.main()
