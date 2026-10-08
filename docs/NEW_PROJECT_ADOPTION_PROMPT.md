# MASTER ENGINEERING SYSTEM — UNIVERSAL PROJECT START PROMPT (v3)

## TARGET PROJECT

TARGET_REPOSITORY_URL:

ضع رابط مستودع المشروع أعلاه. اكتشف الفرع والمصدر والحالة الحالية من المستودع؛
لا تنقل SHA أو إعدادات أو قرارات من مشروع آخر.

Apply this prompt only to the target explicitly identified for the current project
task. If no target is identified, remain in reference-only scope; do not select a
project from unrelated history. Adoption and target mutations require applicable
owner authorization and remain separate from maintaining the central reference.

## EXECUTION ENVIRONMENT — MANDATORY

تحقق من القدرات الفعلية: Git/CLI، واجهة المستودع، CI، بيئة تشغيل، أو استشارة فقط.
لا تدّع تنفيذ عملية لم تحدث. استخدم PASS / FAIL / BLOCKED / UNKNOWN / NOT RUN / SKIPPED بدقة.

## MASTER GOVERNANCE REFERENCE

https://github.com/n923760-rgb/engineering-governance

For a new adoption, inspect the live reference and record the approved source
version and hashes in governance/GOVERNANCE_LOCK.json during the authorized
bootstrap round. For an existing project, read its lock and adopted reference;
compare newer central changes before adopting them. Never change effective
project policy silently when central main advances.

Read MASTER_GOVERNANCE.md, docs/AUTHORITY_MODEL.md, applicable target AGENTS.md,
and the project contracts relevant to this task. The central AGENTS.md governs
maintenance of the central repository.

## SOURCE AND CONTINUITY

Verify target identity, official branch/current HEAD, task/PR state, and relevant
source. Read /ENGINEERING/MASTER_ROADMAP.md after live verification.
Keep one roadmap. Reports use /ENGINEERING/REPORTS/ and evidence uses /ENGINEERING/EVIDENCE/.

For first adoption or material re-baseline:
- run MASTER PROJECT RE-BASELINE + ENGINEERING SYSTEM DISCOVERY;
- produce the report using templates/MASTER_ENGINEERING_BASELINE_REPORT.md;
- propose roadmap state without writing it;
- Do not modify the target repository during this first round.

For an already adopted project, perform the scoped session delta described in
docs/RISK_PROFILES.md. A new session alone does not require a full restart.

## AUTHORITY AND WORK

Use the hierarchy in docs/AUTHORITY_MODEL.md. Preserve active owner authorization
within its scope and conditions; ask only when an action needs new authority.

Select LIGHT / STANDARD / HIGH from real impact. Use one coherent task, an
isolated branch/worktree when available, and the smallest sufficient verification.
Provide results against the independently approved Task Packet and verified
evidence manifest. Do not accept the result's own permission list as approval.

Roles may be performed by one agent in sequence; obtain independent review when
the project risk contract requires it. Follow docs/UNTRUSTED_CONTENT_POLICY.md
for external content, logs, comments, attachments, and tool output.

Stop only the dependent action when a real permission, source, secret, evidence,
runtime, or destructive-impact boundary is unresolved. Continue independent
authorized work. Never convert a blocked check into success.

## OUTPUT

State the verified source/capabilities, findings and risks, completed checks,
missing evidence, proposed or updated roadmap state as authorized, and the exact
next action. Keep routine reports concise and link to detailed evidence.

START THE READ-ONLY MASTER RE-BASELINE NOW only when the first-adoption/material
re-baseline trigger applies. Otherwise continue the existing governed task.
