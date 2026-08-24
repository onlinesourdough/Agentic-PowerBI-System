#!/usr/bin/env node
import { spawnSync } from "node:child_process";

const checks = [
  { cmd: "node", args: ["--version"], label: "Node.js 20+", required: true },
  { cmd: "git", args: ["--version"], label: "Git", required: true },
  { cmd: "python3", args: ["--version"], label: "Python 3.9+", required: true },
  { cmd: "fab", args: ["--version"], label: "Fabric CLI (fab)", required: false },
  { cmd: "pbir", args: ["--version"], label: "pbir CLI", required: false },
  { cmd: "pbi-tools", args: ["--version"], label: "pbi-tools", required: false },
  { cmd: "pbi-tools.core", args: ["--version"], label: "pbi-tools core", required: false },
  { cmd: "te", args: ["--version"], label: "Tabular Editor CLI", required: false },
  { cmd: "dotnet", args: ["--version"], label: ".NET SDK/runtime", required: false },
  { cmd: "uv", args: ["--version"], label: "uv", required: false },
];

function run(cmd, args) {
  const result = spawnSync(cmd, args, {
    encoding: "utf8",
    shell: process.platform === "win32",
  });
  return {
    ok: result.status === 0,
    text: `${result.stdout || result.stderr || result.error?.message || ""}`
      .trim()
      .split(/\r?\n/)[0] || "not found",
  };
}

let requiredMissing = 0;
console.log("Agentic Power BI System toolchain check\n");
for (const check of checks) {
  const result = run(check.cmd, check.args);
  const icon = result.ok ? "✓" : check.required ? "✗" : "-";
  if (!result.ok && check.required) requiredMissing++;
  console.log(`${icon} ${check.label.padEnd(24)} ${result.text}`);
}

console.log("\nOptional native checks are reported only when installed:");
console.log("- pbir validate <Report.Report> --all");
console.log("- fab exists <approved-workspace/item>");
console.log("- Tabular Editor, DAX Studio, Power BI Desktop, or pbi-tools");

process.exit(requiredMissing ? 2 : 0);
