# Power BI agentic toolchain

## Core tools

### Power BI Desktop

Required for local authoring and opening PBIP/PBIX. Enable PBIP/PBIR/TMDL preview features as needed in Desktop options.

### Fabric CLI (`fab`)

Install:

```bash
pip install ms-fabric-cli
fab auth login
fab ls
```

Use for workspaces, items, import/export, refreshes, and Fabric APIs.

### pbir CLI

Install:

```bash
uv tool install pbir-cli
# or
pip install pbir-cli
```

Use for PBIR report browsing/editing/validation:

```bash
pbir tree "Report.Report" -v
pbir backup "Report.Report" -m "Before edits"
pbir validate "Report.Report" --all
```

### pbi-tools

Download from pbi.tools releases. Use for PBIX/PBIT extraction/compile/deploy workflows and diagnostics.

### Tabular Editor

Use TE2/TE3 CLI for semantic model scripting, BPA, and validation when installed.

### DAX Studio

Use for DAX query debugging and performance diagnosis.

## Project-local check

```bash
node scripts/doctor.mjs
```
