# Engineering Governance v1.0.0

First stable release of the reusable Engineering Governance System for AI-assisted software engineering.

## Included

- Master Governance authority model
- Current-source / Live Gate verification
- Pull-request state verification
- Protected-action authorization contracts
- Task Packet and Result Packet validation
- Evidence Manifest integrity with SHA-256
- Execution-environment capacity preflight
- Baseline secret scanning
- Adversarial governance qualification
- Safe project bootstrap and adoption workflow
- GitHub Actions Governance CI
- v1 readiness gate

## Core Principle

Current Problem → Current Source → Isolated Change → Evidence → Review → Merge Decision

## Adoption

Use `scripts/bootstrap-project.py` to generate a DRAFT governance pack for a target project. The generated pack must be qualified against that project's live source and environment before it is marked qualified.

## Release Integrity

The `v1.0.0` tag must reference the exact stable `main` SHA whose Governance CI run completed successfully.
