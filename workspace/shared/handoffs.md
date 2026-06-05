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

96. 2026-06-06 — FROM human TO orchestrator — v13: make hold-R restart use the same progress-bar position as hold-Q quit, and color the restart arc violet.
97. 2026-06-06 — FROM orchestrator TO artist — v13: set restart-arc centres = quit-arc centres (PAUSE & GAME_OVER) and recolor the restart arc violet; scoped Artist → Programmer → QA (lazy).
98. 2026-06-06 — FROM artist TO programmer — v13: move R-arc onto the Q-arc centre (PAUSE (300,483) / GAME_OVER (300,545)) and recolor its fill violet BONUS_BOMB #B464F5 per art_spec/v13.md.

99. 2026-06-06 — FROM programmer TO qa-tester — v13: R-arc centres now = Q-arc centres + R fill violet BONUS_BOMB (Q stays amber, R drawn after Q); smoke gate green.
100. 2026-06-06 — FROM qa-tester TO orchestrator — v13 PASS: smoke green, R/Q arcs co-located (PAUSE 300,483 / GAME_OVER 300,545), R fill violet on top of amber Q, timing/idle-visibility unchanged, no AC regression.

101. 2026-06-06 — FROM orchestrator TO human — v13 shipped: backlog ticked, project state updated to v1–v13 shipped & passed QA. Project complete; awaiting next theme/increment.
