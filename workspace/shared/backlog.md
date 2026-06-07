# Backlog — project task board

The studio's shared task board across chats. The **Orchestrator** owns it; every role ticks its own
row when finishing. Status: `todo` | `in-progress` | `done` | `blocked`.

> **Board only.** This file is the board + a one-line status. The *why* lives in each domain's
> `history.md`; the cross-role story is in `handoffs.md`. Full v1–v12 detail (per-version task tables
> + status prose) is archived → `../archive/backlog-v1-v12.md`. See `../README.md` for the map.

## Current game state — "Starshard" (v1–v17 shipped & passed QA, as of 2026-06-07)

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

Contract totals: **R1–R105**, **AC1–AC93**; **pytest suite 94/94** (59 unit / 35 e2e, `workspace/tests/`,
root `pyproject.toml` w/ ruff+pyright). Standing QA docs: `qa/feature_inventory.md`, `qa/test_plan.md`.
(v3 = KB reorg, v4 = QA docs, v9 = process hardening, v15 = test-infra — no game-feature change.)

**Play:** `.\.venv\Scripts\python.exe workspace\game\main.py` — Z fire · X bomb · Esc pause ·
hold Q quit · hold R restart (on PAUSE/GAME_OVER) · Tab stats (on START).

## Last increment — v17: HP-feedback + bullet-clarity polish (UI/UX, render-only) — ✅ SHIPPED (QA PASS 2026-06-07)

Three render-only UI/UX improvements (no mechanic/economy/copy change): (1) HP bar fades **green→red
gradually** (replaces the stepped `≥40/<40/<20` thresholds in art_spec v1-base §4.3); (2) a **subtle,
non-distracting red vignette** at **HP < 25 %**; (3) recolor the **HEAVY green pellet** (`#8CF03C`) to a
**non-green** hue — it clashes with the Repair/HP green `#3CD25A`. Color/render only; shapes, sizes,
collisions, and all gameplay numbers unchanged. Framing + locked decisions: `brief.md`.

| # | Role | Task | Owner | Status |
|---|---|---|---|---|
| 1 | artist | Define the HP-bar green→red gradient (endpoints+curve, supersedes v1-base §4.3), the HP<25% red vignette (tint/alpha/falloff/pulse, subtle), and a non-green HEAVY-pellet hue re-verified clear of all entities (art_spec vN) | artist | done |
| 2 | programmer | Implement the three render changes (gradient fill, vignette overlay, new pellet color); ruff+pyright+pytest+smoke green | programmer | done |
| 3 | qa-tester | Verify gradient fades smoothly, vignette appears <25% & stays subtle, pellet no longer green/clash-free, no AC1–AC93 regression, suite+smoke green | qa-tester | done |

Skipped (no impact): business-analyst, lead-game-designer, writer, level-designer.

## Previous increment — v16: second boss + random boss pool (new content) — ✅ SHIPPED (QA PASS 2026-06-07)

Add a **second boss** and make every boss-spawn pick **uniformly at random** from an **extensible boss
pool** (today: Mothership + new boss; future bosses = one registry entry). Human's hard constraints: the
new boss **spawns no ships/enemies** and has **deadlier attacks** than the Mothership. Boss appearance
cadence (≈75 s then +90 s) and the field-clear/spawn-freeze/reward framing are **unchanged** — only
*which* boss appears is randomized. Framing + locked decisions: `brief.md`.

| # | Role | Task | Owner | Status |
|---|---|---|---|---|
| 1 | business-analyst | Formalize requirements: new boss as content, random extensible-pool selection rule, the 2 hard constraints (no ship spawning, deadlier attacks) → new R#/AC# | business-analyst | done |
| 2 | lead-game-designer | Design the new boss: identity/theme, moveset/attack patterns (deadlier, ship-free), HP, reward, defeat behavior + the pool-selection concept (GDD vN) | lead-game-designer | done |
| 3 | artist | Placeholder shapes + palette for the new boss (distinct from Mothership) + any new attack/projectile visuals (art_spec vN) | artist | done |
| 4 | writer | New boss name + on-screen copy (boss banner / warning), matching Mothership treatment (story vN) | writer | done |
| 5 | level-designer | Random-pool selection rule + extensibility, new boss balance numbers (HP/damage/fire-rate so "deadlier" is concrete), confirm spawn timing unchanged (level_spec vN) | level-designer | done |
| 6 | programmer | Implement: new boss entity + attacks, refactor boss spawn → random pick from extensible pool, wire art/copy/balance; ruff+pyright+unit pytest+smoke green | programmer | done |
| 7 | qa-tester | Full rigor: new boss appears, random selection works & extensible, boss spawns NO ships, attacks deadlier, Mothership parity, no AC1–AC85 regression, suite+smoke green | qa-tester | done |

## Parked (non-blocking)

- **AC13 long runs** — expert pure-dodging can exceed 3 min; tuning levers in `levels/level_spec/`
  §8 / §V2.4. Act only if a human playtest confirms.
- **R35 screen-clear bonus** — deferred since v2 (GDD §V2); non-failing.
