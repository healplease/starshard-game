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

117. 2026-06-07 — FROM human TO orchestrator — v16: create a new boss; each boss-spawn picks randomly between Mothership and the new boss (pool extensible to future bosses); new boss must spawn NO ships and have deadlier attacks.
118. 2026-06-07 — FROM orchestrator TO business-analyst — v16 (new content, full pipeline): formalize requirements for the second boss + random extensible boss-pool selection, with the 2 hard constraints (no ship spawning, deadlier attacks) as new R#/AC#.
119. 2026-06-07 — FROM business-analyst TO lead-game-designer — v16: locked R99–R105/AC86–AC93 (extensible boss registry, uniform-random pick per spawn, v7 framing+cadence unchanged, R103 no-ship + R104 deadlier-than-Mothership as hard gates) → requirements/v16.md; design the new boss's identity/moveset/HP/reward + the deadlier lever (concrete numbers).

120. 2026-06-07 — FROM lead-game-designer TO artist — v16: designed NOVA (projectile-only energy-core boss; reuses v7 loop verbatim, picked uniformly from a 2-entry extensible pool) — 4 bullet-only steps RAKE/BURST/LANCE/ARC, deadlier-than-Mothership (dmg 25>15, ram 80>60, cadence 90<150f, ~4.7× density) → gdd/v16-second-boss.md; design NOVA's silhouette + bullet hue + HUD bar (distinct from the Mothership).

121. 2026-06-07 — FROM artist TO writer — v16: NOVA = electric-blue radiant pulsar (disc r=62 + 12 spikes, white-hot core; covers r=60), plasma-azure bullets, blue NOVA boss bar reusing the v7 geometry (vs the magenta Mothership) → art_spec/v16-second-boss.md; supply NOVA's display name + WARNING/banner/defeat copy + HUD label.

122. 2026-06-07 — FROM writer TO level-designer — v16: blessed boss name/HUD label NOVA (4 chars, inside the v7 AC47 label envelope) + WARNING/NOVA INBOUND banner + NOVA DOWN defeat line + live +{points} popup, mirroring the v7 Mothership set → story/v16-second-boss.md; own the pool-selection rule + finalize the deadlier numbers + confirm cadence unchanged.

123. 2026-06-07 — FROM level-designer TO programmer — v16: owned the uniform i.i.d. 1/N pool-selection rule (N-from-length, one-entry extensible, seedable), CONFIRMED cadence unchanged (75 s/+90 s), and LOCKED NOVA's deadlier balance (HP 120, bullet 25>15, ram 80>60, step 90<150 f, densities, kill 1500) vs AC13/fight-length → level_spec/v16-second-boss.md; implement the boss pool + NOVA per the locked specs.

124. 2026-06-07 — FROM programmer TO qa-tester — v16: built the extensible boss pool/registry + uniform-1/N seedable selection and NOVA (projectile-only 4-step moveset, deadlier consts, blue art/copy/HUD); SMOKE_BOSS_TYPE="NOVA" forces NOVA headlessly; pytest 91/91 + smoke exit 0.

125. 2026-06-07 — FROM qa-tester TO orchestrator — v16 PASS: AC86–AC93 verified (extensible length-driven pool, uniform seedable pick ≈½/½, cadence unchanged, NOVA distinct + zero ships + deadlier every axis 25>15, Mothership parity), full pytest 91/91 + smoke exit 0, no AC1–AC85 regression.

126. 2026-06-07 — FROM orchestrator TO human — v16 SHIPPED & DONE: backlog ticked, project state → v1–v16 (R1–R105, AC1–AC93, pytest 91/91); awaiting next theme/increment.

127. 2026-06-07 — FROM human TO orchestrator — v17: UI/UX polish — HP bar fades green→red gradually, a subtle red vignette below 25% HP, and recolor the green HEAVY enemy bullet (clashes with the green HP bonus).
128. 2026-06-07 — FROM orchestrator TO artist — v17 (render-only polish): make the HP bar a continuous green→red gradient (replaces v1-base §4.3 steps), add a subtle non-distracting red vignette at HP<25%, and recolor the HEAVY green pellet to a non-green hue clear of all entities; scoped Artist → Programmer → QA (BA/Designer/Writer/Level-designer skipped).

129. 2026-06-07 — FROM artist TO programmer — v17: specced the HP-bar green→amber→red gradient (`hp_bar_color()`, supersedes v1-base §4.3), the HP<25 red vignette (`#E63C3C`, edge-only falloff + slow pulse), and the HEAVY pellet recolor `#8CF03C`→`#D230DC` (rename `EB_COLOR_GREEN`→`EB_COLOR_PURPLE`, anti-clash proven) → art_spec/v17-hp-feedback-bullet-clarity.md; implement all three render changes.

130. 2026-06-07 — FROM programmer TO qa-tester — v17: implemented all three render changes (gradient `hp_bar_color()`, low-HP red vignette at slot 8.5, pellet recolor + `EB_COLOR_GREEN`→`EB_COLOR_PURPLE`); unit pytest 59/59 + smoke exit 0, pyright clean on changed files.

131. 2026-06-07 — FROM qa-tester TO orchestrator — v17 PASS: HP bar smooth green→amber→red (no stepped jumps), red vignette only <25% HP (edge-only/center-clear, breathes, distinct from v6 flash), HEAVY pellet now orchid `#D230DC` (clash-free), full pytest 94/94 (+3 e2e) + smoke exit 0, no AC1–AC93 regression.

132. 2026-06-07 — FROM orchestrator TO human — v17 SHIPPED & DONE: backlog ticked, project state → v1–v17 (R1–R105, AC1–AC93, pytest 94/94); awaiting next theme/increment.
