# Art Spec — "Starshard" (placeholder visuals)

Owner: artist · Date: 2026-06-05 · Status: complete
Inputs: `workspace/design/gdd.md` (§6 entities, §7 numbers, §9 HUD, §10 visuals), `workspace/requirements/requirements.md`
(C2 shapes-only), `workspace/shared/brief.md`.

> **Constraint reminder (C2):** every element below is drawn with `pygame.draw.*` and `pygame.font`
> only — **no external image or sound files**. All sizes/positions match the GDD §7.3 master table and
> §9 HUD layout exactly; the Programmer should not have to invent any color, size, or shape.

---

## 1. Palette (named RGB — paste as constants)

Tight 12-color palette. Colors are plain `(R, G, B)` tuples ready for pygame; hex shown for reference.

```python
# ── Space / backdrop ────────────────────────────────────────────────
BG          = (10, 12, 22)     # #0A0C16  near-black space blue (whole window clear color)
STAR_FAR    = (90, 100, 130)   # #5A6482  far parallax layer — dim blue-grey
STAR_MID    = (160, 170, 200)  # #A0AAC8  mid parallax layer — medium
STAR_NEAR   = (235, 240, 255)  # #EBF0FF  near parallax layer — bright near-white

# ── Player ──────────────────────────────────────────────────────────
PLAYER      = (80, 220, 255)   # #50DCFF  cyan ship body
PLAYER_EDGE = (220, 250, 255)  # #DCFAFF  near-white outline / cockpit accent
BULLET_P    = (120, 255, 245)  # #78FFF5  bright cyan player bullet

# ── Hazards ─────────────────────────────────────────────────────────
ASTEROID_S  = (150, 150, 160)  # #9696A0  small asteroid — light grey
ASTEROID_L  = (110, 110, 122)  # #6E6E7A  large asteroid — darker/heavier grey
FLASH       = (255, 255, 255)  # #FFFFFF  hit flash (asteroid survives a hit / destroy frame)

# ── Enemy ───────────────────────────────────────────────────────────
ENEMY       = (255, 70, 200)   # #FF46C8  magenta enemy fighter
ENEMY_EDGE  = (255, 180, 235)  # #FFB4EB  enemy outline accent
BULLET_E    = (255, 90, 40)    # #FF5A28  orange-red enemy bullet

# ── HUD / health ────────────────────────────────────────────────────
HP_GREEN    = (60, 210, 90)    # #3CD25A  health >= 40
HP_AMBER    = (240, 190, 50)   # #F0BE32  health < 40
HP_RED      = (230, 60, 60)    # #E63C3C  health < 20
HP_BACK     = (40, 44, 58)     # #282C3A  empty portion of the health bar (track)
HP_BORDER   = (210, 215, 235)  # #D2D7EB  health-bar outline
TEXT        = (235, 240, 255)  # #EBF0FF  all HUD / screen text (same as STAR_NEAR)
TEXT_DIM    = (140, 148, 170)  # #8C94AA  secondary text (hints, "BEST", controls)
OVERLAY     = (10, 12, 22)      # GAME_OVER / PAUSE dim — blit at alpha ~160 over the frozen field
```

**Why these:** cyan player vs. magenta enemy are maximal-contrast complements (instant friend/foe
read); greys keep asteroids visually "neutral" so the colored actors pop; orange-red enemy bullets
are the one warm hazard color, easy to track against the cool blue field. Particles inherit their
source color (GDD §6.7), so no extra palette entries are needed.

---

## 2. Per-entity visuals (shape + size + color)

All triangles are given as vertex offsets from the entity **center** `(cx, cy)`; +y is **down**
(GDD §5). Pass the three points straight to `pygame.draw.polygon`.

| Element | Shape & draw call | Size (px) | Fill color | Outline / detail | State variations |
|---|---|---|---|---|---|
| **Background** | `screen.fill(BG)` each frame | 600×800 window | `BG` | — | static; actors drawn on top |
| **Starfield — Far** | `pygame.draw.rect` or `set_at` per star | 1×1 | `STAR_FAR` | none | 35 stars, scroll 1.0 px/f ↓ (GDD §6.6) |
| **Starfield — Mid** | small filled square | 2×2 | `STAR_MID` | none | 25 stars, scroll 2.0 px/f ↓ |
| **Starfield — Near** | small filled square | 3×3 | `STAR_NEAR` | none | 10 stars, scroll 3.5 px/f ↓ |
| **Player ship** | `pygame.draw.polygon(PLAYER, pts)` then 2px `polygon(..., width=2)` in `PLAYER_EDGE` | 28 w × 30 h (collision r=13) | `PLAYER` | `PLAYER_EDGE` outline; optional 3px `PLAYER_EDGE` dot at `(cx, cy)` as cockpit | **i-frames (R18):** blink — draw only on frames where `(iframe_timer // 6) % 2 == 0`; skip draw otherwise. 60-frame window. |
| **Player bullet** | `pygame.draw.rect` | 4 w × 12 h | `BULLET_P` | none (optional: top 2px brighter = same color) | travels up 10 px/f; despawn `y < -12` |
| **Asteroid — small** | `pygame.draw.circle` | r = 12 | `ASTEROID_S` | optional 1px `BG` ring for separation | 1 hit → destroy + 6 particles (`ASTEROID_S`) |
| **Asteroid — large** | `pygame.draw.circle` | r = 26 | `ASTEROID_L` | optional 2px `STAR_FAR` outline | **hit-survive flash (R17):** fill `FLASH` for ~5 frames after a non-lethal hit, then revert. Destroy → 6 particles (`ASTEROID_L`) |
| **Enemy fighter** | `pygame.draw.polygon(ENEMY, pts)` (downward chevron) + 2px `ENEMY_EDGE` outline | 26 w × 24 h (collision r=13) | `ENEMY` | `ENEMY_EDGE` outline | flash `FLASH` 1 frame on taking a bullet hit (optional, matches asteroid feel) |
| **Enemy bullet** | `pygame.draw.circle` | r = 5 | `BULLET_E` | none | aimed vector 4.5 px/f, no homing |
| **Particle (debris)** | `pygame.draw.rect` | 2×2 | source object's color | none | 6 per death, 20-frame life; see §5 for fade |

### 2.1 Triangle / chevron vertex math (paste-ready)

```python
# Player ship — upward-pointing triangle, 28 wide × 30 tall, center (cx, cy)
player_pts = [(cx,      cy - 15),   # nose (top)
              (cx - 14, cy + 15),   # rear-left
              (cx + 14, cy + 15)]   # rear-right

# Enemy fighter — downward-pointing chevron, 26 wide × 24 tall, center (cx, cy)
# 4-point chevron reads as a hostile arrowhead; falls back to a plain triangle if preferred.
enemy_pts  = [(cx,      cy + 12),   # bottom point (aimed at player)
              (cx + 13, cy - 12),   # top-right wing
              (cx,      cy - 5),    # center notch (the chevron "V"); drop this point for a plain triangle
              (cx - 13, cy - 12)]   # top-left wing
```

---

## 3. Background & starfield

- **Clear:** `screen.fill(BG)` first, every frame, in every state (START / PLAY / GAME_OVER / PAUSED).
- **Three parallax layers** drawn back-to-front: Far → Mid → Near (so bright near-stars sit on top).
  Counts/speeds/sizes/colors are in the §2 table and match GDD §6.6 exactly (70 stars total).
- Stars are pure rectangles/points — cheapest possible. **No twinkle required**; an optional cheap
  polish is in §6.
- Wrap behavior (GDD §6.6) is gameplay logic, not art: when `y > 800`, respawn at `y = 0`, new random x.

---

## 4. HUD & on-screen text

### 4.1 Font
- **One font only:** `pygame.font.SysFont(None, SIZE)` (built-in default — no asset files, satisfies C2).
- Sizes:
  - `FONT_HUD  = SysFont(None, 28)` — score, health label.
  - `FONT_BIG  = SysFont(None, 64)` — "STARSHARD" title, "GAME OVER".
  - `FONT_MID  = SysFont(None, 32)` — "SCORE n" / "BEST n" on Game Over.
  - `FONT_SMALL= SysFont(None, 22)` — control hints, "Press any key", restart/quit line.
- **All text color = `TEXT`**; secondary/hint lines use `TEXT_DIM`.

### 4.2 Score (R11) — PLAY + GAME_OVER
- `FONT_HUD`, color `TEXT`, top-left at **`(12, 10)`**, zero-padded to 5 digits: `f"SCORE {score:05d}"`.

### 4.3 Health bar (R10) — the green/amber/red thresholds
Outlined bar, **120 × 14 px**, top-left of the bar at **`(468, 12)`** (GDD §9).

```python
HP_BAR_RECT   = pygame.Rect(468, 12, 120, 14)
# 1) track (empty background)
pygame.draw.rect(screen, HP_BACK, HP_BAR_RECT)
# 2) fill, proportional to health, inset 2px so the border frames it
inner_w = int((HP_BAR_RECT.width - 4) * max(0, health) / 100)
fill = pygame.Rect(HP_BAR_RECT.x + 2, HP_BAR_RECT.y + 2, inner_w, HP_BAR_RECT.height - 4)
if   health < 20: color = HP_RED        # GDD §9: red  < 20
elif health < 40: color = HP_AMBER      # GDD §9: amber < 40
else:             color = HP_GREEN      # green >= 40
pygame.draw.rect(screen, color, fill)
# 3) border on top
pygame.draw.rect(screen, HP_BORDER, HP_BAR_RECT, width=2)
```
- Thresholds (single source of truth, from GDD §9): **`>= 40` green · `< 40` amber · `< 20` red**.
  Evaluate `< 20` **before** `< 40` (order matters; code above is correct).
- Optional label: `FONT_SMALL`, `TEXT`, `f"HP {health}/100"` right-aligned just left of the bar at
  about `(456, 14)` (anchor its right edge to x=460). Cut first if cramped.

### 4.4 Start screen (R16)
Center column on the scrolling starfield (no solid panel needed):
- Title "STARSHARD" — `FONT_BIG`, `PLAYER` color (cyan, branded), centered at y ≈ 250.
- Pitch line — `FONT_SMALL`, `TEXT`, centered y ≈ 320 (Writer supplies the exact words).
- Controls — `FONT_SMALL`, `TEXT_DIM`, centered y ≈ 470 & 500 (Writer copy).
- "Press any key to fly" — `FONT_SMALL`, `TEXT`, centered y ≈ 560 (Writer copy). Optional blink:
  show on `(frame // 30) % 2 == 0`.

### 4.5 Game Over (R12)
- Dim the frozen field: blit a full-screen `OVERLAY` surface at **alpha 160**
  (`s = pygame.Surface((600,800)); s.set_alpha(160); s.fill(OVERLAY); screen.blit(s,(0,0))`).
- "GAME OVER" — `FONT_BIG`, `HP_RED`, centered y ≈ 300.
- "SCORE n" — `FONT_MID`, `TEXT`, centered y ≈ 380.
- "BEST n" (R19, optional) — `FONT_MID`, `TEXT_DIM`, centered y ≈ 420.
- "R restart  ·  Esc quit" — `FONT_SMALL`, `TEXT_DIM`, centered y ≈ 480.

### 4.6 Paused (R22, optional)
- Same `OVERLAY` dim at alpha 120 + "PAUSED" `FONT_BIG`, `TEXT`, centered.

---

## 5. Particles & hit feedback (R17)

- **Death burst (GDD §6.7):** on any asteroid/enemy destroy, spawn **6** `2×2` rects at the death
  point, random velocity `[-3, 3]` px/f per axis, **20-frame** life. Color = **the destroyed object's
  fill color** (`ASTEROID_S` / `ASTEROID_L` / `ENEMY`). Cap ~60, oldest expires first.
- **Fade/shrink (cheap):** drawing a fading 2×2 is simplest by **shrinking** — draw `1×1` once
  `life < 10`, drop at `life <= 0`. (True alpha-fade needs a per-particle Surface; not worth it at
  2px — shrink is the recommended cheap version. Programmer may skip even the shrink.)
- **Large-asteroid hit flash:** see §2 table — fill `FLASH` for ~5 frames on a survived hit.
- **Player i-frame blink:** see §2 table — skip the player draw on alternate 6-frame intervals.

---

## 6. Optional polish (juice) — draw-call-only, all cuttable

In rough priority order; each is a few lines and uses only `pygame.draw.*`:
1. **Engine flame:** a tiny `BULLET_E`/amber 3-wide triangle flickering behind the player nose-down
   (2 frames on / 2 off). Sells "thrust" for ~3 lines.
2. **Player bullet trail:** draw the bullet rect plus a 1px dimmer (`PLAYER`) rect just below it.
3. **Muzzle flash:** 1-frame `PLAYER_EDGE` 6px circle at the nose when a shot fires.
4. **Near-star streak:** draw near-layer stars as 3px-tall vertical lines instead of squares to imply
   speed (already within the §2 size budget).
5. **Game-over field tint:** already covered by the §4.5 overlay.

If the line budget (C3, ≤~500) gets tight, drop polish first, then particles, then the HP text label —
in that order. None of these affect collisions or the GDD numbers.

---

## 7. Render order (so layering reads correctly)

Back-to-front each frame:
1. `screen.fill(BG)`
2. Starfield Far → Mid → Near
3. Asteroids (large then small) and enemy bullets
4. Player bullets
5. Enemies
6. Player ship (respecting i-frame blink)
7. Particles
8. HUD (score, health bar) — always on top
9. State overlays (Start text / Game Over dim+text / Pause) last

---

## 8. Definition-of-done check (self-audit)
Every Done-when element has hex + shape + size: background ✓, 3-layer starfield ✓, player ship ✓,
player bullets ✓, small & large asteroids + hit flash ✓, enemy fighter ✓, enemy bullets ✓, health-bar
green/amber/red with `<40`/`<20` thresholds ✓, particles ✓, HUD/screen text color & font ✓. All numbers
trace to GDD §7.3/§9; shapes-only & keyboard-only scope respected. A programmer can render every
on-screen element from this file without choosing any color, size, or shape.

— end of art_spec (v1) —

---
---

