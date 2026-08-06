#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const NAME_RE = /^[A-Za-z0-9_][A-Za-z0-9_-]*$/;
const args = process.argv.slice(2);
const ignoreTests = args.includes("--ignore-tests");
const changedIndex = args.indexOf("--changed");
const changedPath = changedIndex >= 0 ? args[changedIndex + 1] : undefined;
const targetArg =
  args.find(
    (argument, index) =>
      !argument.startsWith("--") &&
      (changedIndex < 0 || (index !== changedIndex && index !== changedIndex + 1)),
  ) || ".";
const root = path.resolve(process.cwd(), targetArg);

const findings = [];
const add = (level, file, message, remediation = "") => findings.push({ level, file, message, remediation });
const isDir = (p) => fs.existsSync(p) && fs.statSync(p).isDirectory();
const isFile = (p) => fs.existsSync(p) && fs.statSync(p).isFile();
const rel = (p) => path.relative(process.cwd(), p).replaceAll(path.sep, "/") || ".";

function readJson(file) {
  try {
    return { ok: true, value: JSON.parse(fs.readFileSync(file, "utf8")) };
  } catch (error) {
    add("ERROR", file, `Invalid JSON: ${error.message}`, "Fix JSON syntax before opening in Power BI Desktop.");
    return { ok: false, value: undefined };
  }
}

function walk(dir, predicate, out = []) {
  if (!isDir(dir)) return out;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.name === ".git" || entry.name === "node_modules" || entry.name === ".pi") continue;
    if (ignoreTests && entry.name === "tests") continue;
    if (entry.isDirectory()) walk(full, predicate, out);
    else if (predicate(full)) out.push(full);
  }
  return out;
}

function findDirs(start, suffix) {
  const out = [];
  function visit(dir) {
    if (!isDir(dir)) return;
    if (path.basename(dir).endsWith(suffix)) out.push(dir);
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      if ([".git", "node_modules", ".pi"].includes(entry.name)) continue;
      if (ignoreTests && entry.name === "tests") continue;
      visit(path.join(dir, entry.name));
    }
  }
  visit(start);
  return out;
}

function validateName(kind, file, name) {
  if (!name) return;
  if (!NAME_RE.test(name)) {
    add("ERROR", file, `${kind} name '${name}' contains characters Power BI may silently ignore.`, "Use letters, numbers, underscores, or hyphens only.");
  }
}

function validateDefinitionPbir(file) {
  const parsed = readJson(file);
  if (!parsed.ok) return;
  const json = parsed.value;
  if (!json.version) add("ERROR", file, "definition.pbir is missing version.");
  if (!json.datasetReference) add("ERROR", file, "definition.pbir is missing datasetReference.");
  const byPath = json.datasetReference?.byPath;
  const byConnection = json.datasetReference?.byConnection;
  if (!byPath && !byConnection) add("ERROR", file, "datasetReference must contain byPath or byConnection.");
  if (byPath) {
    if (!byPath.path) add("ERROR", file, "datasetReference.byPath.path is missing.");
    else {
      const resolved = path.resolve(path.dirname(file), byPath.path);
      if (!isDir(resolved)) add("ERROR", file, `byPath target does not exist: ${byPath.path}`, "Ensure the referenced .SemanticModel folder exists relative to definition.pbir.");
    }
  }
  if (byConnection && !byConnection.connectionString) {
    add("ERROR", file, "datasetReference.byConnection.connectionString is missing.");
  }
}

function validateReport(reportDir) {
  const pbir = path.join(reportDir, "definition.pbir");
  if (!isFile(pbir)) add("ERROR", reportDir, "Report folder is missing definition.pbir.");
  else validateDefinitionPbir(pbir);

  const definitionDir = path.join(reportDir, "definition");
  const reportJson = path.join(definitionDir, "report.json");
  if (isFile(reportJson)) {
    const parsed = readJson(reportJson);
    if (parsed.ok) {
      const json = parsed.value;
      if (!json.$schema) add("WARN", reportJson, "report.json is missing $schema.");
      if (!json.themeCollection) add("WARN", reportJson, "report.json is missing themeCollection.");
      const packages = Array.isArray(json.resourcePackages) ? json.resourcePackages : [];
      for (const pkg of packages) {
        const type = pkg.type;
        const items = Array.isArray(pkg.items) ? pkg.items : [];
        for (const item of items) {
          if (!type || !item.path) continue;
          const resource = path.join(reportDir, "StaticResources", type, item.path);
          if (!isFile(resource)) add("ERROR", reportJson, `Theme/resource package item missing on disk: ${type}/${item.path}`);
        }
      }
    }
  }

  const pagesRoot = path.join(definitionDir, "pages");
  const pagesJson = path.join(pagesRoot, "pages.json");
  let pageOrder = [];
  if (isFile(pagesJson)) {
    const parsed = readJson(pagesJson);
    if (parsed.ok) {
      pageOrder = Array.isArray(parsed.value.pageOrder) ? parsed.value.pageOrder : [];
      if (parsed.value.activePageName && !pageOrder.includes(parsed.value.activePageName)) {
        add("ERROR", pagesJson, "activePageName is not present in pageOrder.");
      }
    }
  }

  if (isDir(pagesRoot)) {
    for (const pageFolder of fs.readdirSync(pagesRoot, { withFileTypes: true }).filter((e) => e.isDirectory())) {
      const pageDir = path.join(pagesRoot, pageFolder.name);
      const pageFile = path.join(pageDir, "page.json");
      if (pageFolder.name.includes(" ")) add("ERROR", pageDir, "Page folder contains spaces.");
      if (isFile(pageFile)) {
        const parsed = readJson(pageFile);
        if (parsed.ok) {
          const name = parsed.value.name;
          validateName("Page", pageFile, name);
          const folderName = pageFolder.name.replace(/\.Page$/i, "");
          if (name && folderName !== name) add("WARN", pageFile, `Page name '${name}' does not match folder '${pageFolder.name}'.`);
          if (pageOrder.length && name && !pageOrder.includes(name)) add("WARN", pageFile, `Page '${name}' is not listed in pages.json pageOrder.`);
        }
      }
      const visualsRoot = path.join(pageDir, "visuals");
      if (isDir(visualsRoot)) {
        for (const visualFolder of fs.readdirSync(visualsRoot, { withFileTypes: true }).filter((e) => e.isDirectory())) {
          const visualDir = path.join(visualsRoot, visualFolder.name);
          const visualFile = path.join(visualDir, "visual.json");
          if (visualFolder.name.includes(" ")) add("ERROR", visualDir, "Visual folder contains spaces.");
          if (!isFile(visualFile)) continue;
          const parsed = readJson(visualFile);
          if (!parsed.ok) continue;
          const json = parsed.value;
          if (!json.name) add("ERROR", visualFile, "visual.json is missing name.");
          if (!json.position) add("ERROR", visualFile, "visual.json is missing position.");
          if (!json.visual && !json.visualGroup) add("ERROR", visualFile, "visual.json must contain visual or visualGroup.");
          validateName("Visual", visualFile, json.name);
          const folderName = visualFolder.name.replace(/\.Visual$/i, "");
          if (json.name && folderName !== json.name) add("WARN", visualFile, `Visual name '${json.name}' does not match folder '${visualFolder.name}'.`);
        }
      }
    }
  }
}

function validateSemanticModel(modelDir) {
  const defPbism = path.join(modelDir, "definition.pbism");
  if (isFile(defPbism)) readJson(defPbism);
  const tmdlModel = path.join(modelDir, "definition", "model.tmdl");
  const bim = path.join(modelDir, "model.bim");
  if (isFile(tmdlModel) && isFile(bim)) add("ERROR", modelDir, "Semantic model contains both TMDL definition/model.tmdl and model.bim.");
  if (!isFile(tmdlModel) && !isFile(bim)) add("WARN", modelDir, "No TMDL model.tmdl or model.bim found.");
  for (const file of walk(modelDir, (p) => p.endsWith(".tmdl"))) validateTmdl(file);
}

function validateTmdl(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^ +\S/.test(line)) add("WARN", file, `Line ${i + 1}: TMDL indentation starts with spaces; tabs are safer for TMDL.`);
    if (line.trim().startsWith("///")) {
      const next = lines[i + 1] ?? "";
      if (!next.trim() || next.trim().startsWith("///")) add("WARN", file, `Line ${i + 1}: TMDL description should immediately precede a declaration.`);
    }
  }
}

function validateChanged(file) {
  const absolute = path.resolve(process.cwd(), file);
  if (!isFile(absolute)) return;
  const normalized = absolute.replaceAll(path.sep, "/");
  if ((absolute.endsWith(".json") || absolute.endsWith(".pbir")) && normalized.includes(".Report/")) {
    if (path.basename(absolute) === "definition.pbir") validateDefinitionPbir(absolute);
    else readJson(absolute);
  }
  if (absolute.endsWith(".tmdl")) validateTmdl(absolute);
}

if (changedPath) {
  validateChanged(changedPath);
} else {
  const start = isDir(root) ? root : path.dirname(root);
  for (const report of findDirs(start, ".Report")) validateReport(report);
  for (const model of findDirs(start, ".SemanticModel")) validateSemanticModel(model);
}

const errors = findings.filter((f) => f.level === "ERROR");
const warnings = findings.filter((f) => f.level === "WARN");

if (findings.length === 0) {
  console.log("PBIP validation clean.");
  process.exit(0);
}

console.log("PBIP VALIDATION REPORT");
console.log("======================\n");
for (const level of ["ERROR", "WARN"]) {
  const group = findings.filter((f) => f.level === level);
  if (!group.length) continue;
  console.log(`${level}S:`);
  for (const f of group) {
    console.log(`- [${rel(f.file)}] ${f.message}${f.remediation ? ` Remediation: ${f.remediation}` : ""}`);
  }
  console.log("");
}

process.exit(errors.length ? 2 : warnings.length ? 1 : 0);
