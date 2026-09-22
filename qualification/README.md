# Governance Qualification

This directory contains adversarial tests for the governance safety gates.

The suite deliberately creates disposable, synthetic bad states and verifies that the tooling stops safely rather than mutating source or claiming success.

## Covered in this phase

- valid Task Packet accepted;
- missing required Task Packet field rejected;
- malformed expected SHA rejected;
- clean expected repository state accepted;
- repository identity mismatch rejected;
- wrong branch rejected;
- dirty worktree rejected;
- unexpected official remote HEAD rejected;
- clean tracked text passes the baseline secret scanner;
- a synthetic secret-like value is rejected.

All Git repositories and secret-like values used by the suite are temporary fixtures. No production repository, credential, or infrastructure is modified.

## Run

```bash
python qualification/run-qualification.py
```

A successful run ends with:

```text
PASS: governance stop-condition qualification suite completed
```

This phase does not yet qualify protected-action authorization or Result Packet evidence completeness; those are separate governance controls and should be added as bounded follow-up tasks.
