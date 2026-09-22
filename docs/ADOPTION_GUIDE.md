# Adopting Engineering Governance in Any Project

The governance repository is a reusable control system. A target project must still derive its own facts from its current production source and environment.

## 1. Bootstrap

From a trusted checkout of this governance repository:

```bash
python scripts/bootstrap-project.py \
  --project-name "Example Project" \
  --repository "owner/example-project" \
  --official-branch main \
  --destination /path/to/example-project
```

The command creates only a `governance/` directory in the target project. It refuses to overwrite any generated governance file that already exists.

## 2. Live Qualification

Do not treat generated values as proof.

Verify from the target project's current state:
- repository identity;
- official branch;
- remote official HEAD;
- repository instructions;
- CI system and required checks;
- runtime/deployment environment;
- test strategy;
- evidence paths;
- secret handling;
- backup/restore strategy;
- protected paths;
- project-specific stop conditions.

Keep live SHAs in Task Packets and Result Packets, not in long-lived project profiles.

## 3. First Governed Task

Start with a READ-ONLY DIAGNOSIS:
- issue a Task Packet;
- run Live Gate;
- inspect only;
- produce a Result Packet;
- verify evidence attribution.

Then perform one small isolated IMPLEMENTATION task:
- one concern;
- one branch/worktree;
- smallest deterministic test first;
- CI verification;
- controlled merge only when authorized.

## 4. Adoption Qualification

Only mark `governance/ADOPTION_STATUS.md` as QUALIFIED after both workflows succeed and the evidence points to the exact tested source.

## Safety Properties

The bootstrapper intentionally does not:
- copy credentials;
- copy environment paths;
- copy historical SHAs;
- copy project-specific contracts from another repository;
- infer production topology;
- overwrite existing governance files;
- declare a project qualified automatically.
