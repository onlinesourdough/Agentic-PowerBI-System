# Getting started

## Existing Power BI project

```bash
cd your-powerbi-project
pi install -l git:github.com/gustavonline/agentic-powerbi
pi
```

Run:

```bash
/powerbi-doctor
/powerbi-validate .
```

## New project from starter

```bash
git clone https://github.com/gustavonline/agentic-powerbi.git
mkdir my-powerbi-project
cd my-powerbi-project
node ../agentic-powerbi/scripts/init-project.mjs . --source ../agentic-powerbi
```

Then add your PBIP project under `powerbi/` or `cases/<case>/powerbi/`.

## Recommended first prompt

```text
Read AGENTS.md and .agent/SYSTEM.md, inspect the repo structure, then tell me what Power BI artifacts are present and what validation can be run.
```
