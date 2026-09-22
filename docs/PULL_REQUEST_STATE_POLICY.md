# Pull Request State Policy

When a task references an existing pull request, its live state is part of the source identity.

Before mutation or merge decisions, verify:
- repository identity;
- PR number;
- PR state;
- exact PR head SHA;
- expected base branch.

When a task expects no active PR for the work branch, verify that no open PR exists for that head branch.

Use:

```bash
python scripts/verify-github-pr-state.py \
  --repository owner/repo \
  --pr-number 123 \
  --expected-head <sha> \
  --expected-base main
```

Or to prove that a branch has no open PR:

```bash
python scripts/verify-github-pr-state.py \
  --repository owner/repo \
  --expect-no-open-pr-for-head feature/example
```

Live mode requires `GITHUB_TOKEN` with the minimum read permission needed for pull requests. Qualification uses offline fixtures and does not require network access.

A PR-state mismatch is a stop condition. Do not continue from a stale Task Packet.
