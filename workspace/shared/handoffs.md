# Handoffs — the agent-to-agent log (active)

Append-only routing log: **one line per handoff** (FROM → TO + the one-sentence task / verdict).
All detail — numbers, rationale, evidence — lives in your spec or your domain's `history.md`, never
here. More than one line = wrong file.

Format: `<n>. <YYYY-MM-DD> — FROM <role> TO <role> — <one-line task>`
BLOCKER (route upstream): `<n>. <YYYY-MM-DD> — FROM <role> TO <upstream-role> — BLOCKER: <one-line issue>`

> **Fresh page (2026-06-07, for v20).** v1–v19 shipped & passed QA; their handoffs are archived
> (`../archive/handoffs-v1.md`, `handoffs-v2-v5.md`, `handoffs-v6-v12.md`, `handoffs-v13-v19.md`).
> Numbering continues from 153. The next increment's entries start below.

---

153. 2026-06-07 — FROM manager TO human — Turned a new page for v20: archived v13–v19 handoffs + the v16–v19 backlog detail + the v19 framing to `../archive/`; slimmed the shared hot path. Added **automated handoff chains** — the Orchestrator now dispatches each role as a fresh-context subagent (auto mode) instead of relying on human copy-paste; manual HANDOFF blocks remain the fallback. No spec/code changed.
