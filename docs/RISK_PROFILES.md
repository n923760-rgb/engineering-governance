# Risk Profiles and Session Continuity

Select the profile from the actual impact, rather than the number of changed
lines. Record the choice and reason in the project profile or task.

| Profile | Typical work | Required proof |
|---|---|---|
| LIGHT | Wording, documentation, reversible presentation changes | Live relevant source, scope, reviewed diff, smallest applicable check; concise result |
| STANDARD | Features, API behavior, normal source changes | Bounded task, relevant regression coverage, approved task/result binding, CI and affected runtime checks |
| HIGH | Authorization, payments, user data, production, destructive migration, signing or release | STANDARD plus applicable independent review, backup/restore, rollback and exact-artifact/runtime gates |

All profiles retain authorization, source integrity, truthful reporting, secret
protection, and protected-action boundaries. A small security change is HIGH.
Profiles do not grant permissions or exempt protected actions.

Machine-readable packets must satisfy the same schemas. LIGHT human workflows
may use a concise task and result when no automation consumes a packet; avoid
inventing files or tests that do not establish a changed contract.

## Full baseline versus session delta

Run the full read-only Master Re-baseline at first adoption or when repository
identity, architecture, release model, or operating boundaries change materially.

For normal continuation:
- verify execution capabilities and current repository/PR state;
- read the existing canonical roadmap and applicable scoped contracts;
- inspect changes since the last relevant checkpoint;
- reuse unaffected evidence with an explicit applicability justification;
- update only affected state, risks, and the next task.

A new conversation alone is not a reason to restart adoption.

## Scoped blockers

Identify the action or claim blocked by missing capability. An unavailable device
blocks that device qualification and dependent release gates. It does not
automatically block independent authorized source work or other available checks.
Never relabel missing verification as PASS.

Do not stop for another approval when an active authorization already covers
the exact action and its conditions. Stop the dependent action when permission,
source integrity, secrets, or destructive consequences are unresolved.
