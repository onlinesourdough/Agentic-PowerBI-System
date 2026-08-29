from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree, rmtree


ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT / "workspace" / "engine"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


checks = _load_module("agentic_powerbi_checks", ENGINE / "checks.py")
tracer = _load_module("agentic_powerbi_tracer", ENGINE / "tracer.py")


class AgenticPowerBISystemTests(unittest.TestCase):
    def test_repository_shell_is_canonical(self) -> None:
        self.assertEqual(checks.check_structure(ROOT), [])
        self.assertTrue((ROOT / "workspace" / "history" / "runs.jsonl").is_file())

    def test_required_path_is_enforced(self) -> None:
        temporary, root = self._temporary_seed()
        self.addCleanup(temporary.cleanup)
        (root / ".agents" / "skills" / "validation" / "SKILL.md").unlink()

        errors = checks.check_structure(root)

        self.assertIn(
            "required path is missing: .agents/skills/validation/SKILL.md",
            errors,
        )
        self.assertIn(
            "skill folder is missing a regular payload: "
            ".agents/skills/validation/SKILL.md",
            errors,
        )

    def _temporary_skill_root(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name) / "repository"
        (root / ".agents").mkdir(parents=True)
        copytree(ROOT / ".agents" / "skills", root / ".agents" / "skills")
        return temporary, root

    def test_skill_shelf_is_regular_and_complete(self) -> None:
        self.assertEqual(checks.check_skill_shelf(ROOT), [])

    def test_skill_frontmatter_and_folder_name_are_enforced(self) -> None:
        cases = (
            ("malformed", lambda text: text.removeprefix("---\n"), "malformed frontmatter"),
            (
                "name mismatch",
                lambda text: text.replace("name: powerbi", "name: other-powerbi", 1),
                "skill folder and frontmatter name disagree",
            ),
        )
        for label, mutate, expected in cases:
            with self.subTest(label=label):
                temporary, root = self._temporary_skill_root()
                self.addCleanup(temporary.cleanup)
                payload = root / ".agents/skills/powerbi/SKILL.md"
                payload.write_text(
                    mutate(payload.read_text(encoding="utf-8")), encoding="utf-8"
                )

                errors = checks.check_skill_shelf(root)

                self.assertTrue(any(expected in error for error in errors), errors)

    def test_skill_shelf_rejects_nesting_direct_files_and_symlinks(self) -> None:
        for defect in ("nested", "direct-file", "symlink"):
            with self.subTest(defect=defect):
                temporary, root = self._temporary_skill_root()
                self.addCleanup(temporary.cleanup)
                shelf = root / ".agents/skills"
                if defect == "nested":
                    nested = shelf / "powerbi/nested/SKILL.md"
                    nested.parent.mkdir()
                    nested.write_text("nested\n", encoding="utf-8")
                    expected = "nested skill payload is not allowed"
                elif defect == "direct-file":
                    (shelf / "NOTES.md").write_text("unexpected\n", encoding="utf-8")
                    expected = "unexpected direct skill shelf file"
                else:
                    (shelf / "linked-index").symlink_to("README.md")
                    expected = "skill tree symlink is not allowed"

                errors = checks.check_skill_shelf(root)

                self.assertTrue(any(expected in error for error in errors), errors)

    def test_skill_index_rejects_missing_duplicate_and_unknown_entries(self) -> None:
        cases = (
            (
                "missing",
                lambda text: "\n".join(
                    line for line in text.splitlines() if "/dax/SKILL.md`" not in line
                )
                + "\n",
                "skill shelf index is missing entry: dax",
            ),
            (
                "duplicate",
                lambda text: text
                + "\n- `.agents/skills/dax/SKILL.md`: duplicate test entry.\n",
                "skill shelf index repeats entry: dax",
            ),
            (
                "unknown",
                lambda text: text
                + "\n- `.agents/skills/unknown/SKILL.md`: unknown test entry.\n",
                "skill shelf index contains unknown entry: unknown",
            ),
        )
        for label, mutate, expected in cases:
            with self.subTest(label=label):
                temporary, root = self._temporary_skill_root()
                self.addCleanup(temporary.cleanup)
                index = root / ".agents/skills/README.md"
                index.write_text(
                    mutate(index.read_text(encoding="utf-8")), encoding="utf-8"
                )

                errors = checks.check_skill_shelf(root)

                self.assertIn(expected, errors)

    def _temporary_seed(self, source_root: Path = ROOT):
        temporary = tempfile.TemporaryDirectory()
        temp_root = Path(temporary.name) / "seed"
        copytree(
            source_root,
            temp_root,
            ignore=lambda _path, names: {".git", "__pycache__"}.intersection(names),
        )
        self._reset_operational_state(temp_root)
        return temporary, temp_root

    @staticmethod
    def _reset_operational_state(root: Path) -> None:
        history = root / "workspace" / "history" / "runs.jsonl"
        history.write_text("", encoding="utf-8")
        for relative in (
            "workspace/runs",
            "workspace/learning",
            "workspace/state",
            "examples",
        ):
            directory = root / relative
            if not directory.is_dir():
                continue
            for child in directory.iterdir():
                if child.name == ".gitkeep":
                    continue
                if child.is_dir() and not child.is_symlink():
                    rmtree(child)
                else:
                    child.unlink()

    def test_success_route_appends_then_promotes(self) -> None:
        temporary, root = self._temporary_seed()
        self.addCleanup(temporary.cleanup)

        result = tracer.trace_once(root, promote_example=True)

        self.assertEqual(result.run_id, "run-0001")
        self.assertEqual(result.status, "succeeded")
        self.assertIsNone(result.previous_run_id)
        self.assertIsNone(result.previous_run_relation)
        self.assertTrue(result.output_path.is_file())
        self.assertTrue(result.proof_path.is_file())
        self.assertTrue(result.example_path is not None and result.example_path.is_dir())
        self.assertEqual(checks.check_structure(root), [])
        ledger_lines = (root / "workspace/history/runs.jsonl").read_text().splitlines()
        self.assertEqual(len([line for line in ledger_lines if line.strip()]), 1)
        record = json.loads(ledger_lines[-1])
        self.assertEqual(record["run_id"], "run-0001")
        self.assertEqual(record["input_ref"], tracer.INPUT_REF)
        self.assertEqual(record["status"], "succeeded")
        self.assertIsNone(record["failure"])
        self.assertIsNone(record["recovery"])
        proof = json.loads(result.proof_path.read_text())
        self.assertEqual(
            proof["curated_example_ref"],
            "examples/powerbi-system-proof/run-0001/",
        )
        example_proof = json.loads((result.example_path / "proof.json").read_text())
        self.assertTrue(example_proof["curated"])
        self.assertEqual(example_proof["product"], tracer.PRODUCT_NAME)

    def test_second_run_inspects_predecessor_and_history_is_append_only(self) -> None:
        temporary, root = self._temporary_seed()
        self.addCleanup(temporary.cleanup)

        first = tracer.trace_once(root)
        second = tracer.trace_once(root)

        self.assertEqual(first.run_id, "run-0001")
        self.assertEqual(second.run_id, "run-0002")
        self.assertEqual(second.previous_run_id, "run-0001")
        self.assertEqual(second.previous_run_relation, "predecessor")
        ledger_lines = [
            line
            for line in (root / "workspace/history/runs.jsonl").read_text().splitlines()
            if line.strip()
        ]
        self.assertEqual(len(ledger_lines), 2)
        self.assertEqual(json.loads(ledger_lines[1])["previous_run_id"], "run-0001")
        self.assertEqual(
            json.loads(ledger_lines[1])["previous_run_relation"], "predecessor"
        )

    def test_failure_and_recovery_evidence_are_linked(self) -> None:
        temporary, root = self._temporary_seed()
        self.addCleanup(temporary.cleanup)

        failed = tracer.trace_once(root, simulate_failure=True)
        continuation = tracer.trace_once(root)
        recovered = tracer.trace_once(root, recover=True, promote_example=True)

        self.assertEqual(failed.status, "failed")
        self.assertTrue(failed.failure_path is not None and failed.failure_path.is_file())
        self.assertEqual(continuation.run_id, "run-0002")
        self.assertEqual(continuation.previous_run_id, "run-0001")
        self.assertEqual(continuation.previous_run_relation, "predecessor")
        self.assertEqual(recovered.status, "succeeded")
        self.assertEqual(recovered.previous_run_id, "run-0001")
        self.assertEqual(recovered.previous_run_relation, "recovery")
        self.assertTrue(
            recovered.recovery_path is not None and recovered.recovery_path.is_file()
        )
        with self.assertRaises(tracer.TraceError):
            tracer.trace_once(root, recover=True)
        records = [
            json.loads(line)
            for line in (root / "workspace/history/runs.jsonl").read_text().splitlines()
            if line.strip()
        ]
        self.assertEqual(
            records[0]["failure"]["ref"],
            "workspace/runs/run-0001/failure.json",
        )
        self.assertIsNone(records[0]["recovery"])
        self.assertIsNone(records[1]["recovery"])
        self.assertEqual(records[2]["recovery"]["from_run_id"], "run-0001")
        self.assertEqual(
            records[2]["recovery"]["ref"],
            "workspace/runs/run-0003/recovery.json",
        )
        self.assertEqual(records[0]["previous_run_relation"], None)
        self.assertEqual(records[1]["previous_run_relation"], "predecessor")
        self.assertEqual(records[2]["previous_run_relation"], "recovery")
        self.assertEqual(checks.check_structure(root), [])

    def test_recovery_is_single_use_per_failed_run(self) -> None:
        temporary, root = self._temporary_seed()
        self.addCleanup(temporary.cleanup)

        failed = tracer.trace_once(root, simulate_failure=True)
        recovered = tracer.trace_once(root, recover=True)

        self.assertEqual(failed.run_id, "run-0001")
        self.assertEqual(recovered.run_id, "run-0002")
        self.assertEqual(recovered.previous_run_id, "run-0001")
        with self.assertRaisesRegex(TraceErrorAlias, "previous unresolved failed"):
            tracer.trace_once(root, recover=True)

        second_failure = tracer.trace_once(root, simulate_failure=True)
        second_recovery = tracer.trace_once(root, recover=True)
        self.assertEqual(second_failure.run_id, "run-0003")
        self.assertEqual(second_recovery.run_id, "run-0004")
        self.assertEqual(second_recovery.previous_run_relation, "recovery")

    def test_stale_public_wording_is_rejected(self) -> None:
        temporary, root = self._temporary_seed()
        self.addCleanup(temporary.cleanup)
        bad_wording = "This is a " + "hand" + " off " + "sche" + "ma.\n"
        (root / "docs" / "bad.md").write_text(bad_wording, encoding="utf-8")

        errors = checks.check_structure(root)

        self.assertTrue(any("stale public wording" in error for error in errors))

    def test_legacy_root_route_is_rejected(self) -> None:
        temporary, root = self._temporary_seed()
        self.addCleanup(temporary.cleanup)
        (root / ("prom" + "pts")).mkdir()

        errors = checks.check_structure(root)

        self.assertTrue(any("legacy root path" in error for error in errors))

    def test_ledger_checker_rejects_repeated_recovery_reference(self) -> None:
        temporary, root = self._temporary_seed()
        self.addCleanup(temporary.cleanup)

        tracer.trace_once(root, simulate_failure=True)
        tracer.trace_once(root, recover=True)
        records = [
            json.loads(line)
            for line in (root / "workspace/history/runs.jsonl").read_text().splitlines()
            if line.strip()
        ]
        duplicate = dict(records[1])
        duplicate["run_id"] = "run-0003"
        duplicate["output_ref"] = "workspace/runs/run-0003/output.json"
        duplicate["proof_ref"] = "workspace/runs/run-0003/proof.json"
        history = root / "workspace/history/runs.jsonl"
        history.write_text(
            "\n".join(json.dumps(record, sort_keys=True) for record in records + [duplicate])
            + "\n",
            encoding="utf-8",
        )

        errors = checks.check_structure(root)

        self.assertTrue(any("more than once" in error for error in errors))

    def test_source_operational_state_is_unchanged_by_temporary_proof(self) -> None:
        source_history = (ROOT / "workspace/history/runs.jsonl").read_text(
            encoding="utf-8"
        )
        temporary, root = self._temporary_seed()
        self.addCleanup(temporary.cleanup)

        tracer.trace_once(root, promote_example=True)
        tracer.trace_once(root, simulate_failure=True)
        tracer.trace_once(root, recover=True, promote_example=True)

        self.assertEqual(
            (ROOT / "workspace/history/runs.jsonl").read_text(encoding="utf-8"),
            source_history,
        )

    def test_cli_supports_explicit_root(self) -> None:
        temporary, root = self._temporary_seed()
        self.addCleanup(temporary.cleanup)

        result = subprocess.run(
            [
                sys.executable,
                str(ENGINE / "tracer.py"),
                "--root",
                str(root),
                "--promote-example",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("system: Agentic Power BI System", result.stdout)
        self.assertIn("run: run-0001", result.stdout)


TraceErrorAlias = tracer.TraceError


if __name__ == "__main__":
    unittest.main()
