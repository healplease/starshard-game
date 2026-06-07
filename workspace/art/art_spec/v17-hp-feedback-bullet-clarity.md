# v17 increment — HP-bar gradient + low-HP red vignette + non-green HEAVY pellet (placeholder visuals)

Owner: artist · Date: 2026-06-07 · Status: complete
Inputs: `workspace/shared/brief.md` (v17 locked decisions), `v1-base.md` (§1 palette, §4.3 HP bar),
`v5-enemy-bullets.md` (§V5.2 GREEN pellet), `v6-bomb-flash.md` (§V6.5 flash — kept distinct),
`v11.md` (§V11.5 SRCALPHA `set_alpha` gotcha — reused below), `v16-second-boss.md` (NOVA blue cast).

> **Render-only polish (C2 holds):** all `pygame.draw.*` + `pygame.font`, no assets. **No new mechanic,
> economy, copy, collision, or size.** This increment **supersedes** two shipped sections — `v1-base.md`
> §4.3 (HP-bar stepped thresholds) and `v5-enemy-bullets.md` §V5.2 GREEN hue — and **adds** one effect
> (low-HP vignette). **Zero genuinely new colors:** the gradient + vignette reuse `HP_GREEN/HP_AMBER/HP_RED`;
> the pellet swaps one hex. Hex + formulas are the contract.

---

## V17.1 HP bar = continuous green→amber→red gradient (supersedes `v1-base.md` §4.3)

The stepped `≥40 green / <40 amber / <20 red` selector is **retired**. The fill color is now a
**continuous 2-segment linear interpolation in RGB through the three existing palette anchors** — so the
bar fades smoothly green→amber→red as HP drops and **reuses the exact v1 colors** (no new palette).

**Why piecewise (not a single green→red lerp):** a naïve `HP_GREEN→HP_RED` lerp passes through a muddy
olive/brown at the middle. Anchoring `HP_AMBER` at the midpoint forces the gradient through a clean amber,
preserving the old "green=safe / amber=warning / red=critical" read as a smooth ramp instead of 3 steps.

```python
HP_GRAD_PIVOT = 50          # HP where the bar is pure HP_AMBER (the green↔red midpoint anchor)

def _lerp(c1, c2, t):       # t 0→1 returns c1→c2, rounded int RGB
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))

def hp_bar_color(health):
    h = max(0, min(100, health))
    if h >= HP_GRAD_PIVOT:                       # 100→50 : green → amber
        t = (h - HP_GRAD_PIVOT) / (100 - HP_GRAD_PIVOT)
        return _lerp(HP_AMBER, HP_GREEN, t)      # t=1 → green, t=0 → amber
    t = h / HP_GRAD_PIVOT                         # 50→0  : amber → red
    return _lerp(HP_RED, HP_AMBER, t)            # t=1 → amber, t=0 → red
```

**Anchors (health → color), linear between adjacent anchors:**

| HP | Color | Hex |
|---|---|---|
| 100 | `HP_GREEN` | `#3CD25A` (60,210,90) |
| 50 (`HP_GRAD_PIVOT`) | `HP_AMBER` | `#F0BE32` (240,190,50) |
| 0 | `HP_RED` | `#E63C3C` (230,60,60) |

- **Curve = linear** (no easing) in each segment — predictable and cheap. Segment 1: HP 100→50 green→amber;
  segment 2: HP 50→0 amber→red.
- **Amber's role:** retained as the **mid-anchor** of the gradient (not a threshold). The bar passes through
  amber at HP 50, reads ~80% amber at HP 40 and ~orange at HP 25, ~60% red at HP 20 — so the old danger zones
  survive as a continuous fade. The discrete `<40`/`<20` branches are gone.
- **Drop-in:** in `v1-base.md` §4.3, the `HP_BAR_RECT` / track / `inner_w` / border draws are **unchanged**;
  replace **only** the 3-line `if health < 20 … else …` color selector with `color = hp_bar_color(health)`.

---

## V17.2 Low-HP red vignette (NEW) — subtle danger glow at the screen edges, HP < 25

A gentle red **edge** vignette that breathes while `health < 25`. It tints **only the borders**, leaving the
center fully clear, so it reads "danger" without obscuring play. **Independent of the v6 bomb flash** (that is
a brief full-screen near-white bloom; this is a persistent, low-alpha, red, edge-only glow).

```python
VIGNETTE_TINT         = HP_RED   # (230,60,60) #E63C3C — REUSE the critical-HP red (ties to the bar's red end)
VIGNETTE_HP_TRIGGER   = 25       # show while health < 25 (= "HP < 25%"); fully off (not drawn) at health >= 25
VIGNETTE_MAX_ALPHA    = 110      # edge alpha at pulse PEAK  (~43%) — corners only; subtle
VIGNETTE_MIN_ALPHA    = 60       # edge alpha at pulse TROUGH (~24%) — an always-on glow floor while active
VIGNETTE_INNER_R      = 300      # px from center (300,400) kept fully CLEAR (protects the play area)
VIGNETTE_OUTER_R      = 500      # px from center = the corner distance (hypot(300,400)) → full edge alpha
VIGNETTE_FALLOFF_K    = 1.5      # ramp exponent: gentle just past the inner radius, stronger toward the edge
VIGNETTE_PULSE_PERIOD = 60       # frames per breathe cycle (~1.0 s @60fps) — a slow, calm pulse
```

**Falloff (the contract):** alpha is a function of distance `d` from screen center `(300, 400)`:
`alpha(d) = 0` for `d ≤ 300`; else `VIGNETTE_MAX_ALPHA · clamp01((d − 300)/200) ** 1.5`, capped at `VIGNETTE_MAX_ALPHA`.
→ center & most of the vertical play column are untouched; only the corners (d→500) reach full alpha; the
top/bottom mid-edges sit at ~half. This is the "frame", heaviest in the four corners.

**Build ONCE at init** (cheap concentric-circle bake — no per-pixel loop, no numpy):

```python
import math
_VCX, _VCY = 300, 400
vignette = pygame.Surface((600, 800), pygame.SRCALPHA)     # per-pixel alpha
for d in range(VIGNETTE_OUTER_R, VIGNETTE_INNER_R, -1):    # large→small; smaller circles overwrite the center
    f = (d - VIGNETTE_INNER_R) / (VIGNETTE_OUTER_R - VIGNETTE_INNER_R)
    a = int(VIGNETTE_MAX_ALPHA * (f ** VIGNETTE_FALLOFF_K))
    pygame.draw.circle(vignette, (*VIGNETTE_TINT, a), (_VCX, _VCY), d)
# result: alpha ≈ 0 inside r=300, ramping to VIGNETTE_MAX_ALPHA at the corners. Baked at PEAK alpha.
```

**Per frame (PLAY state only, while `health < 25`)** — pulse + draw. The baked surface has **per-pixel alpha**,
so `surface.set_alpha()` is unreliable on it (**the v11 §V11.5 SRCALPHA gotcha**). Modulate with
`BLEND_RGBA_MULT` instead:

```python
phase = (frame % VIGNETTE_PULSE_PERIOD) / VIGNETTE_PULSE_PERIOD
pulse = 0.5 - 0.5 * math.cos(2 * math.pi * phase)                       # smooth 0→1→0
edge_a = VIGNETTE_MIN_ALPHA + (VIGNETTE_MAX_ALPHA - VIGNETTE_MIN_ALPHA) * pulse   # 60↔110
mul = int(round(255 * edge_a / VIGNETTE_MAX_ALPHA))                     # scale baked PEAK down to current
frame_v = vignette.copy()                                               # reused scratch is fine
frame_v.fill((255, 255, 255, mul), special_flags=pygame.BLEND_RGBA_MULT)  # scale alpha only, RGB intact
screen.blit(frame_v, (0, 0))
```

- **Subtle by design:** center clear (alpha 0 within r=300); peak alpha **110/255 ≈ 43% at the extreme
  corners only**; a **slow ~1 s cosine breathe** between 60 and 110 (never strobes, never fully opaque).
  Satisfies "reads as danger without obscuring play."
- **Trigger:** binary on/off at `health < 25` (a render trigger, not a balance number); when `health ≥ 25`
  it is not drawn. No per-frame intensification (keeping it calm); fixed envelope while active.
- **Distinct from the v6 bomb flash:** flash = full-screen, near-white `#F0F8FF`, peak α200, 18-frame one-shot
  fade, covers the whole screen incl. center. Vignette = red `#E63C3C`, edge-only, α≤110, persistent slow
  pulse, center untouched. They may co-occur (a panic-bomb at low HP) and don't conflict — the flash sits
  above the HUD and reads over the vignette.

---

## V17.3 HEAVY pellet recolor — `#8CF03C` lime → `#D230DC` orchid-purple (supersedes `v5-enemy-bullets.md` §V5.2 GREEN)

The HEAVY enemy's pre-split pellet leaves the green family entirely. **Color only** — shape (circle), draw
radius (`PELLET_DRAW_R = 8`), white-hot core (`FLASH` 2px), and collision (`r = 5`, GDD-owned) are **unchanged**.

```python
# v5 §V5.2 EB_COLOR_GREEN is RETIRED. Rename the constant and reuse it everywhere the pellet was drawn:
EB_COLOR_PURPLE = (210, 48, 220)   # #D230DC  vivid ORCHID-PURPLE — HEAVY pellet (pre-split). Hue ~296°,
                                   #          the widest open gap on the wheel, clear of every actor (V17.3.1).
```

- **Constant rename:** `EB_COLOR_GREEN → EB_COLOR_PURPLE` (the symbol named a color it no longer is). Update
  every reference — the V5.3 GREEN pellet draw block and the optional V5.4 split-burst particles. The pellet's
  white core (`pygame.draw.circle(screen, FLASH, …, 2)`) and `PELLET_DRAW_R = 8` body stay exactly as in §V5.3;
  only the body fill hex changes. (Keeping the old `EB_COLOR_GREEN` symbol works but is misleading — rename.)
- **Why purple, not another color:** the wheel is crowded — red 0–14°, orange 28°, gold/yellow 44–55°,
  green 136° (the clash to fix), mint 174°, cyans 196–198°, pale-blue 211°, NOVA blues 219–230°, bomb violet
  268°, magenta 324°. The only non-green gap ≥50° wide is **268→324 (purple)**; ~296° sits ~28° from each
  neighbor — maximal separation. Purple also reads as "charged energy," apt for the round that bursts into red.

### V17.3.1 Anti-clash proof — `#D230DC` (210,48,220) vs EVERY listed entity

| Entity | Hex / form | Why the purple pellet is unmistakable |
|---|---|---|
| **RED split-children / enemy bullet** | `#FF5A28` (255,90,40), small red dot | hue 14° vs 296° (~78° apart) — opposite warm/cool. Bonus: purple **charge** visibly differs from the red **shards** it becomes (good telegraph). ✓ |
| **Magenta enemy body** | `#FF46C8` (255,70,200), large polygon | nearest neighbor (~28°), but enemy is **R-dominant hot-pink** (R255) vs the pellet's **balanced R210/B220 purple**; and a big body polygon vs a small r=8 glowing dot with a white core. ✓ |
| **Player ship (cyan)** | `#50DCFF` (80,220,255) | cyan (G,B high / R low) vs purple (R,B high / G low) — ~100° apart. ✓ |
| **Player bullet (mint)** | `#78FFF5` (120,255,245) | mint 174°, travels **up** as a rect; purple dot travels down. ✓ |
| **Scout CYAN bullet** | `#2DCDFF` (45,205,255) | hue 198° (~98° apart) + scout is a thin **streak**, not a fat dot. ✓ |
| **Repair / HP green** *(the fix)* | `#3CD25A` (60,210,90) | hue 136° vs 296° — ~160° apart, the maximal separation. The green-confusion is fully gone. ✓✓ |
| **Bonus Fan (orange)** | `#FF8C28` (255,140,40) | warm orange 28° vs cool purple. ✓ |
| **Bonus Rapid (cyan)** | `#50DCFF` | = player cyan, see above. ✓ |
| **Bonus Shield (pale-blue)** | `#B4DCFF` (180,220,255) | desaturated light blue 211°; pellet is saturated purple 296°. ✓ |
| **Bonus Score (gold)** | `#FFD246` (255,210,70) | warm gold 46° vs cool purple. ✓ |
| **Bomb pickup (violet)** | `#B464F5` (180,100,245) | nearest neighbor (~28°), but bomb is **B-dominant blue-violet** (B245≫R180) vs the pellet's **balanced R210/B220** (more magenta-purple); and the bomb is a slow-drifting **diamond pickup** with a dark "B" + white outline, not a fast dot with a white core. ✓ |
| **Boss yellow / Mothership hull** | `#FFEA00` / `#342C4A` | opposite/dark. Also: bosses **field-clear + spawn-freeze**, so HEAVY/pellets never co-occur with a boss. ✓ |
| **NOVA blue family** | `#3C5AFF`/`#5A96FF`/`#4A7CFF` (~219–230°) | ~66–77° apart; and (as above) never on screen with HEAVY. ✓ |
| Stars / asteroids / BG | greys, near-white, near-black | neutral/desaturated — no hue clash. ✓ |

**Verdict:** `#D230DC` is clear of every actor; its two nearest hues (bomb violet, magenta) are further
separated by hue-lean **and** shape/role, with the pellet's unique white-hot core sealing the read. ✓

---

## V17.4 Render order (extends `v6-bomb-flash.md` §V6.6)

One insertion: the vignette is a **PLAY-state, below-HUD** layer so it never dims the gauges and the bomb
flash still reads over it.

1–8 unchanged (BG → starfield → asteroids+enemy bullets → pickups → player bullets → enemies → player → particles)
8.5 **Low-HP red vignette (V17.2)** — PLAY only, while `health < 25`; below the HUD so score/HP bar stay crisp
9. HUD (score, **HP bar now gradient-filled, V17.1**, pills, popups, bomb readout)
10. Bomb activation flash (V6.5) — full-screen, above the HUD (a panic-bomb pops over the vignette)
11. State overlays (Start / Game Over / Pause)

---

## V17.5 Definition-of-done check (v17 self-audit)
- **HP gradient:** continuous green→amber→red, paste-ready `hp_bar_color()` + 3 anchors (HP 100/50/0),
  linear 2-segment, reuses v1 palette, drop-in for §4.3's color selector; supersedes the stepped thresholds ✓.
- **Vignette:** tint `#E63C3C`, trigger `health < 25`, edge-only radial falloff (clear r≤300 → α110 at r=500,
  k=1.5), slow cosine pulse 60↔110 over 60 f, build-once + per-frame `BLEND_RGBA_MULT` recipe (SRCALPHA gotcha
  handled), distinct from the v6 flash, render slot 8.5 ✓.
- **Pellet:** `#D230DC` (rename `EB_COLOR_GREEN→EB_COLOR_PURPLE`), color-only (shape/size/core/collision
  unchanged), anti-clash proof vs all 13 listed entity groups ✓.
- All `pygame.draw.*` + `pygame.font`, **no new palette colors, no assets** ✓. A programmer can render every
  v17 change without choosing any color, number, or shape.

— end of art_spec (v17) —
