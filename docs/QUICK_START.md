# Quick Start — Any Project

## New project

1. Create or identify the project repository.
2. Start governance adoption in READ-ONLY mode.
3. Verify repository identity, official branch, current HEAD, instructions, open/conflicting PRs, CI, branch protection/rulesets, secret scanning, execution environment, test strategy, evidence/report locations, and backup/restore policy.
4. Bootstrap the `governance/` directory.
5. Fill placeholders only from live project facts.
6. Run governance qualification fixtures.
7. Mark adoption `QUALIFIED` only after safe-stop behavior is proven.
8. Begin normal engineering with atomic Task Packets.

## Existing project

1. Do not rewrite product architecture merely to fit this governance system.
2. Map the current repository and existing authoritative contracts first.
3. Reuse existing project documentation where it already owns a subject.
4. Add only missing governance layers.
5. Keep governance adoption separate from product behavior changes.
6. Require exact-source validation on the adoption PR.
7. Verify post-merge validation on the resulting official HEAD.

## Before every source mutation

Verify live state again.

## Before every protected action

Verify explicit current owner authorization for that exact action and scope.
