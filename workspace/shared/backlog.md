# Backlog — project task board

The studio's shared task board across chats. The **Orchestrator** owns it; every role ticks its own
row when finishing. Status: `todo` | `in-progress` | `done` | `blocked`.

> **Kept lean on purpose.** This file is only the board + a one-line status. The *why* behind each
> increment lives in each domain's `history.md` (e.g. `design/history.md`); the cross-role story is in
> `handoffs.md`. Older narrative is in `../archive/`. See `../README.md` for the workspace map.

### v1 — "Starshard" (shipped & passed QA, 2026-06-05) ✅
| # | Task | Owner role | Status | Artifact |
|---|------|-----------|--------|----------|
| 1 | Capture theme & plan | orchestrator | done | shared/brief.md |
| 2 | Requirements | business-analyst | done | requirements/requirements/ |
| 3 | Game Design Document | lead-game-designer | done | design/gdd/ |
| 4 | Art spec (palette + shapes) | artist | done | art/art_spec/ |
| 5 | Story / UI copy | writer | done | story/story/ |
| 6 | Level / difficulty spec | level-designer | done | levels/level_spec/ |
| 7 | Implement the game | programmer | done | game/main.py |
| 8 | QA: run & verify | qa-tester | done | qa/qa_report/ |
| 9 | Declare project DONE | orchestrator | done | shared/handoffs.md |

### v2 — Bonuses / power-ups + modular refactor (shipped & passed QA, 2026-06-05) ✅
| # | Task | Owner role | Status | Artifact |
|---|------|-----------|--------|----------|
| 1 | Capture v2 feature + architecture decision | orchestrator | done | shared/brief.md |
| 2 | Requirements: bonuses (types, spawn, durations, stacking, ACs) | business-analyst | done | requirements/requirements/ |
| 3 | GDD update: buff set, numbers, stacking + module map | lead-game-designer | done | design/gdd/ |
| 4 | Art spec: bonus pickup shapes + active-buff HUD indicators | artist | done | art/art_spec/ |
| 5 | Writer: bonus names + HUD buff/timer labels | writer | done | story/story/ |
| 6 | Level spec: bonus spawn rates, drop rules, buff-duration balance | level-designer | done | levels/level_spec/ |
| 7 | Modular refactor + implement bonuses | programmer | done | game/ |
| 8 | QA: verify bonuses + smoke gate after refactor | qa-tester | done | qa/qa_report/ |
| 9 | Declare v2 DONE | orchestrator | done | shared/handoffs.md |

### v3 — Knowledge-base reorganization (2026-06-05) ✅
| # | Task | Owner role | Status | Artifact |
|---|------|-----------|--------|----------|
| 1 | Introduce the Manager role + scope workspace into per-role folders; split history out of the hot path | manager | done | workspace/ (this layout) + roles/manager.md |

### v4 — QA documentation: feature inventory + checklists + test plans (2026-06-05)
| # | Task | Owner role | Status | Artifact |
|---|------|-----------|--------|----------|
| 1 | Document implemented features (v1+v2) mapped to requirements/ACs; per-feature QA checklists; smoke + regression test plans | qa-tester | done | qa/feature_inventory.md, qa/test_plan.md |
| 2 | Declare v4 DONE | orchestrator | done | shared/handoffs.md |

### v5 — Three enemy types (varied movement, fire & bullet behaviors) (2026-06-05)
| # | Task | Owner role | Status | Artifact |
|---|------|-----------|--------|----------|
| 1 | Capture v5 feature + framing | orchestrator | done | shared/brief.md |
| 2 | Requirements: 3 enemy types (regular+deviation, heavy/splitting-green, scout/fast-cyan), ACs | business-analyst | done | requirements/requirements/ |
| 3 | GDD: per-type size/speed/bullet/cadence/deviation numbers, split mechanic, fan angle | lead-game-designer | done | design/gdd/ |
| 4 | Art spec: 3 enemy shapes/sizes + red/green/cyan bullet visuals | artist | done | art/art_spec/ |
| 5 | Writer: enemy kind names / any UI labels | writer | done | story/story/ |
| 6 | Level spec: spawn mix/weighting per type, fold into ramp (keep AC13) | level-designer | done | levels/level_spec/ |
| 7 | Implement 3 enemy types + splitting projectile | programmer | done | game/ |
| 8 | QA: verify all 3 types + split lifecycle + smoke gate | qa-tester | done | qa/qa_report/ |
| 9 | Declare v5 DONE | orchestrator | done | shared/handoffs.md |

### v6 — Bombs (panic button) + control remap (Z fire / X bomb) (shipped & passed QA, 2026-06-05) ✅
| # | Task | Owner role | Status | Artifact |
|---|------|-----------|--------|----------|
| 1 | Capture v6 feature + framing | orchestrator | done | shared/brief.md |
| 2 | Requirements: bomb charges (start 2, replenish via scarce pickup, 0-guard), screen-flush effect, flash visual, Z-fire/X-bomb remap, ACs | business-analyst | done | requirements/requirements/ |
| 3 | GDD: charge cap, flush semantics (what clears + score rule), pickup scarcity/cap, flash timing, full keymap | lead-game-designer | done | design/gdd/ |
| 4 | Art spec: full-screen flash overlay + bomb-charge HUD readout + bomb-pickup shape | artist | done | art/art_spec/ |
| 5 | Writer: bomb pickup name + HUD bomb-count label + updated controls copy (Z/X) | writer | done | story/story/ |
| 6 | Level spec: bomb-pickup spawn rate/scarcity, fold into economy, keep AC13 | level-designer | done | levels/level_spec/ |
| 7 | Implement bombs + flush + flash + bomb pickup + Z/X remap | programmer | done | game/ |
| 8 | QA: verify bomb lifecycle + flush + 0-guard + remap + smoke gate (seed a bomb) | qa-tester | done | qa/qa_report/ |
| 9 | Declare v6 DONE | orchestrator | done | shared/handoffs.md |

### v7 — Bosses (periodic mothership boss fights) (2026-06-05)
| # | Task | Owner role | Status | Artifact |
|---|------|-----------|--------|----------|
| 1 | Capture v7 feature + framing | orchestrator | done | shared/brief.md |
| 2 | Requirements: boss-fight loop (breakpoint trigger, field-clear+spawn-freeze, entrance/oscillation, defeat reward, resume), Mothership 4-step moveset, boss damage/HUD, ACs | business-analyst | done | requirements/requirements/v7.md |
| 3 | GDD: breakpoint metric+value (reconcile AC13), boss HP/size/speed/oscillation, moveset cadence/order/loop, attack-4 fan+split counts/angles, reward value, bomb-vs-boss rule, smoke-seed plan | lead-game-designer | done | design/gdd/v7-bosses.md |
| 4 | Art spec: Mothership shape/size, boss health bar, yellow + red boss bullets, reuse v6 flush flash | artist | done | art/art_spec/v7-bosses.md |
| 5 | Writer: boss name (Mothership), WARNING/intro + defeat copy, boss HUD label | writer | done | story/story/v7.md |
| 6 | Level spec: breakpoint cadence folded into the ramp/economy (keep AC13), spawn-freeze + resume rules, reward balance | level-designer | done | levels/level_spec/v7-bosses.md |
| 7 | Implement boss encounter manager + Mothership moveset + yellow→red split (reuse v5) + system field-clear (reuse v6 flush/flash) + boss HUD | programmer | done | game/ |
| 8 | QA: verify boss loop + moveset + reward + spawn-freeze/resume + smoke gate (seed a boss) + no AC1–AC38 regression | qa-tester | done | qa/qa_report/v7.md |
| 9 | Declare v7 DONE | orchestrator | done | shared/handoffs.md |

### v8 — Pause / Unpause + Q-hold to quit (shipped & passed QA, 2026-06-05) ✅
| # | Task | Owner role | Status | Artifact |
|---|------|-----------|--------|----------|
| 1 | Capture v8 feature + framing | orchestrator | done | shared/brief.md |
| 2 | Requirements: pause behaviour, freeze list, Q-hold threshold+arc, restart-from-pause, smoke-gate plan, ACs | business-analyst | done | requirements/requirements/v8.md |
| 3 | GDD: exact freeze list, Esc toggle semantics per state, Q-hold numbers, arc position/style, pause-screen layout, restart-from-pause rule | lead-game-designer | done | design/gdd/v8-pause.md |
| 4 | Art spec: pause overlay + Q-hold arc visuals | artist | done | art/art_spec/v8-pause.md |
| 5 | Writer: pause-screen copy (unpause / restart / quit hints), updated controls copy | writer | done | story/story/v8.md |
| 6 | Level spec: no economy changes expected — skip or confirm | level-designer | done | levels/level_spec/v8-pause.md (confirmed no-op) |
| 7 | Implement pause state, freeze all timers, pause-screen overlay, Q-hold arc, Esc→pause/unpause, remove Esc-quit | programmer | done | game/ |
| 8 | QA: verify pause/unpause (state preserved), Q-hold arc + quit, no regression, smoke gate still green | qa-tester | done | qa/qa_report/v8.md |
| 9 | Declare v8 DONE | orchestrator | done | shared/handoffs.md |

### v9 — Process hardening (retro-driven: verification + feedback loops) (shipped & passed QA, 2026-06-05) ✅
| # | Task | Owner role | Status | Artifact |
|---|------|-----------|--------|----------|
| 1 | Facilitate team retrospective; collect 8 role cards; apply Manager-owned process changes | manager | done | shared/retrospective.md (+ CLAUDE.md, roles/*, index updates) |
| 2 | Committed, growing regression harness (accumulates AC1–AC60) | programmer | done | qa/regression_harness.py |
| 3 | SMOKE_TIMELINE source of truth + headless `--event-script` injection (behaviorally test pause/bomb/quit) | programmer | done | game/config.py + app.py |
| 4 | Render-smoke (no draw raises + key rects don't overlap) + `string_widths` width/glyph assertion | programmer | done | qa/regression_harness.py |
| 5 | AC13 `--balance-probe` (K scripted runs → median/95th survival time) | programmer | done | game/app.py + main.py |
| 6 | QA: verify the new gates catch a planted defect (prove the FAIL loop) + 1 human playtest checkpoint | qa-tester | done | qa/qa_report/v9.md |
| 7 | Declare v9 DONE | orchestrator | done | shared/handoffs.md |

### v10 — Q-hold-to-quit on the START + GAME_OVER screens (shipped & passed QA, 2026-06-05) ✅
| # | Task | Owner role | Status | Artifact |
|---|------|-----------|--------|----------|
| 1 | Capture v10 feature + framing | orchestrator | done | shared/brief.md |
| 2 | Requirements: Q-hold-to-quit enabled in START + GAME_OVER (reuse v8 threshold/arc/reset), quit-hint visible on both, ACs | business-analyst | done | requirements/requirements/v10.md |
| 3 | GDD: confirm v8 numbers reused; arc behaviour/position across START+GAME_OVER; hold-counter reset on state transitions | lead-game-designer | done | design/gdd/v10.md |
| 4 | Art spec: arc placement on START + GAME_OVER (no text collision; render-smoke safe) | artist | done | art/art_spec/v10.md |
| 5 | Writer: START quit hint + GAME_OVER key-list quit hint (width-safe, no stale Esc-quit) | writer | done | story/story/v10.md |
| 6 | Level spec: economy no-op — confirm/skip | level-designer | done | levels/level_spec/v10.md (confirmed no-op) |
| 7 | Implement Q-hold + arc in START + GAME_OVER (reuse v8); reset hold counter on transitions | programmer | done | game/ |
| 8 | QA: verify Q-hold quits from START + GAME_OVER + arc + cancel-on-release; render-smoke + no v1–v9 regression | qa-tester | done | qa/qa_report/v10.md |
| 9 | Declare v10 DONE | orchestrator | done | shared/handoffs.md |

## Status

> **Board only.** One line per shipped version + the parked items. The *why* lives in `history.md`
> (cross-cutting → `shared/history.md`; per-domain → each role folder's `history.md`); the recent
> agent-to-agent story is in `handoffs.md`; closed-increment handoffs are in `../archive/`.

- **v10 SHIPPED & DONE** (2026-06-05) — **Q-hold-to-quit on START + GAME_OVER.** v8 shipped the gesture+arc
  but only wired it into PAUSE; v10 extends it (reusing the v8 threshold/arc/reset) to the START and
  GAME_OVER screens + shows the quit hint on both. Orchestrator framed it (`shared/brief.md` v10) +
  opened the v10 backlog. BA→Designer→Artist→Writer→Level-designer all done (economy no-op confirmed).
  **Programmer DONE** — generalised the v8 hold-counter block to `state in (START, PAUSE, GAME_OVER)`
  (PLAY excluded, R81); paired every `self.state = …` with `q_hold_frames = 0` across all six transitions
  (esp. PLAY→GAME_OVER so dying with Q held can't instant-quit); carved Q out of START "any key starts"
  (§V10.5); factored a reusable `hud.draw_quit_arc` + START/GAME_OVER guarded calls (drawn only while held,
  `draw_pause` untouched); wired the Writer's `START_QUIT_HINT` line + `GAMEOVER_KEYS`/`CONTROLS_2` rewrites
  + the two Artist arc centres. Smoke exits 0/120 f (×3-form + `-m` + event-script + compileall); regression
  harness **58/58** (49 prior + 9 new v10: render-smoke START+GAME_OVER with/without arc + arc-rect anti-collision,
  6-transition reset spine, START Q carve-out, hold-quit on both screens, no-accumulation, PLAY-excluded);
  no AC1–AC60 regression. **QA PASS** (`qa/qa_report/v10.md`) — smoke exit 0 / exactly 120 f (×2-form +
  `-m` + compileall); harness 58/58; event-script 5/5; AC61–AC68 all PASS; render-smoke + arc anti-collision
  green; **11 QA-authored independent probes** PASS (exact-30 threshold boundary, the #1-risk die-with-Q-held
  end-to-end through the live loop → no instant quit, arc-fill mapping, negative PLAY-exclusion test); no
  v1–v9 regression. **Orchestrator declared v10 DONE** — Q-hold-to-quit now works on START + PAUSE + GAME_OVER.
- **v9 SHIPPED & DONE** (2026-06-05) — **process hardening** from the post-v8 retrospective (`shared/retrospective.md`).
  Manager applied the doc/role changes (BLOCKER + SKIP handoffs, required Open-values table, lever-ownership +
  no-placeholder color/alpha, QA independence + negative test, named volume-neutral re-slice, copy-surface
  map, Programmer-invariants stub). **Programmer tooling DONE** — `qa/regression_harness.py` (49 checks,
  AC1–AC60 + render-smoke + `string_widths`), `config.SMOKE_TIMELINE` source-of-truth + ordering check,
  headless `--event-script` behavioral gate (pause/bomb/quit via the real `_handle_events`), and the AC13
  `--balance-probe`. Smoke still exits 0; all gates green; 3 planted defects proved the new gates FAIL (the
  smoke gate stayed green on the behavioral defect — exactly the retro's T1 point). **QA PASS** (`qa/qa_report/v9.md`):
  all gates green on the clean tree (smoke exit 0 ×3-form + compileall; harness 49/49; event 5/5; balance median 48.5 s /
  p95 75.0 s); **FAIL loop proven** with 3 *independent* QA-planted defects (flush-no-op → event+regression red; HP-bar↔score
  overlap → AC47; CONTROLS_1 overflow → AC47w) **each with smoke staying green** (T1 demonstrated, not asserted); first
  **human live-playtest checkpoint PASS** (AC47 anti-collision + pause/Q-hold arc + feel/flash all confirmed live — T3 closed).
  **Orchestrator declared v9 DONE** — the retro action register's verification half (A10–A15) is now live and proven.
- **v8 SHIPPED & DONE** (2026-06-05) — pause/unpause + Q-hold-to-quit. QA PASS (R69–R75, AC53–AC60); smoke exit 0 × 3 + package import; no v1–v7 regression.
- **v7 SHIPPED & DONE** (2026-06-05) — **bosses** (periodic mothership boss fights). Orchestrator
  framed it (`shared/brief.md` v7); **BA done** — `requirements/v7.md` (**R56–R68 MUST + AC39–AC52**);
  **Designer done** — `design/gdd/v7-bosses.md` (every §26 lever locked). **★ Breakpoint-vs-AC13 RESOLVED:**
  **TIME-based, first boss @ 75 s, then every +90 s** — chose **(a) lower the gate** (boss 1 reliably seen
  before the ~120 s median death; bosses 2+ are the late/expert event); one run clock never pauses (no
  difficulty discount). Boss HP 120 / rest y=400 / ±120 px osc; moveset 5 REG→2 HEAVY→7 SCOUT→yellow-fan→12-red
  ring (reuses v5 split); arrival clear reuses v6 flush (free); bomb→boss immune; reward +1000. **Artist done**
  — `art_spec/v7-bosses.md`: Mothership = dark `#342C4A` hull + magenta `ENEMY` trim + yellow core (~180×152,
  painted body ⊇ r=70); boss health bar center-top `(140,52,320,16)` magenta-fill (AC47 anti-collision proven);
  yellow fan `EB_COLOR_YELLOW #FFEA00` (new), 12 red children reuse `EB_COLOR_RED`; arrival flash reuses v6
  verbatim. **Writer done** — `story/v7.md`: boss name + HUD label blessed `MOTHERSHIP` (AC47-safe), optional
  arrival `WARNING`/`MOTHERSHIP INBOUND`, defeat `MOTHERSHIP DOWN` + honest `+{points}` popup (tracks Score×2).
  **Level-designer done** — `level_spec/v7-bosses.md`: CONFIRMED the locked pacing (TIME breakpoint 75 s/+90 s,
  `BOSS_HP=120`, `BOSS_KILL_SCORE=1000`); **freeze** the v1 asteroid + v5 enemy + v2 drip spawners on `not boss_active`
  **skip-no-bank** (no backlog dump), **resume** immediate on DEFEAT `BOSS_RESUME_LULL=0`; **fight economy** = drip
  frozen + minion pickup-drops suppressed + minion score ON (AC13-orthogonal — gate is TIME not points); **AC13 held
  (median)** — run clock never pauses, ~5 s entrance bounded/one-shot, parked caveat extended; smoke boss seed @f40
  coexists with v5 (f16) + v6 (f20). **Programmer done** — `entities/boss.py` + `systems/encounter.py`
  (boss sub-state in PLAY; factored `bombs.trigger_flush` for the free arrival clear; boss folded into §V2.7;
  spawn-freeze skip-no-bank; yellow→12-red split reuses the v5 frozen split; boss HUD bar/label/warn/defeat).
  Smoke exits 0 / 120 f; logic probes pass AC39–AC52, no AC1–AC38 regression. **QA PASS** — smoke gate
  green (exit 0 / exactly 120 f / 3× + `-m` + compileall) AND a seeded boss exercised (free arrival clear @
  charge-1, entrance→settle y=400 @f60, 5R/2H/7S waves, yellow→even-12-red ring); AC39–AC52 all PASS; no
  v1/v2/v5/v6 regression (`qa/qa_report/v7.md`). **Orchestrator declared v7 DONE.**
- **v6 SHIPPED & DONE** (2026-06-05) — bombs / panic button + Z-fire / X-bomb remap. QA PASS
  (R45–R54, AC30–AC38); smoke gate green + bomb-activation-exercising; no v1/v2/v5 regression.
- **v5 SHIPPED & DONE** — three enemy types (REGULAR/HEAVY/SCOUT + splitting GREEN pellet). QA PASS (AC22–AC29).
- **v4 SHIPPED & DONE** — standing QA docs (`qa/feature_inventory.md` + `qa/test_plan.md`). No code change.
- **v3 DONE** — knowledge-base reorg into per-role folders (Manager). Specs unchanged.
- **v2 SHIPPED & DONE** — pickup bonuses + modular MVC refactor (~500-line cap retired). QA PASS (AC14–AC21).
- **v1 SHIPPED & DONE** — "Starshard" base game. QA PASS (R1–R14, AC1–AC13).
- **Game is playable:** `.\.venv\Scripts\python.exe workspace\game\main.py` (Z = fire · X = bomb · Esc = pause · Q-hold = quit).

### Parked (non-blocking)
- **AC13 long runs** — expert pure-dodging can exceed 3 min; tuning levers in `levels/level_spec/`
  §8 / §V2.4. Act only if a human playtest confirms.
- **R35 screen-clear bonus** — deferred since v2 (GDD §V2); non-failing.

> **Spec-splitting DONE (Manager, 2026-06-05):** the six big specs (gdd / art_spec / level_spec /
> requirements / qa_report / story) are now per-increment folders, each with an `index.md` navigation
> header. Content relocated verbatim; see `shared/history.md`.
