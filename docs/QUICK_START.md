# Quick Start — Master Engineering System

## New or existing project

1. Identify the target repository.
2. Verify the actual execution mode available in the current session.
3. Start in **READ-ONLY** mode.
4. Perform the Master Re-baseline: repository identity/live state, authority, architecture/source ownership, build/release model, tests/CI, security/privacy, runtime evidence, governance gaps, existing roadmap, and lab/toolchain requirements.
5. Produce one `MASTER ENGINEERING BASELINE REPORT`.
6. If `/ENGINEERING/MASTER_ROADMAP.md` exists, read it after live truth verification; if it does not, propose its initial contents in the report.
7. Do **not** create/update the roadmap during the read-only round.
8. In a later explicitly authorized governance-mutation round, bootstrap or establish:
   - `/ENGINEERING/MASTER_ROADMAP.md`
   - `/ENGINEERING/REPORTS/`
   - `/ENGINEERING/EVIDENCE/`
   - repository governance/profile/environment files.
9. Fill placeholders only from live target-project facts.
10. Qualify the execution environment / engineering lab.
11. Prove governance stop conditions fail closed.
12. Begin normal engineering with bounded Task Packets and attributable Result Packets.

## Existing projects

Do not rewrite working architecture merely to fit governance. Reuse authoritative project documentation where it already owns a subject and add only missing governance layers.

Never create a second roadmap for the same project.

## Before every source mutation

Verify live repository state and actual execution capability again.

## Before every protected action

Verify explicit current owner authorization for that exact action and scope.

## Validation vocabulary

`PASS` / `FAIL` / `BLOCKED` / `UNKNOWN` / `NOT RUN` / `SKIPPED`
