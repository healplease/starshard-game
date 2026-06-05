# Backlog — project task board

The studio's shared task board across chats. The **Orchestrator** owns it; every role ticks its own
row when finishing. Status: `todo` | `in-progress` | `done` | `blocked`.

> **Board only.** This file is the board + a one-line status. The *why* lives in each domain's
> `history.md`; the cross-role story is in `handoffs.md`. Full v1–v12 detail (per-version task tables
> + status prose) is archived → `../archive/backlog-v1-v12.md`. See `../README.md` for the map.

## Current game state — "Starshard" (v1–v13 shipped & passed QA, as of 2026-06-06)

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

Contract totals: **R1–R91**, **AC1–AC77**; regression harness **65/65**. Standing QA docs:
`qa/feature_inventory.md`, `qa/test_plan.md`. (v3 = KB reorg, v4 = QA docs, v9 = process hardening —
no game-feature change.)

**Play:** `.\.venv\Scripts\python.exe workspace\game\main.py` — Z fire · X bomb · Esc pause ·
hold Q quit · hold R restart (on PAUSE/GAME_OVER).

## Active increment — none (v13 shipped 2026-06-06)

v13 (restart hold-arc co-located on quit-arc centre + recolored violet) is **shipped & passed QA**
(smoke green; R/Q arcs co-located PAUSE 300,483 / GAME_OVER 300,545; R fill violet `BONUS_BOMB` on top
of amber Q; hold timing & idle-visibility unchanged; no AC regression). *Why* → `art/history.md`.
Awaiting next theme/increment from the human.

## Parked (non-blocking)

- **AC13 long runs** — expert pure-dodging can exceed 3 min; tuning levers in `levels/level_spec/`
  §8 / §V2.4. Act only if a human playtest confirms.
- **R35 screen-clear bonus** — deferred since v2 (GDD §V2); non-failing.
