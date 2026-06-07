# Brief — archived increment framings (v13–v19)

Frozen 2026-06-07 when the studio turned a new page for v20. These are the Orchestrator's kickoff
framings, moved out of `../shared/brief.md` so that file holds only the theme + the *current*
increment. All of these shipped & passed QA; their final specs are canonical in each role folder.
Earlier framings: v2/v5 → `brief-increments-v2-v5.md`; v7–v12 → `brief-increments-v7-v12.md`.

> v13–v18 were lightweight increments whose kickoff framings were not retained separately in the brief
> (they were captured in the backlog tables + each domain's `history.md` at the time). Only the full
> v19 framing was live in `brief.md` at page-turn; it is preserved verbatim below.

---

## v19 increment — precise controls (focus mode + circular player hitbox + larger bullets)

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

**Scoped roles:** full pipeline — **BA → Designer → Artist → Writer → Level-designer → Programmer → QA.**
