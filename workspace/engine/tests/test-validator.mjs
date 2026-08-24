import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const ROOT = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../../..",
);

const cases = [
  { path: "workspace/engine/tests/fixtures/valid", expected: 0 },
  { path: "workspace/engine/tests/fixtures/invalid", expected: 2 },
];

function runValidatorFixtures() {
  for (const testCase of cases) {
    const result = spawnSync(
      process.execPath,
      ["workspace/engine/validate-pbip.mjs", testCase.path],
      { cwd: ROOT, encoding: "utf8" },
    );
    if (result.status !== testCase.expected) {
      process.stderr.write(
        `Validator case ${testCase.path} returned ${result.status}; expected ${testCase.expected}.\n${result.stdout}${result.stderr}`,
      );
      process.exit(1);
    }
  }
  process.stdout.write("PBIP validator fixtures: PASS\n");
}

function temporarySeed() {
  const parent = fs.mkdtempSync(
    path.join(os.tmpdir(), "agentic-powerbi-system-pack-"),
  );
  const root = path.join(parent, "seed");
  fs.cpSync(ROOT, root, {
    recursive: true,
    filter(source) {
      const relative = path.relative(ROOT, source);
      if (!relative) return true;
      const parts = relative.split(path.sep);
      return !parts.includes(".git") && !parts.includes("node_modules") && !parts.includes("__pycache__");
    },
  });
  return {
    root,
    cleanup() {
      fs.rmSync(parent, { recursive: true, force: true });
    },
  };
}

function pack(root) {
  return spawnSync("npm", ["pack", "--dry-run", "--json"], {
    cwd: root,
    encoding: "utf8",
    timeout: 60_000,
  });
}

function packFiles(result) {
  assert.equal(
    result.status,
    0,
    `npm pack failed unexpectedly:\n${result.stdout}\n${result.stderr}`,
  );
  const payload = JSON.parse(result.stdout);
  assert.equal(Array.isArray(payload), true);
  assert.equal(Array.isArray(payload[0]?.files), true);
  return payload[0].files.map((file) => file.path);
}

function snapshotFiles(root, relative) {
  const base = path.join(root, relative);
  const output = [];

  function visit(directory) {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true }).sort((left, right) => left.name.localeCompare(right.name))) {
      const absolute = path.join(directory, entry.name);
      const relativePath = path.relative(root, absolute).split(path.sep).join("/");
      if (entry.isDirectory()) {
        visit(absolute);
      } else if (entry.isSymbolicLink()) {
        output.push(`${relativePath}:link:${fs.readlinkSync(absolute)}`);
      } else {
        const digest = crypto
          .createHash("sha256")
          .update(fs.readFileSync(absolute))
          .digest("hex");
        output.push(`${relativePath}:file:${digest}`);
      }
    }
  }

  visit(base);
  return output;
}

function operationalSnapshot(root) {
  const ledger = path.join(root, "workspace", "history", "runs.jsonl");
  return {
    ledger: crypto
      .createHash("sha256")
      .update(fs.readFileSync(ledger))
      .digest("hex"),
    runs: snapshotFiles(root, "workspace/runs"),
    state: snapshotFiles(root, "workspace/state"),
  };
}

function runTracer(root, args) {
  const result = spawnSync(
    "python3",
    ["workspace/engine/tracer.py", ...args],
    { cwd: root, encoding: "utf8" },
  );
  assert.equal(
    result.status,
    0,
    `tracer failed for ${args.join(" ")}:\n${result.stdout}\n${result.stderr}`,
  );
}

function testCleanSeedPackage() {
  const temporary = temporarySeed();
  try {
    const files = packFiles(pack(temporary.root));
    assert(files.includes("workspace/engine/seed-guard.mjs"));
    assert(files.includes("workspace/history/runs.jsonl"));
    assert(files.includes("workspace/runs/.gitkeep"));
    assert(!files.some((file) => file.startsWith("workspace/runs/run-")));
    assert(!files.some((file) => file.startsWith("workspace/state/") && !file.endsWith(".gitkeep")));
  } finally {
    temporary.cleanup();
  }
}

function testCuratedExampleRemainsPackageable() {
  const temporary = temporarySeed();
  try {
    const example = path.join(temporary.root, "examples", "curated-seed");
    fs.mkdirSync(example, { recursive: true });
    fs.writeFileSync(example + "/README.md", "# Curated seed proof\n");
    fs.writeFileSync(
      example + "/proof.json",
      JSON.stringify({ curated: true, example: "curated-seed", source_run_id: "seed", status: "succeeded" }) + "\n",
    );

    const files = packFiles(pack(temporary.root));
    assert(files.includes("examples/curated-seed/README.md"));
    assert(files.includes("examples/curated-seed/proof.json"));
  } finally {
    temporary.cleanup();
  }
}

function testPackRefusesTracedStateAndPreservesEvidence() {
  const temporary = temporarySeed();
  try {
    runTracer(temporary.root, ["--promote-example"]);
    runTracer(temporary.root, ["--simulate-failure"]);
    runTracer(temporary.root, ["--recover", "--promote-example"]);
    const before = operationalSnapshot(temporary.root);

    const result = pack(temporary.root);
    assert.notEqual(result.status, 0);
    assert.match(
      `${result.stdout}\n${result.stderr}`,
      /seed guard: refusing to pack mutable operational state/i,
    );
    assert.deepEqual(operationalSnapshot(temporary.root), before);
    assert(fs.existsSync(path.join(temporary.root, "examples", "powerbi-system-proof", "run-0001", "proof.json")));
    assert(fs.existsSync(path.join(temporary.root, "workspace", "runs", "run-0003", "recovery.json")));
  } finally {
    temporary.cleanup();
  }
}

function testPackRefusesStateFileAndPreservesIt() {
  const temporary = temporarySeed();
  try {
    const stateFile = path.join(temporary.root, "workspace", "state", "local-state.json");
    fs.writeFileSync(stateFile, JSON.stringify({ fixture: true }) + "\n");
    const before = operationalSnapshot(temporary.root);

    const result = pack(temporary.root);
    assert.notEqual(result.status, 0);
    assert.match(`${result.stdout}\n${result.stderr}`, /workspace\/state\/local-state\.json/);
    assert.deepEqual(operationalSnapshot(temporary.root), before);
  } finally {
    temporary.cleanup();
  }
}

runValidatorFixtures();
testCleanSeedPackage();
testCuratedExampleRemainsPackageable();
testPackRefusesTracedStateAndPreservesEvidence();
testPackRefusesStateFileAndPreservesIt();
process.stdout.write(
  "Seed packaging guard: PASS (clean allow; curated allow; traced success/failure/recovery deny+preserve; state deny+preserve)\n",
);
