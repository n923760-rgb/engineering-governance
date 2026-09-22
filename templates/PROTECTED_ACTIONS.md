# Protected Actions Authorization

Protected actions normally require explicit current owner authorization. A stricter target-project policy may require more.

## Default Protected Actions

- merge
- release
- tag
- signing
- production deployment
- destructive database migration
- production credential rotation
- server destruction/reinstall
- repository deletion
- branch history rewrite / force push
- permanent artifact deletion
- billing/cloud-resource destruction

Technical access does not equal authorization.

## Authorization Record

ACTION:
STATUS: [AUTHORIZED | NOT AUTHORIZED]
AUTHORIZED BY:
AUTHORIZATION SOURCE: [current owner instruction/reference]
SCOPE:
TARGET:
BOUNDARY: [one task / one PR / one release / other]
REQUIRED EVIDENCE BEFORE EXECUTION:
RESULT:

A previous, historical, or unrelated authorization must never be silently reused for a different protected action.
