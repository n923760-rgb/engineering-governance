# Pre-Merge Checklist

- [ ] Merge authority is explicit.
- [ ] Exact PR head is known.
- [ ] Full diff was reviewed.
- [ ] Scope remains bounded.
- [ ] Required tests actually ran.
- [ ] BLOCKED / SKIPPED / NOT RUN items remain visible.
- [ ] Required CI checks are complete.
- [ ] No accidental files are included.
- [ ] No secrets are present.
- [ ] Residual risks are documented.
- [ ] Result packet identifies exact tested HEAD.
- [ ] Revert path is understood.
- [ ] Changes to MCP/skills/AGENTS.md/CLAUDE.md and tool authority were independently reviewed, if present.
- [ ] Any security control change has negative-path tests against actual enforcement (or an explicit blocker).
- [ ] Action pins/optional lockfile, OIDC trust rules, PR event privilege and dependency provenance are reviewed if affected.
- [ ] Claims of runtime patching, backup recovery or agent sandboxing are supported by deployed-runtime/restore evidence, not documentation alone.
