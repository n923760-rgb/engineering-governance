# Engineering Task Packet

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

Rules:
- every requested action must be present in Authorized actions;
- protected actions may appear in Authorized actions only when the current owner explicitly authorized them;
- each authorized protected action must record source = CURRENT_OWNER_INSTRUCTION and a non-empty reference;
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
