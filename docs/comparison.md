# Comparison: Claude plugin marketplace vs agentic-powerbi

Some Power BI agent resources are distributed as Claude plugin marketplaces with plugins, hooks, commands, and subagents.

`agentic-powerbi` intentionally uses a simpler, harness-agnostic model:

| Concern | Claude-style marketplace | agentic-powerbi |
|---|---|---|
| Distribution | Claude plugin marketplace | Pi package + normal files |
| Scope | Often installed through agent plugin system | Project-local `.pi/settings.json` |
| Agents | Subagent markdown/runtime | Normal Agent Skills only |
| Commands | Claude commands | Pi prompt templates |
| Hooks | Claude hook JSON/scripts | Pi TypeScript extension + local scripts |
| Other harnesses | Often Claude-first | `AGENTS.md`, Agent Skills, scripts |
| Branding/assets | Marketplace presentation | Minimal, no images required |

## Why this approach

- Easier to inspect and modify.
- Easier to install per project.
- Easier to use with Pi, Codex, Copilot, Cursor, and Claude.
- Avoids coupling workflows to one agent runtime.
- Keeps deterministic validation in scripts/extensions instead of relying on model behavior.
