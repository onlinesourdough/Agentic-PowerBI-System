# agentic-powerbi

Harness-agnostic Agent Skills, Pi package, prompt templates, and guardrails for **Power BI / Business Analytics development as code**.

The goal is simple: clone or install this repo into a Power BI project and give your coding agent a project-local way to work with PBIP, PBIR, TMDL, DAX, Power Query, Fabric, and report validation — without installing global Claude-style plugins.

## Why this exists

Power BI development is becoming source-controlled and file-based:

- **PBIP**: project container
- **TMDL**: semantic model as text
- **PBIR**: report definition as text
- **Fabric CLI / pbir / pbi-tools / Tabular Editor**: deterministic tools agents can call

Agents are useful here, but only if they are given:

1. domain-specific instructions,
2. deterministic validation,
3. project-local setup,
4. safe workflows for brittle report/model files.

This repo packages that into a reusable, lightweight starter.

## Design philosophy

- **Project-local, not global**: install into each repo via `.pi/settings.json`.
- **Skills over subagents**: every capability is a normal Agent Skill. No Claude-only agent runtime required.
- **Progressive disclosure**: keep `AGENTS.md` concise; detailed docs live under `.agent/docs/` and skills.
- **Deterministic first**: prefer `pbir validate`, `fab`, `pbi-tools`, `Tabular Editor`, scripts, and JSON/TMDL checks before manual LLM reasoning.
- **Harness-agnostic**: Pi-first package, but usable from Codex, Claude, Copilot, Cursor, and other coding harnesses that can read Agent Skills / `AGENTS.md`.

## Quick start with Pi

Install this package project-locally inside an existing Power BI repo:

```bash
cd path/to/your-powerbi-project
pi install -l git:github.com/gustavonline/agentic-powerbi
```

Then start Pi from that project:

```bash
pi
```

The install writes to `.pi/settings.json`, so the package is active only for that project.

### Local development install

If you cloned this repo next to your Power BI project:

```bash
cd path/to/your-powerbi-project
pi install -l ../agentic-powerbi
```

## Use as a starter template

```bash
git clone https://github.com/gustavonline/agentic-powerbi.git
mkdir my-powerbi-analytics
cd my-powerbi-analytics
node ../agentic-powerbi/scripts/init-project.mjs . --source ../agentic-powerbi
```

This creates:

- `.pi/settings.json` with a project-local package reference
- `AGENTS.md` for harnesses that read root instructions
- `.agent/` progressive-disclosure docs and task template
- `.gitignore` tuned for PBIP projects

## Recommended Power BI toolchain

Install what you need; the skills will prefer deterministic tools when present and fall back gracefully when absent.

| Tool | Why use it | Install / check |
|---|---|---|
| **Power BI Desktop** | Author/open PBIP/PBIX locally | Windows app |
| **Pi Coding Agent** | Primary local harness for this package | `npm install -g @mariozechner/pi-coding-agent` |
| **Fabric CLI (`fab`)** | Workspaces, items, import/export, Fabric automation | `pip install ms-fabric-cli` then `fab auth login` |
| **pbir CLI** | Browse/edit/validate PBIR reports | `uv tool install pbir-cli` or `pip install pbir-cli` |
| **pbi-tools** | PBIX/PBIT source-control workflows and diagnostics | download from pbi.tools releases |
| **Tabular Editor 2/3** | Semantic model scripting, BPA, validation | install TE and add CLI to PATH |
| **DAX Studio** | Query/performance diagnosis | install desktop tool |
| **Git + Node 20+** | Source control and local scripts | `git --version`, `node --version` |

Run a quick local check:

```bash
node scripts/doctor.mjs
```

See also: [`docs/comparison.md`](docs/comparison.md) for how this differs from Claude-style plugin marketplaces.

## Included package resources

### Skills

- `toolchain-setup` — install/check Power BI CLI tooling
- `powerbi-business-analytics` — translate business questions into analytical Power BI work
- `pbip-workflow` — PBIP/TMDL/PBIR project structure and safe file workflows
- `semantic-modeling` — star schema, relationships, model quality
- `dax-measures` — DAX authoring and validation workflow
- `power-query` — M/query shaping and refresh guidance
- `pbir-report-editing` — PBIR report edits, pages, visuals, themes
- `powerbi-validation` — deterministic validation and post-rename checks
- `fabric-deployment` — Fabric CLI deployment/refresh/workspace workflow
- `agentic-powerbi-reviewer` — end-to-end model/report review checklist

### Prompt templates

- `/validate-pbip`
- `/audit-powerbi`
- `/plan-report-page`
- `/create-measures`
- `/prepare-business-case`

### Pi extension

`extensions/powerbi-guard.ts` adds project-local guardrails:

- validates edited PBIR JSON / `definition.pbir` / TMDL-ish files after `write` and `edit`
- provides `/powerbi-doctor`
- provides `/powerbi-validate [path]`

## Repository modes

You can use this repo in two ways:

1. **As a Pi package** installed into another project.
2. **As a project starter** by running `scripts/init-project.mjs`.

Both modes are project-based and avoid global agent state.

## Attribution

This repo is original MIT-licensed work, but it is inspired by the broader agentic Power BI community and Microsoft’s PBIP/TMDL/PBIR direction. It does **not** vendor third-party skills or Claude plugin assets. See `docs/attribution.md`.

## Safety notes

PBIR and TMDL are text, but they are still brittle. Recommended habits:

- Make a backup before large report edits.
- Prefer `pbir` CLI for report mutations when available.
- Run validation after every structural change.
- Open Power BI Desktop only after local validation is clean.
- Keep `.pbi/cache.abf` and local settings out of Git.
