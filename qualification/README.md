# Governance Qualification

This directory contains adversarial tests for the governance safety gates.

The suite deliberately creates disposable, synthetic bad states and verifies that the tooling stops safely rather than mutating source, exceeding authority, accepting corrupted evidence, or claiming unsupported success.

## Covered

Repository live-state safety:
- clean expected repository state accepted;
- repository identity mismatch rejected;
- wrong branch rejected;
- dirty worktree rejected;
- unexpected official remote HEAD rejected.

Task Packet authority:
- valid Task Packet accepted;
- missing required Task Packet field rejected;
- malformed expected SHA rejected;
- requested action outside authority rejected;
- protected action without explicit owner authorization rejected;
- protected action with explicit current-owner authorization accepted.

Result Packet evidence:
- valid Result Packet accepted;
- PASS without attributable evidence rejected;
- NOT RUN without a reason rejected;
- action performed outside task authority rejected.

Evidence manifest integrity:
- valid manifest and artifact accepted;
- SHA-256 mismatch rejected;
- missing artifact rejected;
- parent-directory traversal rejected.

Secret hygiene:
- clean tracked text passes the baseline secret scanner;
- a synthetic secret-like value is rejected.

All Git repositories and secret-like values used by the suite are temporary fixtures. No production repository, credential, or infrastructure is modified.

## Run

```bash
python qualification/run-qualification.py
```

A successful run ends with:

```text
PASS: governance qualification suite completed
```

Further bounded qualification may add conflicting active PR-state enforcement and environment/resource-instability simulation.
