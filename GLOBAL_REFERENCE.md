# Global Engineering Governance Reference

This is the navigation entry point for the central, project-agnostic governance system.

## Authoritative files

1. `MASTER_GOVERNANCE.md` — global rules and authority model.
2. `docs/ADOPTION_GUIDE.md` — project adoption process.
3. `templates/TASK_PACKET.md` — one bounded engineering work order.
4. `templates/RESULT_PACKET.md` — attributable task result.
5. `templates/PROJECT_PROFILE.md` — target-project customization.
6. `templates/REPOSITORY_ENGINEERING_INSTRUCTIONS.md` — repository-specific execution rules.
7. `templates/ENGINEERING_ENVIRONMENT_CONTRACT.md` — execution environment contract.
8. `templates/ADOPTION_STATUS.md` — adoption qualification ledger.
9. `templates/PROTECTED_ACTIONS.md` — protected-action authorization record.

## Permanent operating loop

OWNER GOAL
→ LIVE REPOSITORY VERIFICATION
→ ATOMIC SCOPE
→ TASK PACKET
→ ISOLATED EXECUTION
→ VALIDATION
→ DIFF + EVIDENCE
→ RESULT PACKET
→ CONTROLLER QUALIFICATION
→ OWNER / MERGE DECISION

## Five mandatory questions

Every significant engineering task must answer:

1. What exact source are we working from?
2. Who authorized this exact action?
3. What changed and why?
4. What evidence proves the result?
5. What actions were intentionally not performed?

If any answer is ambiguous, the task is not ready for production use.

## Target-project rule

This repository is the **reference**, not the source of live truth for another project.

Never copy this repository's current SHA into another project's expected HEAD. Never copy a different project's repository identity, secrets, environment paths, infrastructure, CI facts, test counts, or historical decisions.

Derive target facts live.
