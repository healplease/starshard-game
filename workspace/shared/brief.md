# Project Brief

## Theme (from the human)
> A top-down auto-scrolling 2D space shooter. A little spaceship flies through the cosmos,
> avoiding debris and asteroids while fighting enemy ships.

## One-line pitch (Orchestrator's framing)
"**Starshard**" — pilot a lone scout ship through an endless scrolling starfield; dodge drifting
asteroids/debris and blast enemy fighters to rack up a score before your ship is destroyed.

## Genre & shape
- **Genre:** top-down vertical auto-scroller / arcade shoot-'em-up (shmup).
- **Camera:** fixed single screen; the world scrolls past the player (starfield + hazards move
  downward, ship moves within the screen).
- **Win/lose:** arcade-style — survive and score as high as possible; lose when health runs out.

## Hard constraints (from CLAUDE.md — every role respect these)
- One single screen, keyboard-only, 2D.
- Placeholder art ONLY: colored shapes + on-screen text, no external image/sound files.
- Code is modular; `main.py` stays the entry point and supports `--smoke-test` (120 frames, simulated
  input, exits 0). Keep the smoke gate green.
- Python 3.14 + `pygame-ce` from the `.venv`.

## Current state & where the detail lives
v1–v15 shipped & passed QA — see `backlog.md` for the capability summary and the canonical specs in
each role folder. Closed-increment framings (v2, v5, v7–v15) are archived in
`../archive/brief-increments-*.md`.

## Current increment — v16: second boss + random boss pool (new content)

**Human's words:** create a new boss and add it to the game. Whenever a boss spawns, pick **randomly**
between the Mothership and this new boss — and all **future bosses join the pool** too. One condition:
the new boss must **NOT spawn any new ships** (that's the Mothership's gimmick) and must have **deadlier
attacks**.

This is a **new-content / mechanic increment** — the **full creative pipeline** runs
(BA → Designer → Artist → Writer → Level-designer → Programmer → QA).

**Decisions locked at kickoff (2026-06-07):**
- **Selection = uniform random from the boss pool** at each boss-spawn event (today: Mothership + the new
  boss). The pool must be an **extensible registry** — adding a future boss = one entry, no rework.
- **New boss hard constraints (from the human, non-negotiable):** (1) spawns **no ships/enemies** of any
  kind; (2) its attacks are **deadlier** than the Mothership's (higher threat — more damage / denser /
  harder to dodge, Designer+Level-designer decide the exact lever).
- **Boss appearance cadence is UNCHANGED** (first ~75 s, then +90 s); only *which* boss appears is
  randomized. Field-clear + spawn-freeze + reward-on-defeat boss framing stays.

**Open decisions delegated downstream (creative freedom within the constraints):**
- **BA:** formalize requirements — new boss as content, the random extensible-pool selection rule, and
  the two hard constraints, as new R#/AC#.
- **Designer:** invent the boss's **identity/theme + moveset/attack patterns** (deadlier, ship-free),
  HP, reward, defeat behavior, and the pool-selection concept.
- **Artist:** placeholder **shapes + palette** for the new boss (clearly distinct from the Mothership)
  and any new attack/projectile visuals.
- **Writer:** the boss **name** + any on-screen copy (boss banner / warning), matching the Mothership's
  treatment.
- **Level-designer:** the **random-pool selection rule** + extensibility, the new boss's **balance
  numbers** (HP / damage / fire-rate) so "deadlier" is concrete, and confirm spawn timing is unchanged.

**Smoke + test contract untouched:** `main.py --smoke-test` (120 frames, exit 0) stays the first gate;
the pytest suite (now 75) stays green and **grows** with new checks for the boss + random pool.

**Scoped roles:** full pipeline — **no roles skipped** (new content touches every lane).
