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

## Status

> **Board only.** One line per shipped version + the parked items. The *why* lives in `history.md`
> (cross-cutting → `shared/history.md`; per-domain → each role folder's `history.md`); the recent
> agent-to-agent story is in `handoffs.md`; closed-increment handoffs are in `../archive/`.

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
- **Game is playable:** `.\.venv\Scripts\python.exe workspace\game\main.py` (Z = fire · X = bomb).

### Parked (non-blocking)
- **AC13 long runs** — expert pure-dodging can exceed 3 min; tuning levers in `levels/level_spec/`
  §8 / §V2.4. Act only if a human playtest confirms.
- **R35 screen-clear bonus** — deferred since v2 (GDD §V2); non-failing.

> **Spec-splitting DONE (Manager, 2026-06-05):** the six big specs (gdd / art_spec / level_spec /
> requirements / qa_report / story) are now per-increment folders, each with an `index.md` navigation
> header. Content relocated verbatim; see `shared/history.md`.
