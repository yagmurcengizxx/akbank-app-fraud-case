# Cross-agent instructions (Codex / coding agents)

For Claude Code use CLAUDE.md; for Codex and other agents this file is the equivalent entry point.
Read CLAUDE.md, docs/TEAM_WORKFLOW.md, docs/ARCHITECTURE.md and docs/API_CONTRACTS.md **before** editing.
Five developers own five paths: mobile/, backend/, fraud_engine/, webapp/, ops/ plus existing demo/ for SRE. Respect the owner and the contract freeze.
Never overwrite another agent's uncommitted work, reset --hard, force push, amend shared commits or auto-merge without an explicit instruction. Use small PRs with test evidence.
All data is synthetic. Do not claim that stock Android or iOS lets a third-party app transcribe ordinary cellular calls. Do not add banking credentials or real customer records.
Prefer existing dependency-free demo over untested rewrites. Run python -m unittest discover -s tests -v and Python demo for relevant changes.
Reusable role instructions live in .claude/skills/; read the matching SKILL.md even if your coding assistant does not automatically discover Claude skills.

