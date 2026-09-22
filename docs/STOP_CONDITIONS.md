# Stop Conditions

Mutation stops when a safety assumption becomes false.

Common conditions:
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
- test environment cannot prove the required behavior;
- requested action would expand scope.

Stopping safely is an engineering success, not a failure.
