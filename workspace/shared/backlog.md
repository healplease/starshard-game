# Backlog — project task board

The studio's shared task board across chats. The **Orchestrator** owns it; every role ticks its own
row when finishing. Status: `todo` | `in-progress` | `done` | `blocked`.

> **Board only.** This file is the board + a one-line status. The *why* lives in each domain's
> `history.md`; the cross-role story is in `handoffs.md`. Closed-increment detail (per-version task
> tables) is archived → `../archive/backlog-v1-v12.md` (v1–v12) + `../archive/backlog-v13-v19.md`
> (v16–v19 tables; v13–v15 folded into the summary). See `../README.md` for the map.

## Current game state — "Starshard" (v1–v19 shipped & passed QA, as of 2026-06-07)

Top-down auto-scrolling space shooter, modular `pygame-ce` package under `game/`. Shipped capabilities:

- **Core (v1):** ship moves (Arrows/WASD), **Z** fires (cooldown), asteroids/debris + enemy fighters,
  HP + score, START / PLAY / GAME_OVER states. Spec contract: R1–R14, AC1–AC13.
- **Power-ups (v2):** 6 `BonusKind` pickups (Repair / Fan / Rapid / Shield / Score×2 / Bomb), HUD buff
  pills. MVC module split (no line cap). AC14–AC21.
- **Enemies (v5):** REGULAR / HEAVY / SCOUT types + GREEN splitting pellet → 3 RED children. AC22–AC29.
- **Bombs (v6):** **X** = screen-flush + flash (charges start 2 / cap 4, refilled by rarest pickup);
  controls Z=fire / X=bomb. AC30–AC38.
- **Bosses (v7):** Mothership @75 s then +90 s — field-clear, spawn-freeze, 4-step moveset, +1000 reward.
  AC39–AC52.
- **Pause + quit (v8/v10):** **Esc** pauses (full freeze); **hold Q** (~0.5 s, progress arc) quits from
  START / PAUSE / GAME_OVER. AC53–AC68.
- **Polish (v11/v12):** softer invuln pulse (never fully invisible); **hold R** (~0.5 s arc) restarts on
  PAUSE / GAME_OVER. AC69–AC77.
- **Polish (v13):** restart (R) hold-arc co-located on its screen's quit (Q) arc centre (PAUSE 300,483 /
  GAME_OVER 300,545), recolored violet `BONUS_BOMB`; keys told apart by colour not position. Render-only.
- **Save + stats (v14):** one-file versioned JSON save (`game/save.py`, atomic write, %APPDATA%\Starshard
  path, env-overridable for headless) persisting 5 lifetime values — highscore, runs, enemies/asteroids/
  bosses killed; counted at the `scoring.award` destroy sites, flushed **only** on GAME_OVER + hold-Q quit;
  missing/corrupt/unknown-version → zeros. New first-class **STATS** GameState off START (**Tab** toggles
  START⇄STATS, **Esc** backs out; arc-free). AC78–AC85.
- **Second boss + boss pool (v16):** **NOVA**, a projectile-only energy-core boss (4 bullet-only steps;
  spawns **zero** ships) that is **deadlier** than the Mothership on every axis (per-hit 25>15, ram 80>60,
  faster cadence/speed, reward 1500). Every boss-spawn now picks **uniformly at random** from an extensible,
  length-driven registry (`BOSS_POOL`/`BOSS_SPECS`, seedable; future boss = one entry). v7 framing + cadence
  (≈75 s, +90 s) unchanged. AC86–AC93.
- **HP-feedback + bullet-clarity polish (v17):** HP bar fades a **continuous green→amber→red gradient**
  (`hud.hp_bar_color`, supersedes the stepped v1-base §4.3 thresholds); a **subtle red vignette** (`#E63C3C`,
  edge-only falloff + slow breathing pulse) at **HP < 25 %** (render slot 8.5, PLAY only); the **HEAVY green
  pellet** recolored `#8CF03C`→**orchid `#D230DC`** (`EB_COLOR_GREEN`→`EB_COLOR_PURPLE`) to clear the
  Repair/HP green. Render/color only — shapes, sizes, collisions, economy unchanged. No new R#/AC#.
- **Bonus rebalance (v18):** **Fan** nerfed — side beams (±12°) fire at **half** the center cadence (2:1,
  parity resets on collect) and Fan rarer (ladder weight 20→**12**); center beam unchanged. **Rapid retired**
  everywhere; two new timed kinds split its weight 20 → **Overdrive** (`O`, electric-lime `#A6F03C`; cd 12→6 +
  bullet speed 10→12) and **Railgun** (`V`, cyan `#50DCFF`; bullet speed 10→**16** + cd 12→9). **Bullet speed**
  is now a buffable stat; cross-stat stacking = **strongest-wins per stat** (min cd / max speed), bounded +
  clean-reverting; restart resets. Ladder re-sliced to sum 100 over 7 kinds. AC94–AC101.
- **Precise controls (v19):** hold **Shift** = **FOCUS** — ship move speed halved (×0.5, PLAY-only, held-not-
  toggle; firing/bombs/i-frames untouched). Player **damage** hitbox is now an always-on circle `P_HITBOX_R=6`
  (≈50% of `P_R=13`), decoupled from the unchanged ship drawing; **pickup** reach stays generous at `P_R`. All
  bullets **~1.5× larger**, draw==collision every family (`EB_R 5→8`; player bullet `6×18`, coll `r=9`;
  `CYAN_TAIL_LEN 18`). While Shift held in PLAY, a **red 50%-opacity disc** (`#FF2840` @ alpha 128) draws the
  true hitbox (render-only). Enemy/boss body radii unchanged. AC102–AC108.

Contract totals: **R1–R119**, **AC1–AC108**; **pytest suite 117/117** (80 unit / 37 e2e, `workspace/tests/`,
root `pyproject.toml` w/ ruff+pyright). Standing QA docs: `qa/feature_inventory.md`, `qa/test_plan.md`.
(v3 = KB reorg, v4 = QA docs, v9 = process hardening, v15 = test-infra — no game-feature change.)

**Play:** `.\.venv\Scripts\python.exe workspace\game\main.py` — Z fire · X bomb · hold Shift Focus ·
Esc pause · hold Q quit · hold R restart (on PAUSE/GAME_OVER) · Tab stats (on START).

## Current increment — v20: (awaiting kickoff)

No increment open. The Orchestrator opens v20 here when the human gives the next theme/task — write
the framing into `brief.md`, scope the queue, and drop the per-role table here.

> **Closed-increment detail archived.** The v16–v19 task tables are frozen in
> `../archive/backlog-v13-v19.md` (v13–v15 were condensed into the capability summary above at ship
> time). The capability summary up top is the canonical compact state; canonical specs live in each
> role folder.

## Parked (non-blocking)

- **AC13 long runs** — expert pure-dodging can exceed 3 min; tuning levers in `levels/level_spec/`
  §8 / §V2.4. Act only if a human playtest confirms.
- **R35 screen-clear bonus** — deferred since v2 (GDD §V2); non-failing.
