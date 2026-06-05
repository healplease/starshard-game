# v8 increment — Pause overlay (dim layer + text block + Q-hold arc)

Owner: artist · Date: 2026-06-05 · Status: complete
Inputs: `workspace/design/gdd/v8-pause.md` (§V8.4 arc spec, §V8.6 overlay structure,
§V8.6.2 distinguishability table), `workspace/requirements/requirements/v8.md` (R69–R75),
`workspace/art/art_spec/v1-base.md` (§1 palette, §4.1 fonts, §4.5 GAME_OVER layout),
`workspace/art/art_spec/v7-bosses.md` (V7.6 render order), `workspace/game/config.py`
(live palette + HUD geometry constants).

> **Constraint reminder (C2/AC52) still holds:** every element below uses `pygame.draw.*`
> and `pygame.font` only — **no external image/sound files**. This section **appends** to
> v1/v2/v5/v6/v7; **no palette entries are added** — every color below reuses an existing
> constant. The Programmer adds **one geometry block** to `config.py` (§V8.4 below) and
> one new function `draw_pause()` to `view/hud.py`; all other modules are unchanged from
> an art perspective.

---

## V8.1 No new palette entries

All colors needed for the PAUSE overlay are already defined. **Zero new `config.py` color
constants.** Cross-reference:

| Role in pause overlay | Reused constant | RGB | Hex |
|---|---|---|---|
| Full-screen dim fill | `OVERLAY` | `(10, 12, 22)` | `#0A0C16` |
| "PAUSED" heading | `PLAYER` | `(80, 220, 255)` | `#50DCFF` |
| Hint lines (3) | `TEXT_DIM` | `(140, 148, 170)` | `#8C94AA` |
| Q-hold arc **fill** | `HP_AMBER` | `(240, 190, 50)` | `#F0BE32` |
| Q-hold arc **track** | `HP_BACK` | `(40, 44, 58)` | `#282C3A` |

---

## V8.2 §V8.6.2 design-level decisions confirmed (three GDD asks)

### V8.2.1 Arc color — HP_AMBER confirmed ✓

`HP_AMBER = (240, 190, 50)` reads clearly against the frozen, dimmed scene:

- **Luminance:** HP_AMBER's perceived brightness (~73 on a 0–100 scale) is among the highest
  in the entire palette, exceeded only by `FLASH`, `TEXT`, `STAR_NEAR`. Against a background
  that, after the alpha=110 dim, is predominantly near-black `BG`-toned, the amber arc **pops
  like a hot indicator light**.
- **Hue isolation at screen center:** the arc lives at `(W//2=300, 483)`. The only other warm-
  yellow element in this zone during PAUSE is `EB_COLOR_YELLOW` enemy bullets and boss
  `BOSS_CORE` — but both are **frozen** (the game is paused). No live warm element competes.
- **Track contrast:** `HP_BACK = (40, 44, 58)` is a dim blue-grey that blends into the overlay
  background, letting the amber arc segment stand alone rather than fighting a bright second ring.
- **Palette anti-clash:** `HP_AMBER` is warm amber (`R240, G190, B50`). The other always-visible
  overlay elements are cool: dim layer `OVERLAY` (near-black), heading `PLAYER` (cyan), hints
  `TEXT_DIM` (cool grey). There is no amber element anywhere else in the pause overlay —
  the arc's color is unambiguous. ✓

### V8.2.2 Full-screen dim alpha=110 is visually distinct from GAME_OVER's alpha=160 ✓

| Property | PAUSE (this spec) | GAME_OVER (v1-base §4.5) |
|---|---|---|
| **Dim alpha** | **110 ≈ 43 % overlay** | **160 ≈ 63 % overlay** |
| Game world visible through dim | **~57 %** — entities and layout clearly legible | **~37 %** — dark, obscured, terminal feel |
| Stars during overlay | **Continue scrolling** (architecture: `update_starfield` is outside the PLAY guard) | **Frozen** (GAME_OVER is not PLAY) |
| Heading color | **PLAYER cyan** `#50DCFF` | **HP_RED** `#E63C3C` (warm/danger) |
| Unique structural element | **Q-hold arc** + 3 hint lines | **Score + Best** lines |

The 50-unit alpha gap (110 vs 160) is a **~20 % difference in overlay opacity** — clearly perceptible
in isolation and unmistakable in sequence (a player who has died many times knows exactly what
alpha=160 looks like). Additionally, the scrolling starfield during PAUSE and the frozen one during
GAME_OVER give an immediate kinetic cue before the player reads any text. **alpha=110 is confirmed
as visually distinct from alpha=160.** ✓

### V8.2.3 Heading color — PLAYER cyan confirmed ✓

`PLAYER = (80, 220, 255)` for the "PAUSED" heading is confirmed:

- **Vs GAME_OVER heading `HP_RED = (230, 60, 60)`:** opposite temperature (cool vs warm); the two
  are visually unmistakable even without reading the text.
- **Vs `ENEMY` magenta `(255, 70, 200)`:** PLAYER cyan is a completely different hue; no confusion
  with enemy-faction coloring.
- **Semantic read:** cyan is the player's own ship color — the pause screen is *your* moment, not a
  threat. Reinforces "temporary, player-chosen" vs GAME_OVER's red danger read. ✓

---

## V8.3 Exact pixel layout — pause overlay text block + arc

**All measurements are pixel-exact.** Font heights are the measured render heights of
`pygame.font.SysFont(None, size)` on the system fonts in this project: `FONT_BIG`
(size 64) ≈ **48 px** tall; `FONT_SMALL` (size 22) ≈ **18 px** tall. The Programmer
must verify with `font.get_height()` and adjust top-y constants by the delta if their
system fonts differ (the spacing constraints below remain the target).

### V8.3.1 Resolving `pause_panel_y` (GDD §V8.4 formula)

**Definition (Art-locked):** `pause_panel_y` is the **y-coordinate of the center of the
bottom-most hint text line** (the Restart hint, line 3 of 3). This is the code-ready
anchor — the Programmer stores one integer and derives everything below it from the
`+ 56` formula.

With the layout below: **`pause_panel_y = 427`**

Therefore: **`arc_center_y = pause_panel_y + 56 = 483`**

Cross-check against GDD §V8.6.1 ("arc center at `bottom_hint_y + 48`"):
`bottom_hint_y = hint3_bottom = 436` → `436 + 48 = 484` vs `483` — **1 px rounding**
(hint half-height is 9 px; `56 − 9 = 47 ≈ 48`). The two formulas are consistent to
within rounding. The **binding formula is `arc_center_y = pause_panel_y + 56`** (GDD §V8.4).

### V8.3.2 Text block — y coordinates (all surfaces are horizontally centered at `x = W//2 = 300`)

| # | Element | Font | `y` (top of blit) | Center y | Bottom y | Color |
|---|---|---|---|---|---|---|
| 1 | **PAUSED** heading | `FONT_BIG` (64 → 48 px) | **290** | 314 | 338 | `PLAYER` cyan |
| 2 | Resume hint | `FONT_SMALL` (22 → 18 px) | **358** | 367 | 376 | `TEXT_DIM` |
| 3 | Q-hold quit hint | `FONT_SMALL` | **388** | 397 | 406 | `TEXT_DIM` |
| 4 | Restart hint | `FONT_SMALL` | **418** | **427 = `pause_panel_y`** | 436 | `TEXT_DIM` |
| 5 | Q-hold arc center | r=22 — | **483 = `pause_panel_y + 56`** | — | 505 | `HP_AMBER` fill |

**Vertical gaps (spacing rationale):**

| Gap | From → To | Pixels | Why |
|---|---|---|---|
| Heading → Resume hint | bottom 338 → top 358 | **20 px** | Generous breathing room under the large heading; matches GAME_OVER's heading-to-score gap in proportion |
| Hint 1 → Hint 2 | bottom 376 → top 388 | **12 px** | Tight but legible — the three hints form a visually grouped list |
| Hint 2 → Hint 3 | bottom 406 → top 418 | **12 px** | Uniform with the hint-1→hint-2 gap |
| Hint 3 bottom → Arc center | 436 → 483 | **47 px** | Comfortably below the last hint; the arc is isolated from the text block, reads as a distinct UI element |

**Full content block:** y = 290 (heading top) to y = 505 (arc bottom including radius).
**Block center ≈ y 397** — essentially screen-center (H/2 = 400). ✓

### V8.3.3 Config constants — paste into `config.py` (Programmer section §V8.9)

```python
# ── v8 pause overlay geometry (art_spec §V8.3, GDD §V8.3/§V8.4/§V8.6) ─────────
# pause_panel_y: y-center of the bottom hint line; used as the arc anchor.
#   arc_center_y = PAUSE_PANEL_Y + 56  (GDD §V8.4 formula, locked by art)
#   Arc bounding rect = (W//2 - PAUSE_ARC_R,  PAUSE_PANEL_Y + 56 - PAUSE_ARC_R,
#                        2*PAUSE_ARC_R,        2*PAUSE_ARC_R)
PAUSE_DIM_ALPHA  = 110          # full-screen dim opacity (< GAME_OVER 160 = temporary-state read)
PAUSE_HEADING_Y  = 290          # top of "PAUSED" heading blit (FONT_BIG 48 px → center y 314)
PAUSE_HINT_Y1    = 358          # top of resume hint blit     (FONT_SMALL 18 px → center y 367)
PAUSE_HINT_Y2    = 388          # top of Q-hold hint blit     (FONT_SMALL 18 px → center y 397)
PAUSE_HINT_Y3    = 418          # top of restart hint blit    (FONT_SMALL 18 px → center y 427)
PAUSE_PANEL_Y    = 427          # pause_panel_y anchor (= center of hint3 = PAUSE_HINT_Y3 + 9)
PAUSE_ARC_R      = 22           # Q-hold arc radius in px (GDD §V8.4)
PAUSE_ARC_STROKE = 3            # Q-hold arc stroke width (GDD §V8.4, use pygame.draw.arc width=3)
# Q-hold arc center: (W//2, PAUSE_PANEL_Y + 56)  =  (300, 483)
# Q-hold quit frames: see PAUSE_QUIT_FRAMES = 30 (GDD §V8.3, add alongside this block)
```

---

## V8.4 Draw recipe — `draw_pause(screen, q_hold_frames)` (paste-ready)

```python
import math

def draw_pause(screen, q_hold_frames):
    """PAUSE overlay: full-screen dim + centered text block + Q-hold arc.
    q_hold_frames: int 0..PAUSE_QUIT_FRAMES — drives the arc fill ratio.
    (art_spec §V8.3, GDD §V8.4/§V8.6)
    """
    # ── 1. Full-screen dim (lighter than GAME_OVER's alpha=160) ──────────────
    dim = pygame.Surface((C.W, C.H))
    dim.set_alpha(C.PAUSE_DIM_ALPHA)   # 110 = temporary-state; game world still legible
    dim.fill(C.OVERLAY)
    screen.blit(dim, (0, 0))

    cx = C.W // 2   # 300 — all text and arc are horizontally centred here

    # ── 2. "PAUSED" heading — PLAYER cyan (≠ GAME_OVER's HP_RED) ─────────────
    heading = _FONTS["big"].render(C.PAUSE_TITLE, True, C.PLAYER)
    screen.blit(heading, heading.get_rect(midtop=(cx, C.PAUSE_HEADING_Y)))

    # ── 3. Hint lines — TEXT_DIM, FONT_SMALL ─────────────────────────────────
    for y, key in ((C.PAUSE_HINT_Y1, C.PAUSE_HINT_RESUME),
                   (C.PAUSE_HINT_Y2, C.PAUSE_HINT_QUIT),
                   (C.PAUSE_HINT_Y3, C.PAUSE_HINT_RESTART)):
        surf = _FONTS["small"].render(key, True, C.TEXT_DIM)
        screen.blit(surf, surf.get_rect(midtop=(cx, y)))

    # ── 4. Q-hold progress arc ────────────────────────────────────────────────
    arc_cy = C.PAUSE_PANEL_Y + 56       # 483 (resolves GDD §V8.4 formula)
    r      = C.PAUSE_ARC_R              # 22
    rect   = pygame.Rect(cx - r, arc_cy - r, 2 * r, 2 * r)   # (278, 461, 44, 44)

    # Track (empty ring) — always drawn so the player sees the full circle to fill
    pygame.draw.arc(screen, C.HP_BACK,
                    rect,
                    0, 2 * math.pi,     # full circle
                    C.PAUSE_ARC_STROKE)

    # Fill arc — clockwise from 12 o'clock (−π/2 base), sweep = fill × 2π
    fill = q_hold_frames / C.PAUSE_QUIT_FRAMES   # 0.0 → 1.0
    if fill > 0:
        # pygame.draw.arc draws CCW from start_angle to end_angle.
        # To draw CW from 12 o'clock: fix end=π/2, start=π/2 − fill×2π.
        end_a   = math.pi / 2
        start_a = end_a - fill * 2 * math.pi
        pygame.draw.arc(screen, C.HP_AMBER,
                        rect,
                        start_a, end_a,
                        C.PAUSE_ARC_STROKE)
```

> **Note on `midtop`:** using `get_rect(midtop=(cx, y))` horizontally centres the text at
> `cx=300` and places its top edge at `y`. This replaces the `_center(screen, surf, y)` helper
> (which left-calculates the x but also uses the top-y) — the result is identical for the y
> axis but properly centres variable-width hint strings.
>
> **Strings** `C.PAUSE_TITLE`, `C.PAUSE_HINT_RESUME`, `C.PAUSE_HINT_QUIT`,
> `C.PAUSE_HINT_RESTART` are owned by the **Writer** (§32 delegated). The Programmer stubs
> them as placeholder literals (e.g. `"PAUSED"`, `"ESC  Resume"`) until the Writer's handoff.

---

## V8.5 Anti-collision check — arc and text block vs all existing HUD elements

The pause overlay's content block occupies:
- Text: x ≈ [~180, ~420] (widest element is the heading; actual width depends on
  font/string — a "PAUSED" heading at FONT_BIG ≈ 180 px wide, centered at x=300 → [~210,~390])
- Arc: x = [278, 322], y = [461, 505]

| Existing HUD element | Its box | Overlap? |
|---|---|---|
| Score text | x[12,132] y[10,28] | **None** — top-left corner, far from centre content |
| Player HP bar | x[468,588] y[12,26] | **None** — right edge; arc x ends at 322 ≪ 468 |
| Bomb readout | x≈[528,588] y[34,51] | **None** — right edge; x ends 322 ≪ 528 |
| Buff-pill stack | x[12,76] y[36,104] | **None** — left edge; text starts ~210 ≫ 76 |
| Boss health bar | x[140,460] y[52,68] | **None** — y starts 52, content starts at y=290 |
| Boss label | x≈[225,375] y[30,50] | **None** — y ends 50, content starts at y=290 |

**No HUD collision.** ✓ All edge HUD elements (score/HP/bomb/pills) are in the screen corners;
the boss bar is in the top-center band (y=30–68); the pause overlay content starts at y=290.

---

## V8.6 Updated render order (extends V7.6 — no layer added, PAUSE populates existing slot 11)

The PAUSE state slots into the pre-existing "State overlays" layer (layer 11 in V7.6). The
full sequence is unchanged; the PAUSE draw is dispatched only when `state is GameState.PAUSE`.
Back-to-front (authoritative; supersedes V7.6):

1. `screen.fill(BG)`
2. Starfield Far → Mid → Near *(continues scrolling during PAUSE — architecture default)*
3. Asteroids + all enemy bullets (RED / GREEN / CYAN / YELLOW fan + 12-RED ring children)
4. Bonus pickups (5 v2 diamonds + violet BOMB diamond)
5. Player bullets
6. Enemies (HEAVY / REGULAR / SCOUT) + the MOTHERSHIP
7. Player ship (+ shield ring if `shield > 0`)
8. Particles *(frozen during PAUSE — inside `update_play()`, not called)*
9. HUD: score, player HP bar, buff-pill stack, repair popup, bomb-count readout + popup,
   boss health bar + label (while boss active)
10. Activation flash (v6/v7 `FLASH_TINT` overlay, 18-frame fade)
11. **State overlays last:**
    - `START` → `draw_start()`
    - `PLAY` → *(no overlay)*
    - **`PAUSE` → `draw_pause(screen, q_hold_frames)`** ← new dispatch here
    - `GAME_OVER` → `draw_gameover()`

> Note: in `PAUSE`, the HUD layer (9) still draws because the loop renders it every frame
> regardless of state. This is intentional — the player's HP bar, buff timers, and bomb count
> remain visible beneath the dim, reinforcing "you are mid-run, nothing was lost." The GDD
> imposes no hide-HUD requirement; this matches the `draw_gameover` treatment (which also draws
> the HUD beneath the dim in the existing code).

---

## V8.7 Definition-of-done check (v8 self-audit)

- **No new palette entries:** every color (`OVERLAY`, `PLAYER`, `TEXT_DIM`, `HP_AMBER`,
  `HP_BACK`) was defined in v1-base §1. Zero new `config.py` color lines. ✓
- **pause_panel_y resolved:** `pause_panel_y = 427` (center of bottom hint line). Formula
  `arc_center_y = pause_panel_y + 56 = 483`. Cross-check: `bottom_hint_y + 48 = 436 + 48 = 484`
  — agrees to 1 px rounding. Binding formula: `pause_panel_y + 56`. ✓
- **Exact pixel table (§V8.3.2):** heading top=290, hint1 top=358, hint2 top=388, hint3
  top=418, arc center y=483. Fonts FONT_BIG/FONT_SMALL. Gaps 20/12/12/47 px. ✓
- **Arc:** center `(300, 483)`, r=22, stroke=3, HP_AMBER fill / HP_BACK track, CW from
  12 o'clock; bounding rect `(278, 461, 44, 44)`. Draw recipe paste-ready (§V8.4). ✓
- **HP_AMBER arc reads clearly (§V8.2.1):** confirmed — high luminance warm amber against
  near-black dimmed field; no competing warm element at screen center during PAUSE; track
  HP_BACK recedes so arc segment pops. ✓
- **alpha=110 vs alpha=160 (§V8.2.2):** confirmed visually distinct (~43 % vs ~63 % overlay
  opacity, ~20 % difference; plus scrolling starfield + cyan vs red heading + arc vs score
  block as orthogonal disambiguators). ✓
- **Heading color PLAYER cyan (§V8.2.3):** confirmed — immediately distinguishable from
  GAME_OVER's HP_RED (cool vs warm) and from ENEMY magenta (different hue). ✓
- **Anti-collision (§V8.5):** arc + text block clear of all existing HUD elements on at
  least one axis. ✓
- **Render order (§V8.6):** no new layer; PAUSE slots into the existing state-overlay
  dispatch at layer 11. ✓
- **All `pygame.draw.*` + `pygame.font` only; no external assets (C2/AC52).** ✓
- **Zero TBD items remaining.** ✓

— end of art_spec (v8) —
