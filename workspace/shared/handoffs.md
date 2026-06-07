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

133. 2026-06-07 — FROM human TO orchestrator — v18: nerf Fan (side bullets fire 2× slower than the main beam + make it rarer); replace the fire-rate bonus with two kinds sharing its RNG weight — (a) fire rate up + bullet speed up a bit, (b) bullet speed up a lot + fire rate up a bit.
134. 2026-06-07 — FROM orchestrator TO business-analyst — v18 (mechanic+content+economy, full pipeline): formalize the Fan side-beam 2:1 cadence + rarity nerf and the Rapid→two-bonus split (effects 2a/2b, shared weight) as new R#/AC#; magnitudes/weights/names/colors left to downstream roles.

135. 2026-06-07 — FROM business-analyst TO lead-game-designer — v18: locked R106–R113/AC94–AC101 (R106 Fan side beams 2:1 half-cadence amends R25; R107 Fan rarer; R108 RETIRE Rapid/R26; R109 two new timed fire/speed kinds — (a) cooldown-halved+speed-up-a-bit, (b) speed-up-a-lot+rate-up-a-bit; R110 bullet speed = buffable stat; R111 two kinds split Rapid's weight 20 + ladder sums 100; R112 deterministic cross-stat stacking) → requirements/v18.md; design the two kinds' identity/feel/durations + the cross-stat stacking rule + name them conceptually.

136. 2026-06-07 — FROM lead-game-designer TO artist — v18: designed the two new kinds (Overdrive = cadence/cd-12→6+speed-a-bit; Railgun = velocity/speed-a-lot+rate-a-bit; both 480 f), confirmed Fan's 2:1 side-beam = width-not-×3 feel, locked R112 cross-stat stacking = strongest-wins per stat (min cd / max speed; bounded + clean-revert) → gdd/v18.md; give each new kind a distinct HUD pill letter + palette color (drop Rapid's; may reuse cyan for the velocity kind).

137. 2026-06-07 — FROM artist TO writer — v18: locked the two new pickup styles — Overdrive `O` electric-lime `#A6F03C` (new) + Railgun `V` cyan `#50DCFF` (reuses freed Rapid hue), proven distinct from the live palette; dropped Rapid's visual; reused the v2 diamond+pill verbatim → art_spec/v18.md; supply each new kind's on-screen name/label (O/V are render targets to override).

138. 2026-06-07 — FROM writer TO level-designer — v18: named the two kinds OVERDRIVE (`O`) + RAILGUN (`V`, kept over freed `R` to avoid a stale-Rapid read since it reuses Rapid's cyan), no popup (timed buffs, pill only), removed RAPID's name + `R` letter → story/v18.md; lock all magnitudes/weights (ladder sums 100).

139. 2026-06-07 — FROM level-designer TO programmer — v18: LOCKED magnitudes (base speed PB_SPEED=10; Overdrive cd 6 f + speed 12; Railgun speed 16 + cd 9; stacking min-cd 6/max-speed 16) + re-sliced RNG ladder (Fan 20→12, Rapid→Overdrive 10/Railgun 10, Score×2 12→20, sums 100) + CONFIRMED Fan 2:1 as non-tunable feel contract → level_spec/v18.md; implement v18 per the locked specs.

140. 2026-06-07 — FROM programmer TO qa-tester — v18: built Fan 2:1 side cadence + RAPID retired everywhere + Overdrive(O)/Railgun(V) buffable cd+speed (strongest-wins min-cd/max-speed, clean revert) + re-sliced ladder (sums 100) + smoke seed → Overdrive; unit pytest 70/70, full suite 105/105, smoke exit 0.

141. 2026-06-07 — FROM qa-tester TO orchestrator — v18 PASS: Fan sides 2:1 (100/50) & rarer (12), Rapid gone everywhere, Overdrive/Railgun apply+refresh+expire→baseline+restart-reset, strongest-wins bounded/clean-revert, ladder sums 100, real-smoke Overdrive lifecycle; full pytest 106/106 + smoke exit 0; no AC1–AC93 regression.

142. 2026-06-07 — FROM orchestrator TO human — v18 SHIPPED & DONE: backlog ticked, project state → v1–v18 shipped & passed QA (R1–R113, AC1–AC101, pytest 106/106); project complete, awaiting next theme/increment.

143. 2026-06-07 — FROM human TO orchestrator — v19: precise controls — hold SHIFT halves ship speed; shrink player hitbox to a circle ~50% of ship size (display unchanged); make all bullets ~50% larger to balance; show the hitbox as a red 50%-opacity circle while SHIFT held; enemy hitboxes unchanged.
144. 2026-06-07 — FROM orchestrator TO business-analyst — v19 (mechanic+balance, full pipeline): formalize SHIFT precise mode (×0.5 move, PLAY-only, held), always-on circular player hitbox (~50% of ship), all-bullets-~50%-larger balance, precise-mode red hitbox indicator, enemy hitboxes unchanged → new R#/AC#; magnitudes/colors/copy left to downstream roles. Hitbox-always-on confirmed with human.

145. 2026-06-07 — FROM business-analyst TO lead-game-designer — v19: locked R114–R119/AC102–AC108 (R114 hold-SHIFT ×0.5 move PLAY-only/held amends R3; R115 always-on circular player hitbox ≈50% of draw, decoupled from draw size, amends R16–R18; R116 all bullets ~50% larger draw+collision every family; R117 SHIFT-only red 50%-opacity hitbox indicator, render-only; R118 enemy hitboxes unchanged) → requirements/v19.md; design precise-mode feel + indicator semantics + the bonus-pickup-radius call, magnitudes to Level-designer.
146. 2026-06-07 — FROM lead-game-designer TO artist — v19: named the mechanic FOCUS, locked the feel (held-not-toggle instant ×0.5↔full, PLAY-only, firing/bombs/i-frames/boss untouched), the always-on circular damage hitbox identity + red indicator = literal readout of the true hitbox (SHIFT-held/PLAY only), confirmed ~50%-larger bullets fair (draw=collision), and DECIDED bonus-pickup radius stays generous at P_R → gdd/v19.md; define the red indicator (hue/alpha~50%/blend/slot) + per-family ~50%-larger bullet draw sizes (draw=collision), ship draw unchanged.
147. 2026-06-07 — FROM artist TO writer — v19: specced the SHIFT hitbox indicator (HITBOX_RED #FF2840 @ alpha 128, filled disc + 1-px opaque rim, radius = LD's P_HITBOX_R, straight-alpha SRCALPHA, after-particles slot, PLAY+SHIFT-only) + the draw==collision invariant for ~50%-larger bullets (EB_R 5→8 all enemy/boss families, player bullet 6×18, CYAN tail 18; retires PELLET/NOVA/hardcoded draw radii) → art_spec/v19.md; supply the optional SHIFT/Focus control-hint copy (or confirm none).
148. 2026-06-07 — FROM writer TO level-designer — v19: ADD the Focus hint via a CONTROLS_1 ⚠ REWRITE — "MOVE  Arrows / WASD  ·  Hold Shift  Focus      Z = fire · X = bomb" (462 px, fits; matches the Hold-Q/R idiom); no new HUD label/popup/screen → story/v19.md; lock the magnitudes (×0.5 move, P_HITBOX_R ≈50% of P_R=13, per-family bullet sizes ~1.5× draw=collision, no-tunneling).
149. 2026-06-07 — FROM level-designer TO programmer — v19: LOCKED FOCUS_SPEED_MULT=0.5, P_HITBOX_R=6 (damage tests only; pickup + draw stay P_R=13), EB_R 5→8 (all enemy/boss families draw=collision, retire PELLET/NOVA/hardcoded draws), player PB_W,PB_H 4,12→6,18 (coll r=PB_H/2=9), CYAN_TAIL_LEN 12→18, pellet=shared EB_R; CONFIRMED no tunneling (gap 14, threshold 28 ≫ fastest 7.5) / no mis-cull; v1 ramp+economy+speeds unchanged → level_spec/v19.md; implement v19 per the locked specs (ruff+pyright+unit pytest+smoke green).

150. 2026-06-07 — FROM programmer TO qa-tester — v19: implemented Focus (InputState.focus = either SHIFT → ×0.5 move, PLAY-only/held), the always-on P_HITBOX_R=6 damage circle (4 damage tests swapped; pickup stays P_R=13), ~1.5× bullets (EB_R 8 all families draw=collision, player 6×18, CYAN tail 18; PELLET/NOVA/hardcoded/CYAN_HEAD draws retired), the SHIFT red hitbox indicator, and CONTROLS_1 rewrite; smoke exercises a SHIFT-held ×0.5 window + shrunk hitbox; full pytest 117/117 + smoke exit 0, ruff/pyright clean on changed files.

151. 2026-06-07 — FROM qa-tester TO orchestrator — v19 PASS: AC102–AC108 verified (Focus ×0.5 both-axes/revert/firing-untouched, P_HITBOX_R=6 always-on + negative test "old-P_R-hit now misses" across ebullet/asteroid/enemy/boss, pickup stays P_R, all bullets draw==collision ~1.5× measured, red indicator at true radius SHIFT+PLAY-only/collision-neutral, enemy bodies unchanged, no tunnel); full pytest 117/117 + smoke exit 0 (3× + package + compileall) + 39/39 independent probe; no AC1–AC101 regression.

152. 2026-06-07 — FROM orchestrator TO human — v19 SHIPPED & DONE: backlog ticked, project state → v1–v19 shipped & passed QA (R1–R119, AC1–AC108, pytest 117/117); project complete, awaiting next theme/increment.
