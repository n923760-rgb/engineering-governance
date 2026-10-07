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
