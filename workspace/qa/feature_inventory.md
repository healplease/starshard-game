# Feature Inventory — "Starshard" (v1 + v2)

Owner: qa-tester · Date: 2026-06-05 · Status: complete · Type: standing doc (not a per-run verdict)
Inputs traced against: `requirements/requirements/` (R1–R35, AC1–AC21), `design/gdd/`,
`levels/level_spec/`, `art/art_spec/`, `story/story/`, and the shipped `game/` package.

> **What this is.** A durable map of *every implemented feature* in the game, each traced to the
> requirement IDs (R#) and acceptance criteria (AC#) it satisfies and the **module(s)** that implement
> it. Pair it with `test_plan.md` (per-feature checklists + smoke & regression plans). The per-run
> verdict log stays in `qa_report/` — this file is the **what-exists/where map**, not a verdict.
>
> **How to use it.** After any change, find the touched feature here, jump to its modules, then run its
> checklist in `test_plan.md`. The Feature IDs (F1…F32) are the shared key between the two docs.

---

## 0. Environment of record
- Python **3.14.3** · `pygame-ce` **2.5.7** (SDL 2.32.10) · Windows 11, in the project `.venv`.
- Entry point: `workspace/game/main.py` (also importable as `python -m game.main`).
- Headless gate: `main.py --smoke-test` with `SDL_VIDEODRIVER=dummy` / `SDL_AUDIODRIVER=dummy`.
- Package shape (R32/AC21): **21 files** under `game/` — `config` · `world` · `app` · `input` · `main`
  + `entities/` (player, hazards, projectiles, bonus, fx) + `systems/` (spawning, physics, combat,
  buffs, scoring) + `view/` (render, hud). Dependency direction `config ← entities ← systems ← app → view`.

---

## 1. Traceability matrix (the one-screen index)

Legend — **Tier:** MUST / SHOULD / COULD. **Check:** [Smoke] headless · [Play] observe · [Code] inspect.

### v1 — "Starshard" base game

| F# | Feature | Req | AC | Tier | Check | Primary module(s) |
|----|---------|-----|----|----|------|-------------------|
| **F1** | Single fixed 600×800 window, top-down, world-scrolls | R1 | AC1 (window built), AC3 | MUST | [Play] | `config.py` (W,H,FPS), `app.py` (`_init_pygame`) |
| **F2** | Player ship (cyan triangle, near bottom-center at start) | R2 | AC3 | MUST | [Play] | `entities/player.py`, `view/render.py` (`_draw_player`), `config.py` (`P_START`) |
| **F3** | Keyboard move (arrows+WASD, 4-dir, diagonals) + on-screen clamp | R3 | AC3 | MUST | [Play] | `input.py` (`read_input`), `systems/physics.py` (`update_play` move+clamp), `config.py` (`P_SPEED`) |
| **F4** | Auto-scrolling parallax starfield (input-independent, all states) | R4 | AC4 | MUST | [Play] | `entities/fx.py` (`make_starfield`), `systems/physics.py` (`update_starfield`), `view/render.py` (`draw_starfield`) |
| **F5** | Scrolling asteroids/debris, small + large, downward drift, damage on contact | R5, R9 | AC5 | MUST | [Play] | `entities/hazards.py` (`Asteroid`,`make_asteroid`), `systems/spawning.py`, `systems/physics.py`, `systems/combat.py`, `view/render.py` |
| **F6** | Enemy fighter that enters, strafes, and fires aimed bullets | R6, R9 | AC6 | MUST | [Play] | `entities/hazards.py` (`Enemy`,`make_enemy`), `entities/projectiles.py` (`make_enemy_bullet`), `systems/physics.py` (enemy AI+fire), `systems/combat.py`, `view/render.py` |
| **F7** | Player weapon: Space fires upward, cooldown-gated (~5/s) | R7 | AC7 | MUST | [Play] | `entities/projectiles.py` (`make_player_shots`), `systems/physics.py` (firing), `config.py` (`FIRE_CD`,`PB_SPEED`) |
| **F8** | Combat collisions: player bullets destroy asteroids (1–2 hits) & enemies (2 HP); removed on kill | R8 | AC7 | MUST | [Play] | `systems/combat.py` (steps 1–2), `entities/fx.py` (`make_burst`) |
| **F9** | Damage collisions: asteroid/enemy/enemy-bullet contact reduces HP (first-hit-wins) | R9 | AC5, AC6, AC9 | MUST | [Play] | `systems/combat.py` (step 4), `config.py` (damage consts) |
| **F10** | Health pool (100 HP, 1 life) + on-screen HP bar (green/amber/red) | R10 | AC9 | MUST | [Play] | `entities/player.py` (`hp`), `view/hud.py` (`_draw_health_bar`), `config.py` (`P_MAX_HP`) |
| **F11** | Score (kills + survival tick) + always-on display | R11 | AC8 | MUST | [Play] | `systems/scoring.py` (`award`,`survival_tick`), `view/hud.py` (score), `config.py` (score consts), `level_spec §7` |
| **F12** | Game-over state on HP≤0: freeze + dim + final score | R12 | AC10 | MUST | [Play] | `app.py` (`_step_play`→GAME_OVER, `_draw`), `world.py` (`GameState`), `view/hud.py` (`draw_gameover`) |
| **F13** | Restart (`R`) full reset without relaunch + clean quit (`Esc`/close) | R13 | AC11 | MUST | [Play] | `app.py` (`_handle_events`), `world.py` (`reset_run`) |
| **F14** | Headless smoke test: 120 frames, simulated input, exit 0, no hang | R14 | AC1, AC2 | MUST | [Smoke] | `main.py`, `app.py` (smoke branch in `run`), `input.py` (`smoke_input`), `systems/spawning.py` (`seed_smoke`) |
| **F15** | Difficulty ramp (asteroid/enemy spawn, enemy fire, enemy cap, hazard speed, large%) | R15 | AC13 | SHOULD | [Play] | `config.py` (ramp formulas), `systems/spawning.py`, `systems/physics.py` (fire interval), `entities/hazards.py`, `level_spec §3` |
| **F16** | Start screen (title/pitch/controls/blinking prompt), starfield behind | R16 | — (observe) | SHOULD | [Play] | `view/hud.py` (`draw_start`), `app.py` (state machine), `story §2` |
| **F17** | Hit/destroy feedback (large-rock white flash + 6-particle death burst) | R17 | — (observe) | SHOULD | [Play] | `entities/hazards.py` (`flash`), `entities/fx.py` (`make_burst`), `systems/combat.py`, `view/render.py` |
| **F18** | Brief post-hit i-frames (60 f) with blink visualization | R18 | — (observe) | SHOULD | [Play] | `entities/player.py` (`iframes`,`invulnerable`,`blink_timer`), `systems/combat.py`, `systems/physics.py`, `view/render.py` |
| **F19** | Session high score ("BEST") shown on Game Over | R19 | AC10 | COULD | [Play] | `world.py` (`best`), `app.py` (`_step_play`), `view/hud.py` (`draw_gameover`) |

### v2 — Pickup bonuses + modular refactor

| F# | Feature | Req | AC | Tier | Check | Primary module(s) |
|----|---------|-----|----|----|------|-------------------|
| **F20** | Bonus pickup entity (diamond + letter, drifts down at flat 2.0 px/f, collected on overlap, no-penalty miss) | R23 | AC14 | MUST | [Play] | `entities/bonus.py`, `systems/spawning.py`, `systems/physics.py` (drift+despawn), `systems/combat.py` (step 3), `view/render.py` (`_draw_bonus`) |
| **F21** | Repair bonus (instant +40 HP, clamp-no-overheal, "+40" popup, never stacks) | R24 | AC15 | MUST | [Play] | `systems/buffs.py` (`apply` REPAIR), `config.py` (`REPAIR_HP`,`REPAIR_POPUP_*`), `view/hud.py` (`_draw_repair_popup`) |
| **F22** | Spread/Fan bonus (timed 8 s): 3 beams at −12/0/+12°, reverts on expiry | R25 | AC16 | MUST | [Play] | `config.py` (`FAN_VELOCITIES`,`FAN_ANGLES_DEG`), `entities/player.py` (`fan_active`), `entities/projectiles.py` (`make_player_shots`), `systems/buffs.py` |
| **F23** | Rapid-fire bonus (timed 8 s): cooldown 12→6 f, reverts on expiry | R26 | AC16 | MUST | [Play] | `config.py` (`RAPID_CD`), `entities/player.py` (`rapid_active`,`fire_cooldown`), `systems/physics.py` (firing), `systems/buffs.py` |
| **F24** | Shield bonus (timed 5 s): full invuln, reuses blink + bubble ring, reverts on expiry | R27 | AC16 | MUST | [Play] | `entities/player.py` (`shield_active`,`invulnerable`,`blink_timer`), `systems/combat.py` (step 4 skip), `view/render.py` (`_draw_player` ring/blink), `systems/buffs.py` |
| **F25** | Bonus spawning: timed drip (`randint(600,840) f`) + 15% bullet-kill enemy-drop; weighted kind; cap 3 | R28 | AC14, AC20 | MUST | [Play]/[Smoke] | `systems/spawning.py` (`update`,`roll_enemy_drop`,`spawn_bonus`), `config.py` (`DRIP_*`,`ENEMY_DROP_CHANCE`,`BONUS_WEIGHTS`,`BONUS_CAP`,`pick_bonus_kind`), `world.py` (`rng_drip`), `level_spec §V2.1` |
| **F26** | Active-buff HUD: one pill per timed buff (letter box + shrinking timer bar), stable order, Repair has none | R29 | AC17 | MUST | [Play] | `view/hud.py` (`_draw_buff_pills`), `config.py` (`TIMED_ORDER`,`PILL_*`), `world.py` (`TIMED_KINDS`) |
| **F27** | Stacking & refresh: different timed types coexist; re-collect = hard refresh (no accumulate/double); Repair never stacks | R30 | AC18 | MUST | [Play] | `systems/buffs.py` (`apply`), `entities/player.py` (`buff_timers`,`buff`), `entities/bonus.py` (`buff_duration`) |
| **F28** | Buff expiry → clean revert; restart wipes all buff/pickup/popup state (no leak) | R31 | AC16, AC19 | MUST | [Play]/[Smoke] | `systems/buffs.py` (`tick`), `world.py` (`reset_run`) |
| **F29** | Modular MVC-ish architecture, no line cap, importable, thin `main.py` | R32 | AC21 | MUST | [Code] | whole `game/` package; `main.py` (thin entry), `config`/`entities`/`systems`/`view` split |
| **F30** | Smoke gate preserved across refactor AND exercises a full bonus lifecycle (spawn→collect→apply→expire) | R33 | AC20 | MUST | [Smoke] | `app.py` (`run` smoke seed hook), `systems/spawning.py` (`seed_smoke_bonus`), `config.py` (`SMOKE_*`), `level_spec §V2.5` |
| **F31** | Score×2 bonus (timed 10 s): doubles all score while active; own HUD pill | R34 | AC16, AC17, AC18 | COULD (IN) | [Play] | `systems/scoring.py` (`award`), `entities/player.py` (`score_mult_active`), `view/hud.py` (pill), `config.py` (`SCORE_MULT`) |
| **F32** | Screen-clear / bomb pickup | R35 | — | COULD (OUT) | — | **NOT IMPLEMENTED** — deferred by GDD §V2.8; absence does not fail v2 (see §3). |

---

## 2. Feature notes (the non-obvious "how it actually works")

Only the details a tester needs that aren't obvious from the matrix:

- **F3 clamp (R3):** the player bounding box is clamped to `x∈[14, 586]`, `y∈[15, 785]`
  (`physics.update_play`) — not the raw centre to `[0,W]`. So the *visible triangle* never leaves the
  window. Verify against the box, not the centre.
- **F8/F9 collision order (combat.resolve, GDD §V2.7):** strictly (1) player bullets×asteroids →
  (2) player bullets×enemies (+ enemy-drop roll) → (3) player×bonus collect → (4) player damage, then
  the dead-set sweep. **First hit wins** in step 4 (one damage source/frame). Anything destroyed earlier
  in the frame is skipped by later steps (the `dead_*` id-sets).
- **F11 score (scoring.award):** *every* point — asteroid (+10/+20), enemy (+50), and the **+1/sec
  survival tick** (`level_spec §7`) — flows through `award`, so Score×2 (F31) multiplies all of them
  uniformly. Survival tick is credited in `app._step_play` *after* `w.frame += 1`.
- **F14/F30 smoke harness (app.run):** in smoke mode it forces PLAY immediately, seeds 3 asteroids + 1
  enemy at init (`seed_smoke`), and on **frame 2** seeds a short-duration **Rapid** pickup at `(300,700)`
  (`seed_smoke_bonus`) directly in the player's path. Scripted input is a slow L-R sweep firing every
  frame (`input.smoke_input`). Fixed RNG seed `1234`. Hard cap 120 frames → `sys.exit(0)`.
- **F18/F24 invulnerability (player.invulnerable):** the player is invulnerable if **either**
  `iframes>0` (brief post-hit R18) **or** Shield is active (R27) — the two may overlap; both drive the
  same blink (`blink_timer = max(iframes, shield)`). The **bubble ring** (`render._draw_player`) draws
  *only* while Shield is up, distinguishing a 5 s shield from a ~1 s i-frame blink.
- **F20 bonus drift (physics):** bonuses drift at a **flat** `BONUS_SPEED = 2.0 px/f` and are **not**
  subject to `hazard_speed_bonus(t)` — so they stay interceptable all run. Missed bonuses despawn at
  `y − 13 > H` with no penalty.
- **F25 spawn paths:** the **drip** timer is drawn at run start (`rng_drip`) so the first bonus lands
  ~10–14 s in; it re-draws whether or not a spawn happened (no banking), and is skipped at the cap of 3.
  The **enemy-drop** (15%) fires only on a **bullet-kill** (combat step 2) — **ram-kills never drop**.
  Both paths share one weight ladder (`config.pick_bonus_kind`): Repair 30 / Fan 20 / Rapid 20 / Shield
  15 / Score 15.
- **F27 refresh (buffs.apply):** a timed buff is a **hard reset** to one full duration, never an add —
  so the timer bar can never exceed full, and effects never double. Repair is applied and discarded
  (no entry stored). `buff_timers` holds *only* currently-active timed buffs.
- **F28 restart boundary (world.reset_run):** rebuilds player + clears `bonuses`/`particles`/all bullets
  + resets `repair_popup_timer`, score, frame, spawn timers — but **preserves** `rng`, `stars`, and
  `best` (session-level, not run-level). That split is the R31/AC19 boundary.
- **F31 Score×2 (R34) is IN; F32 screen-clear (R35) is OUT** — see §3.

---

## 3. Deliberately-not-built (documented gaps, not defects)

These are *intentional* per the upstream specs — a tester should not file them as bugs:

- **R35 — Screen-clear / bomb pickup (F32):** **OUT.** Deferred by GDD §V2.8 (swings balance / needs its
  own clear+score-attribution rules). COULD-tier → its absence does not fail v2. No code, no HUD entry,
  not in the `BonusKind` enum.
- **R20 — Combo / score popups:** not built (GDD §13 / `level_spec §7` chose a quiet +1/sec survival
  tick instead, no combo). COULD-tier, non-failing.
- **R22 — Pause toggle:** not built. The GDD specs it as optional (`P`); no `PAUSED` state exists in
  `world.GameState` (only START/PLAY/GAME_OVER). COULD-tier, non-failing.
- **First-1.5 s no-spawn-on-player-x anti-cheap-shot rule** (`level_spec §4`, optional): not implemented
  (it was explicitly "skip if it costs lines"). Non-failing.

---

## 4. Open caveat carried forward (non-blocking)

- **AC13 run length (F15):** the difficulty ramp is implemented verbatim and *every* run terminates, but
  **expert pure-dodging can exceed the 3-min ceiling** (v1 QA measured a near-optimal dodge-bot at
  ~2.7–5.7 min). Flagged **non-blocking** (R15 is SHOULD-tier and met); the v2 buff economy was analyzed
  to be net-neutral on this (`level_spec §V2.3`). Tuning levers, cheapest-first, live in `level_spec §8`
  (v1) and `§V2.4` (v2) — apply **only if a human playtest confirms** long runs. Tracked in `backlog.md`
  "Parked" items.

---

*Maintenance: when a feature is added or a module moves, update this file's matrix + notes and the
matching checklist in `test_plan.md` in the same change. Keep verdicts in `qa_report/`.*
