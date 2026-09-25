# Protected Actions Authorization

Protected actions normally require explicit current owner authorization.

## Default Protected Actions

- merge
- release
- tag
- signing
- store publication
- production deployment
- DNS changes
- destructive database migration
- production credential rotation
- protected production database operations
- server/VPS/cloud destruction or reinstall
- repository deletion
- branch history rewrite / force push
- permanent release-artifact deletion
- destructive billing/cloud-resource actions

Technical access does not equal authorization.

## Authorization Record

ACTION:
STATUS: [AUTHORIZED | NOT AUTHORIZED]
AUTHORIZED BY:
AUTHORIZATION SOURCE:
SCOPE:
TARGET:
BOUNDARY:
REQUIRED EVIDENCE BEFORE EXECUTION:
RESULT:

Historical or unrelated authorization must never be silently reused.
