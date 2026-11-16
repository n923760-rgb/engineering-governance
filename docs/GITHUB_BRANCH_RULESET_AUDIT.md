# Read-only GitHub Branch Ruleset Audit

This optional reference-only guard helps detect dangerous gaps in **one specific
GitHub branch ruleset** before proposing any settings changes. It does not edit
GitHub, prove the authenticated owner's approval, or establish the effective
combined protections of all repository, organization and legacy branch rules.
Inspect all applicable protections separately before protected decisions.

## Live audit

Use a scoped read credential in `GITHUB_TOKEN` if GitHub requires authentication.
Do not print or commit the credential. For public repositories, an unauthenticated
read may work; rate limiting and access failures result in UNKNOWN, not PASS.

```bash
python scripts/audit-github-ruleset.py \
  --repository owner/repository \
  --ruleset-id 123456 \
  --branch main \
  --required-context 'Validate Master Engineering System' \
  --min-approvals 1
```

Offline mode: save the **complete** GitHub REST ruleset response as local JSON,
then pass `--fixture path/to/ruleset.json` instead of `--repository` and
`--ruleset-id`. Treat fixture output as diagnostic, not live repository evidence.

Exit `0` = PASS for the configured single-ruleset checks, `1` = FAIL,
`2` = UNKNOWN/unavailable input. Every status blocks a *claim* of complete
protection unless corroborated by current live evidence. Audited checks are:
active branch scope, no deletion/force push, PR reviewer count, dismissal of
stale approvals, exact required status check and strict update policy, and absence
of bypass actors. Unknown GitHub pattern semantics yield UNKNOWN, not PASS.

## Correcting review-approval gaps

Requiring at least one independent approval is desirable **where a legitimate
separate reviewer can actually approve**. On a one-person repository, an approval
requirement can deadlock all merges: the PR author cannot simply approve their
own work. First establish a trusted collaborator/maintainer and an independently
reviewed merge process, then qualify the new ruleset and verify actual behavior
with a disposable PR. Avoid weakening the control or silently adding a bypass to
escape deadlocks. Protect the required CI check and require it on the exact head.

**Owner authorization is distinct from reviewer approval.** Even a ruleset
showing one or more reviews cannot prove that the owner approved a specific
merge or deployment. Owner approval must remain independently attributable at
the protected-action boundary. This script must not automatically change
repository protection settings or trigger merges.

For deterministic offline regression coverage:

```bash
python -m unittest discover -s qualification -p 'test_github_ruleset_audit.py'
```

Always compare the inspected live ruleset with current branch/PR state and CI.
This guard is reference-only until a target project expressly adopts it.
