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
v1–v18 shipped & passed QA — see `backlog.md` for the capability summary and the canonical specs in
each role folder. Closed-increment framings (v2, v5, v7–v18) are archived in
`../archive/brief-increments-*.md`.

## Current increment — v19: precise controls (focus mode + circular player hitbox + larger bullets)

**Human's words:** introduce **precise controls** — when the player **holds SHIFT, ship movement becomes
twice as slow**, allowing precise avoiding. To accompany this, make the **ship's hitbox smaller** (not the
display — only the hitbox): **~50% smaller than the ship's actual size, and circular**. To balance for
this, make **all bullets ~50% larger**. Also, **while holding SHIFT (precise mode), display the actual
hitbox as a red circle at 50% opacity** on the ship. **Enemy hitboxes don't change.**

This is a **mechanic + balance** change (new input modifier, player collision-shape change, projectile
size/collision rebalance, plus a render indicator) → **full pipeline**: BA → Designer → Artist → Writer →
Level-designer → Programmer → QA.

**Baseline being changed (current code, `game/config.py`, for reference):**
- **Player:** `P_SPEED = 5` (move speed), `P_R = 13` (the ship's size constant — used today for both draw
  and collision). The smaller hitbox is a new circular collision radius ~50% of `P_R`; the **drawn ship is
  unchanged** at `P_R`.
- **Player bullets:** rectangular `PB_W, PB_H = 4, 12`.
- **Enemy/other bullets:** collision is a flat `EB_R = 5` across families (NOVA/pellet/boss have render-only
  draw radii: `NOVA_BULLET_DRAW_R = 6`, `PELLET_DRAW_R = 8`, etc.).

**Decisions locked at kickoff (2026-06-07):**
- **Precise mode = hold SHIFT (PLAY only).** While held, player move speed is **halved** (×0.5, "twice as
  slow"); release → normal. Does **not** change firing, and is a held modifier (not a toggle). Either
  Shift key. Exact key handling is the Programmer's; the rate contract is ×0.5 move speed.
- **Player hitbox is ALWAYS the smaller circle (confirmed with human 2026-06-07).** The shrink is a
  **permanent** change to the player's collision shape — **circular, radius ≈50% of the ship's drawn
  size** — active at all times, *not* only during precise mode. SHIFT does not change the hitbox; it only
  slows movement and **reveals** the hitbox (red circle). The **drawn ship sprite/size is unchanged.**
- **All bullets ~50% larger (balance).** Every projectile family grows ~50% in size — **both its drawn
  size and its collision size** so the visual matches the hitbox. This is the balancing lever for the
  shrunk player hitbox. ("All bullets" = player **and** enemy/boss projectiles.) Exact per-family numbers
  are the Level-designer's to lock.
- **Precise-mode hitbox indicator:** while SHIFT is held, draw the player's actual (always-on) hitbox as a
  **red circle at 50% opacity**, centered on the ship, radius = the real hitbox radius. PLAY only; not
  shown when SHIFT is released. Exact red hue/alpha/blend is the Artist's.
- **Enemy hitboxes are unchanged.** Only the **player** collision shape shrinks; enemy/asteroid/boss
  collision radii stay as-is (bullet sizes grow for *all* families, but that's the projectile change, not
  the enemy-body change).

**Open questions left to downstream roles (not pre-decided here):** exact precise-mode multiplier (default
×0.5); exact player hitbox radius (≈50% of `P_R` → a concrete px); exact per-family bullet size deltas
(≈1.5×); the red indicator's hue/alpha/render slot; whether any control hint copy is added for SHIFT.

**Out of scope / unchanged:** the drawn ship and all entity sprites; enemy/asteroid/boss collision radii;
the bonus ladder + economy; HP/score; screen flow; all existing copy except an optional SHIFT control hint.

**Smoke + test contract:** `main.py --smoke-test` (120 frames, exit 0) stays the first gate; the pytest
suite (106) stays green and grows with precise-mode + hitbox + bullet-size behavior. The smoke path may
need to exercise SHIFT-held movement and the shrunk hitbox.

**Scoped roles:** full pipeline — **BA → Designer → Artist → Writer → Level-designer → Programmer → QA.**
