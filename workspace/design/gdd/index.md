# GDD — index / navigation

> The Game Design Document for "Starshard" (owner: **lead-game-designer**). Split by increment so a
> role loads only the version(s) it needs. **Every file is live, code-matching contract** — where a
> later increment says *"supersedes §X"*, the newer rule wins. The cross-increment *why* is in
> `../history.md`.

## Files (in build order)
| File | Increment | Covers (sections) | Status |
|------|-----------|-------------------|--------|
| `v1-base.md` | v1 base | §1 pitch · §2 core loop · §3 controls · §4 state machine · §5 window/coords · §6 entities (player/bullet/asteroid/enemy/enemy-bullet/starfield/particles) · §7 scoring + difficulty + **master numbers table** · §8 collision rules · §9 HUD · §10 placeholder visuals · §11 smoke-test · §12 scope · §13 coverage · §14 open Qs | shipped ✅ |
| `v2-bonuses.md` | v2 | §V2.1–V2.11 — buff set · stacking/refresh · pickup entity · spawn approach · buff-pill HUD · **§V2.7 collision order (supersedes §8)** · R34/R35 · **§V2.9 MVC module map** · coverage | shipped ✅ |
| `v5-enemies.md` | v5 | §V5.1–V5.9 — **§V5.2 enemy roster table** (REGULAR/HEAVY/SCOUT) · §V5.3 aim cones · **§V5.4 splitting green pellet** · §V5.5 config consts · §V5.6 smoke · §V5.7 ramp intent · coverage | shipped ✅ |
| `v6-bombs.md` | v6 | §V6.1–V6.13 — §V6.2 charge pool · **§V6.3 flush** · §V6.4 lockout · §V6.5 flash · §V6.6 bomb pickup · §V6.7 lull · §V6.8 AC13 · **§V6.9 keymap (supersedes §3 — Z fire / X bomb)** · §V6.10 smoke · §V6.11 consts · coverage | shipped ✅ |
| `v7-bosses.md` | v7 | §V7.1–V7.18 — **§V7.2 breakpoint + AC13 reconcile** · §V7.3 fight-loop/clock · §V7.4 boss HP · §V7.5 arrival clear (reuse v6) · §V7.6 spawn-freeze+economy · §V7.7 entrance/rest/oscillation · §V7.8 no-attack-on-entrance · §V7.9 damage+reward · §V7.10 moveset cadence · §V7.11 minion waves+cap · **§V7.12 yellow→12-red split (reuse v5)** · §V7.13 collision · §V7.14 bomb-vs-boss · §V7.15 smoke · §V7.16 consts · coverage | shipped ✅ |
| `v8-pause.md` | v8 | §V8.1–V8.12 — §V8.2 Esc-toggle state machine (PAUSE as first-class GameState; no-op in START/GAME_OVER) · **§V8.3 t_quit = 30 f (0.5 s @ 60 FPS)** · §V8.4 Q-hold arc (circular, r=22, HP_AMBER fill, HP_BACK track) · **§V8.5 freeze list** (8 subsystems enumerated by module) · §V8.6 pause overlay (full-screen dim α=110; PLAYER-cyan heading; 3 hint lines; arc below) · **§V8.7 restart = K_r** · §V8.8 starfield continues / particles freeze · §V8.9 consts · §V8.10 programmer guide · coverage | shipped ✅ |
| `v10.md` | v10 | §V10.1–V10.12 — extends the v8 Q-hold-to-quit gesture to START + GAME_OVER · **§V10.2 v8 reuse verbatim** (PAUSE_QUIT_FRAMES=30 + arc, no per-state variation) · **§V10.3 active-state set = START+PAUSE+GAME_OVER, NOT PLAY** · **§V10.4 reset-on-transition spine** (one shared `q_hold_frames`, 6 transitions named) · **§V10.5 START "any key starts" Q carve-out** · §V10.6 arc idle-visibility (only-while-held on the new screens) + placement constraint for Artist · §V10.10 programmer guide · coverage | shipped ✅ |
| `v12.md` | v12 | §V12.1–V12.13 — hold-R-to-restart on PAUSE + GAME_OVER (mirrors the v8/v10 Q-hold gesture) · **§V12.2 threshold reuse** (`RESTART_HOLD_FRAMES = PAUSE_QUIT_FRAMES` = 30, coupled alias) · **§V12.3 two independent counters** (`q_hold_frames` + new `r_hold_frames`, never cross-fill; §V12.3.1 quit-precedence tie-break) · **§V12.4 reset-on-transition spine extended to BOTH counters** (6 transitions; #5/#6 rewritten) · **§V12.5 restart moves off the `K_r` KEYDOWN edge → held trigger** (branches removed, à la v8 Esc) · §V12.6 cancel-on-release for R · **§V12.7 two coexisting arcs** (visual reused verbatim, per-screen idle-visibility, Artist placement) · **§V12.8 active set = PAUSE+GAME_OVER, NOT START/PLAY** · §V12.11 programmer guide · coverage | shipped ✅ |
| `v14.md` | v14 | §V14.1–V14.11 — lifetime-stats screen placement + navigation · **§V14.2 new first-class `STATS` GameState** (off START; GAME_OVER-panel + PLAY-toggle rejected) · **§V14.3 nav** (Tab START⇄STATS; Esc STATS→back; no other key acts) · **§V14.4 START Tab carve-out** (mirrors v10 Q carve-out) · §V14.5 reset-spine extended to the 2 new transitions · §V14.6 highscore = existing GAME_OVER BEST, STATS = full ledger · **§V14.7 active sets unchanged** (STATS NOT in Q/R hold sets → no arc) · §V14.8 smoke/render-smoke · coverage | in progress 🚧 |

## Where is …? (topic → file)
- **Master numbers / tuning table** → `v1-base.md` §7.3
- **Controls / keymap** → `v1-base.md` §3 → **superseded by** `v6-bombs.md` §V6.9 (Z fire · X bomb)
- **Collision order** → `v1-base.md` §8 → **superseded by** `v2-bonuses.md` §V2.7 (+ bomb runs before damage, `v6-bombs.md` §V6.3)
- **Player / asteroid / enemy / enemy-bullet entities** → `v1-base.md` §6
- **Power-ups / buffs (Repair/Fan/Rapid/Shield/Score×2)** → `v2-bonuses.md` §V2.2
- **MVC module map (the `game/` package layout)** → `v2-bonuses.md` §V2.9
- **Enemy roster REGULAR/HEAVY/SCOUT + aim cones** → `v5-enemies.md` §V5.2–V5.3
- **Splitting green pellet → 3 red fan** → `v5-enemies.md` §V5.4
- **Bomb charge pool / flush / flash / pickup** → `v6-bombs.md` §V6.2–V6.6
- **Boss breakpoint + AC13 reconciliation (time, 75 s / +90 s)** → `v7-bosses.md` §V7.2
- **Mothership stats / entrance / oscillation / moveset / reward** → `v7-bosses.md` §V7.4, §V7.7–V7.12
- **Yellow fan → 12-red 360° ring (reuses the v5 frozen split)** → `v7-bosses.md` §V7.12
- **Arrival field-clear (free, reuses the v6 flush/flash)** → `v7-bosses.md` §V7.5
- **Bomb-vs-boss rule (boss immune)** → `v7-bosses.md` §V7.14
- **Pause state machine / freeze list / Q-hold arc / overlay layout** → `v8-pause.md` §V8.2–§V8.6
- **Q-hold-to-quit on START + GAME_OVER (reuse v8 arc) / shared-counter reset-on-transition / START Q carve-out** → `v10.md` §V10.2–§V10.6
- **Hold-R-to-restart on PAUSE + GAME_OVER (two coexisting gestures) / two independent hold counters / restart moved off the K_r KEYDOWN edge / both-counters-reset-on-transition / two arcs** → `v12.md` §V12.2–§V12.8
- **Lifetime-stats screen: STATS GameState placement / Tab nav from START / Esc-back / Tab carve-out of "any key starts" / STATS not in Q/R hold sets** → `v14.md` §V14.2–§V14.7
- **Smoke-test design** → `v1-base.md` §11 (base) + each increment's smoke section (§V5.6, §V6.10, §V7.15, §V8.11 R75 row)

## Updating this spec
- **New increment:** add `vN-<topic>.md` starting with `# vN increment — …`, add a row above + a
  topic-map entry, and flag any section it *supersedes*. One-line the why in `../history.md`.
- **Fix a shipped feature:** edit that version's file **in place** (keep it matching `workspace/game/`)
  and record the why in `../history.md`. Numbers here are the contract — don't rewrite casually.
