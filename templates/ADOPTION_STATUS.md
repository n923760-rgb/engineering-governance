# Governance Adoption Status

Status: DRAFT_LIVE_VERIFICATION_REQUIRED
Governance baseline: Global Engineering Governance Reference

## Project Identity

PROJECT NAME:
REPOSITORY:
OFFICIAL BRANCH:

## Live Qualification

- [ ] Repository identity verified from live source.
- [ ] Official branch verified.
- [ ] Current official remote HEAD verified for the current adoption task.
- [ ] Repository/project instructions identified and read.
- [ ] Applicable subsystem contracts identified.
- [ ] Open/conflicting PR state inspected.
- [ ] CI system and required checks identified.
- [ ] Branch protection/rulesets inspected.
- [ ] Secret scanning/security baseline inspected.
- [ ] Execution environment identified.
- [ ] Protected actions defined.
- [ ] Stop conditions defined.
- [ ] Test strategy defined.
- [ ] Evidence/report locations defined.
- [ ] Secrets mechanism verified.
- [ ] Backup/restore policy defined where applicable.
- [ ] Task Packet / Result Packet protocol accepted.

## Governance Qualification Fixtures

- [ ] Wrong expected SHA stops safely.
- [ ] Dirty canonical source stops safely where required.
- [ ] Unauthorized protected action stops safely.
- [ ] Conflicting PR stops safely where applicable.
- [ ] Missing evidence remains visible and does not become PASS.
- [ ] Resource/environment failure stops safely.
- [ ] Secret exposure attempt is rejected.
- [ ] Scope expansion is rejected until separately authorized.

## First Governed Workflows

- [ ] One READ-ONLY DIAGNOSIS completed with attributable Result Packet.
- [ ] One isolated IMPLEMENTATION completed with attributable validation.
- [ ] Exact-source CI/result verified.
- [ ] Any merge used explicit owner authorization.
- [ ] Post-merge validation recorded when applicable.

Change status to `QUALIFIED` only after the applicable checks are proven.

Governance qualification does not mean the product itself is production-qualified.
