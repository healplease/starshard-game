# v16 increment — NOVA silhouette + plasma-blue bullets + NOVA boss bar (placeholder visuals)

Owner: artist · Date: 2026-06-07 · Status: complete
Inputs: `workspace/design/gdd/v16-second-boss.md` (§V16.3 identity, §V16.4 stats r=60/HP 120, §V16.5 moveset,
§V16.8 consts, §V16.10 Artist ask), `v7-bosses.md` art_spec §V7.2 (Mothership silhouette — stay distinct),
§V7.3 (boss-bar treatment — reuse, recolor), §1/§V5.2/§V6.1 palettes, `workspace/shared/handoffs.md` (119–120).

> **C2/AC52 holds:** all `pygame.draw.*` + `pygame.font`, no external assets. This **appends** to v1–v15;
> nothing prior changes. NOVA is the **second boss**, picked uniformly vs the Mothership (GDD §V16.2) — only
> one boss is ever active, so it reuses the Mothership's **bar geometry and render slots verbatim** and is told
> apart by **shape + a blue palette** (vs the carrier's dark hull / magenta / yellow). The **arrival flash is
> the v6 `FLASH_*` verbatim — nothing new** (GDD §V16.10). NOVA is *"a star that shoots"*: a compact radiant
> blue **pulsar core** with a white-hot heart. **3 new colors total** (`NOVA_BODY`, `NOVA_RAY`, `NOVA_BULLET`);
> everything else reuses existing entries.

---

## V16.1 New palette — the blue pulsar family (paste as constants, extends §1 / §V7.1)

```python
# ── v16 second boss: NOVA, an electric-blue pulsar core (GDD §V16.3) ──────────────────────────
# Deliberately the Mothership's opposite: that boss is a DARK indigo carrier trimmed magenta with a
# YELLOW core; NOVA is a RADIANT electric-BLUE star with a white-hot heart. Blue is the one open hue
# slot (between scout cyan ~194° and bomb violet ~273°) — far from every existing actor.
NOVA_BODY   = (60, 90, 255)    # #3C5AFF  deep electric blue — the solid star disc (the mass)
NOVA_RAY    = (90, 150, 255)   # #5A96FF  lighter blue — radiant spikes + inner ring + bar frame
NOVA_BULLET = (74, 124, 255)   # #4A7CFF  bright plasma azure — NOVA's bullets + its bar fill/label
#   white-hot core REUSES STAR_NEAR (#EBF0FF) + a FLASH (#FFFFFF) rim — no new color.

# NOVA boss bar — REUSE the v7 boss-bar GEOMETRY verbatim (center-top (140,52,320,16), §V7.3);
# only the 3 colors differ so the two bosses' bars never look alike (magenta Mothership vs blue NOVA).
NOVA_BAR_FILL = NOVA_BULLET    # the draining HP, blue (= NOVA's shot color) — NOT the Mothership magenta
NOVA_BAR_BACK = HP_BACK        # #282C3A  REUSE the dark empty track (same as both HP bars)
NOVA_BAR_EDGE = NOVA_RAY       # #5A96FF  light-blue frame — second NOVA signal (vs pink ENEMY_EDGE)
NOVA_HP_MAX   = 120            # = GDD NOVA_HP; bar fills nova_hp / NOVA_HP_MAX, drains right→left
```

**Anti-clash check** — NOVA's blue beats every existing hue:

| Compared to | Their hex | RGB | Why NOVA blue is distinct |
|---|---|---|---|
| Player cyan | `#50DCFF` | (80, 220, 255) | NOVA G=90 vs **220** → far deeper/bluer, never "your ship". Also: boss is huge/central w/ HUD bar |
| Player bullet | `#78FFF5` | (120, 255, 245) | mint vs blue; player bullet travels **up**, NOVA's are fat blue dots |
| Scout CYAN | `#2DCDFF` | (45, 205, 255) | G=124/205 — clearly bluer; scout is a thin **streak**, NOVA a round plasma dot |
| Bomb violet | `#B464F5` | (180, 100, 245) | R=74 vs **180** → blue not purple |
| Mothership yellow/magenta | `#FFEA00` / `#FF46C8` | — | opposite side of the wheel |

---

## V16.2 The NOVA silhouette (GDD §V16.3, r=60) — a radiant pulsar, shapes only

**Read story:** a **compact radiant energy-core** — a tight solid disc with a white-hot heart, ringed by
**12 radiant spikes** ("a star that shoots"). It is *not* the Mothership: that's a wide blocky **dark** carrier
with wings/bridge/prongs; NOVA is a **radially-symmetric electric-blue star** — different shape **and** color.

| Property | Value | Why |
|---|---|---|
| **Painted silhouette** | **~180 px tip-to-tip** (disc r=62 + 12 spikes to r=90) | "still huge" (GDD §V16.4); the **solid mass** is the tight r=62 disc → the "compact core" read; spikes are thin rays |
| **Collision (GDD, fixed)** | circle **r = 60** at center | the **solid disc r=62 ⊇ the r=60 circle in every direction** (62 ≥ 60) → no phantom hits, even in the gaps between spikes |
| **Star disc** | `NOVA_BODY` `#3C5AFF`, filled circle r=62 | the deep-blue mass; covers the collision circle |
| **Radiant spikes** | 12 thin `NOVA_RAY` `#5A96FF` triangles, disc-edge → r=90 | the "pulsar/emitter" silhouette; clearly not a circle, carrier, or fighter polygon |
| **Inner ring** | 3 px `NOVA_RAY` circle r≈40 | "energy core" depth; flavor, cuttable |
| **White-hot heart** | `STAR_NEAR` `#EBF0FF` filled r≈16 + 2 px `FLASH` rim | the radiant core where bullets originate — **pre-reads** the threat (like the Mothership's yellow core) |

### V16.2.1 Vertex / draw math (paste-ready) — center `(cx, cy)`, +y down

```python
import math
NOVA_DISC_R  = 62    # solid disc (>= r=60 collision → painted body ⊇ circle)
NOVA_SPIKE_R = 90    # radiant spike tip radius (overall ~180 px)
NOVA_RING_R  = 40    # inner energy ring
NOVA_HOT_R   = 16    # white-hot core
NOVA_SPIKES  = 12
NOVA_SPIKE_HALF_DEG = 7   # spike half-width at the disc edge

# 1) radiant spikes FIRST (behind the disc; disc overlaps their roots)
for k in range(NOVA_SPIKES):
    a  = math.radians(k * (360.0 / NOVA_SPIKES))
    aL = a - math.radians(NOVA_SPIKE_HALF_DEG)
    aR = a + math.radians(NOVA_SPIKE_HALF_DEG)
    tip = (cx + NOVA_SPIKE_R * math.cos(a),  cy + NOVA_SPIKE_R * math.sin(a))
    bL  = (cx + NOVA_DISC_R  * math.cos(aL), cy + NOVA_DISC_R  * math.sin(aL))
    bR  = (cx + NOVA_DISC_R  * math.cos(aR), cy + NOVA_DISC_R  * math.sin(aR))
    pygame.draw.polygon(screen, NOVA_RAY, [tip, bL, bR])
# 2) solid star disc — guarantees coverage of the r=60 collision circle
pygame.draw.circle(screen, NOVA_BODY,  (int(cx), int(cy)), NOVA_DISC_R)
# 3) inner energy ring (flavor, cuttable)
pygame.draw.circle(screen, NOVA_RAY,   (int(cx), int(cy)), NOVA_RING_R, 3)
# 4) white-hot pulsar core (where the bullets spawn) + bright rim
pygame.draw.circle(screen, STAR_NEAR,  (int(cx), int(cy)), NOVA_HOT_R)
pygame.draw.circle(screen, FLASH,      (int(cx), int(cy)), NOVA_HOT_R, 2)
```

- **Pulse (cuttable polish, on-theme):** scale the core rim radius or the spike length by a cheap
  `1 + 0.12*sin(2π·frame/40)` "pulsar throb" — reuse the v11 cosine idea on a frame counter. **No** change to
  the r=60 collision or the locked draw radii. First thing to drop.
- **Hit feedback (cuttable):** 1-frame `FLASH` brighten of the core rim on a player-bullet hit — the **NOVA bar
  (V16.3) is the primary damage read**, so this is pure juice.
- **Distinctness audit (GDD §V16.3 / AC90):** vs **Mothership** — radial blue star vs wide dark magenta-trimmed
  carrier (shape **and** hue) ✓; vs **v5 enemies** — huge blue star vs ≤36 px magenta polygons ✓; vs **player** —
  blue star vs small cyan triangle ✓; vs **pickups/buff pills** — no diamond/pill shape ✓.

---

## V16.3 NOVA bullets — plasma azure (GDD §V16.5)

All NOVA bullets (RAKE 5, BURST 24, LANCE 4, ARC 9) are **ordinary `EnemyBullet`s** on the existing path — the
draw below is **render-only; collision stays the uniform `EB_R = 5`** (GDD §V16.5). Drawn a touch bigger than the
plain r=5 reds so the denser/deadlier barrage reads as "hot plasma".

```python
NOVA_BULLET_DRAW_R = 6   # plasma body (collision still EB_R = 5)
pygame.draw.circle(screen, NOVA_BULLET, (int(x), int(y)), NOVA_BULLET_DRAW_R)   # azure plasma round
pygame.draw.circle(screen, FLASH,       (int(x), int(y)), 2)                    # hot white core
```

- The **2 px white core is cuttable for the 24-bullet BURST ring** (avoid HUD-level clutter); keep it on the
  aimed RAKE/LANCE/ARC rounds where it reads as "incoming". Body color/size identical for all four patterns —
  no per-step hue (one boss, one bullet identity). The step-3 LANCE is faster (GDD `NOVA_LANCE_SPEED=6.0`) but
  **same color/shape** — speed alone telegraphs it.

---

## V16.4 NOVA boss bar + label (GDD R64 / §V16.10) — reuse the v7 bar, recolor blue

**Reuse the v7 §V7.3 boss-bar verbatim** — same rect `(140, 52, 320, 16)`, same track/fill/frame/label recipe,
same center-top placement (so the v7 **AC47 anti-collision proof carries over unchanged** — only one boss is ever
active). **Only the three colors + the HP source differ**, so the player instantly reads *which* boss: the
Mothership bar is **magenta**, NOVA's is **blue**.

```python
# Identical to v7 §V7.3, with the NOVA_BAR_* colors and nova_hp / NOVA_HP_MAX. Shown only while NOVA is active.
BOSS_BAR_RECT = pygame.Rect(140, 52, 320, 16)            # REUSED from v7 (unchanged)
pygame.draw.rect(screen, NOVA_BAR_BACK, BOSS_BAR_RECT)                                  # 1) track
inner_w = int((BOSS_BAR_RECT.width - 4) * max(0, nova_hp) / NOVA_HP_MAX)
fill = pygame.Rect(BOSS_BAR_RECT.x + 2, BOSS_BAR_RECT.y + 2, inner_w, BOSS_BAR_RECT.height - 4)
pygame.draw.rect(screen, NOVA_BAR_FILL, fill)                                           # 2) blue fill, drains R→L
pygame.draw.rect(screen, NOVA_BAR_EDGE, BOSS_BAR_RECT, width=2)                         # 3) light-blue frame
label = FONT_HUD.render(boss_label_text, True, NOVA_BAR_FILL)   # blue label; Writer owns the literal name
screen.blit(label, label.get_rect(midbottom=(300, BOSS_BAR_RECT.y - 2)))               # 4) centered above bar
```

| Element | Geometry | Mothership (v7) | **NOVA (v16)** |
|---|---|---|---|
| Track | `(140,52,320,16)` | `HP_BACK` | `HP_BACK` (same) |
| Fill | inset 2 px, ∝ hp/120, drains R→L | `ENEMY` magenta `#FF46C8` | **`NOVA_BULLET` blue `#4A7CFF`** |
| Frame | 2 px | `ENEMY_EDGE` pink `#FFB4EB` | **`NOVA_RAY` blue `#5A96FF`** |
| Label | `FONT_HUD`, `midbottom=(300,50)` | magenta | **blue** (Writer's NOVA name) |

- **Data-driven (matches the registry, GDD §V16.2):** the bar fill/frame/label color + the body draw + the
  bullet color are part of each boss's **visual key** in its pool spec — the HUD picks them from the active boss,
  not a hard-coded `if`. Boss #3 supplies its own three-color bar theme the same way.

---

## V16.5 Render order (extends §V7.6) — no new layer

NOVA occupies the **same slots as the Mothership**: the **enemy layer** (the star body; player ship draws over it
on a ram), the **enemy-bullet layer** (its plasma rounds, alongside RED/GREEN/CYAN/yellow), and the **HUD layer**
(its blue bar + label, while active). Arrival flash = the **existing v6 flash layer** (V7.5/§V16.10), unchanged.
No structural change.

---

## V16.6 Definition-of-done check (v16 self-audit)
- **NOVA silhouette:** electric-blue pulsar — solid `NOVA_BODY` disc r=62 + 12 `NOVA_RAY` spikes to r=90 + inner
  ring + white-hot `STAR_NEAR`/`FLASH` core; paste-ready draw; **disc r=62 ⊇ the r=60 collision circle** (no
  phantom hits) ✓; distinct from Mothership / v5 enemies / player / pickups / pills (shape **and** blue hue) ✓.
- **NOVA bullet hue:** new `NOVA_BULLET` `#4A7CFF` plasma azure (anti-clash table vs player cyan / scout cyan /
  player bullet / bomb violet / Mothership yellow) ✓; one identity for all 4 patterns, collision still EB_R=5 ✓.
- **NOVA boss bar:** reuses the v7 bar geometry + recipe (AC47 carries over), recolored **blue** (fill
  `NOVA_BULLET`, frame `NOVA_RAY`, blue label) tracking `nova_hp / NOVA_HP_MAX` (120→0) — tells NOVA apart from
  the magenta Mothership bar ✓.
- **Arrival flash:** reuses v6 `FLASH_*` verbatim — nothing new ✓.
- **3 new colors total** (`NOVA_BODY`, `NOVA_RAY`, `NOVA_BULLET`); everything else reuses `STAR_NEAR`, `FLASH`,
  `HP_BACK`, fonts. All `pygame.draw.*` + `pygame.font`, no external assets (C2/AC52) ✓. A programmer can render
  every NOVA element from this file without choosing any color, size, or shape.

— end of art_spec (v16) —
