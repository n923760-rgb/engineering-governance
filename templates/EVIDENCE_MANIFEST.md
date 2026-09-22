# Engineering Evidence Manifest

Each important artifact should be represented by a machine-readable manifest entry.

Required manifest identity:
- Task ID
- Source SHA
- Execution environment
- Timestamp

Required per-artifact fields:
- relative path
- SHA-256
- size in bytes
- sensitive-data flag

Rules:
- artifact paths must remain inside the manifest directory tree;
- absolute paths and parent-directory traversal are invalid;
- the recorded file must exist when integrity is verified;
- recorded size must match the actual file size;
- recorded SHA-256 must match the actual file bytes;
- missing or mismatched evidence must never be silently accepted.

Use `scripts/validate-evidence-manifest.py <manifest.json>` to verify integrity.
