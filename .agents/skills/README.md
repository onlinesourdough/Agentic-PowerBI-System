# Repository-local skill shelf

This standalone System owns this shelf. New repeatable methods specific to
Power BI or this System live here; cross-project and Global skills stay
plugin- or harness-installed outside the repository. AIOS, templates, and
releases may invoke these repository-local skills, but they do not overwrite
them.

Each direct skill uses the standard `.agents/skills/<name>/SKILL.md` path. The
folder name and the skill's frontmatter `name` must agree.

## Skill index

- `.agents/skills/agentic-powerbi-system/SKILL.md`: primary route for prior-run
  inspection, specialist routing, and durable proof.
- `.agents/skills/powerbi/SKILL.md`: business questions, decisions, KPI
  contracts, and Power BI domain audit.
- `.agents/skills/pbip/SKILL.md`: safe PBIP, PBIR, and TMDL structure and edits.
- `.agents/skills/dax/SKILL.md`: explicit measures and semantic logic.
- `.agents/skills/report/SKILL.md`: report pages, states, visuals, filters, and
  layout.
- `.agents/skills/fabric/SKILL.md`: authority-gated Fabric and Power BI Service
  work.
- `.agents/skills/validation/SKILL.md`: deterministic local and optional native
  completion proof.
- `.agents/skills/system-audit/SKILL.md`: read-only periodic evaluation of
  accumulated repository and workspace health.

Validate this shelf directly with
`python3 workspace/engine/checks.py --skills-only`.
