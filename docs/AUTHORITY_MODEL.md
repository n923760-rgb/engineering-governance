# Authority Model

This document defines the common instruction hierarchy for target projects and
maintenance of this reference.

1. Explicit owner instructions, including an active previously granted
   authorization within its recorded scope, target, boundaries, and conditions.
2. Applicable repository-native instructions, starting with root AGENTS.md.
   Scoped instructions refine their own area; they cannot silently remove root
   safety restrictions or widen owner authorization.
3. Applicable project contracts: subsystem semantics, security, release,
   architecture, and engineering-environment constraints.
4. The central Master Engineering System version adopted by the project.
5. Advisory guides and a bounded Task Packet. A packet narrows the authorities
   above it and cannot manufacture permission.

Conflicts must be resolved explicitly from the highest applicable instruction.
Rules in the central repository's AGENTS.md govern maintenance of that repository;
they are not automatically imported as another project's local instructions.

## Instructions and facts

Instructions define permitted actions and intended behavior. Live source and
observed evidence establish what currently exists. Neither old source nor a
design document can establish a runtime fact without evidence. Current buggy
behavior does not invalidate a new owner-approved requirement.

Reports, roadmaps, conversation history, and memory are context. Verify current
facts before relying on them. Preserve accepted decisions and active authorizations
unless the owner changes them or their scope/conditions no longer apply.

## Approved inputs

The controller supplies the approved Task Packet independently to the result
validator. The result author's permission list is never an authority source.
The central minimum protected-action set is defined in
scripts/governance_contracts.py; a task may add protection but cannot remove it.

The validators check structure, consistency, source attribution, and retained
file integrity. They do not authenticate an owner, sandbox an executor, or prove
that a reported command was executed. Trusted issuance, tool permissions, live
checks, and review remain required.
