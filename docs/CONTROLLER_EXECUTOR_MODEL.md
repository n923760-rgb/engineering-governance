# Controller / Executor Model

The controller owns task interpretation, live-state checks, scope, approved
inputs, architectural judgment, evidence/diff review, and the next decision.

The executor owns authorized source work, commands, tests, builds, artifacts,
and attributable results. It cannot issue its own approval or widen task scope.

One agent may perform these roles sequentially for LIGHT and STANDARD work.
Label execution and review accurately; self-review is not independent review.
Use an independent reviewer for HIGH work when the applicable project contract
requires one. Do not create multiple agents merely to satisfy a role diagram.

For multiple executors, assign one writer per task/owned area, isolated worktrees,
shared-resource locks where needed, and a controller responsible for conflicts.
No agent may silently modify another task's approved inputs.

The human owner remains authority for protected decisions. An active standing
authorization may cover repeated actions within its scope; verify its target,
boundaries, conditions, expiry, and revocation state before use.
