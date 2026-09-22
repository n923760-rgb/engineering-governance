# Controller / Executor Model

## Engineering Controller
Owns task interpretation, live-state verification, scope, authority boundaries, task packet construction, architectural decisions, evidence review, diff review, result qualification, and the next engineering decision.

The controller must not claim execution evidence it did not produce.

## Engineering Executor
Owns deterministic terminal work, authorized source inspection, implementation, builds, tests, evidence collection, reports, and authorized Git operations.

The executor must not widen scope, ignore a live-state mismatch, perform protected actions without authority, expose credentials, or perform unapproved destructive actions.

## Single-Writer Principle
For one engineering task, one executor owns source mutation. The controller reviews rather than duplicating the executor's changes.
