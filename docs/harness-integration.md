# Harness integration

## Pi Coding Agent

Recommended setup:

```bash
cd your-powerbi-project
pi install -l git:github.com/gustavonline/agentic-powerbi
pi
```

This writes the package to `.pi/settings.json` and keeps it project-local.

## Codex / other AGENTS.md harnesses

Copy or keep `AGENTS.md` in the root of your project. If your harness supports Agent Skills, point it at this repo's `skills/` directory or copy selected skill folders into your project-local skill directory.

## Claude Code

This repo is intentionally not a Claude plugin marketplace. If using Claude Code, add the `skills/` directory as normal Agent Skills if your setup supports it, or paste relevant skill instructions into project-local context. The design avoids Claude-only subagents.

## GitHub Copilot / Cursor

Use `AGENTS.md` plus the skill markdown files as project context. Prefer invoking deterministic CLIs (`pbir`, `fab`, `pbi-tools`) from the terminal.

## General rule

Do not install globally unless you intentionally want the same Power BI behavior in all projects. Prefer project-local configuration.
