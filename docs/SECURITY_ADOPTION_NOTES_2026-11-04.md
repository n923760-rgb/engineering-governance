# Security Governance Intake — 2026-11-04

Status: **proposed central reference controls**. These notes are not evidence
that any target project has adopted them or that its VPS is safe.

| Source and publication | New/recent insight | Central reference decision | Project qualification |
|---|---|---|---|
| Glow Labs, MCPhantom, 2026-11-02 | Agent-suggested deprecated MCP packages may evade normal managed-dependency inventory | Add server provenance, lifecycle review and deny-by-default installation | AI Lab: inspect actual per-user MCP configuration and ephemeral installs |
| GitHub, Dependabot APM, 2026-11-03 | Version updates now support APM manifests; not security update coverage | Treat agent skills/instructions as reviewed supply-chain inputs | Activate only where APM manifests exist; inspect PR and lock changes |
| GitHub, Actions lockfile GA, 2026-10-28 | Lock transitive action dependencies for onboarded workflows | Optional qualified lockfile adoption while retaining reviewed SHA pins | Compare a sandbox lockfile with current Actions and Dependabot |
| GitHub, `pull_request_target` rule, 2026-11-02 | Default block on public repositories from 2026-12-02 | Document event isolation and narrow exception criteria | Inventory project workflows before 2026-11-09 brownout |
| GitHub, Agentic Workflows GA, 2026-10-28 | Agent workflow sandboxing and safe-output mechanisms exist | Evaluate as optional bounded automation, not an authorization substitute | Test write permissions, provenance, budgets and safe-output review |
| OWASP, MCP secure development guide, 2026-02-16 | Scoped authorization and session isolation principles | Add MCP threat model and real runtime adversarial tests | Require an isolated Executor permission exercise |

Evidence links:
- https://www.glow.io/blogs/mcphantom-ai-coding-agents-are-installing-vulnerable-deprecated-mcp-servers-from-training-data
- https://github.blog/changelog/2026-11-03-dependabot-version-updates-support-agent-package-manager/
- https://github.blog/changelog/2026-10-28-github-actions-workflow-lockfiles-are-generally-available/
- https://github.blog/changelog/2026-11-02-pull_request_target-blocked-by-default-december-2/
- https://github.blog/changelog/2026-10-28-github-agentic-workflows-generally-available/
- https://genai.owasp.org/resource/a-practical-guide-for-secure-mcp-server-development/

No public article or remembered service version establishes actual exposure.
Previously reported PDF, Brotli, and kernel advisories remain **unverified at
deployment** until checked against running artifacts. Do not duplicate alerts
without new attributable evidence. Reference-only work must not mutate TYFINO,
Telegram Services, Smart Merchant, AI Lab, or any target project.
