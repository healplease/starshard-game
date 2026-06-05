# v2 increment — Bonus pickups + active-buff HUD (placeholder visuals)

Owner: artist · Date: 2026-06-05 · Status: complete
Inputs: `workspace/design/gdd.md` v2 (§V2.2 buff table, §V2.4 pickup intent, §V2.6 HUD intent, §V2.7 render
order), `workspace/requirements/requirements.md` v2 (R23 pickup, R27 shield, R29 HUD indicator), `workspace/art/art_spec.md`
v1 (palette above).

> **Constraint reminder (C2) still holds:** every element below is drawn with `pygame.draw.*` and
> `pygame.font` only — **no image/sound files**. This section **appends** to v1; all v1 palette entries
> and sizes above are unchanged. Where a v2 color matches a v1 entry I **reuse** it (noted); only four
> genuinely new colors are introduced. The Programmer should not have to invent any color, size, or shape.
> **Writer owns the final letters/labels** (the letters below — `+ F R S 2` — match GDD §V2.2 and are the
> render targets unless Writer overrides); **Level-designer owns spawn rates.** The Artist owns hex + geometry.

---

## V2.1 Bonus palette (named RGB — paste as constants, extends §1)

```python
# ── Bonus pickups & buff indicators (v2) ────────────────────────────
# Color intent (GDD §V2.4): Repair=green · Fan=amber/orange · Rapid=cyan · Shield=pale-blue · Score×2=gold
BONUS_REPAIR = (60, 210, 90)    # #3CD25A  green  — REUSE of v1 HP_GREEN (ties "repair" to the health color)
BONUS_FAN    = (255, 140, 40)   # #FF8C28  orange — NEW (warm, distinct from gold Score & red enemy bullet)
BONUS_RAPID  = (80, 220, 255)   # #50DCFF  cyan   — REUSE of v1 PLAYER (rapid = "your gun", player color)
BONUS_SHIELD = (180, 220, 255)  # #B4DCFF  pale blue — NEW (desaturated, reads as a protective bubble)
BONUS_SCORE  = (255, 210, 70)   # #FFD246  gold   — NEW (reward/treasure color)

BONUS_INK    = (10, 12, 22)     # #0A0C16  the kind-letter glyph color — REUSE of v1 BG (dark on bright fills)
PILL_TRACK   = (40, 44, 58)     # #282C3A  empty portion of a buff-pill timer bar — REUSE of v1 HP_BACK
```

**Per-kind quick reference (single source of truth — pickup fill, letter, buff-pill color all share one hex):**

| Kind | Letter | Hex | RGB | Origin |
|---|---|---|---|---|
| Repair | `+` | `#3CD25A` | (60, 210, 90) | reuse `HP_GREEN` |
| Spread / Fan | `F` | `#FF8C28` | (255, 140, 40) | new `BONUS_FAN` |
| Rapid | `R` | `#50DCFF` | (80, 220, 255) | reuse `PLAYER` |
| Shield | `S` | `#B4DCFF` | (180, 220, 255) | new `BONUS_SHIELD` |
| Score ×2 | `2` | `#FFD246` | (255, 210, 70) | new `BONUS_SCORE` |

**Why these:** all five are bright enough that the dark `BONUS_INK` letter pops on them, and all five are
mutually distinguishable in hue (green / orange / cyan / pale-blue / gold) **and** by their letter, so a
color-blind read still works via the glyph. Repair borrows the health green and Rapid borrows the player
cyan to make their meaning self-evident; the diamond shape (below) keeps even the cyan Rapid pickup from
being confused with the cyan triangular ship or its rectangular bullets.

A paste-ready registry (matches GDD `entities/bonus.py`):

```python
# kind → (letter, color)   — letters are Writer-overridable; colors are final.
BONUS_STYLE = {
    "REPAIR": ("+", BONUS_REPAIR),
    "FAN":    ("F", BONUS_FAN),
    "RAPID":  ("R", BONUS_RAPID),
    "SHIELD": ("S", BONUS_SHIELD),
    "SCORE":  ("2", BONUS_SCORE),
}
```

---

## V2.2 Bonus pickup — the diamond (R23, GDD §V2.4)

A **diamond** (square rotated 45°), **26 px point-to-point**, color-coded per kind, with the kind letter
centered. Collision is a circle, **radius 13** (GDD §V2.4) — the diamond's points just reach the collide
circle, so the visual matches the hitbox.

```python
# Diamond vertices from center (cx, cy); 26 px point-to-point → half-diagonal = 13.
diamond_pts = [(cx,      cy - 13),   # top
               (cx + 13, cy),        # right
               (cx,      cy + 13),   # bottom
               (cx - 13, cy)]        # left
pygame.draw.polygon(screen, fill, diamond_pts)            # fill = BONUS_STYLE[kind][1]
pygame.draw.polygon(screen, FLASH, diamond_pts, width=1)  # 1px white outline → separates from dark space
# kind letter, centered:
glyph = FONT_PICKUP.render(BONUS_STYLE[kind][0], True, BONUS_INK)
screen.blit(glyph, glyph.get_rect(center=(cx, cy)))
```

| Property | Value |
|---|---|
| Shape | diamond (4-pt polygon), 26 px point-to-point (half-diagonal 13) |
| Fill | per-kind `BONUS_STYLE[kind][1]` (table V2.1) |
| Outline | 1 px `FLASH` (#FFFFFF) — universal, keeps every kind crisp on the dark field |
| Letter | `BONUS_STYLE[kind][0]` in `FONT_PICKUP`, color `BONUS_INK`, centered on `(cx, cy)` |
| Collision | circle r = 13 (GDD §V2.4) |
| Motion | 2.0 px/f straight down, no h-drift, **not** ramp-accelerated (GDD §V2.4 — art draws, physics owns) |

- **Letter glyph intent:** all five glyphs (`+ F R S 2`) are single characters rendered from the built-in
  font in dark `BONUS_INK` so they read as a stamped label on a bright gem. The `+` for Repair is the font's
  plus glyph (no need to draw crossed rects). Center-anchor every glyph with `get_rect(center=...)` so
  different glyph widths stay visually centered in the diamond.
- **Collect feedback (brief, optional, GDD §V2.4 "brief collect feedback"):** on collect, emit **6 particles
  in the pickup's fill color** at the pickup center (reuse the §5 death-burst: 2×2 rects, `[-3,3]` px/f,
  20-f life). This is the cheapest "pop" and reuses existing code. A 1-frame `FLASH` ring
  (`pygame.draw.circle(screen, FLASH, (cx,cy), 16, 2)`) is an even cheaper alternative; either satisfies the
  feedback intent. Cuttable.

New font for the pickup glyph (extends §4.1):

```python
FONT_PICKUP = pygame.font.SysFont(None, 22)   # diamond kind-letter (fits inside the 26 px gem)
FONT_PILL   = pygame.font.SysFont(None, 18)   # buff-pill letter box glyph (fits the 14×14 box)
```

---

## V2.3 Active-buff HUD — the pill stack (R29, GDD §V2.6)

A **vertical stack at top-left, under SCORE**. SCORE is `FONT_HUD` at `(12, 10)` (§4.2); pills begin at
`(12, 36)` and stack downward, **one row per active timed buff**, each row **18 px** tall. **Repair has NO
pill** (it's instant — see V2.4). Four possible timed buffs (Fan, Rapid, Shield, Score) → the stack ends by
`y ≈ 104`, well clear of the play area.

**One pill = `[14×14 letter box] [gap 4] [40×6 timer bar]`.** Exact geometry for the pill in stack slot
`i` (i = 0,1,2,3 in enum order):

```python
PILL_X      = 12                 # left edge of the stack (aligned under SCORE at x=12)
PILL_TOP    = 36                 # y of the first pill (just under the 28px SCORE line)
PILL_ROW_H  = 18                 # vertical pitch between pills
BOX_SIZE    = 14                 # letter box is 14×14
BAR_W, BAR_H = 40, 6             # timer bar
BAR_GAP     = 4                  # gap between box and bar

y = PILL_TOP + i * PILL_ROW_H
# 1) colored letter box
box = pygame.Rect(PILL_X, y, BOX_SIZE, BOX_SIZE)
pygame.draw.rect(screen, color, box)                 # color = BONUS_STYLE[kind][1]
pygame.draw.rect(screen, HP_BORDER, box, width=1)    # thin frame so a dark-edged buff still has an edge
glyph = FONT_PILL.render(letter, True, BONUS_INK)     # letter = BONUS_STYLE[kind][0]
screen.blit(glyph, glyph.get_rect(center=box.center))
# 2) shrinking timer bar, vertically centered against the 14px box: (14-6)//2 = 4
bar_x, bar_y = PILL_X + BOX_SIZE + BAR_GAP, y + 4     # = (30, y+4)
pygame.draw.rect(screen, PILL_TRACK, (bar_x, bar_y, BAR_W, BAR_H))             # empty track
fill_w = int(BAR_W * frames_remaining / full_duration)                         # drains as it counts down
pygame.draw.rect(screen, color, (bar_x, bar_y, fill_w, BAR_H))                 # buff-colored fill
```

| Pill part | Geometry | Color |
|---|---|---|
| Letter box | 14×14 at `(12, 36 + 18·i)` | fill = buff color; 1 px `HP_BORDER` frame |
| Box letter | `FONT_PILL` (18), centered in box | `BONUS_INK` |
| Timer track | 40×6 at `(30, 36 + 18·i + 4)` | `PILL_TRACK` (#282C3A) |
| Timer fill | `40 · remaining/full` wide, left-anchored | buff color (matches the box) |

- **Stable order (no jump):** iterate buffs in **BonusKind enum order — Fan, Rapid, Shield, Score** — and
  render a pill **only while its timer > 0**, packing live pills from `PILL_TOP` downward (slot `i` =
  position among *currently active* buffs in enum order). Because the iteration order is fixed, pills never
  reorder; a buff expiring just removes its row and the ones below shift up by one `PILL_ROW_H`. (If you
  prefer zero shifting, you may reserve a fixed slot per kind instead — either reads cleanly; packing is the
  GDD's "stack" intent and keeps the column tight.)
- **Bar drains left→right** as `remaining/full` falls (GDD §V2.6). Fill color = the buff color so box and bar
  always agree.
- **Optional seconds number (Writer's call):** if shown, `FONT_SMALL` (22) in `TEXT`, right of the bar at
  `(76, y)`. Cut first if cramped — the shrinking bar already conveys "time left".

---

## V2.4 Repair popup — the transient "+40" (R29, GDD §V2.6)

Repair is instant and gets **no pill**; instead a **transient green popup** appears near the HP bar (top-
right) and the HP bar visibly jumps (the §4.3 bar already does this for free). **Writer owns the exact text**
(the GDD's placeholder is `+40`).

| Property | Value |
|---|---|
| Text | Writer's string (placeholder `"+40"`) |
| Font | `FONT_HUD` (28) |
| Color | `BONUS_REPAIR` / `HP_GREEN` (#3CD25A) — same green as the bar it's near |
| Anchor | centered at the HP-bar center x. HP bar = `(468, 12, 120, 14)` → center x = **528** |
| Start y | **30** (just under the bar) |
| Lifetime | **30 f** (GDD §V2.6) |
| Motion (optional juice) | drift up 0.5 px/f over its life (`y = 30 − 0.5·age`); cuttable |

```python
# while repair_popup_timer > 0:
age = REPAIR_POPUP_LIFE - repair_popup_timer          # REPAIR_POPUP_LIFE = 30
surf = FONT_HUD.render(repair_text, True, HP_GREEN)    # repair_text from Writer; placeholder "+40"
screen.blit(surf, surf.get_rect(center=(528, 30 - 0.5 * age)))   # drift optional: drop the "- 0.5*age" to hold still
```

Constant to add to config: `REPAIR_POPUP_LIFE = 30`.

---

## V2.5 Shield read — blink + optional bubble ring (R27, GDD §V2.2)

Shield reuses the **R18 blink** (the player is drawn only on frames where `(timer // 6) % 2 == 0`; §2 table).
The player is invulnerable while **either** `iframes > 0` **or** `shield > 0`, and **both drive the same
blink** — so the existing blink code already covers Shield with no new art required. ✅ **Confirmed: the blink
alone reads as "can't be hit."**

**Distinguishing Shield from the brief post-hit i-frame blink (recommended, optional):** the two look
identical for their first second, and Shield lasts 5 s, so add a **faint steady bubble ring** around the ship
**only while `shield > 0`**, drawn on the frames the ship is visible:

```python
# after drawing the player ship, while shield > 0 and the ship is in a visible blink frame:
pygame.draw.circle(screen, BONUS_SHIELD, (int(px), int(py)), 18, width=2)   # ring just outside the ship
```

| Property | Value |
|---|---|
| Shape | circle outline (ring), **radius 18**, **width 2** |
| Color | `BONUS_SHIELD` (#B4DCFF) — ties the ring to the Shield pickup/pill |
| Center | player center `(px, py)` |
| When | `shield > 0` only, on visible (non-blink-off) frames |

Radius 18 sits just outside the player's collision circle (r=13) and the 28×30 hull, so the bubble clearly
hugs the ship without obscuring it. The pale-blue ring is distinct from the brief white i-frame flash, so a
player can tell "I have my shield" (steady blue bubble, 5 s) from "I just got hit" (no ring, ~1 s). This is
the GDD §V2.2 "faint steady ring" option; if cut, the shared blink still satisfies R27.

---

## V2.6 Updated render order (supersedes §7 for v2)

Back-to-front each frame (additions in **bold**):
1. `screen.fill(BG)`
2. Starfield Far → Mid → Near
3. Asteroids (large then small) and enemy bullets
4. **Bonus pickups (diamonds)** — same layer as hazards, before player bullets
5. Player bullets
6. Enemies
7. Player ship (respecting i-frame/shield blink) → **then the Shield bubble ring (V2.5) if `shield>0`**
8. Particles (death bursts **+ collect bursts**)
9. HUD: score, health bar, **buff-pill stack (V2.3)**, **repair popup (V2.4)** — always on top
10. State overlays (Start / Game Over dim+text / Pause) last

---

## V2.7 Definition-of-done check (v2 self-audit)
- Five diamond pickups: each has exact hex + diamond geometry + letter glyph intent ✓ (V2.1, V2.2).
- Buff pills: 14×14 letter box + 40×6 shrinking bar, per-buff color, exact positions, stable enum order,
  Repair excluded ✓ (V2.3).
- Repair "+40" popup: color, font, anchor (528, 30), 30-f life ✓ (V2.4).
- v1 palette reused (Repair=HP_GREEN, Rapid=PLAYER, ink=BG, track=HP_BACK); only 4 new colors added ✓.
- Shield blink confirmed to read; optional pale-blue r=18 bubble ring specced to distinguish it ✓ (V2.5).
- Render order updated for pickups, shield ring, collect particles, pills, popup ✓ (V2.6).
- All shapes-only / `pygame.draw.*` + `pygame.font` ✓. A programmer can render every v2 element from this
  file without choosing any color, size, or shape.

— end of art_spec (v2) —

---
---

