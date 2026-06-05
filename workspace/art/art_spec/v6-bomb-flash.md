# v6 increment — Bomb pickup + bomb-count HUD readout + activation flash (placeholder visuals)

Owner: artist · Date: 2026-06-05 · Status: complete
Inputs: `workspace/design/gdd.md` v6 (§V6.2 HUD readout, §V6.3 flush, §V6.5 flash timing, §V6.6 bomb pickup,
§V6.11 constants), `workspace/requirements/requirements.md` v6 §20 Open-values (flash color/opacity, bomb-pickup
shape/glyph, HUD readout), `workspace/art/art_spec.md` v2 (§V2.1 diamond palette + §V2.3 pill-stack layout to
sit clear of) + v5 (§V5.2 enemy/bullet hues to avoid), `workspace/shared/handoffs.md` (entry 37).

> **Constraint reminder (C2) still holds:** every element below is drawn with `pygame.draw.*` and
> `pygame.font` only — **no image/sound files**. This section **appends** to v1/v2/v5; all prior palette
> entries, sizes, fonts, and the §V2.6 pill stack are unchanged. **One new color** is introduced (the bomb
> violet); the flash reuses near-white. **Designer locked the flash duration (18 f) + linear fade**; this spec
> sets only the **color + peak alpha** it left to the Artist (§V6.5). **Writer owns the literal glyph/label**
> (the letter `B` and any "BOMBS"/"+1 BOMB" wording below are the render targets unless Writer overrides);
> **Level-designer owns spawn scarcity.** The Programmer should not have to invent any color, size, or shape.

---

## V6.1 Bomb palette — one new color (paste as constants, extends §1 / §V2.1)

```python
# ── v6 bomb pickup + flash (GDD §V6.x) ───────────────────────────────────────
BONUS_BOMB   = (180, 100, 245)  # #B464F5  vivid electric VIOLET — the 6th pickup kind; distinct from the
                                #          5 v2 diamonds, the magenta enemy body, and every bullet hue.
FLASH_TINT   = (240, 248, 255)  # #F0F8FF  near-white, barely cool — the full-screen activation flash color.
                                #          NOT pure #FFFFFF FLASH (kept distinct from the asteroid hit-flash).
```

**Why violet for the bomb (the §V6.6 / R51 anti-clash check):** the five v2 diamonds already claim green
(Repair `#3CD25A`), orange (Fan `#FF8C28`), cyan (Rapid `#50DCFF`), pale-blue (Shield `#B4DCFF`), and gold
(Score `#FFD246`); the v5 bullets claim red `#FF5A28`, lime `#8CF03C`, and ice-cyan `#2DCDFF`; the enemy body
is pink-magenta `#FF46C8`. The one clean, unused hue band left on the wheel is **violet/purple (~268°)**, so
`#B464F5` is unmistakable against the whole cast:

| Compared to | Their hex | Why the bomb violet is distinct |
|---|---|---|
| Repair green | `#3CD25A` | different hue family entirely |
| Fan orange | `#FF8C28` | warm vs. cool-violet |
| Rapid cyan / player | `#50DCFF` | cyan (G+B high) vs. violet (R+B high, low G) |
| Shield pale-blue | `#B4DCFF` | Shield is *desaturated light blue* (G 220 / B 255); violet is *saturated* (G 100) and redder |
| Score gold | `#FFD246` | warm yellow vs. cool violet |
| Enemy magenta | `#FF46C8` | magenta is **R-dominant pink** (R 255 > B 200); violet is **B-dominant** (B 245 > R 180) |
| Red / lime / ice-cyan bullets | `#FF5A28`/`#8CF03C`/`#2DCDFF` | no violet overlap with any |

`#B464F5` (luminance ≈ 140) is bright enough that the dark `BONUS_INK` (`#0A0C16`) glyph still pops, matching
how the other five diamonds carry a dark-on-bright letter.

Registry — append the 6th entry to the V2.1 `BONUS_STYLE` map (letter is Writer-overridable, color is final):

```python
BONUS_STYLE = {
    "REPAIR": ("+", BONUS_REPAIR),
    "FAN":    ("F", BONUS_FAN),
    "RAPID":  ("R", BONUS_RAPID),
    "SHIELD": ("S", BONUS_SHIELD),
    "SCORE":  ("2", BONUS_SCORE),
    "BOMB":   ("B", BONUS_BOMB),   # v6 — Writer names it; "B" is the suggested glyph (GDD §V6.6)
}
```

---

## V6.2 Bomb pickup — the violet diamond (R51, GDD §V6.6)

The bomb pickup is the **6th kind in the v2 diamond framework** — it reuses the **exact V2.2 diamond geometry**
(26 px point-to-point, half-diagonal 13, 1 px `FLASH` outline, centered glyph, collision circle r=13, 2.0 px/f
downward drift). **Only the fill color and the glyph change.** No new shape, no new draw path.

```python
# Identical to V2.2 — fill = BONUS_BOMB (#B464F5), glyph = "B".
diamond_pts = [(cx, cy - 13), (cx + 13, cy), (cx, cy + 13), (cx - 13, cy)]
pygame.draw.polygon(screen, BONUS_BOMB, diamond_pts)            # violet body
pygame.draw.polygon(screen, FLASH,      diamond_pts, width=1)   # 1px white outline (universal, as v2)
glyph = FONT_PICKUP.render(BONUS_STYLE["BOMB"][0], True, BONUS_INK)   # dark "B", centered
screen.blit(glyph, glyph.get_rect(center=(cx, cy)))
```

| Property | Value |
|---|---|
| Shape | diamond (4-pt polygon), 26 px point-to-point — **same as the 5 v2 pickups** |
| Fill | `BONUS_BOMB` `#B464F5` (the only per-kind difference) |
| Outline | 1 px `FLASH` (#FFFFFF) — universal, as v2 |
| Letter | `"B"` in `FONT_PICKUP` (22), color `BONUS_INK`, center-anchored on `(cx, cy)` |
| Collision / motion | circle r=13; 2.0 px/f straight down, no h-drift, not ramp-accelerated (GDD §V6.6 — physics owns) |

- **Optional bomb-glyph polish (cuttable):** if a literal bomb reads better than the letter, draw a small
  **bomb sphere** in the diamond instead of `"B"` — a `BONUS_INK` filled circle r=5 at center with a 2 px
  `BONUS_INK` fuse stub up-right. **Default is the letter `"B"`** (consistent with the other five diamonds and
  with whatever the Writer finalizes); the sphere is pure flavor and the first thing to drop.
- **Collect feedback:** identical to the v2 pickup pop (§V2.2) — 6 particles in the pickup's fill color
  (`BONUS_BOMB`) at the pickup center, or the 1-frame `FLASH` ring. Plus the optional collect popup in V6.4.

---

## V6.3 Bomb-count HUD readout (R45, GDD §V6.2) — top-right, under the HP bar

**Placement rationale (the §V6.2 "clear of the §V2.6 pill stack" requirement):** the buff-pill stack owns the
**top-left column** — `(12, 36)` down to `y≈104`, spanning x≈12–76, and it grows/shrinks as buffs come and go.
Stacking the bomb count there would make it **jump** as pills appear. Instead the bomb count lives **top-right,
directly under the HP bar**, right-aligned to the bar's right edge — pairing the two **survival-resource
gauges** (health + bombs) in one corner, away from the dynamic left column. The HP bar is the fixed 120×14 rect
at `(468, 12)` (ends at `y=26`, right edge `x=588`); the bomb readout sits just below it.

```python
BOMB_HUD_RIGHT = 588   # right edge — aligned with the HP bar's right edge (468 + 120)
BOMB_HUD_Y     = 34    # top of the readout row — 8 px below the HP bar (which ends at y=26)
BOMB_ICON_R    = 6     # radius of the small bomb-sphere icon
```

**Recommended look — one bomb-sphere icon + "× N" count (the "icons ×N" option), right-aligned:**

```python
# count text — Writer may prefer "×N" / "x N"; "BOMBS: N" fallback below.
empty   = (charges == 0)
col     = TEXT_DIM if empty else TEXT                      # dim the whole readout when out of bombs
count_s = FONT_HUD.render(f"x{charges}", True, col)        # FONT_HUD = SysFont(None, 28), already defined
tx = BOMB_HUD_RIGHT - count_s.get_width()                  # right-align the text to x=588
screen.blit(count_s, (tx, BOMB_HUD_Y))

# bomb-sphere icon, just left of the text, vertically centered on the ~14px glyph row
icx, icy = tx - 8 - BOMB_ICON_R, BOMB_HUD_Y + 11
if empty:                                                  # OUT OF BOMBS → hollow ring (reads "empty")
    pygame.draw.circle(screen, BONUS_BOMB, (icx, icy), BOMB_ICON_R, 2)
else:                                                      # have bombs → filled violet sphere
    pygame.draw.circle(screen, BONUS_BOMB, (icx, icy), BOMB_ICON_R)
    pygame.draw.circle(screen, BONUS_INK,  (icx, icy), BOMB_ICON_R, 1)        # thin dark rim
    pygame.draw.line(screen, TEXT,  (icx + 3, icy - 5), (icx + 6, icy - 9), 2)  # short fuse, up-right
    pygame.draw.circle(screen, FLASH, (icx + 6, icy - 9), 1)                   # spark at the fuse tip
```

| Element | Geometry | Color |
|---|---|---|
| Count text | `FONT_HUD` (28), **right edge anchored to x=588**, top y=34 | `TEXT` (have ≥1) / `TEXT_DIM` (at 0) |
| Bomb icon | filled circle r=6 + 1 px `BONUS_INK` rim + fuse, centered ~`(564, 45)` | `BONUS_BOMB` violet (ties to the pickup) |
| Icon at **0 charges** | r=6 violet **ring** (width 2), unfilled | `BONUS_BOMB` outline — reads "empty / can't bomb" |

- **Updates the same frame the count changes** (−1 on a bomb, +1 on a pickup, →2 on restart) — it just reads
  the live `charges` integer, so it is correct by construction (AC30/AC34/AC36).
- **The 0-charge "empty" state matters:** dimming the text to `TEXT_DIM` and hollowing the icon gives the
  player an at-a-glance "you're out" read, reinforcing why an X press does nothing (R47).
- **Why it never collides with the persistent HUD:** the only persistent furniture near this corner is the HP
  bar **above** it (`y` 12–26) — the readout starts at `y=34`. The pills are far left. The two transient
  popups that *can* briefly share the corner — the Repair **"+40"** (`(528,30)`, ≤30 f, drifts up *away*) and
  the bomb's own **"+1 BOMB"** (V6.4) — are short-lived and color-distinct (green / violet vs. the white count).

**Alternatives (equally blessed; Writer's wording decides):**
- **`BOMBS: N` text label** — same right-aligned anchor (`right=588, y=34`), `FONT_HUD`, `TEXT`/`TEXT_DIM`. Drop
  the icon. Simplest; clearest in words. Use this if the Writer prefers a spelled-out label.
- **Pip row** — draw `charges` small filled violet diamonds (or bomb-spheres) in a row, right-aligned to x=588,
  each ~12 px wide with a 4 px gap (cap 4 → ≤60 px wide). Most "game-y" (count = number of icons), no number to
  read. Empty slots shown as hollow violet outlines so the cap (4) is implied.

The **icon + "× N"** form is recommended: compact, scales trivially if the cap is ever retuned, and pairs an
unmistakable bomb glyph with the exact integer.

---

## V6.4 Optional "+1 BOMB" collect popup (GDD §V6.6) — mirrors Repair's "+40"

The bomb pickup is instant with **no buff-pill** (it is exempt from the §V2.3 pill HUD). To echo Repair's
feedback, an optional transient popup near the V6.3 readout confirms the gain. **Writer owns the text**
(placeholder `"+1 BOMB"`); cuttable (the readout ticking up already shows it).

| Property | Value |
|---|---|
| Text | Writer's string (placeholder `"+1 BOMB"`) |
| Font | `FONT_SMALL` (22) — smaller than Repair's so the longer string fits the corner |
| Color | `BONUS_BOMB` `#B464F5` — same violet as the pickup/readout |
| Anchor | **right edge x=588**, start `y=58` (just under the V6.3 readout row), drifts up 0.5 px/f |
| Lifetime | **30 f** (reuse `REPAIR_POPUP_LIFE`) |

```python
# while bomb_popup_timer > 0:
age  = REPAIR_POPUP_LIFE - bomb_popup_timer
surf = FONT_SMALL.render(bomb_pickup_text, True, BONUS_BOMB)   # text from Writer; placeholder "+1 BOMB"
screen.blit(surf, surf.get_rect(topright=(588, 58 - 0.5 * age)))
```

No new constant needed (reuses `REPAIR_POPUP_LIFE = 30`). If both the Repair "+40" and the bomb "+1 BOMB" ever
fire close together they sit on different rows (`y≈30` vs `y≈58`) and are different colors — no clash.

---

## V6.5 Activation flash (R50, GDD §V6.5) — Artist sets COLOR + PEAK ALPHA; Designer's 18-f linear fade CONFIRMED

The Designer **locked** the timing: a **full-screen overlay**, **`FLASH_FRAMES = 18` (0.30 s)**, **peak on the
activation frame, linear fade to 0** — `alpha(f) = peak · (1 − f/18)` for `f` in `[0, 18)`. **I confirm that
curve as-is** (a single linear fade from an instant peak — the instant peak *is* the snap, so a 2-stage ramp
adds nothing here) and set the two levers left to me:

| Lever (Artist-owned, §V6.5/§20) | **Value (LOCKED)** | Why |
|---|---|---|
| **Color** | `FLASH_TINT` = `#F0F8FF` (240, 248, 255) | **Near-white with a barely-there cool tint** — reads as an energy bloom in the cool space palette, and is **deliberately not pure `#FFFFFF`** so it never reads as the asteroid/enemy **hit-flash** (`FLASH = #FFFFFF`, §1) or the split-burst ring. Distinct from the cyan player-bullet (`#78FFF5`, a saturated mint) and the Shield ring (`#B4DCFF`, a saturated blue ring hugging the ship — a full-screen pale bloom won't be confused with a 36 px ring). |
| **Peak alpha** | `FLASH_PEAK_ALPHA` = `200` (≈ **78 %**) | Squarely in the Designer's ~190–205 / ~75–80 % intent — bright enough to read "everything got wiped," **NOT a full white-out (255)** so the player still sees the now-clear field *through* the flash and can react immediately. |
| **Fade curve** | `alpha(f) = 200 · (1 − f/18)`, linear | **Confirmed exactly as the Designer locked it.** Peak 200 on the activation frame → ~11 at frame 17 → gone at 18. Stays in lockstep with `BOMB_LOCKOUT = 18` (the screen fully settles before another bomb can fire — no strobe). |

```python
FLASH_PEAK_ALPHA = 200            # ~78% peak opacity (Designer intent 190–205); NOT 255 / white-out
FLASH_COLOR      = FLASH_TINT     # (240, 248, 255) #F0F8FF — overrides the GDD §V6.11 (255,255,255) default

# Build the overlay ONCE at init (constant color) — only set_alpha changes per frame (cheap, no per-frame alloc):
flash_surf = pygame.Surface((600, 800))
flash_surf.fill(FLASH_COLOR)

# Each frame the flash is active (flash_timer counts 18 -> 1), AFTER entities + HUD, BEFORE state overlays:
f = FLASH_FRAMES - flash_timer                              # f = 0 on the activation frame .. 17
flash_surf.set_alpha(int(FLASH_PEAK_ALPHA * (1 - f / FLASH_FRAMES)))   # 200 -> ~11, linear
screen.blit(flash_surf, (0, 0))
```

- **Shapes-only (C2):** one screen-covering `Surface` blit with per-frame alpha — no asset, one allocation total
  (built at init), one `set_alpha` + one `blit` per active frame.
- **Tied 1:1 to a successful activation (R50):** the flash is started only when a bomb actually fires
  (charges > 0, outside lockout); the 0-charge no-op (R47) and a lockout-blocked press draw **no** flash.

---

## V6.6 Updated render order (extends V2.6 for v6)

Back-to-front each frame; the bomb pickup slots into the existing pickup layer, and the **flash is a new top
layer drawn after the HUD but before the GAME_OVER/Pause overlays** (it is a PLAY-state effect):

1. `screen.fill(BG)`
2. Starfield Far → Mid → Near
3. Asteroids + all enemy bullets (RED dots / GREEN pellets / CYAN streaks)
4. Bonus pickups (5 v2 diamonds **+ the violet BOMB diamond**) — same layer
5. Player bullets
6. Enemies (HEAVY / REGULAR / SCOUT)
7. Player ship (+ shield ring if `shield>0`)
8. Particles (death / collect / optional split burst)
9. HUD: score, health bar, buff-pill stack, repair popup, **bomb-count readout (V6.3) + optional "+1 BOMB" popup (V6.4)**
10. **Activation flash (V6.5)** — full-screen `FLASH_TINT` overlay at per-frame alpha, while `flash_timer > 0`
11. State overlays (Start / Game Over dim+text / Pause) last

The flash sits **above** the HUD so a panic-bomb visibly pops over everything, but **below** the Game-Over dim
(they never co-occur — flash is PLAY-only). Per V6.5 the flush of entities happens in the systems step *before*
rendering; this is purely the draw of the resulting flash.

---

## V6.7 Definition-of-done check (v6 self-audit)
- **Bomb pickup:** violet `#B464F5` diamond, glyph `"B"`, reusing the exact v2 diamond geometry/collision/drift;
  **one new color**, distinct from all 5 v2 diamonds, the magenta enemy, every bullet hue, the cyan player, and
  the pale-blue Shield (V6.1 anti-clash table) ✓.
- **HUD bomb-count readout:** top-right under the HP bar (`right=588, y=34`), **clear of the §V2.6 left-column
  pill stack**; bomb-sphere icon + `× N` (with `BOMBS: N` / pip-row alternatives), distinct **empty (0)** state,
  updates the frame the count changes ✓.
- **Activation flash:** color `#F0F8FF` (near-white, not pure-white, not a white-out) + **peak alpha 200 (~78 %)**,
  with the Designer's **18-f linear fade `200·(1−f/18)` CONFIRMED** and in lockstep with `BOMB_LOCKOUT` ✓.
- **All `pygame.draw.*` + `pygame.font`, no external assets (C2)** ✓. New constants: `BONUS_BOMB`, `FLASH_TINT`,
  `FLASH_PEAK_ALPHA=200`, `FLASH_COLOR=FLASH_TINT`, `BOMB_HUD_RIGHT/Y`, `BOMB_ICON_R` (overrides the GDD §V6.11
  `FLASH_PEAK_ALPHA`/`FLASH_COLOR` placeholders; all other §V6.11 numbers unchanged). A programmer can render
  every v6 element from this file without choosing any color, size, or shape.

— end of art_spec (v6) —
