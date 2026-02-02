# AI Pair Workflow (Codex + Claude)

## Roles
- Claude: plan, constraints, architecture, review, docs
- Codex: implement, produce diff, fix build/test issues

## Steps
1) Claude writes ai/task-brief.md
2) Codex implements strictly per ai/task-brief.md (plan -> diff -> apply)
3) Run: lint + tests + build/typecheck
4) Claude reviews diff using ai/review-checklist.md
5) Codex fixes blockers only
6) Claude writes PR description + risk + rollback

## Hard rules
- No scope creep
- No drive-by formatting
- Every change must be verifiable (tests/logs)
