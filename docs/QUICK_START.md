# Quick Start — Master Engineering System

## استخدام المرجع لاحقًا

هذا المستودع مرجع رئيسي عام فقط؛ مراجعته أو تحديثه لا يطبّق الحوكمة تلقائيًا
على أي مشروع. عند الرغبة في التطبيق، افتح دردشة المشروع وحدد مستودعه، ثم استخدم
docs/NEW_PROJECT_ADOPTION_PROMPT.md مع رابط المشروع المستهدف.

ابدأ بمراجعة المصدر الحي وتعليمات المشروع والتقرير المطلوب دون تعديل المشروع.
بعد مراجعة النتيجة، يكون أي اعتماد أو تعديل ضمن التفويض الصريح الخاص بالمشروع.
احتفظ بإصداره المعتمد؛ لا تستبدله تلقائيًا كلما تغيّر المرجع الرئيسي.

جاهزية مصدر المرجع لا تعني تأهيل المشروع أو أدوات الذكاء الاصطناعي أو إصدارًا
مستقرًا جديدًا. لكل منها أدلته وقراره المنفصل، ولا يلزم حل عائق تشغيل مشروع
للاستفادة من قواعد المرجع في أعمال أخرى مستقلة ومصرّح بها.

## Adoption and continuation

For a new project or material re-baseline, verify capabilities/source and run a
read-only baseline. Use templates/MASTER_ENGINEERING_BASELINE_REPORT.md. Propose
/ENGINEERING/MASTER_ROADMAP.md without writing it in that round.

For an already adopted project, verify live state, read its adopted lock and
existing roadmap, then inspect only relevant changes and contracts. A new session
does not restart adoption.

Install requirements.txt before running validators. Run bootstrap only in an
authorized mutation round; it preserves existing AGENTS.md and generates draft
governance files, the version/source lock, roadmap, reports, and evidence locations.

Use docs/AUTHORITY_MODEL.md, docs/RISK_PROFILES.md, and
docs/UNTRUSTED_CONTENT_POLICY.md. Keep protected actions within active owner
authorization; do not ask again when its exact scope and conditions still apply.

Validate a result with independently supplied --task and --evidence-manifest.
Never accept a result's own permission list or nonexistent evidence as proof.

PASS / FAIL / BLOCKED / UNKNOWN / NOT RUN / SKIPPED
