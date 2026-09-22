# Changelog

## Unreleased

- Make the repository explicitly the global, project-agnostic engineering governance reference for all software projects.
- Add a global reference entry point, quick-start guide, and ready project-adoption prompt.
- Add standalone adoption-status and protected-action templates.
- Expand bootstrap defaults to the complete protected-action baseline and qualification checks.
- Clarify that published release tags are immutable and project live facts must be derived from the target environment.

## 1.0.0

First stable source baseline for reusable AI-assisted engineering governance.

Includes:
- Master Governance and authority hierarchy;
- Task Packet and Result Packet contracts;
- machine-readable protected-action authorization;
- repository Live Gate and pull-request state verification;
- execution-environment resource preflight;
- Evidence Manifest integrity verification;
- baseline secret scanning;
- adversarial governance qualification;
- safe project bootstrap and adoption guide;
- GitHub Actions Governance CI;
- v1 readiness gate.

Release rule:
- the `v1.0.0` tag must point to the exact `main` SHA that passes Governance CI after this version is merged.

## 1.0.0-rc.1

Qualified release-candidate baseline used to prove the v1 controls before stable promotion.
