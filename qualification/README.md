# Governance Qualification

This directory contains adversarial tests for the governance safety gates.

The suite deliberately creates disposable, synthetic bad states and verifies that the tooling stops safely rather than mutating source, exceeding authority, accepting corrupted evidence, continuing in an unhealthy environment, or claiming unsupported success.

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

Environment / resource gate:
- healthy writable environment accepted;
- missing working path rejected;
- insufficient free disk rejected before mutation.

Project adoption bootstrap:
- creates a bounded governance starter pack;
- leaves unknown live fields unresolved rather than inventing values;
- marks the project DRAFT until live qualification;
- refuses to overwrite existing governance files;
- rejects invalid repository identities.

Pull request state:
- matching PR repository/number/state/head/base is accepted;
- stale PR head is rejected;
- unexpected closed PR is rejected;
- wrong PR base is rejected;
- no-open-PR expectation is accepted when true;
- conflicting open PR on the work branch is rejected.

Secret hygiene:
- clean tracked text passes the baseline secret scanner;
- a synthetic secret-like value is rejected.

All Git repositories, evidence artifacts, and secret-like values used by the suite are temporary or synthetic fixtures. No production repository, credential, or infrastructure is modified.

## Run

```bash
python -m pip install -r requirements.txt
python qualification/run-qualification.py
```

A successful run ends with:

```text
PASS: governance qualification suite completed
```

The baseline governance safety gates are now covered by deterministic qualification. Project-specific runtime contracts remain the responsibility of each adopted project.

## Hardened contracts

Additional adversarial coverage includes task-type action limits, minimum protected
actions omitted by a packet, standing/revoked/expired/wrong-target approval,
independent approved-task binding, result self-authorization, missing/tampered
retained evidence, manifest source identity, UNKNOWN handling, full source SHAs,
stale/ahead local baselines, declared task descendants, exact repository identity,
governance source hashes/coverage, and dirty/clean reference qualification.

Fixtures qualify these validator contracts only. They do not authenticate owners,
prove actual AI-agent resistance to prompt injection, or qualify product runtime.

## Complete controlled workflows

The same suite also runs a real disposable Git workflow, rather than relying only
on prewritten example results:

- a read-only diagnosis reproduces a failing assertion, retains its actual output,
  and produces a valid FAIL result without changing tracked source or HEAD;
- a separately approved implementation corrects only the synthetic source in an
  isolated worktree, commits it, executes the assertion, and binds its PASS result
  to the actual tested commit and retained command output;
- the diagnosis branch and official fixture main remain unchanged by remediation;
- evidence replay from the diagnosis into implementation is rejected;
- an independently advanced official fixture HEAD blocks dependent continuation.

Tasks and evidence are prepared and supplied by the deterministic fixture harness.
This exercises the CLI integration and attribution contracts; it does not make the
harness an independent reviewer, authenticate a human owner, or test a real AI
executor's tool-permission isolation. Those remain separate qualification gates.
