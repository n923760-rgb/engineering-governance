AI-Assisted Engineering Governance Master Plan

Purpose

This document defines a reusable engineering governance model for a production software project developed with assistance from AI engineering agents.

The goal is not to define the product architecture itself.

The goal is to ensure that every engineering action is:

- based on current source truth;
- explicitly authorized;
- isolated in scope;
- reviewable;
- reproducible;
- attributable to a specific execution environment;
- supported by real evidence;
- safe to merge or revert;
- protected from accidental repository or production damage.

This governance model should be customized for the target project before implementation begins.

1. Core Engineering Principle

Production source is the authority.

Historical conversations, planning documents, AI memory, old Pull Requests, screenshots, previous reports, and archived SHAs may provide context, but they must never silently replace current repository truth.

Before making any source change, verify the current state directly from the authoritative repository.

The normal rule is:

Current Problem → Current Source → Isolated Change → Evidence → Review → Merge Decision

Never:

Old Context → Assumption → Modification

2. Authority Hierarchy

Every engineering task must follow an explicit hierarchy.

From highest to lowest authority:

1. Current Owner Instruction
   - Defines the current goal.
   - Defines whether the task is read-only or implementation.
   - Defines allowed protected actions.
   - May define expected repository, branch, SHA, PR, environment, or evidence.

2. Repository Engineering Instructions
   - Example: AGENTS.md, CONTRIBUTING.md, engineering policies, or applicable scoped overrides.
   - Own Git safety, mutation rules, testing requirements, stop conditions, and repository-specific constraints.

3. Subsystem Contracts
   - Apply only when their subsystem is actually in scope.
   - Examples:
     - authentication;
     - player;
     - payments;
     - compatibility;
     - deployment;
     - database;
     - API;
     - runtime testing.

4. Engineering Environment Contract
   - Defines execution-machine rules.
   - Examples:
     - development VPS;
     - CI runner;
     - build machine;
     - emulator lab;
     - artifact paths;
     - resource limits;
     - backup/retention.

5. Engineering Guides
   - Advisory technical judgment only.
   - They may guide diagnosis and implementation but do not override repository authority.

6. Task Packet
   - The atomic work order issued for one specific task.
   - It may narrow authority but must never widen authority above the layers that govern it.

No lower layer may override a higher layer.

3. Live Truth Policy

Repository facts must be verified whenever they matter.

Before source mutation, record at minimum:

- repository identity;
- official branch;
- current official remote HEAD;
- local branch;
- local HEAD;
- working-tree state;
- current Pull Request when applicable;
- PR base;
- PR head;
- relevant CI state;
- applicable repository instructions.

Do not rely on a SHA remembered from an earlier conversation when GitHub can be queried directly.

If an expected SHA was supplied and current live state differs:

STOP source mutation.

Investigate the mismatch first.

Never silently continue from an unexpected repository state.

4. Task Classification

Every task must have exactly one primary task type.

Recommended task types:

READ-ONLY DIAGNOSIS

Allowed:

- inspect source;
- inspect Git history;
- inspect PRs;
- inspect CI;
- inspect logs;
- inspect runtime evidence;
- produce findings and reports.

Not allowed unless separately authorized:

- edit source;
- commit;
- push;
- open/modify PR;
- rerun workflows;
- merge.

IMPLEMENTATION

Allowed only within the explicit task scope.

Typical flow:

current source → isolated branch/worktree → implementation → local validation → diff review → final commit → push/PR if authorized.

Implementation authority does not automatically grant merge, release, tag, signing, production deployment, or destructive infrastructure authority.

RUNTIME QUALIFICATION

Used to evaluate existing binaries or source behavior.

Its job is evidence collection, not product correction.

A runtime failure does not automatically authorize editing the product.

CI INVESTIGATION

Used when an existing workflow fails.

Required sequence:

identify the first causal failure → separate secondary failures → inspect relevant artifacts/logs → determine root cause.

CI should not be used as an experimental development shell.

INFRASTRUCTURE / LAB MAINTENANCE

Used for machine-level changes.

Examples:

- packages;
- firewall;
- SSH;
- build environment;
- SDK;
- emulator environment;
- disk/resource policies;
- execution-agent configuration.

This authority must never be inferred from ordinary source implementation authority.

5. Scope Policy

Use:

One Confirmed Problem = One Engineering Scope

For repository changes:

One Confirmed Problem = One Branch = One Pull Request

Do not combine independent defects merely because they were discovered during the same review.

Out-of-scope findings may be recorded but should not be fixed unless the owner expands the task.

Avoid opportunistic cleanup.

Do not redesign neighboring systems while correcting one defect.

Small changes are easier to:

- review;
- test;
- merge;
- revert;
- attribute;
- audit.

6. Canonical Source Policy

All new implementation must start from the current official source unless the owner explicitly authorizes another base.

Do not use:

- an old PR;
- a stale branch;
- an archived ZIP;
- a historical snapshot;
- an old local clone;

as the development base merely because it already contains useful code.

Historical material may be inspected for context.

It must not silently become canonical source.

7. Branch and Worktree Policy

Do not create an implementation branch until there is an authorized implementation task.

The new branch must originate from the exact verified official source expected by the task.

Prefer isolated worktrees when multiple engineering tasks may exist.

Maintain a clean canonical clone if the engineering environment supports it.

Suggested model:

canonical clone
    ↓
verify remote official HEAD
    ↓
create isolated task worktree
    ↓
create task branch
    ↓
perform authorized work

Never perform ordinary task edits directly inside the canonical clone.

8. Git History Protection

Forbidden unless explicitly authorized by a separate exceptional task:

- force push;
- destructive rebase;
- rewriting published history;
- modifying old commits;
- deleting valid commits;
- pushing directly to the protected official branch;
- deleting branches that may still contain needed work;
- creating releases or tags;
- signing release artifacts.

Engineering convenience must not override repository integrity.

9. Commit Policy

Do not commit while development is incomplete.

Before the final task commit:

- inspect repository status;
- inspect changed files;
- inspect the full diff;
- confirm scope;
- run the appropriate validation;
- confirm no accidental files or secrets are included.

Then create one coherent final commit for the bounded task whenever practical.

Avoid:

- diagnostic commits;
- experiment commits;
- one commit per file;
- meaningless “fix” commits;
- repeatedly pushing only to discover compile failures.

A commit represents completed engineering work, not experimentation history.

10. Pull Request Policy

Create or update a PR only after the implementation itself is complete enough for review.

Before PR readiness:

- code change is complete;
- changed files are reviewed;
- full diff is reviewed;
- relevant tests were run;
- known failures are documented;
- scope is clean;
- no secrets are present.

A PR is a review surface, not a development scratchpad.

Do not merge unless merge authority was explicitly granted.

11. CI Policy

CI is a final verification surface.

It should not replace local engineering reasoning.

Do not:

- push repeatedly merely to test whether code compiles;
- rerun successful workflows without cause;
- modify workflows randomly until green;
- treat a green CI result as proof that runtime behavior is correct;
- treat a failed downstream job as the root cause without inspecting the first actual failure.

When CI fails:

1. inspect the complete failure chain;
2. identify the first causal failure;
3. distinguish dependent failures;
4. inspect produced artifacts where relevant;
5. reproduce locally when reasonably possible;
6. correct the root cause;
7. review the entire resulting diff;
8. rerun only the verification needed to prove the correction.

12. Testing Policy

Never claim that a test ran when it did not run.

Every validation item must be classified accurately.

Recommended statuses:

- PASS
- FAIL
- BLOCKED
- SKIPPED
- NOT RUN

BLOCKED is not PASS.

NOT RUN is not a failure, but it must remain visible.

Choose the smallest deterministic test that proves the changed contract, then broaden to relevant regressions.

Testing must follow actual risk rather than ritual.

13. Evidence Policy

Engineering conclusions should be based on attributable evidence.

Possible evidence:

- command output;
- test reports;
- CI runs;
- screenshots;
- runtime recordings;
- logs;
- profiler output;
- checksums;
- APK/build artifacts;
- Git diff;
- Git SHA;
- repository state;
- database query evidence;
- API responses;
- device evidence.

Each important artifact should record:

- task identity;
- source SHA;
- execution environment;
- timestamp;
- command or procedure;
- result;
- artifact path;
- checksum where appropriate.

Do not fabricate missing evidence.

14. Facts, Inferences, and Assumptions

Engineering reports must distinguish:

Facts

Directly observed.

Example:

Test X failed with assertion Y on commit Z.

Inferences

Engineering conclusions drawn from observed facts.

Example:

The evidence indicates the newer request is being overwritten by an older asynchronous result.

Assumptions

Unverified conditions.

Example:

It is assumed that the production API behaves identically to staging.

Assumptions must never be presented as verified facts.

15. Root-Cause Policy

Fix the first causal failure, not merely the most visible symptom.

A proper diagnosis asks:

- who owns the state?
- where does the incorrect state first appear?
- which layer violated its contract?
- is the visible failure dependent on an earlier failure?
- can an older operation overwrite a newer one?
- is there a lifecycle or ownership mismatch?
- is persisted state inconsistent?
- is the error caused by runtime environment rather than product source?

Avoid adding workaround logic when evidence points to a deeper authoritative owner.

16. AI Role Separation

For AI-assisted engineering, use a clear controller/executor architecture.

Engineering Controller

The controller owns:

- task interpretation;
- current live-state verification;
- scope;
- authority boundaries;
- task packet construction;
- architectural decisions;
- evidence review;
- diff review;
- result qualification;
- next engineering decision.

The controller must not claim execution evidence that it did not produce.

Engineering Executor

The executor owns:

- deterministic terminal work;
- source inspection requested by the task;
- authorized implementation;
- builds;
- tests;
- evidence collection;
- report generation;
- authorized Git operations.

The executor must not:

- widen scope;
- ignore a live-state mismatch;
- change protected source;
- merge;
- release;
- expose credentials;
- perform unapproved destructive actions.

Owner

The human owner remains authority for protected decisions such as:

- production-impacting decisions;
- credentials;
- destructive infrastructure actions;
- signing;
- releases;
- tags;
- production deployment;
- final merge when protected by project policy.

The AI system does not replace product ownership.

17. Single-Writer Principle

Two AI agents should not independently modify the same engineering task.

Use:

Owner
  ↓
Controller
  ↓
Atomic Task Packet
  ↓
Executor
  ↓
Commands + Diff + Tests + Evidence
  ↓
Controller Review
  ↓
Owner / Next Engineering Decision

The controller should not duplicate the executor's source modifications.

The executor should not independently decide product scope.

This keeps attribution clear.

18. Standard Engineering Task Packet

Every implementation or investigation should use a bounded task packet.

Recommended template:

TITLE

[One atomic engineering outcome]

ROLE

Act as the execution engineer for this task.

TASK TYPE

[READ-ONLY DIAGNOSIS | IMPLEMENTATION | RUNTIME QUALIFICATION |
 CI INVESTIGATION | INFRASTRUCTURE MAINTENANCE]

AUTHORITY

[Exactly what may be read, modified, committed, pushed,
 triggered or changed.]

REPOSITORY

[Repository]

OFFICIAL BRANCH

[Official branch]

EXPECTED OFFICIAL HEAD

[Exact SHA verified immediately before issuing the packet]

EXISTING PR

[When applicable]

EXPECTED PR HEAD

[When applicable]

SCOPE

[Exact concern being addressed]

OUT OF SCOPE

[Neighboring systems and protected actions]

LIVE GATE

Before mutation:
- read the current task;
- read applicable repository instructions;
- verify Git state;
- verify remote official HEAD;
- verify PR state when applicable;
- apply all stop conditions.

TASK

[Outcome-focused engineering instruction.]

VALIDATION

[Required tests, checks, runtime evidence, static validation,
 builds, or review steps.]

ARTIFACTS

[Required output artifacts or NONE.]

STOP CONDITIONS

[Task-specific stop conditions.]

REPORT PATH

[Where the final result will be stored.]

SUCCESS CRITERIA

[Observable state that proves completion.]

Do not duplicate the entire repository governance document inside every task packet.

Reference stable contracts instead.

19. Standard Engineering Result Packet

Every significant task should produce an attributable final report.

Recommended structure:

# Engineering Task Result

## Task Identity
Task ID:
Task type:
Executor:
Execution environment:
Started:
Completed:

## Repository Identity
Repository:
Official branch:
Verified remote official HEAD:
Work branch/worktree:
Exact tested HEAD:
PR:
Git status before:
Git status after:

## Authority
Authorized actions:
Actions actually performed:

## Scope
Completed:
Observed but intentionally left out of scope:

## Commands Actually Run
Command:
Exit code:
Result:
Evidence path:

## Validation Actually Run
Check:
Result: PASS / FAIL / BLOCKED / SKIPPED
Evidence:

## Validation Not Run
Check:
Reason:

## Findings

### Facts
...

### Inferences
...

### Assumptions
...

## Changes
Files changed:
Purpose:
Diff summary:
Commit:
Push:
PR:

## Artifacts
Path:
SHA-256:
Size:
Sensitive data: yes/no

## Failure Analysis
First causal failure:
Secondary failures:
Stop condition reached:

## Residual Risks
...

## Recommended Next Action
One smallest next engineering action.

Never transform a planned command into an executed result.

20. Secrets Policy

Secrets must never appear in:

- Git;
- task prompts;
- AI reports;
- screenshots intended for sharing;
- shell history when avoidable;
- CI logs;
- evidence archives;
- PR comments.

Examples:

- API keys;
- access tokens;
- SSH private keys;
- passwords;
- signing keys;
- recovery codes;
- database credentials.

Prefer:

- secret stores;
- environment injection;
- owner-entered credentials;
- least-privilege machine credentials;
- repository-scoped access.

Reports may include the secret's logical name and rotation state, never the value.

21. Engineering Environment Policy

The development machine or VPS should be treated as reproducible infrastructure rather than a manually maintained mystery machine.

Maintain:

- machine/tool versions;
- environment manifest;
- bootstrap automation;
- health checks;
- storage policy;
- cache policy;
- report/evidence directories;
- backup policy;
- secret inventory;
- rebuild instructions.

Separate:

Source
Evidence
Reports
Artifacts
Caches
Temporary Runs
Machine Configuration
Secrets

Caches are disposable.

Evidence and reports may be durable.

Source authority remains the repository.

22. Resource and Concurrency Policy

Define explicit resource ownership for constrained engineering machines.

Avoid running multiple heavy operations simultaneously when doing so could invalidate results or destabilize the system.

Examples of heavy operations:

- clean builds;
- emulator workloads;
- integration tests;
- packaging;
- large static-analysis runs.

If needed, use a machine-level lock so only one heavy workload runs at once.

Performance conclusions are invalid when the host itself is under abnormal memory, swap, storage, or CPU pressure.

23. Storage and Retention Policy

Classify stored data.

Never automatically delete

- repository source required for active work;
- reports tied to open work;
- accepted evidence;
- release evidence;
- security evidence;
- manifests;
- governance contracts.

Safe candidates for bounded cleanup

- caches;
- temporary builds;
- stale test runs;
- reproducible emulator state;
- old non-authoritative artifacts.

Cleanup must never use broad unresolved paths.

Destructive cleanup should support dry-run and produce an audit manifest.

24. Backup Policy

Snapshots are not backups.

Critical engineering state should have an independent backup strategy.

Back up:

- governance configuration;
- manifests;
- important reports;
- accepted evidence;
- selected artifacts;
- non-secret infrastructure definitions.

Do not waste backup capacity on easily regenerated caches.

A backup system is not considered qualified until a restore test succeeds.

25. Document Architecture

Avoid creating several overlapping rulebooks.

Recommended responsibility split:

Project Instructions

Own:

- project-level task authority;
- controller behavior;
- communication;
- protected product decisions;
- current project workflow.

Repository Engineering Instructions

Own:

- Git rules;
- branch rules;
- commit/PR rules;
- mutation authority;
- tests/evidence requirements;
- repository stop conditions.

Engineering Guide

Own:

- technical diagnostic guidance;
- architecture principles;
- review heuristics.

It should be advisory rather than authority for Git operations.

Subsystem Contracts

Own only their subsystem semantics.

Engineering Environment Contract

Own:

- execution-machine behavior;
- resource rules;
- paths;
- toolchain;
- evidence storage;
- retention;
- backup;
- rebuild.

Project Sources / Resource Map

Own:

- links and locations of authoritative resources.

It should not become a second rulebook.

26. Stop Conditions

Mutation must stop when a safety assumption becomes false.

Typical stop conditions:

- unexpected official HEAD;
- wrong branch;
- dirty canonical source;
- conflicting active PR;
- task authority ambiguity;
- repository instruction conflict;
- secret exposure;
- destructive operation not explicitly authorized;
- unexpected production data;
- missing required evidence;
- environment instability;
- resource exhaustion;
- test environment incapable of proving the required behavior;
- requested action would expand scope.

Stopping safely is an engineering success, not a failure.

27. Protected Actions

The following should normally require explicit owner authorization:

- merge;
- release;
- tag;
- signing;
- production deployment;
- destructive database migration;
- production credential rotation;
- server destruction/reinstall;
- repository deletion;
- branch history rewrite;
- permanent artifact deletion;
- billing or cloud-resource destruction.

Technical access does not equal authorization.

28. Completion Definition

A task is not complete merely because code was written.

Completion requires the applicable combination of:

- correct current source;
- bounded scope;
- reviewed diff;
- repository instructions followed;
- no accidental files;
- appropriate validation;
- evidence collected;
- failures honestly classified;
- final commit when authorized;
- PR state when authorized;
- no protected action performed without authority;
- residual risks documented.

29. Governance Rollout Plan

A new project can adopt this model incrementally.

Phase 0 — Governance Design

Define:

- repository authority;
- project instructions;
- role split;
- task types;
- protected actions;
- report structure;
- stop conditions.

Phase 1 — Repository Foundation

Create:

- repository engineering instructions;
- branch protection;
- basic CI;
- PR discipline;
- secret scanning.

Phase 2 — Engineering Environment

Create a reproducible development/build environment with manifests, health checks, backups, and resource policy.

Phase 3 — Task / Result Protocol

Standardize task packets and result packets.

Phase 4 — AI Executor Qualification

Prove that the executor:

- obeys scope;
- stops on mismatches;- cannot silently widen authority;
- reports commands honestly;
- protects secrets.

Phase 5 — CI Qualification

Verify builds, tests, evidence, artifact attribution, and exact-SHA execution.

Phase 6 — Governance Qualification

Run controlled fixture tasks that intentionally introduce:

- wrong SHA;
- dirty worktree;
- unauthorized action;
- missing test evidence;
- resource failure.

The system should stop safely.

Phase 7 — Production Engineering

Only after governance is proven should the same process be used for normal production development.

30. Final Operating Model

The desired permanent engineering loop is:

OWNER GOAL
     ↓
LIVE REPOSITORY VERIFICATION
     ↓
CONTROLLER DEFINES ATOMIC SCOPE
     ↓
TASK PACKET
     ↓
EXECUTOR WORKS IN ISOLATION
     ↓
LOCAL VALIDATION
     ↓
DIFF + TESTS + EVIDENCE
     ↓
FINAL RESULT PACKET
     ↓
CONTROLLER QUALIFICATION
     ↓
OWNER / NEXT TASK / MERGE DECISION

The system should optimize for:

correctness over speed

evidence over claims

current source over memory

small changes over broad rewrites

explicit authority over implied permission

root cause over visible symptom

reproducibility over manual machine knowledge

reviewability over automation for its own sake

Customization Before Use

Before adopting this governance model, replace the generic concepts with the target project's real information:

PROJECT NAME:
REPOSITORY:
OFFICIAL BRANCH:
REPOSITORY INSTRUCTION FILE:
PROJECT INSTRUCTION FILE:
ENGINEERING GUIDE:
SUBSYSTEM CONTRACTS:
CI SYSTEM:
EXECUTION ENVIRONMENT:
CONTROLLER:
EXECUTOR:
PROTECTED ACTIONS:
TEST STRATEGY:
EVIDENCE LOCATION:
REPORT LOCATION:
BACKUP STRATEGY:

Do not copy repository names, SHAs, server identities, credentials, paths, test counts, infrastructure details, or historical decisions from another project.

Derive them from the new project's own current environment.

Final Governance Principle

The engineering system should always be able to answer five questions:

1. What exact source are we working from?
2. Who authorized this exact action?
3. What changed and why?
4. What evidence proves the result?
5. What actions were intentionally not performed?

If any of those answers is ambiguous, the engineering task is not yet ready for production use.