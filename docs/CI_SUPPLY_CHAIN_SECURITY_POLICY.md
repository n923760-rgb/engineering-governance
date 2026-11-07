# GitHub Actions and Software Supply-Chain Policy

This is a project-agnostic review checklist, not a mandate to rewrite existing
workflows or provision features a target project does not use.

## Workflow identity and trust

- Require explicit workflow/job least-privilege `permissions`; use
  `contents: read` by default. Grant `id-token: write` only to a specific job
  that actually performs trusted OIDC federation.
- Continue pinning externally supplied GitHub Actions to reviewed full commit
  SHAs. Review ownership and update provenance even for pinned SHAs.
- GitHub Actions workflow lockfiles became generally available 2026-10-28.
  `.github/workflows/actions.lock` can additionally lock transitive workflow
  dependencies. Evaluate `gh actions-lock` in an isolated PR, validate stale
  lockfile detection, inspect generated diffs, and measure Dependabot behavior
  before enforcing a Require lockfile policy. Locking is reproducibility, not a
  malware verdict; SHA pinning is still a valid existing baseline.
- Do not grant PR authors access to privileged tokens, secrets, or caches from
  trusted contexts. Treat fork code, workflow artifacts, untrusted build output,
  and mutable external actions as attacker-controlled until validated.
- `pull_request_target` on public repositories is blocked by default starting
  2026-12-02 unless explicitly allowed by applicable Actions policy; GitHub
  announced brownouts on 2026-11-09 and 2026-11-16 (16:00–18:00 UTC).
  Inventory event usage and Insights findings. Retain the default block unless
  a narrow, reviewed use case proves isolation; never checkout/execute untrusted
  PR code in a privileged base-repository context.
- Restrict reusable workflows, artifact permissions, runner/network access and
  cache trust boundaries. Do not grant untrusted CI writes to protected branches.

## Credentials, attestations, and dependency changes

Prefer short-lived GitHub App/OIDC credentials with exact audience, subject,
repository, ref, environment, and cloud trust policy matching. Rotate and scope
legacy credentials as an authorized operation, never as automatic CI remediation.
Avoid broad personal tokens and long-lived cloud keys.

Track direct and transitive dependencies, artifact/image provenance, and
license/advisory status; generate SBOM/attestations where supported and useful.
Record the source commit, builder/runner trust, digest and verification result
before protected releases. Use SLSA/OpenSSF practices proportionate to project
risk; do not claim SLSA compliance from a single tool or unsigned SBOM.

GitHub's 2026-11-03 Dependabot APM support updates supported git dependencies
in `apm.yml` and `apm.lock.yaml`, but provides **version updates, not security
updates**. Enable it only if APM is actually adopted; review diffs in prompts,
skills, AGENTS.md and tool permissions as authority-adjacent code. Never merge
such changes unattended.

## Qualification before adoption

On a disposable branch, verify expected allowed/denied PR events, a deliberately
stale lockfile, artifact verification with a changed digest, and OIDC rejection for
an unexpected ref/subject. Evaluate tradeoffs in runtime, cost, false alarms,
and availability. Preserve current protections until replacement CI evidence
passes and an authorized reviewer approves the migration.

Original vendor sources:
- Workflow lockfiles GA (2026-10-28):
  https://github.blog/changelog/2026-10-28-github-actions-workflow-lockfiles-are-generally-available/
- `pull_request_target` policy timeline (2026-11-02):
  https://github.blog/changelog/2026-11-02-pull_request_target-blocked-by-default-december-2/
- Dependabot APM (2026-11-03):
  https://github.blog/changelog/2026-11-03-dependabot-version-updates-support-agent-package-manager/
- GitHub Agentic Workflows (2026-10-28):
  https://github.blog/changelog/2026-10-28-github-agentic-workflows-generally-available/
