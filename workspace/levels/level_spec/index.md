# Level / Difficulty Spec — index / navigation

> Spawn economy, difficulty ramp, and balance for "Starshard" (owner: **level-designer**). Split by
> increment; **the v1 ramp is UNCHANGED by every later increment** — each one *appends* a spawn slice
> without touching the curve. **All files are live, code-matching contract.** Cross-increment *why* →
> `../history.md`.

## Files (in build order)
| File | Increment | Covers (sections) | Status |
|------|-----------|-------------------|--------|
| `v1-base.md` | v1 base | §1 GDD-default tuning · §2 run-reset values · **§3 difficulty curve (formulas — core)** · §4 spawn rules · §5 milestones/phases · §6 entity caps · §7 survival-bonus · **§8 tuning levers (AC13)** · §9 traceability | shipped ✅ |
| `v2-economy.md` | v2 | **§V2.1 bonus spawn numbers** (drip cadence / enemy-drop % / kind weights / cap) · §V2.2 buff economy/run · §V2.3 AC13 balance · §V2.4 levers · §V2.5 smoke seed · §V2.6 traceability | shipped ✅ |
| `v5-spawn-mix.md` | v5 | **§V5.1 enemy-kind spawn mix** (per-band weights + gates) · §V5.2 realized-mix self-balance · §V5.3 AC13 · §V5.4 levers · §V5.5 smoke coexistence · §V5.6 traceability | shipped ✅ |
| `v6-bomb-economy.md` | v6 | **§V6.1 bomb-pickup weight** (BOMB=6, re-slice of the v2 table) · §V6.2 bomb economy/run · §V6.3 AC13 · §V6.4 `BOMB_SPAWN_LULL=0` · §V6.5 levers · §V6.6 smoke · §V6.7 traceability | shipped ✅ |
| `v7-bosses.md` | v7 | **§V7.1 breakpoint cadence** (75 s / +90 s, CONFIRM) · **§V7.2 spawn-freeze/resume** (skip-no-bank, `BOSS_RESUME_LULL=0`) · §V7.3 fight economy (drip frozen / minion-drops suppressed / minion-score ON) · §V7.4 +1000 reward · §V7.5 AC13 (`BOSS_HP=120` lever) · §V7.6 levers · §V7.7 smoke coexistence · §V7.8 traceability | spec ✅ |
| `v8-pause.md` | v8 | **§V8.1 verdict** (confirmed no-op — zero spawn/pickup/ramp/timing changes) · §V8.2 edge case (real-world vs in-game time, non-issue) · §V8.3 traceability | confirmed no-op ✅ |
| `v10.md` | v10 | **§V10.1 verdict** (confirmed no-op — Q-hold-to-quit on START+GAME_OVER, UI-only, no spawn/pickup/ramp/timing change) · §V10.2 edge case (UI counter, not a game clock) · §V10.3 traceability | confirmed no-op ✅ |
| `v12.md` | v12 | **§V12.1 verdict** (confirmed no-op — hold-R-to-restart on PAUSE+GAME_OVER, UI-only, no spawn/pickup/ramp/timing change) · §V12.2 edge case (second UI hold counter, not a game clock; `reset_run()` unchanged) · §V12.3 traceability | confirmed no-op ✅ |
| `v16-second-boss.md` | v16 | **§V16.1 pool-selection rule** (uniform i.i.d. 1/N per spawn, N-from-length extensibility, seedable) · **§V16.2 cadence UNCHANGED** (75 s / +90 s CONFIRM) · **§V16.3 NOVA balance LOCK** (HP 120 · bullet 25>15 · ram 80>60 · step 90<150 f · densities · kill 1500) · §V16.4 AC13/fight-length · §V16.5 levers · §V16.6 smoke · §V16.7 traceability | spec ✅ |
| `v18.md` | v18 | **§V18.1 magnitudes LOCK** (base bullet speed `PB_SPEED=10`; Overdrive cd 6 f + speed +2→12; Railgun speed +6→16 + cd 12→9; stacking min-cd 6/max-speed 16) · **§V18.2 RNG ladder re-slice** (Fan 20→12, Rapid→Overdrive 10/Railgun 10, freed 8→Score×2 12→20; sums 100) · **§V18.3 Fan 2:1 feel contract** (not tunable) · §V18.4 smoke/AC13 · §V18.5 levers · §V18.6 traceability | spec ✅ |
| `v19.md` | v19 | **§V19.1 Focus multiplier LOCK** (`FOCUS_SPEED_MULT=0.5`, P_SPEED 5→2.5 focused) · **§V19.2 player hitbox LOCK** (`P_HITBOX_R=6`, ≈50% of P_R=13; damage tests swap to it, pickup + draw stay at `P_R=13`) · **§V19.3 bullet sizes LOCK** (`EB_R 5→8` all enemy/boss families draw=collision; player `PB_W,PB_H 4,12→6,18`→coll r=9; `CYAN_TAIL_LEN 12→18`; pellet = shared EB_R, no special) · **§V19.4 no-tunneling/no-cull CONFIRM** (gap 14, threshold 28 ≫ fastest 7.5) · §V19.5 net=fairer/AC13 safe · §V19.6 levers · §V19.7 traceability. **v1 ramp + economy UNCHANGED.** | spec ✅ |
| `v20.md` | v20 | **§V20L.1 magnitudes LOCK** (LASER `HP=3`/`SCORE=100`/`R=14`; beam `WINDUP_F=30`/`DAMAGE_F=60`/`COOLDOWN_F=90`=180 f cycle; width `2→6 px` linear, draw==collision; `SWEEP_DPS=0.45`≈0.1× P_SPEED, cap 18°; `BEAM_DMG=15`==EB_DMG, i-frame-gated ≤1 tick/phase; reposition drift `2`/desc `0.3` COOLDOWN-only) · **§V20L.4 FAIRNESS PROOF** (no unavoidable beam — out-walkable at P_SPEED 5 *and* focused 2.5) · **§V20L.5 volume-neutral re-slice** (`LASER_GATE=60 s`, `LASER_WEIGHT=12` from REGULAR; cap/interval UNCHANGED) · §V20L.6 AC13 CONFIRM · §V20L.7 levers · §V20L.8 smoke seed · §V20L.9 traceability. **v1 ramp + prior economy UNCHANGED.** | spec ✅ |

## Where is …? (topic → file)
- **Difficulty ramp formulas (the curve)** → `v1-base.md` §3 (untouched by v2/v5/v6)
- **AC13 (1–3 min run length) levers** → `v1-base.md` §8 (+ per-increment AC13 sections §V2.3, §V5.3, §V6.3)
- **Run-reset / starting values** → `v1-base.md` §2
- **Bonus pickup spawn rates / kind weights** → `v2-economy.md` §V2.1 → **re-sliced** in `v6-bomb-economy.md` §V6.1 (adds BOMB=6) → **re-sliced again** in `v18.md` §V18.2 (Fan 20→12, Rapid retired → Overdrive 10/Railgun 10, Score×2 12→20; sums 100)
- **New fire/speed buff magnitudes (Overdrive/Railgun cd + bullet speed) + base bullet speed** → `v18.md` §V18.1
- **Fan side-beam 2:1 center:side cadence (feel contract, not tunable)** → `v18.md` §V18.3
- **Enemy-kind spawn mix + gates (HEAVY@20s/SCOUT@50s)** → `v5-spawn-mix.md` §V5.1
- **Bomb-pickup scarcity + post-bomb lull** → `v6-bomb-economy.md` §V6.1, §V6.4
- **Boss breakpoint cadence (when a boss fires)** → `v7-bosses.md` §V7.1 (TIME: 75 s, then +90 s) — **unchanged by v16** (`v16-second-boss.md` §V16.2)
- **Which boss appears (random pool selection rule + extensibility)** → `v16-second-boss.md` §V16.1 (uniform i.i.d. 1/N per spawn, seedable, boss #3 = one entry)
- **NOVA balance numbers (HP / deadlier dmg/ram/cadence/density / reward)** → `v16-second-boss.md` §V16.3 (LOCK) + §V16.4 (AC13/fight-length)
- **Spawn-freeze + resume during a boss fight** → `v7-bosses.md` §V7.2 (skip-no-bank, no resume lull)
- **Boss-fight economy (drip / minion drops / minion score / +1000 reward)** → `v7-bosses.md` §V7.3, §V7.4
- **v8 Pause economy impact** → `v8-pause.md` §V8.1 (confirmed no-op — no new spawns/pickups/ramp/timing)
- **v10 START/GAME_OVER Q-hold-to-quit economy impact** → `v10.md` §V10.1 (confirmed no-op — UI-only gesture, no spawn/pickup/ramp/timing)
- **v12 PAUSE/GAME_OVER hold-R-to-restart economy impact** → `v12.md` §V12.1 (confirmed no-op — UI-only gesture, second hold counter, `reset_run()` unchanged)
- **v19 precise-controls magnitudes — Focus ×0.5 multiplier / player damage hitbox `P_HITBOX_R=6` (pickup + draw stay `P_R=13`) / ~1.5× bullet sizes (`EB_R 5→8`, player bullet `6,18`, `CYAN_TAIL_LEN 18`, pellet=shared) / no-tunneling+no-cull confirmation / net=fairer** → `v19.md` (v1 ramp + economy untouched; bullet speeds unchanged R110)
- **v20 LASER enemy magnitudes — HP 3 / score 100 / r 14; beam timings (windup 30 f / damaging 60 f / cooldown 90 f = 3 s cycle); widen `2→6 px` linear (draw==collision); sweep `BEAM_SWEEP_DPS=0.45` (≈0.1× P_SPEED) cap 18°; beam damage 15 (i-frame-gated ≤1 tick/phase); reposition drift 2 / descent 0.3 (cooldown-only)** → `v20.md` §V20L.1
- **v20 spawn gate + weight (LASER earliest 60 s, weight 12 from REGULAR — volume-neutral re-slice; cap/interval unchanged)** → `v20.md` §V20L.5
- **v20 fairness proof (no unavoidable beam — out-walkable at P_SPEED 5 and focused 2.5) + AC13 confirmation** → `v20.md` §V20L.4, §V20L.6

## Updating this spec
- **New increment:** add `vN-<topic>.md` (`# vN increment — …`) + a row + topic-map entry; **state
  explicitly whether the v1 ramp / prior economy is touched** (so far: never). One-line in `../history.md`.
- **Named move — the *volume-neutral re-slice* (retro-blessed 2026-06-05).** To add a pickup/enemy *kind*
  without touching volume: re-slice the existing weight table so it **still sums to 100**, name the **source
  kinds** you took from, and state the **AC13 reason** for each (protect the low-tail compressor, trim the
  high-tail extender). No new spawn path, no extra volume → drip cadence / enemy-drop % / cap stay
  bit-for-bit. This is how v5 re-slid enemy kind and v6 folded in `BOMB=6` — reuse it as a fill-in-the-template
  operation with built-in AC13 protection.
- **Fix shipped balance:** edit that version's file **in place** (keep it matching `workspace/game/`
  spawn/config) and record the why in `../history.md`. The weights/formulas are the contract.
