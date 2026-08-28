# Validation

Validation is deterministic first and tool-assisted only when the tool is
truthfully available.

## Local proof

From the repository root:

```sh
node workspace/engine/doctor.mjs
node workspace/engine/validate-pbip.mjs . --ignore-tests
npm test
npm pack --dry-run
```

The doctor requires Node.js, Git, and Python for the local engine. Fabric,
`pbir`, `pbi-tools`, Tabular Editor, and other native Power BI tools are
optional. A missing optional command is an unavailable check, not a failure
that can be filled by assumption.

The package prepack guard allows blank `.gitkeep` seed placeholders, the blank
`workspace/history/runs.jsonl`, and deliberate curated examples. It refuses to
package non-empty run history or mutable workspace directories and leaves that
operational evidence untouched.

When a Power BI project is present, run the deterministic validator first. If
`pbir` is installed, run:

```sh
pbir validate "Report.Report" --all
```

Use Fabric or workspace checks only with an approved target and authority. Do
not run an authentication-status check as a substitute for publish proof.

## System route proof

Use a disposable checkout or temporary copy so operational artifacts do not
become seed content:

```sh
python3 workspace/engine/tracer.py --promote-example
python3 workspace/engine/tracer.py --simulate-failure
python3 workspace/engine/tracer.py --recover --promote-example
```

The deterministic demonstration records a successful run, a recoverable failed
run, and a recovery whose `previous_run_id` points to the failed predecessor.
The explicit promotion creates a self-contained example with `README.md` and
`proof.json`.

## Clean-copy recipe

For an independent local copy, copy the checkout to a temporary directory and
run the commands above from that copy. A local copy is sufficient; no remote
or service is contacted by the structural checks, validator, tests, package
dry-run, or tracer.

## Validation report

Record:

```text
Validation run:
Blockers:
Warnings:
Files changed:
Unavailable checks:
Remaining risks:
```

Never claim service refresh, RLS, publish, or native Power BI validation unless
the corresponding evidence exists and its owner and boundary are recorded in
the brief.

## Periodic System audit

The periodic audit is separate from the validation ladder and from per-change
Review. Choose its accumulated-state scope explicitly:

```sh
python3 workspace/engine/system_audit.py --scope repository
python3 workspace/engine/system_audit.py --scope workspace
python3 workspace/engine/system_audit.py --scope both
```

Repository scope reads the configured upstream directly and compares ancestry
in temporary storage; it does not fetch into the audited checkout. Workspace
scope reads the project brief, run/history/proof relations, and failure and
recovery evidence without appending an audit record. A missing required fact
that cannot be read is `BLOCKED`, an observed defect is `FAIL`, and only
complete healthy evidence is `PASS`.

Remote identities must be credential-free. The audit accepts ordinary HTTPS,
SSH/scp-style, and local/file identities, but rejects HTTPS userinfo, SSH
passwords, and query or fragment token material before any Git network command.
