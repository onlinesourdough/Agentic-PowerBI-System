#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const args = process.argv.slice(2);
const target = path.resolve(process.cwd(), args[0] && !args[0].startsWith("--") ? args[0] : ".");
const force = args.includes("--force");
const sourceIndex = args.indexOf("--source");
const rawPackageSource = sourceIndex >= 0 ? args[sourceIndex + 1] : "git:github.com/gustavonline/agentic-powerbi";

function copyRecursive(src, dst) {
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    fs.mkdirSync(dst, { recursive: true });
    for (const entry of fs.readdirSync(src)) copyRecursive(path.join(src, entry), path.join(dst, entry));
    return;
  }
  if (fs.existsSync(dst) && !force) return;
  fs.mkdirSync(path.dirname(dst), { recursive: true });
  fs.copyFileSync(src, dst);
}

fs.mkdirSync(target, { recursive: true });
copyRecursive(path.join(repoRoot, "templates", "project"), target);

const settingsPath = path.join(target, ".pi", "settings.json");
const settingsDir = path.dirname(settingsPath);
const isRemoteSource = /^(git:|npm:|https?:|ssh:|git@)/.test(rawPackageSource);
const packageSource = isRemoteSource
  ? rawPackageSource
  : path.relative(settingsDir, path.resolve(process.cwd(), rawPackageSource));
const settings = {
  enableSkillCommands: true,
  packages: [packageSource],
};
fs.mkdirSync(settingsDir, { recursive: true });
fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + "\n", "utf8");

// Copy deterministic scripts into the target so non-Pi harnesses can use them too.
const targetScripts = path.join(target, "scripts");
fs.mkdirSync(targetScripts, { recursive: true });
for (const script of ["doctor.mjs", "validate-pbip.mjs"]) {
  const dst = path.join(targetScripts, script);
  if (!fs.existsSync(dst) || force) fs.copyFileSync(path.join(repoRoot, "scripts", script), dst);
}

console.log(`Initialized agentic Power BI project at ${target}`);
console.log(`Pi package source: ${packageSource}`);
console.log("Next steps:");
console.log("  1. Review AGENTS.md and .agent/SYSTEM.md");
console.log("  2. Run: node scripts/doctor.mjs");
console.log("  3. Start pi from the project root: pi");
