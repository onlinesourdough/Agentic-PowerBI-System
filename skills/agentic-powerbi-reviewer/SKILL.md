---
name: agentic-powerbi-reviewer
description: Perform an end-to-end review of a Power BI business analytics project: model, DAX, Power Query, report design, validation status, documentation, and deployment readiness.
---

# Agentic Power BI Reviewer

Use this skill for holistic project review.

## Review sequence

1. Read `AGENTS.md` and `.agent/SYSTEM.md` if present.
2. Inventory PBIP items:
   - `.pbip`
   - `.Report`
   - `.SemanticModel`
   - docs/checklists
3. Run validation:

```bash
node scripts/validate-pbip.mjs .
pbir validate "<Report.Report>" --all
```

4. Review semantic model:
   - star schema
   - relationships
   - hidden keys
   - measure metadata
   - naming consistency
5. Review report:
   - page purpose
   - layout hierarchy
   - slicer/filter usage
   - visual clarity
   - business conclusions
6. Review docs:
   - business questions
   - KPI definitions
   - limitations
   - deployment notes

## Output format

```text
POWER BI REVIEW
===============

Summary:

Blockers:

Model findings:

Report findings:

Business analytics findings:

Recommended next actions:
```
