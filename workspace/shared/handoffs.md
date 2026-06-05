# Handoffs — the agent-to-agent log (active)

Append-only routing log: **one line per handoff** (FROM → TO + the one-sentence task / verdict).
All detail — numbers, rationale, evidence — lives in your spec or your domain's `history.md`, never
here. More than one line = wrong file.

Format: `<n>. <YYYY-MM-DD> — FROM <role> TO <role> — <one-line task>`
BLOCKER (route upstream): `<n>. <YYYY-MM-DD> — FROM <role> TO <upstream-role> — BLOCKER: <one-line issue>`

> **Fresh page (2026-06-06).** v1–v12 shipped & passed QA; their handoffs are archived
> (`../archive/handoffs-v1.md`, `handoffs-v2-v5.md`, `handoffs-v6-v12.md`). Numbering continues from 94.
> The next increment's entries start below.

---

95. 2026-06-06 — FROM manager TO human — Turned a new page: archived v6–v12 handoffs + v1–v12 backlog + v7–v12 framings to `../archive/`; slimmed the shared hot path; taught the Orchestrator to scope the queue (skip no-impact lanes); made roles lazier (effort scales to change size) + specs more concise. No spec/code changed.

(no active increment yet — the next `FROM human TO orchestrator` kickoff opens it)
