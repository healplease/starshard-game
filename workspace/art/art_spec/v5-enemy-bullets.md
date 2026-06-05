# v5 increment — Three enemy bodies + RED/GREEN/CYAN bullet families (placeholder visuals)

Owner: artist · Date: 2026-06-05 · Status: complete
Inputs: `workspace/design/gdd.md` v5 (§V5.2 roster sizes, §V5.4 split lifecycle, §V5.5 placeholder colors +
constants, §V5.9 art notes), `workspace/requirements/requirements.md` v5 (R42 visual distinguishability, AC22),
`workspace/art/art_spec.md` v1 (§1 palette, §2.1 chevron math).

> **Constraint reminder (C2/R42) still holds:** every element below is drawn with `pygame.draw.*` and
> `pygame.font` only — **no external image/sound files**. This section **appends** to v1/v2; all prior palette
> entries and sizes are unchanged. The three enemy **bodies** read apart by **silhouette + size** (HEAVY **>**
> REGULAR **>** SCOUT); the three **bullet families** read apart by **hue** (RED / GREEN / CYAN). Collision radii
> are owned by the GDD (§V5.2/§V5.4) and are **not** changed by any render choice here — the green pellet is only
> *drawn* bigger. The Programmer should not have to invent any color, size, or shape.

---

## V5.1 The three enemy bodies — distinct silhouettes (R42, AC22)

All three keep the **magenta `ENEMY` fill (#FF46C8)** so friend/foe stays instant (cyan = you, magenta = them);
they are told apart by **shape, size, and outline weight**, not color. Silhouette story: **HEAVY = fat armored
octagon**, **REGULAR = mid chevron (unchanged)**, **SCOUT = small sharp dart**. +y is **down** (GDD §5); all
vertices are offsets from the body center `(cx, cy)`. Pass straight to `pygame.draw.polygon`.

| Kind | Shape & draw call | Body size (px) | Collision (GDD, fixed) | Fill | Outline |
|---|---|---|---|---|---|
| **HEAVY** | filled octagon (cut-corner block) + outline | **36 w × 32 h** | circle **r = 18** | `ENEMY` | **3 px** `ENEMY_EDGE` (armored/heavy) |
| **REGULAR** | downward chevron (v1 §2.1, unchanged) | **26 w × 24 h** | circle **r = 13** | `ENEMY` | **2 px** `ENEMY_EDGE` (as v1) |
| **SCOUT** | small sharp downward triangle (dart) | **20 w × 18 h** | circle **r = 10** | `ENEMY` | **1 px** `ENEMY_EDGE` (light/quick) |

Sizes match GDD §V5.2 intent; the descending outline weight (3 → 2 → 1 px) reinforces "armored / normal / flimsy"
on top of the silhouette so the read survives even mid-swarm.

### V5.1.1 Vertex math (paste-ready)

```python
# HEAVY — armored octagon, 36 wide × 32 tall (chamfer 8 px), center (cx, cy). Reads as a fat block.
heavy_pts = [(cx - 18, cy - 8), (cx - 10, cy - 16),   # left-top corner cut
             (cx + 10, cy - 16), (cx + 18, cy - 8),   # right-top corner cut
             (cx + 18, cy + 8), (cx + 10, cy + 16),   # right-bottom corner cut
             (cx - 10, cy + 16), (cx - 18, cy + 8)]   # left-bottom corner cut
pygame.draw.polygon(screen, ENEMY, heavy_pts)
pygame.draw.polygon(screen, ENEMY_EDGE, heavy_pts, width=3)

# REGULAR — downward chevron, 26 wide × 24 tall (UNCHANGED from v1 §2.1).
enemy_pts = [(cx,      cy + 12),   # bottom point (aimed at player)
             (cx + 13, cy - 12),   # top-right wing
             (cx,      cy - 5),    # center notch (chevron "V"); drop for a plain triangle
             (cx - 13, cy - 12)]   # top-left wing
pygame.draw.polygon(screen, ENEMY, enemy_pts)
pygame.draw.polygon(screen, ENEMY_EDGE, enemy_pts, width=2)

# SCOUT — small sharp dart, 20 wide × 18 tall, center (cx, cy). Plain narrow triangle = "darty".
scout_pts = [(cx,      cy + 9),    # nose (aimed at player)
             (cx + 10, cy - 9),    # rear-right
             (cx - 10, cy - 9)]    # rear-left
pygame.draw.polygon(screen, ENEMY, scout_pts)
pygame.draw.polygon(screen, ENEMY_EDGE, scout_pts, width=1)
```

- **Hit flash** (all three): same as v1 — flash `FLASH` (#FFFFFF) for 1 frame on taking a non-lethal bullet hit.
- **Death burst** (all three): v1 §5 — 6× `2×2` particles in the `ENEMY` fill color, `[-3,3]` px/f, 20-f life.
- **Optional tonal variant (cuttable):** if more body separation is ever wanted *without* breaking the magenta
  foe identity, darken HEAVY's fill to `(210, 50, 165)` and brighten SCOUT's to `(255, 120, 220)`. **Default is
  the single `ENEMY` fill for all three** — shape + size + outline weight already satisfy R42/AC22; this is pure
  optional polish.

---

## V5.2 Bullet palette — RED / GREEN / CYAN (paste as constants, extends §1)

```python
# ── v5 enemy-bullet families (GDD §V5.5) ─────────────────────────────────────
# Bodies stay magenta; bullets carry the per-kind read. All three are distinct in HUE and kept
# clear of the player cyan, the Repair/HP green, and the magenta enemy body.
EB_COLOR_RED   = BULLET_E          # #FF5A28 (255, 90, 40)  — REUSE v1 orange-red. Regular + ALL split children.
EB_COLOR_GREEN = (140, 240, 60)    # #8CF03C  toxic lime    — NEW. Heavy pellet (drawn larger; see V5.3).
EB_COLOR_CYAN  = (45, 205, 255)    # #2DCDFF  electric ice  — NEW. Scout bullet (drawn as a fast streak).
```

**Per-family quick reference (single source of truth):**

| Family | Hex | RGB | Fired by | Drawn as (V5.3) | Collision (GDD, fixed) |
|---|---|---|---|---|---|
| **RED** | `#FF5A28` | (255, 90, 40) | REGULAR + every split child | circle **r = 5** (unchanged) | r = 5 |
| **GREEN** | `#8CF03C` | (140, 240, 60) | HEAVY pellet (pre-split) | circle **r = 8** (visually larger) + white core | r = 5 (unchanged) |
| **CYAN** | `#2DCDFF` | (45, 205, 255) | SCOUT | **streak**: r=4 head + 12 px tail | r = 5 |

**Why these hues (the V5.9 / R42 anti-clash check):**
- **RED** is the existing `BULLET_E` reused verbatim — no retint needed; split children **are** ordinary red
  bullets (GDD §V5.4.4), so visual identity = mechanical identity. ✓
- **GREEN = toxic lime `#8CF03C`**, deliberately pushed *yellow-green* so it is unmistakable against the softer,
  bluer **Repair/HP green `#3CD25A` (60,210,90)** — a hazard "acid" green vs. the friendly "health" green. Also
  far from the gold Score `#FFD246` and warm Fan `#FF8C28`. Reads as danger, not pickup. ✓
- **CYAN = electric ice `#2DCDFF`**, pushed *bluer/colder* than the player's warmer **`PLAYER #50DCFF` (80,220,255)**
  and well clear of the minty player bullet **`BULLET_P #78FFF5`**. The decisive separator is **shape + motion**:
  the scout bullet is a thin downward **streak**, never the player's upward rectangle or stationary ship. Cold
  hue + streak + downward travel = "incoming fast round," not "your gun." ✓
- All three stay clear of the **magenta enemy body** `#FF46C8` (no green/cyan overlap with magenta). ✓

---

## V5.3 Bullet shapes & sizes (draw calls)

Collision is a flat **r = 5** for every enemy bullet (GDD §V5.2/§V5.4) — the draws below are **render-only**.

```python
# Config to add (render constants; collision stays EB_R = 5):
PELLET_DRAW_R   = 8     # GREEN heavy pellet is DRAWN at r=8 (collision still 5) — reads "fat & charged"
CYAN_TAIL_LEN   = 12    # px length of the scout streak's tail, drawn behind its heading
CYAN_HEAD_R     = 4     # px radius of the scout streak's head dot
```

**RED — regular + split children (unchanged):**
```python
pygame.draw.circle(screen, EB_COLOR_RED, (int(x), int(y)), 5)   # plain r=5 dot, as v1 §2 enemy bullet
```

**GREEN — heavy pellet, drawn larger with a hot core (so it reads as "about to split"):**
```python
pygame.draw.circle(screen, EB_COLOR_GREEN, (int(x), int(y)), PELLET_DRAW_R)        # r=8 lime body
pygame.draw.circle(screen, EB_COLOR_GREEN, (int(x), int(y)), PELLET_DRAW_R, 1)     # subtle same-color rim (opt.)
pygame.draw.circle(screen, FLASH,          (int(x), int(y)), 2)                    # 2px white core = charged
```
The r=8 body (vs. the r=5 reds and the streaky cyan) makes the splitting pellet the visually heaviest round on
screen — apt for the threat it becomes. Its **collision radius is still 5** (GDD §V5.2) — the extra 3 px is paint.

**CYAN — scout bullet, drawn as a fast streak along its velocity:**
```python
# vx, vy = the bullet's per-frame velocity (already unit*7.5 from the aim routine, GDD §V5.3).
import math
inv = 1.0 / max(1e-6, math.hypot(vx, vy))      # unit heading
ux, uy = vx * inv, vy * inv
tail = (int(x - ux * CYAN_TAIL_LEN), int(y - uy * CYAN_TAIL_LEN))   # tail trails BEHIND the head
pygame.draw.line(screen, EB_COLOR_CYAN, (int(x), int(y)), tail, 3)  # 3px streak
pygame.draw.circle(screen, EB_COLOR_CYAN, (int(x), int(y)), CYAN_HEAD_R)   # bright head dot (collision center)
```
The streak points along travel (tail behind), so the scout's high-velocity shot literally *looks* fast and is
never mistaken for the player's upward rectangle. Head dot sits on the collision center.

---

## V5.4 Optional split "burst" (green → red) — cuttable, not required

On a green pellet's split (GDD §V5.4.3), an optional 1-frame flourish sells the transformation. Reuses existing
machinery; **safe to skip** (the 3 red children appearing is already legible):

```python
# at the split point (px, py), once, on the frame the pellet is replaced:
pygame.draw.circle(screen, FLASH, (int(px), int(py)), 10, 2)   # 1-frame white ring
# + 4 particles fading green→red is overkill; if wanted, emit 4 of the §5 burst in EB_COLOR_GREEN.
```

Single white ring is the recommended cheapest version. If even more "juice" is wanted, emit a few `EB_COLOR_GREEN`
particles (§5 burst) at the split point — but this is pure polish and the first thing to cut.

---

## V5.5 Updated render order (extends V2.6 for v5)

No structural change — the new bullet families slot into the **existing enemy-bullet layer**, the three enemy
bodies into the **existing enemy layer**. Spelled out for clarity:

1. `screen.fill(BG)` → 2. Starfield → 3. Asteroids + **all enemy bullets (RED dots, GREEN pellets, CYAN streaks)**
→ 4. Bonus pickups → 5. Player bullets → 6. **Enemies (HEAVY octagon / REGULAR chevron / SCOUT dart)** →
7. Player ship (+ shield ring) → 8. Particles (death/collect **+ optional split burst, V5.4**) → 9. HUD →
10. State overlays.

Within the enemy-bullet layer, draw order among families doesn't matter (they rarely overlap and read by hue).

---

## V5.6 Definition-of-done check (v5 self-audit)
- Three enemy bodies, each with exact shape + size + paste-ready vertices + collision radius + outline weight:
  HEAVY octagon 36×32 / REGULAR chevron 26×24 (unchanged) / SCOUT dart 20×18 ✓ (V5.1). Distinct at a glance by
  silhouette + size (R42, AC22). ✓
- Three bullet families with final hex: RED `#FF5A28` (reuse), GREEN `#8CF03C`, CYAN `#2DCDFF` ✓ (V5.2), each
  with a draw call + render size (green drawn r=8, collision still 5; cyan streak) ✓ (V5.3).
- Anti-clash verified: GREEN ≠ Repair/HP green; CYAN ≠ player cyan/bullet; both ≠ magenta enemy body ✓ (V5.2).
- Optional split burst specced + marked cuttable ✓ (V5.4). Render order updated ✓ (V5.5).
- All `pygame.draw.*` + `pygame.font`, no external assets (C2/R42) ✓. A programmer can render every v5 element
  from this file without choosing any color, size, or shape.

— end of art_spec (v5) —

---
---

