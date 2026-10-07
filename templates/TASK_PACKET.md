# Engineering Task Packet

## TASK ID
[Stable task identity shared by approved task, result, and evidence.]

## TITLE
[One atomic engineering outcome]

## ROLE
Act as the execution engineer for this task.

## TASK TYPE
[READ-ONLY DIAGNOSIS | IMPLEMENTATION | RUNTIME QUALIFICATION | CI INVESTIGATION | INFRASTRUCTURE MAINTENANCE]

## AUTHORITY
[Exactly what may be read, modified, committed, pushed, triggered, or changed.]

## MACHINE-READABLE ACTION AUTHORITY
Requested actions:
Authorized actions:
Protected actions:
Protected action authorizations:
Action targets:
Risk profile: LIGHT / STANDARD / HIGH

Rules:
- every requested action must be present in Authorized actions;
- the central protected-action minimum cannot be removed by this packet; active owner authorization is required;
- each protected action records source/reference, authorization_id, active status, repository, target, boundary, and optional expiry;
- do not infer protected authorization from implementation authority.

## REPOSITORY
[Repository]

## OFFICIAL BRANCH
[Official branch]

## EXPECTED OFFICIAL HEAD
[Exact SHA verified immediately before issuing the packet]

## EXISTING PR
[When applicable, otherwise NONE]

## EXPECTED PR HEAD
[Exact PR head SHA when applicable, otherwise NONE]

## EXPECTED PR BASE
[Expected PR base branch when applicable, otherwise NONE]

## SCOPE
[Exact concern being addressed]

## OUT OF SCOPE
[Neighboring systems and protected actions]

## LIVE GATE
Before mutation:
- read the current task;
- read applicable repository instructions;
- verify repository identity;
- verify local branch and HEAD;
- verify remote official HEAD;
- verify working-tree state;
- verify PR state when applicable;
- apply all stop conditions.

## TASK
[Outcome-focused engineering instruction.]

## VALIDATION
[Required tests, checks, runtime evidence, static validation, builds, or review steps.]

## ARTIFACTS
[Required output artifacts or NONE.]

## STOP CONDITIONS
[Task-specific stop conditions.]

## REPORT PATH
[Where the final result will be stored.]

## SUCCESS CRITERIA
[Observable state that proves completion.]

Task-type action limits apply independently of the packet's lists. Supply this controller-approved packet independently to the result validator; the executor cannot replace it with its own approval.
