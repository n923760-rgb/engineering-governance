# MCP Server Lifecycle and Trust Policy

Status: reference policy; adopted projects must qualify the relevant controls against their live environment.

## Scope and authority

MCP servers, agent plugins, skills, prompts, and tool manifests are executable or
authority-adjacent supply-chain inputs, not trusted merely because an agent
recommended or installed them. Treat package names, tool descriptions, discovery
responses, and installation commands from models or external content as untrusted.

The Controller selects a verified candidate and grants only task-scoped tool
authority. The Executor may not add, replace, enable, or update an MCP server,
tool connector, plugin, or skill merely to complete its own task. Such changes
require a bounded authorized task and review. No installed tool can self-approve.

## Required inventory and approval

Before enabling a server record in a project-owned inventory:
- exact package/repository identity, publisher, version and immutable digest or
  commit where available; transport, runtime, installation source, and maintainer;
- maintenance and deprecation/archival status, known advisories, dependency
  provenance, license, update owner, and last review date;
- exposed tools and schemas, credentials and delegated scopes, sensitive data
  reachable, file-system/network access, egress endpoints, and audit location;
- an approved task/use case, risk level, independent approver where required,
  tested rollback, and revocation path.

Default to deny. Do not select an abandoned/archived reference package by name
recognition. Prefer an actively maintained, vendor-supported implementation
after independently checking its official provenance. Unknown identity or
maintenance status is BLOCKED for installation and invocation, not PASS.

Treat ephemeral `npx`, `uvx`, downloaded scripts, containers, and local agent
configuration as deployable dependencies: lock and inspect them too. Never
silently execute `latest` or a mutable image tag in a privileged agent context.
A package allowlist does not by itself make tool output or generated instructions
trusted.

## Runtime isolation

- Scope filesystem mounts, process privileges, network egress, credentials,
  session identity, lifetime, resource budgets, and concurrency to the task.
- Separate read-only discovery from credentialed mutations. Require explicit
  Controller approval for tool invocations that cross trust boundaries, change
  repositories/permissions, or access secret-bearing data.
- Reject unsolicited secondary calls, unexpected recipients, and tool call
  chains that exceed the approved task, even if the requested final answer succeeds.
- Validate tool schemas and arguments; treat tool responses and resource text as
  data, not instruction updates. Reject instructions to change AGENTS.md,
  CLAUDE.md, policy files, or tool settings through untrusted results.
- Record the decision and necessary metadata for each allow/deny invocation
  without leaking prompt contents, credentials, or user files into shared logs.

## CI and qualification

Run controlled synthetic tests for: deprecated server recommendation; changed
package digest; unapproved installation/config mutation; unexpected tool call;
secret-bearing egress; forged tool instructions; privilege escalation; and
rollback/revocation. A passing schema validator does not prove runtime isolation.
Test actual Executor permissions in a disposable sandbox and label missing
runtime evidence UNKNOWN or NOT RUN. Preserve approved inventory snapshots and
review all changes to tool or skill authority files in PRs.

Sources (publication date, not proof of local exposure):
- Glow Labs, MCPhantom, 2026-11-02:
  https://www.glow.io/blogs/mcphantom-ai-coding-agents-are-installing-vulnerable-deprecated-mcp-servers-from-training-data
- OWASP, Practical Guide for Secure MCP Server Development, 2026-02-16:
  https://genai.owasp.org/resource/a-practical-guide-for-secure-mcp-server-development/
