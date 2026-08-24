#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ENGINE_DIR = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(ENGINE_DIR, "../..");
const PLACEHOLDER = ".gitkeep";

function relativePath(relative) {
  return path.join(ROOT, relative);
}

function checkPlaceholderDirectory(relative, errors) {
  const directory = relativePath(relative);
  if (!fs.existsSync(directory)) {
    errors.push(`${relative}/ is missing`);
    return;
  }
  if (!fs.lstatSync(directory).isDirectory()) {
    errors.push(`${relative}/ is not a directory`);
    return;
  }

  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (entry.name === PLACEHOLDER && entry.isFile()) continue;
    errors.push(`${relative}/${entry.name} is mutable operational state`);
  }
}

function checkBlankLedger(errors) {
  const relative = "workspace/history/runs.jsonl";
  const ledger = relativePath(relative);
  if (!fs.existsSync(ledger)) {
    errors.push(`${relative} is missing`);
    return;
  }
  if (!fs.lstatSync(ledger).isFile()) {
    errors.push(`${relative} is not a file`);
    return;
  }
  if (fs.readFileSync(ledger, "utf8").trim().length > 0) {
    errors.push(`${relative} contains operational run records`);
  }
}

function checkHistoryDirectory(errors) {
  const relative = "workspace/history";
  const directory = relativePath(relative);
  if (!fs.existsSync(directory)) {
    errors.push(`${relative}/ is missing`);
    return;
  }
  if (!fs.lstatSync(directory).isDirectory()) {
    errors.push(`${relative}/ is not a directory`);
    return;
  }
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (entry.name === "runs.jsonl" && entry.isFile()) continue;
    errors.push(`${relative}/${entry.name} is mutable operational state`);
  }
}

function seedStateErrors() {
  const errors = [];
  checkBlankLedger(errors);
  checkHistoryDirectory(errors);
  for (const relative of [
    "workspace/briefs",
    "workspace/models",
    "workspace/reports",
    "workspace/state",
    "workspace/runs",
    "workspace/learning",
  ]) {
    checkPlaceholderDirectory(relative, errors);
  }
  return errors;
}

const errors = seedStateErrors();
if (errors.length > 0) {
  console.error(
    "Agentic Power BI System seed guard: refusing to pack mutable operational state.",
  );
  for (const error of errors) console.error(`- ${error}`);
  console.error("Operational evidence was not changed or removed.");
  process.exitCode = 1;
}
