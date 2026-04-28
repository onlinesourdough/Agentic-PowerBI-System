---
name: toolchain-setup
description: Check and install the recommended local Power BI agentic development toolchain: Pi, Fabric CLI, pbir, pbi-tools, Tabular Editor, DAX Studio, Git, Node, Python/uv. Use when setting up a project or diagnosing missing CLIs.
---

# Toolchain Setup

Use this skill when a user asks to set up or verify local tooling for agentic Power BI development.

## Default workflow

1. Run the local doctor script when available:

```bash
node scripts/doctor.mjs
```

2. If this repo is installed as a Pi package inside another project, locate the package and run:

```bash
node .pi/git/github.com/gustavonline/agentic-powerbi/scripts/doctor.mjs
```

or ask the user where the package is installed.

3. Recommend only missing tools. Do not force every tool for every project.

## Recommended tools

| Tool | Purpose | Install/check |
|---|---|---|
| Pi Coding Agent | project-local package and interactive harness | `npm install -g @mariozechner/pi-coding-agent`; `pi --version` |
| Fabric CLI (`fab`) | Fabric/Power BI service operations | `pip install ms-fabric-cli`; `fab auth login`; `fab ls` |
| pbir CLI | PBIR report browsing, editing, validation | `uv tool install pbir-cli` or `pip install pbir-cli`; `pbir --version` |
| pbi-tools | PBIX/PBIT extraction/compile/deploy workflows | download from pbi.tools; `pbi-tools --version` |
| Tabular Editor | semantic model scripting/BPA/validation | install TE2/TE3 and add CLI to PATH |
| DAX Studio | DAX query/performance diagnosis | install desktop app |
| Git | source control | `git --version` |
| Node 20+ | local scripts/extensions | `node --version` |
| Python + uv | Python CLIs such as fab/pbir | `python --version`; `uv --version` |

## Rules

- Do not ask the user to install cloud/admin tools unless the task needs cloud access.
- For `fab`, check `fab auth status` before service operations.
- For `pbir`, prefer `pbir backup` before bulk report edits and `pbir validate` after edits.
- For pbi-tools, distinguish it from Microsoft Fabric CLI and pbir CLI.
