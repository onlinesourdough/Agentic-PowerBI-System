import { spawnSync } from "node:child_process";

const cases = [
  { path: "tests/fixtures/valid", expected: 0 },
  { path: "tests/fixtures/invalid", expected: 2 },
];

for (const testCase of cases) {
  const result = spawnSync(process.execPath, ["scripts/validate-pbip.mjs", testCase.path], {
    encoding: "utf8",
  });
  if (result.status !== testCase.expected) {
    process.stderr.write(`Validator case ${testCase.path} returned ${result.status}; expected ${testCase.expected}.\n${result.stdout}${result.stderr}`);
    process.exit(1);
  }
}

process.stdout.write("PBIP validator fixtures: PASS\n");
