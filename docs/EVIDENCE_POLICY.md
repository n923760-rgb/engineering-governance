# Evidence Policy

Important engineering conclusions require attributable evidence.

Record, where applicable:
- task identity;
- source SHA;
- execution environment;
- timestamp;
- command or procedure;
- result;
- artifact path;
- checksum.

Never fabricate missing evidence. Distinguish Facts, Inferences, and Assumptions.

## Evidence Manifest Integrity

Important file artifacts should use a machine-readable evidence manifest containing:
- task ID;
- exact source SHA;
- execution environment;
- timezone-aware timestamp;
- relative artifact path;
- SHA-256;
- byte size;
- sensitive-data flag.

A manifest is not evidence by itself unless the recorded artifact exists and its size and SHA-256 match the recorded values.

Use `scripts/validate-evidence-manifest.py` for deterministic integrity verification. Missing files, path traversal, size mismatches, and checksum mismatches must fail closed.
