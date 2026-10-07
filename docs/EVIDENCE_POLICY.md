# Evidence Policy

Important conclusions require evidence attributable to task, exact source,
execution environment, time, procedure/result, artifact location, and sensitivity.

Use schemas/evidence-manifest.schema.json and validate-evidence-manifest.py.
Retained relative artifacts must exist inside the manifest directory, match their
byte size and SHA-256, and have no traversal or duplicate paths.

Use validate-result-packet.py with a reviewer-selected --task and
--evidence-manifest. It verifies task bytes/identity/authority, manifest identity,
and referenced retained artifacts. An arbitrary string or artifact URI is insufficient.

PASS and FAIL require performed checks with attributable retained proof. UNKNOWN,
BLOCKED, NOT RUN, and SKIPPED require reasons; they may have no execution artifact.
Do not invent evidence merely to satisfy a schema.

Capture external CI/API evidence in a sanitized retained artifact, verify the live
run/response source and status through an available mechanism, and review the claim.
The validator proves retained-byte integrity, not the honesty or authenticity of
an executor or external response. Source and fixture tests do not prove runtime behavior.

Keep historical evidence attached to its original source. Reuse for a changed
source only with an explicit applicability justification. Protect accepted/release/
security evidence and use approved storage for sensitive raw material.
