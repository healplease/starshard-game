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

102. 2026-06-06 — FROM human TO orchestrator — v14: add one-file JSON save system (highscore, runs, enemies/asteroids/bosses killed) — in-memory with occasional writes, file in a user-folder game subfolder; plus a lifetime-stats screen.
103. 2026-06-06 — FROM orchestrator TO business-analyst — v14: lock stat semantics + JSON schema (version, fallback to zeros) + flush-on-game-over/quit contract; scoped BA → Designer → Artist → Writer → Programmer → QA (Level-designer skipped).

105. 2026-06-06 — FROM lead-game-designer TO artist — v14: stats screen = new first-class STATS GameState off START (Tab toggles START⇄STATS, Esc backs out; Tab carved out of "any key starts"; STATS not in Q/R hold sets → arc-free) → gdd/v14.md; lay out the 6-row ledger.

104. 2026-06-06 — FROM business-analyst TO lead-game-designer — v14: locked stat semantics (kill counts only at the `scoring.award` destroy site → split-children/bomb-clears/ram don't count, boss minions do), JSON schema (version + 5 snake_case ints), zero/per-field corrupt fallback, flush-only-on-GAME_OVER/quit contract → `requirements/v14.md` (R92–R98, AC78–AC85); place the stats screen.

106. 2026-06-06 — FROM artist TO writer — v14: laid out STATS screen (5-row ledger over starfield, no dim/arc, label rail x100 / value rail x500, locked y-coords) → art_spec/v14.md; supply STATS_TITLE + 5 row labels (≤260 px each) + back hint string.

107. 2026-06-06 — FROM writer TO programmer — v14: STATS strings final (STATS_TITLE "LIFETIME STATS", 5 single-noun labels, STATS_HINT "Tab / Esc  Back") + NEW START_STATS_HINT "Tab  Stats" line → story/v14.md; build the save system + render STATS/START copy.

108. 2026-06-06 — FROM programmer TO qa-tester — v14: built save system (game/save.py: atomic JSON, %APPDATA% path, zero/per-field-corrupt fallback, env-overridable for headless), wired the 5 counters at their award sites + 2 flush points, added the STATS GameState/nav + screen + START hint; harness 75/75 (fixed a pre-existing v12 AC71 red), smoke/event/balance exit 0.

109. 2026-06-06 — FROM qa-tester TO orchestrator — v14 PASS: harness 75/75, smoke 0/120 f, AC78–AC85 + STATS nav verified, real save provably untouched headlessly, v12-AC71 fix sound; no AC1–AC77 regression.

110. 2026-06-06 — FROM orchestrator TO human — v14 shipped: backlog ticked, project state updated to v1–v14 shipped & passed QA (R1–R98, AC1–AC85, harness 75/75). Project complete; awaiting next theme/increment.

111. 2026-06-06 — FROM human TO orchestrator — v15: replace one-off test scripts with a real pytest suite (e2e fixtures for QA + unit tests for programmer), add ruff/pyright lint+format autofix, and make the programmer run tests+lint-fix after changes.
112. 2026-06-06 — FROM orchestrator TO manager — v15 (process, no game change): design the tests/ layout + pyproject.toml, set the unit-vs-e2e split, define the new testing process, and realign role/process docs; decisions locked (port-then-delete the 75-check harness, pyright basic + lint non-blocking, smoke+pytest blocking); scoped Manager → Programmer → QA (creative pipeline skipped).

113. 2026-06-06 — FROM manager TO programmer — v15: test-infra contract set (tests/ under workspace, root pyproject, 43 unit / 32 e2e split, ruff+pyright+unit-pytest+smoke before every handoff) in qa/test_plan.md §2 — scaffold pyproject + tests/ + conftest and port the 43 unit checks.

114. 2026-06-06 — FROM programmer TO qa-tester — v15: scaffolded root pyproject + workspace/tests/{conftest,unit/}; ported all 43 unit checks (pytest 43/43 green, smoke exit 0); monolith left in place — port the 32 e2e checks, prove ≥75 parity, then delete regression_harness.py.

115. 2026-06-07 — FROM qa-tester TO orchestrator — v15 PASS: ported the 32 e2e checks → tests/e2e/, full pytest suite 75 (43 unit/32 e2e) green, smoke+compileall exit 0, parity old-75↔new-75 proven, regression_harness.py deleted.

116. 2026-06-07 — FROM orchestrator TO human — v15 shipped: backlog ticked, project state updated to v1–v15 shipped & passed QA (R1–R98, AC1–AC85, pytest 75/75). Project complete; awaiting next theme/increment.
