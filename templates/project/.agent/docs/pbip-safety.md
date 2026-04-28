# PBIP safety guide

- Validate before opening Desktop after external edits.
- Do not commit `.pbi/cache.abf` or local settings.
- Do not rewrite `.platform` IDs without explicit intent.
- Use backups before bulk PBIR report edits.
- Prefer `pbir validate` and `node scripts/validate-pbip.mjs`.
