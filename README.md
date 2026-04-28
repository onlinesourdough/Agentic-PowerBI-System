# agentic-powerbi

Clean, project-local skills and guardrails for **agentic Power BI development**.

This repo is meant to be installed into a Power BI / Business Analytics project so your coding agent understands PBIP, PBIR, TMDL, DAX, Fabric, validation, and report/model workflows without global setup.

## Quick start

From your Power BI project:

```bash
pi install -l git:github.com/gustavonline/agentic-powerbi
pi
```

That adds this package to `.pi/settings.json` for the current project only.

## What you get

```text
agentic-powerbi/
├── skills/       # Agent Skills for Power BI work
├── prompts/      # Short slash-command prompt templates
├── extensions/   # Pi guardrails and helper commands
├── scripts/      # Small validation/tooling scripts
├── AGENTS.md     # Optional root instruction file
└── package.json  # Pi package manifest
```

## Skills

| Skill | Use for |
|---|---|
| `powerbi` | Business analytics workflow, KPI thinking, report storytelling |
| `pbip` | PBIP/PBIR/TMDL file structure and safe project edits |
| `dax` | DAX measures, KPI definitions, validation ideas |
| `report` | PBIR report pages, visuals, themes, layout, filters |
| `fabric` | Fabric CLI / Power BI Service workflows |
| `validation` | PBIP/PBIR/TMDL checks before saying a task is done |

## Prompt templates

- `/validate-powerbi [path]`
- `/audit-powerbi [focus]`
- `/plan-powerbi-page <business question>`

## Pi extension

The package includes `extensions/index.ts`, a small Pi extension that adds:

- `/powerbi-doctor` — check recommended local Power BI tooling
- `/powerbi-validate [path]` — run local PBIP/PBIR/TMDL validation
- automatic validation warning after editing `.pbir`, `.tmdl`, and report JSON files

## Recommended toolchain

Install only what your project needs:

| Tool | Why |
|---|---|
| Power BI Desktop | Open and author PBIP/PBIX locally |
| `pbir` CLI | Browse, edit, back up, and validate PBIR reports |
| `fab` / Fabric CLI | Workspaces, reports, semantic models, import/export, refresh |
| `pbi-tools` | PBIX/PBIT source-control workflows and diagnostics |
| Tabular Editor | Semantic model scripting, BPA, model validation |
| DAX Studio | DAX query and performance analysis |

Useful install commands:

```bash
pip install ms-fabric-cli
pip install pbir-cli
npm install -g @mariozechner/pi-coding-agent
```

For `pbi-tools`, download from https://pbi.tools/cli/.

Check your setup:

```bash
node .pi/git/github.com/gustavonline/agentic-powerbi/scripts/doctor.mjs
```

or from this repo:

```bash
npm run doctor
```

## Recommended project setup

In your actual Power BI repo, keep it simple:

```text
your-powerbi-project/
├── .pi/settings.json
├── AGENTS.md                 # optional, copy/adapt from this repo
├── YourReport.pbip
├── YourReport.Report/
└── YourReport.SemanticModel/
```

Suggested `.gitignore` lines:

```gitignore
**/.pbi/localSettings.json
**/.pbi/cache.abf
*.pbix
.pi/*
!.pi/settings.json
```

## Why project-local?

Power BI projects differ by tenant, workspace, model conventions, data sources, and business language. Project-local packages avoid leaking assumptions between projects.

## Notes on TypeScript vs scripts

The Pi extension is TypeScript because Pi loads extensions directly with its TypeScript runtime. The tiny files in `scripts/` are plain Node `.mjs` so they run anywhere without a build step or extra dependencies. That keeps setup simple.

## License

MIT. Inspired by the Power BI agentic development ecosystem, but this repo is intentionally small and original rather than a repackaged Claude plugin marketplace.
