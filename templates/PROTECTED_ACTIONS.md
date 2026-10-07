# Protected Actions Authorization

Use the minimum protected-action policy in scripts/governance_contracts.py and
add project-specific protections where needed. A task cannot remove the minimum.
Technical access does not equal authorization.

## Authorization Record

ACTION:
AUTHORIZATION ID:
STATUS: [ACTIVE | REVOKED | NOT AUTHORIZED]
AUTHORIZED BY:
AUTHORIZATION SOURCE: [CURRENT_OWNER_INSTRUCTION | OWNER_AUTHORIZATION_RECORD]
REFERENCE:
REPOSITORY:
TARGET:
SCOPE:
BOUNDARY:
CONDITIONS / REQUIRED EVIDENCE:
EXPIRES AT: [optional; timezone-aware timestamp]
REVOCATION STATE:
RESULT:

An active previously granted authorization persists within its recorded target,
scope, boundaries, and conditions. Recheck it before a protected action; a new
session alone does not require reapproval. Unrelated, expired, revoked, or
out-of-scope authorization cannot be reused.

Permission authenticity is established by the controller from owner instructions,
not by an executor writing a JSON record. Machine-readable records bind repository
and action target; scope/conditions and live target state still need review.
