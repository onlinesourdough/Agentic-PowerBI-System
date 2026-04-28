# Philosophy

`agentic-powerbi` is built around a simple split:

| Layer | Responsibility |
|---|---|
| Skills | Teach the agent Power BI domain workflows |
| Prompt templates | Start repeatable tasks quickly |
| Extensions/scripts | Deterministic guardrails and validation |
| AGENTS.md / .agent docs | Project-specific operating memory |

## Why skills, not subagents?

Many coding harnesses support some form of reusable instruction, but not all support Claude-style plugin agents. Agent Skills are easier to reuse across Pi, Codex, Claude, Copilot, Cursor, and future tools.

A skill should:

- describe when to use it,
- contain compact instructions,
- point to deterministic commands,
- avoid harness-specific assumptions.

## Why project-local?

Power BI projects differ by workspace, tenant, model conventions, report design rules, and deployment process. Global instructions tend to leak assumptions between projects. Project-local package installation keeps each repo self-contained.
