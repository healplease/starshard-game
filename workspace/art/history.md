# Art Spec — change log (artist)

> Per-domain history. The current spec is `art_spec.md` (canonical). This file holds the dated
> decision notes for this domain only. The cross-role story lives in `../shared/handoffs.md`.

- 2026-06-05 (v1): art_spec.md created — 12-color palette (RGB+hex), per-entity shapes/geometry,
  triangle/chevron vertex math, health-bar green/amber/red thresholds (<40/<20), particles, fonts,
  render order. Implementable with `pygame.draw.*` + `pygame.font` only.
- 2026-06-05 (v2): art_spec.md v2 section added. **5 diamond pickups** (26 px point-to-point,
  half-diag 13, r=13 collide, 1px FLASH/white outline, dark BONUS_INK centered letter): per-kind hex FINAL —
  Repair `#3CD25A` (reuse HP_GREEN, letter `+`) · Fan `#FF8C28` (new orange, `F`) · Rapid `#50DCFF` (reuse
  PLAYER cyan, `R`) · Shield `#B4DCFF` (new pale-blue, `S`) · Score×2 `#FFD246` (new gold, `2`). Only **4 new
  colors**; reused HP_GREEN/PLAYER/BG/HP_BACK. **Buff pills** = 14×14 letter box + 4 px gap + 40×6 shrink bar
  at `(12, 36+18·i)`, drains L→R, stable BonusKind enum order (Fan,Rapid,Shield,Score), Repair has NO pill.
  **Repair "+40" popup** = FONT_HUD HP_GREEN centered `(528,30)`, 30 f life (REPAIR_POPUP_LIFE=30), optional
  upward drift. **Shield**: blink alone confirmed to read; optional pale-blue r=18 width-2 bubble ring (only
  while shield>0, visible frames) distinguishes 5 s shield from ~1 s i-frame blink. Added FONT_PICKUP(22)/
  FONT_PILL(18); updated render order (pickups in hazard layer; ring after player; collect-burst particles;
  pills+popup in HUD). BONUS_STYLE registry provided.
- 2026-06-05 (v5): art_spec.md v5 section added (§V5.1–§V5.6). **3 enemy bodies** kept on one magenta `ENEMY`
  fill (friend/foe unchanged) and told apart by **silhouette + size + outline weight**, not color: HEAVY =
  armored octagon 36×32 / 3px edge (r=18), REGULAR = v1 chevron 26×24 / 2px (r=13, unchanged), SCOUT = small
  sharp dart 20×18 / 1px (r=10) — paste-ready vertices each. Chose shape-not-color for bodies because R42 wants
  bullets to carry hue; spending hue on bodies would crowd the bullet palette. Optional darker-heavy/lighter-
  scout tints noted but defaulted OFF. **3 bullet families by hue:** RED reuse `#FF5A28` (BULLET_E; regular +
  all split children, so visual id = mechanical id), GREEN `#8CF03C` toxic-lime (pushed yellow-green to beat
  the bluer Repair/HP `#3CD25A`; drawn r=8 + 2px white core to read "charged", collision still r=5 per GDD),
  CYAN `#2DCDFF` electric-ice (pushed bluer/colder than player `#50DCFF`, decisively separated by a 12px streak
  + r=4 head along velocity + downward motion vs the player's upward rect). Anti-clash audit vs Repair/HP green,
  player cyan/bullet, magenta body all pass. Added render constants PELLET_DRAW_R=8 / CYAN_TAIL_LEN=12 /
  CYAN_HEAD_R=4. Optional green→red split white-ring burst specced + marked first-to-cut. Render order: new
  bullets reuse the existing enemy-bullet layer, new bodies the enemy layer — no structural change.
- 2026-06-05 (v6): art_spec.md v6 section added (§V6.1–§V6.7). **Bomb pickup = 6th v2 diamond**, fill
  **`BONUS_BOMB` `#B464F5` vivid violet**, glyph `"B"` — reuses the exact v2 diamond geometry/collision/drift,
  only color+glyph change. Chose **violet (~268°)** as the single clean unused hue band: every other slot is
  taken (green Repair/lime bullet, orange Fan, cyan Rapid/player/scout-bullet, pale-blue Shield, gold Score,
  pink-magenta enemy, red bullet). Key separations: vs Shield `#B4DCFF` violet is *saturated* (G 100) not
  desaturated; vs enemy magenta `#FF46C8` violet is *B-dominant* (B 245 > R 180) not R-dominant pink. **One new
  color total.** **HUD bomb-count readout** placed **top-right under the HP bar** (`right=588, y=34`), pairing
  the HP+bomb survival gauges and staying **clear of the dynamic §V2.6 left pill stack** (which would make the
  count jump). Look = bomb-sphere icon + `× N` (FONT_HUD), with **dimmed/hollow-ring empty (0) state** so "out
  of bombs" reads at a glance (reinforces R47); `BOMBS: N` text + pip-row given as equal alternatives (Writer's
  wording). Reuses existing fonts — no new font. **Activation flash:** confirmed the Designer's locked **18-f
  linear fade `200·(1−f/18)`**; set the Artist-owned levers — **color `FLASH_TINT` `#F0F8FF`** (near-white, a
  hair cool, deliberately ≠ pure-white `FLASH` hit-flash) + **peak alpha 200 (~78%)**, not a white-out. Flash =
  one init-time Surface, per-frame `set_alpha` only; drawn after HUD, before Game-Over overlay (PLAY-only).
  Overrides the GDD §V6.11 `FLASH_COLOR`/`FLASH_PEAK_ALPHA` placeholders; all other §V6.11 constants unchanged.
  Optional "+1 BOMB" collect popup (violet, FONT_SMALL, reuses REPAIR_POPUP_LIFE) mirrors Repair's "+40".
- 2026-06-05 (v7): art_spec/v7-bosses.md added (§V7.1–§V7.7). **Mothership** = the magenta fleet's CAPITAL
  SHIP: **dark hull `BOSS_HULL` `#342C4A`** (own body color, stands off BG, tinted violet ≠ grey asteroids,
  far darker than bright bomb violet) + **3 px `ENEMY`-magenta trim/window-lights** (faction read — "boss of
  the magenta fighters") + **yellow `#FFEA00` reactor core** (the weapon emitter, telegraphs attack-4). Chose
  dark-hull-with-magenta-trim over a single saturated boss color so SIZE + dark fill carry the "biggest mass"
  read while magenta binds it to the enemy faction. Silhouette ~180×152 (hull 8-gon + bridge tower + 3 weapon
  prongs), paste-ready vertices; **resolved the GDD §V7.7 conflict** (≤110-tall intent vs "drawn body ≥ r=70
  circle": 110 < 140) by adding bridge (+up to −74) + prongs (+down to +78) so the painted body fully encloses
  the r=70 (140 px) collision circle in EVERY direction — no phantom hits. **Boss health bar** placed
  **center-top** `(140,52,320,16)` (the one empty HUD band; corners are taken by score/HP-bar/bomb-readout, the
  left edge by pills): **magenta `ENEMY` fill** = enemy-faction health (never the player's green/amber/red),
  pink `ENEMY_EDGE` frame, `FONT_HUD` magenta label centered above; drains right→left on `boss_hp/120`; shown
  ARRIVAL→DEFEAT only. Proved AC47 anti-collision with a table (clears HP bar / pills / bomb readout / score /
  popups on ≥1 axis each). **Attack-4 hues:** ONE new `EB_COLOR_YELLOW` `#FFEA00` pure-lemon (B=0) for the
  3-bullet fan — anti-clash vs gold Score `#FFD246` (B 70), amber Fan `#FF8C28`, lime pellet `#8CF03C` (R 140),
  ice scout `#2DCDFF`; doubles as the core color. **12 red children REUSE `EB_COLOR_RED` `#FF5A28`** (no new
  color — identical to v5 red/split children, so visual id = mechanical id). **Arrival flash reuses the v6
  `FLASH_TINT`/alpha-200/18-f fade verbatim** — nothing new picked (only the trigger differs, pure logic). Net:
  **2 new colors total** (`BOSS_HULL`, `EB_COLOR_YELLOW`); reuses `ENEMY`/`ENEMY_EDGE`/`HP_BACK`/`EB_COLOR_RED`/
  `FLASH` + `FONT_HUD`. Render order: boss in the enemy layer (player draws over it), its bullets in the
  enemy-bullet layer, bar/label in HUD (transient), flash unchanged.
