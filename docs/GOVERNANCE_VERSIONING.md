# Adopted Governance Versions

Inspect current central source at adoption. After owner-authorized bootstrap,
governance/GOVERNANCE_LOCK.json records the reference version, source commit when
clean, actual file hashes, date, and selected risk profile.

A lock generated from dirty or non-Git source records null source_commit_sha.
Observed Git HEAD is diagnostic context, not a claim that modified bytes belong
to that commit. All generated adoption files remain DRAFT until live qualification.

Existing projects continue under their approved adopted version. Inspect central
updates, review changed contracts and compatibility, qualify the proposed source,
then update the project's lock through a bounded authorized change. Do not load
current main as a silent replacement for adopted instructions.

Validate an independently selected source snapshot:

```bash
python scripts/verify-governance-lock.py /path/to/project/governance/GOVERNANCE_LOCK.json \
  --source /path/to/approved/reference --require-clean-source
```

Without --require-clean-source, the tool can compare captured snapshot hashes,
but never marks project adoption QUALIFIED. A lock verifies attribution and
content; it is not an owner-approval mechanism, product test, or sandbox.

Keep prior adoption evidence in reports/history. A new major version is needed
for incompatible packet or validator interfaces. Development main may use a
prerelease version. Published tags and releases remain immutable.

## Migration from v1 contracts to 2.0.0-dev.1

This is an unreleased development contract. Migrate only the selected project's
governance in an authorized branch/PR; a central update does not approve a project
upgrade. Keep its existing root AGENTS.md, project contracts, canonical roadmap,
and historical evidence. Do not rerun bootstrap over an adopted project: it
intentionally refuses to overwrite its files.

| Contract | Required migration for new work |
|---|---|
| Toolchain | Install the adopted reference's pinned requirements.txt before validation. |
| Task identity/source | Supply task_id and full 40/64-character Git SHAs; discover current source rather than expanding an old abbreviated SHA by guess. |
| Action limits | Use actions allowed by the declared task type. Source remediation needs an implementation task; read-only/runtime tasks cannot authorize it. |
| Protected approval | Retain only active owner-issued records for authorized protected actions. Include source, reference, authorization_id, status, repository, exact target, boundary, and optional expiry; match action_targets. An omitted protected_actions entry cannot remove the central floor. |
| Approved task binding | Select the approved task independently. Add its exact task_packet_sha256 to the result after the task is finalized; any task change requires renewed review and hash binding. |
| Result invocation | Pass --task explicitly. When evidence is used, supply --evidence-manifest independently and matching packet references resolved from the result directory. |
| Retained evidence | PASS/FAIL must cite real relative artifact paths in a manifest with matching task_id, tested source_sha, and execution_environment; verify bytes, size and SHA-256. |
| Missing verification | Use BLOCKED / UNKNOWN / NOT RUN / SKIPPED with a reason. Preserve historical claims as historical; do not manufacture missing evidence or reclassify old results as newly qualified. |
| Project adoption | Select LIGHT / STANDARD / HIGH, record the approved source/version and complete file hashes in GOVERNANCE_LOCK.json, and reconcile the existing profile without inventing project facts. |

For an existing project, a controller may prepare a proposed lock with make_lock
from scripts/governance_lock.py against the independently selected reference.
Review it before updating governance/GOVERNANCE_LOCK.json; its generated status
remains DRAFT and does not itself authorize or qualify adoption.

Validate the proposed new task/result/manifest with the adopted tools and run the
affected project checks. Review authority changes and migration evidence before
accepting the project upgrade. Older packets retain their original validator
version; do not edit historical approvals or signed evidence to pass a new schema.

If migration fails, keep the previously approved adoption active. If an accepted
upgrade must be rolled back, use a reviewed corrective commit restoring that
project's prior adoption files and source record. Do not rewrite published Git
history, move release tags, or roll back unrelated product work.
