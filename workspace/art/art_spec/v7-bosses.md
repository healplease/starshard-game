# v7 increment — Mothership silhouette + boss health-bar/label + yellow→red boss bullets (placeholder visuals)

Owner: artist · Date: 2026-06-05 · Status: complete
Inputs: `workspace/design/gdd/v7-bosses.md` (§V7.4 size r=70 / ~180×110 intent, §V7.7 entrance/rest/osc,
§V7.5 flash reuse, §V7.12 yellow fan / 12-red ring, §V7.18 Artist asks), `workspace/requirements/requirements/v7.md`
(§26 Artist rows — boss size/shape, health-bar visual, yellow/red bullet hues; AC47 HUD anti-collision, AC52
shapes-only), `workspace/art/art_spec/v1-base.md` (§1 palette, §4.3 HP bar geometry, §7 render order),
`v5-enemy-bullets.md` (§V5.2 RED/GREEN/CYAN hues, §V5.3 bullet draws), `v6-bomb-flash.md` (§V6.1 violet + flash,
§V6.3 bomb-readout placement), `workspace/shared/handoffs.md` (entry 47).

> **Constraint reminder (C2/AC52) still holds:** every element below is drawn with `pygame.draw.*` and
> `pygame.font` only — **no external image/sound files**. This section **appends** to v1/v2/v5/v6; all prior
> palette entries, sizes, fonts, the HP bar, the pill stack, and the bomb readout are unchanged. **The boss
> arrival flash introduces NOTHING new** — it reuses the v6 `FLASH_TINT` / `FLASH_PEAK_ALPHA` / 18-f linear
> fade **verbatim** (§V6.5); see §V7.5 below. New here: **the Mothership silhouette** (one dark hull color +
> magenta faction trim + a yellow weapon core), **the boss health-bar + label frame** (center-top, magenta —
> the enemy-faction read, placed clear of the HP bar / pills / bomb readout), and **one new bullet hue** (the
> attack-4 YELLOW); the 12 red children **reuse `EB_COLOR_RED`**. The Programmer should not have to invent any
> color, size, or shape.

---

## V7.1 New palette — Mothership hull + boss bar + the yellow fan (paste as constants, extends §1 / §V5.2)

```python
# ── v7 bosses: Mothership hull + boss HUD + attack-4 yellow fan (GDD §V7.x) ───────────────────
# The Mothership is the magenta fleet's CAPITAL SHIP: a huge DARK steel hull trimmed in the enemy
# magenta, with a YELLOW weapon core. Body color is its own dark hull; the FACTION read is magenta.
BOSS_HULL  = (52, 44, 74)     # #342C4A  dark indigo-violet steel — the massive hull. Stands off the BG
                              #          (#0A0C16), tinted violet so it's NOT a grey asteroid, far darker
                              #          than the bright bomb violet #B464F5. The biggest mass on screen.
BOSS_PLATE = (84, 72, 116)    # #544874  mid plate — panel lines / hull detail (lighter step of the hull)
BOSS_TRIM  = ENEMY            # #FF46C8  REUSE the enemy magenta as the hull edge + window-lights:
                              #          "this is the mothership of the magenta fighters." No new color.
BOSS_CORE  = (255, 234, 0)    # #FFEA00  the glowing reactor / weapon emitter at the boss center — the
                              #          SAME yellow as the fan (EB_COLOR_YELLOW) so attack-4's origin is
                              #          pre-read. (Defined once here; the bullet alias is below.)

# ── Attack-4 bullet hues (GDD §V7.12) ─────────────────────────────────────────────────────────
EB_COLOR_YELLOW = (255, 234, 0)   # #FFEA00  NEW — the 3-bullet yellow FAN (the telegraph). Pure lemon
                                  #          (B=0): distinct from gold Score #FFD246, amber Fan #FF8C28,
                                  #          lime pellet #8CF03C, ice scout #2DCDFF. Aliases BOSS_CORE.
# Red children REUSE the existing v5 split-child red — NO new color:
#   EB_COLOR_RED  = #FF5A28  (defined v5 §V5.2) — the 12 ring children are ordinary red enemy bullets.

# Boss health bar (GDD §V7.4 BOSS_HP 120; HUD R64) — center-top, magenta = enemy health
BOSS_BAR_FILL  = ENEMY        # #FF46C8  REUSE magenta — the boss's draining health (enemy-faction color,
                              #          never confused with the player's GREEN/amber/red HP bar).
BOSS_BAR_BACK  = HP_BACK      # #282C3A  REUSE the dark track (empty portion), as the player HP bar.
BOSS_BAR_EDGE  = ENEMY_EDGE   # #FFB4EB  REUSE the pink enemy-edge as the bar frame (ties to the boss).
```

**Only TWO genuinely new colors this increment:** `BOSS_HULL` `#342C4A` and `EB_COLOR_YELLOW` `#FFEA00`
(`BOSS_CORE` is the same yellow value; `BOSS_PLATE` is a lighter step of the hull). Everything else **reuses**
existing palette entries (`ENEMY`, `ENEMY_EDGE`, `HP_BACK`, `EB_COLOR_RED`, `FLASH`). This keeps the cast tight
and binds the Mothership to the magenta enemy faction it commands.

---

## V7.2 The MOTHERSHIP silhouette (R59/R64, GDD §V7.4/§V7.7, §26 Artist) — shapes only

**Read story:** the **biggest mass on screen by far** — a wide, blocky **capital warship** that hangs at the
vertical centre and rains fire downward. It is unmistakably *not* one of the v5 fighters: those are small
(≤36 px) magenta polygons; this is a **~180 px-wide dark hull** with stepped wings, an upper bridge tower, and
three downward weapon prongs, edged and lit in the enemy magenta.

| Property | Value | Why |
|---|---|---|
| **Painted silhouette** | **~180 px wide × ~152 px tall** (hull 180×106 + bridge +18 up + prongs +20 down) | "Biggest thing on screen, unmistakably a Mothership" (GDD §V7.7) |
| **Collision (GDD, fixed)** | circle **r = 70** at the boss centre | **Painted body ≥ the r=70 circle in every direction** — see the coverage check below; no "phantom" hits outside the paint |
| **Body fill** | `BOSS_HULL` `#342C4A` | dark steel hull; stands off the BG, distinct from grey asteroids + bright bomb violet |
| **Edge / trim** | **3 px** `BOSS_TRIM` (= `ENEMY` magenta) | thick hostile rim → the magenta faction read; thicker than any fighter (HEAVY 3 px on a 36 px body; this is 3 px on a 180 px body = far heavier mass) |
| **Panel detail** | `BOSS_PLATE` `#544874` lines | hull plating; pure flavor, cuttable |
| **Reactor core** | `BOSS_CORE` `#FFEA00` filled circle r≈12 + 2 px `FLASH` rim, at the centre | the weapon emitter — attack-4's yellow fan spawns here, so the core **pre-reads** the threat |
| **Window-lights** | small `BOSS_TRIM` magenta dots along the hull | "crewed warship" menace; cuttable |

### V7.2.1 Coverage check — painted body ⊇ the r=70 collision circle (the GDD §V7.7 "≥ circle" rule)

The r=70 circle reaches **±70 px** from centre in every direction. The painted silhouette reaches: **±90 px**
horizontally (hull wing tips), **−74 px** up (bridge top), **+78 px** down (centre prong tip). So **70 ≤ 74**
(top), **70 ≤ 78** (bottom), **70 ≤ 90** (sides) — the collision circle is **fully inside the paint**. A player
can never be "hit by air": wherever the r=70 circle overlaps the ship, there is drawn hull/bridge/prong. ✓

### V7.2.2 Vertex math (paste-ready) — center `(cx, cy)`, +y down

```python
# ── MOTHERSHIP — draw at the boss center (cx, cy). All offsets in px; +y is DOWN (GDD §5). ──
# 1) Main hull — wide blocky 8-gon, 180 wide (±90) × ~106 tall (top -48 .. belly +58).
hull = [
    (cx - 70, cy - 48),   # top-left shoulder
    (cx + 70, cy - 48),   # top-right shoulder
    (cx + 90, cy - 10),   # right wing tip  (widest, ±90)
    (cx + 60, cy + 40),   # right lower step
    (cx + 24, cy + 58),   # right belly
    (cx - 24, cy + 58),   # left belly
    (cx - 60, cy + 40),   # left lower step
    (cx - 90, cy - 10),   # left wing tip   (widest, ∓90)
]
# 2) Bridge tower — small trapezoid on top, reaches cy-74 (covers the circle's top).
bridge = [(cx - 28, cy - 48), (cx - 20, cy - 74), (cx + 20, cy - 74), (cx + 28, cy - 48)]
# 3) Three downward weapon prongs — the menacing "fangs"; centre one reaches cy+78 (covers bottom).
prong_L = [(cx - 50, cy + 50), (cx - 40, cy + 74), (cx - 30, cy + 50)]
prong_C = [(cx - 12, cy + 58), (cx,      cy + 78), (cx + 12, cy + 58)]
prong_R = [(cx + 30, cy + 50), (cx + 40, cy + 74), (cx + 50, cy + 50)]

# ── Draw order (back→front), all pygame.draw only ──
for poly in (bridge, prong_L, prong_C, prong_R):
    pygame.draw.polygon(screen, BOSS_HULL, poly)            # appendages first (so the hull overlaps their roots)
pygame.draw.polygon(screen, BOSS_HULL, hull)               # main hull body
# panel lines (BOSS_PLATE) — optional flavor, cuttable:
pygame.draw.line(screen, BOSS_PLATE, (cx - 70, cy - 10), (cx + 70, cy - 10), 2)   # belt
pygame.draw.line(screen, BOSS_PLATE, (cx,      cy - 48), (cx,      cy + 58), 2)   # spine
# magenta window-lights — optional, cuttable:
for wx in (-44, -22, 0, 22, 44):
    pygame.draw.circle(screen, BOSS_TRIM, (cx + wx, cy - 28), 3)
# trim outline (the faction read) — drawn over hull + appendages:
for poly in (hull, bridge, prong_L, prong_C, prong_R):
    pygame.draw.polygon(screen, BOSS_TRIM, poly, width=3)
# reactor / weapon core at the center (where the yellow fan spawns):
pygame.draw.circle(screen, BOSS_CORE, (int(cx), int(cy)), 12)
pygame.draw.circle(screen, FLASH,     (int(cx), int(cy)), 12, 2)
```

- **Hit feedback (cuttable):** on a player-bullet hit, briefly brighten the **core** rim (1 frame `FLASH`) or
  flash the trim — a subtle "it's taking damage" tick. The **boss health bar (V7.3) is the primary damage
  read**, so a per-hit body flash is pure juice and the first thing to drop. No size/collision change.
- **Distinctness audit (R59/§26 "distinct from v5 enemies"):** the v5 bodies are **magenta-filled, ≤36 px,
  pointed** (octagon/chevron/dart); the Mothership is **dark-hulled, ~180 px, blocky with a bright yellow
  core** — separated by **fill (dark vs magenta), size (5×), and silhouette (blocky capital ship vs small
  fighter)**. It also clears the cyan player (dark hull vs cyan, 180 vs 28 px), the pickups (no diamond), and
  the buff pills. ✓

---

## V7.3 Boss health bar + label (R64, AC47) — center-top, magenta, clear of all existing HUD

**Placement rationale (the AC47 anti-collision requirement).** The existing top HUD owns the **corners**: the
**score** top-left (`(12,10)`, ends ≈x132/y28), the **player HP bar** top-right (`(468,12,120,14)`, x[468,588]
y[12,26]) with the **bomb readout** just under it (right≈588, y34–51), and the **buff-pill stack** down the
**left edge** (x[12,76], y[36,104]). The **center-top band is empty.** The boss bar lives there — a wide
**center-top** bar that reads as the enemy's health, far from the player's right-corner survival gauges. It
appears on **ARRIVAL** and is **removed on DEFEAT** (drawn only while a boss is active).

```python
# Boss health bar — wide, center-top, drains right→left. Shown only while a boss is active.
BOSS_BAR_W      = 320
BOSS_BAR_H      = 16
BOSS_BAR_RECT   = pygame.Rect((600 - BOSS_BAR_W) // 2, 52, BOSS_BAR_W, BOSS_BAR_H)  # = (140, 52, 320, 16)
BOSS_LABEL_Y    = 30        # baseline-ish top of the "MOTHERSHIP" label, centered above the bar
BOSS_HP_MAX     = 120       # = GDD BOSS_HP; the bar fills boss_hp / BOSS_HP_MAX

# 1) track (empty)
pygame.draw.rect(screen, BOSS_BAR_BACK, BOSS_BAR_RECT)
# 2) fill, proportional to current boss HP, inset 2 px so the frame frames it; drains from the RIGHT
inner_w = int((BOSS_BAR_RECT.width - 4) * max(0, boss_hp) / BOSS_HP_MAX)
fill = pygame.Rect(BOSS_BAR_RECT.x + 2, BOSS_BAR_RECT.y + 2, inner_w, BOSS_BAR_RECT.height - 4)
pygame.draw.rect(screen, BOSS_BAR_FILL, fill)
# 3) frame on top
pygame.draw.rect(screen, BOSS_BAR_EDGE, BOSS_BAR_RECT, width=2)
# 4) label centered above the bar — Writer owns the literal text (placeholder "MOTHERSHIP")
label = FONT_HUD.render(boss_label_text, True, BOSS_BAR_FILL)   # FONT_HUD(28); magenta = enemy-faction read
screen.blit(label, label.get_rect(midbottom=(300, BOSS_BAR_RECT.y - 2)))   # sits just above the bar (y≈30..50)
```

| Element | Geometry | Color | Distinct from |
|---|---|---|---|
| **Track** | `(140, 52, 320, 16)` | `BOSS_BAR_BACK` (`#282C3A`) | — (just the empty channel) |
| **Fill** | inset 2 px, width ∝ `boss_hp/120`, drains right→left | `BOSS_BAR_FILL` = `ENEMY` magenta `#FF46C8` | **player HP bar** (green/amber/red) — different color **and** corner |
| **Frame** | 2 px around the track | `BOSS_BAR_EDGE` = `ENEMY_EDGE` `#FFB4EB` | player HP border `#D2D7EB` (pink vs blue-white) |
| **Label** | `FONT_HUD`, centered `midbottom=(300, 50)` | magenta `#FF46C8` | white HUD text — color-coded to the boss |

### V7.3.1 Anti-collision check (AC47) — boss bar/label vs every persistent HUD element

| Existing HUD element | Its box | Boss bar `x[140,460] y[52,68]` | Boss label `x≈[225,375] y[30,50]` |
|---|---|---|---|
| **Player HP bar** | x[468,588] y[12,26] | x ends 460 < 468 **and** y starts 52 > 26 → **clear both axes** | x<375<468 **and** y<50; no overlap |
| **Bomb readout** | x≈[540,588] y[34,51] | x ends 460 ≪ 540 → **clear** | x ends 375 ≪ 540 → **clear** |
| **Buff-pill stack** | x[12,76] y[36,104] | x starts 140 > 76 → **clear** | x starts 225 ≫ 76 → **clear** |
| **Score** | x[12,132] y[10,28] | y starts 52 > 28 → **clear** | x starts 225 > 132 → **clear** |
| **Repair "+40" / "+1 BOMB" popups** | right side, x≈[500,588] | x ends 460 < 500 → **clear** | x ends 375 ≪ 500 → **clear** |

Every persistent and transient HUD element is clear of both the bar and the label on at least one axis (most on
both). **AC47 satisfied.** The bar/label draw **only while a boss is active** (encounter ARRIVAL→DEFEAT), so the
center-top band is empty during normal play — no permanent furniture added there.

---

## V7.4 Attack-4 bullet hues — YELLOW fan + RED children (R68, GDD §V7.12)

The step-4 attack fires **3 YELLOW bullets** (the telegraph) that each split into **4 of an even 12-RED 360°
ring**. **Collision is the uniform `EB_R = 5`** for every one (GDD §V7.12) — the draws below are render-only.

### V7.4.1 The YELLOW fan — one new hue (`EB_COLOR_YELLOW` `#FFEA00`)

```python
# Yellow telegraph bullet — drawn a touch emphasized (r=6 body + 2px white core) so it reads as a
# "charged" round about to split, but COLLISION stays EB_R = 5 (GDD §V7.12). 3 of them (the fan).
pygame.draw.circle(screen, EB_COLOR_YELLOW, (int(x), int(y)), 6)     # lemon body
pygame.draw.circle(screen, FLASH,           (int(x), int(y)), 2)     # 2px white core = "about to burst"
```

**Why `#FFEA00` (the §26 / R68 anti-clash check) — the yellow must beat 4 nearby warm/green hues:**

| Compared to | Their hex | RGB | Why the fan yellow is distinct |
|---|---|---|---|
| Gold **Score** pickup | `#FFD246` | (255, 210, 70) | yellow is **purer/brighter** (G 234 vs 210, **B 0 vs 70**); also a fast downward **bullet** vs a slow **diamond pickup** carrying a "2" glyph — context separates |
| Amber **Fan** pickup | `#FF8C28` | (255, 140, 40) | Fan is clearly **orange** (G 140); yellow is high-G lemon (G 234) |
| Lime **HEAVY pellet** | `#8CF03C` | (140, 240, 60) | pellet is **yellow-green** (R 140); the fan is **R 255** → unmistakably yellow, not green |
| Ice **SCOUT** bullet | `#2DCDFF` | (45, 205, 255) | cold cyan vs warm yellow — opposite side of the wheel |
| Repair/HP green | `#3CD25A` | (60, 210, 90) | green vs yellow — different hue family |

`#FFEA00` (luminance ≈ 224) is bright against the cool dark field, and its **pure-lemon (B=0)** identity is the
one warm-yellow slot not yet claimed. It doubles as `BOSS_CORE`, so the player learns "the glowing yellow core
is what spits the yellow fan." ✓

### V7.4.2 The 12 RED children — REUSE `EB_COLOR_RED` (no new color)

```python
# Each of the 12 ring children is an ORDINARY red enemy bullet — identical draw to the v5 red /
# split children (v5 §V5.3): plain r=5 dot, EB_COLOR_RED #FF5A28. Terminal, never re-splits.
pygame.draw.circle(screen, EB_COLOR_RED, (int(x), int(y)), 5)
```

The children **look identical to v5 red bullets / split children** — exactly as the GDD requires (visual
identity = mechanical identity: ordinary red enemy bullets). No new color, no new shape. The yellow→red change
on split therefore reads as "the charged yellow round bursts into a normal red ring." Optional 1-frame white
ring at the split point (reuse the v5 §V5.4 burst) is cuttable polish.

---

## V7.5 Boss-arrival flash — REUSE the v6 flash verbatim (R57, GDD §V7.5)

**Nothing new to pick.** The boss-arrival field-clear shows the **identical v6 activation flash** — the
full-screen `FLASH_TINT` `#F0F8FF` overlay at `FLASH_PEAK_ALPHA = 200`, linear fade `200·(1−f/18)` over
`FLASH_FRAMES = 18` (v6 §V6.5). The encounter manager arms the same `flash_timer`; the render is byte-for-byte
the v6 path. The only difference is **who triggers it** (the system on boss arrival, not a player X press) —
purely game logic, **no art change**. So the boss arrival "reads like a bomb, but free" (GDD §V7.5) using the
existing overlay. (It may appear as a *second* flash distinct from any player bomb the same fight — same look,
both are the one `FLASH_TINT` overlay.)

---

## V7.6 Updated render order (extends V6.6 for v7)

The Mothership is a (big) enemy → it draws in the **enemy layer** (so the player ship and shield ring sit on
top of it on a ram). Its bullets are ordinary enemy bullets → the **enemy-bullet layer**. The boss bar + label
join the **HUD layer**. The arrival flash is the **existing v6 flash layer** (unchanged). Back-to-front:

1. `screen.fill(BG)`
2. Starfield Far → Mid → Near
3. Asteroids + all enemy bullets (RED dots / GREEN pellets / CYAN streaks **+ the YELLOW fan + the 12 RED ring children**)
4. Bonus pickups (5 v2 diamonds + violet BOMB diamond)
5. Player bullets
6. Enemies (HEAVY / REGULAR / SCOUT) **+ the MOTHERSHIP** (drawn in this layer; player ship draws over it next)
7. Player ship (+ shield ring if `shield>0`)
8. Particles (death / collect / optional split burst)
9. HUD: score, player health bar, buff-pill stack, repair popup, bomb-count readout + "+1 BOMB" popup, **+ the boss health bar + "MOTHERSHIP" label (V7.3), while a boss is active**
10. Activation flash (V6.5) — full-screen `FLASH_TINT` overlay, **also armed by the boss arrival (V7.5)**
11. State overlays (Start / Game Over dim+text / Pause) last

No structural change — the boss and its bullets slot into existing layers; the only new HUD furniture (the boss
bar + label) is **transient** (active-boss only) and sits in the empty center-top band.

---

## V7.7 Definition-of-done check (v7 self-audit)
- **Mothership silhouette:** ~180×152 painted, dark `BOSS_HULL` `#342C4A` hull + 3 px `ENEMY`-magenta trim +
  yellow `#FFEA00` reactor core, paste-ready vertices (hull 8-gon + bridge + 3 prongs); **painted body ⊇ the
  r=70 collision circle in all directions** (top 74 / bottom 78 / sides 90 ≥ 70) ✓; distinct from v5 enemies
  (dark vs magenta, 5× larger, blocky capital ship), player cyan, pickups, and pills ✓ (V7.2).
- **Boss health bar + label:** center-top `(140, 52, 320, 16)`, magenta `ENEMY` fill (enemy-faction read,
  never the player's green/amber/red), pink `ENEMY_EDGE` frame, `FONT_HUD` magenta label centered above; drains
  right→left with `boss_hp/120`; shown on ARRIVAL, removed on DEFEAT; **anti-collision table proves it clears
  the player HP bar / buff pills / bomb readout / score / popups** (AC47) ✓ (V7.3).
- **Attack-4 hues:** one new `EB_COLOR_YELLOW` `#FFEA00` (anti-clash table vs gold Score / amber Fan / lime
  pellet / ice scout / HP green) for the 3-bullet fan; the **12 red children REUSE `EB_COLOR_RED` `#FF5A28`**
  (no new color, identical to v5 red children) ✓ (V7.4).
- **Arrival flash:** REUSES the v6 `FLASH_TINT` / `FLASH_PEAK_ALPHA=200` / 18-f linear fade **verbatim** —
  nothing new picked ✓ (V7.5).
- **Two new colors total** (`BOSS_HULL`, `EB_COLOR_YELLOW`); everything else reuses existing palette
  (`ENEMY`, `ENEMY_EDGE`, `HP_BACK`, `EB_COLOR_RED`, `FLASH`) and existing fonts (`FONT_HUD`). All
  `pygame.draw.*` + `pygame.font`, **no external assets (C2/AC52)** ✓. A programmer can render every v7 element
  from this file without choosing any color, size, or shape.

— end of art_spec (v7) —
