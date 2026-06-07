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
- 2026-06-06 (v14): `v14.md` added — STATS-screen layout. Five ledger rows = the five R92 fields
  (highscore headline + runs/enemies/asteroids/bosses counters), title `STATS` + back hint. Reuses
  START's treatment: scrolling starfield, **no dim, no arc, no in-run HUD** (it's a between-runs menu,
  not an end-of-run panel). **No new palette** — 8 reused constants (PLAYER title, STAR_FAR dividers,
  TEXT/TEXT_DIM rows). Two-column ledger: label `midleft` x=100, value `midright` x=500 (≥20 px gap,
  label budget ≤260 px so the Writer's longest label can't collide with the value). Locked y: title 130,
  dividers 204/304, rows cy 264/344/404/464/524, hint 712. Resolved the GDD's "six rows" wording =
  title + 5 data rows (R92 schema has exactly 5 values) — not a blocker. Strings delegated to Writer.
- 2026-06-07 (v17): `v17-hp-feedback-bullet-clarity.md` added — three render-only changes. (1) **HP bar
  gradient** supersedes v1-base §4.3 stepped thresholds: continuous 2-segment linear RGB lerp through the
  existing anchors (green 100 → amber 50 → red 0); piecewise (not a single green→red lerp) so it passes
  through a clean amber instead of olive/brown, preserving the old danger zones as a smooth fade. **No new
  palette.** (2) **Low-HP red vignette** (NEW) at health<25: reuses `HP_RED`, edge-only radial falloff (clear
  within r=300 → α110 at the r=500 corners, k=1.5), slow cosine breathe 60↔110 over 60 f; subtle/non-obscuring,
  drawn below the HUD, distinct from the v6 near-white full-screen bomb flash; per-pixel-alpha pulse via
  `BLEND_RGBA_MULT` to dodge the v11 §V11.5 SRCALPHA `set_alpha` gotcha. (3) **HEAVY pellet** `#8CF03C` lime →
  `#D230DC` orchid-purple (hue ~296°) — the human's playtest showed lime still clashed with the Repair/HP green
  `#3CD25A`; purple is the widest open non-green gap (between bomb violet 268° and enemy magenta 324°, ~28° from
  each, further split by hue-lean + shape + white core). Rename `EB_COLOR_GREEN`→`EB_COLOR_PURPLE`; color only
  (shape/size/core/collision unchanged). Anti-clash proven vs all 13 entity groups.
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
- 2026-06-05 (v8): art_spec/v8-pause.md added (§V8.1–§V8.7). **ZERO new palette entries** — all five colors
  reused (`OVERLAY`, `PLAYER`, `TEXT_DIM`, `HP_AMBER`, `HP_BACK`). Resolved the **`pause_panel_y + 56` formula**
  (GDD §V8.4) by defining `pause_panel_y = 427` as the y-center of the bottom hint line (Restart hint);
  arc center y = 483. Layout: PAUSED heading (FONT_BIG, PLAYER cyan) top=290; three FONT_SMALL TEXT_DIM hint
  lines at tops 358/388/418; 20 px gap heading→hints, 12 px between hints, 47 px hint3-bottom→arc-center
  (≈48 px of §V8.6.1); full content block y=290–505 centered near y=397 ≈ screen center. **HP_AMBER arc
  confirmed**: high-luminance warm amber against dimmed near-black field; no competing warm element at screen
  centre during PAUSE; HP_BACK track recedes so arc pops. **alpha=110 dim confirmed visually distinct from
  GAME_OVER alpha=160**: 43 % vs 63 % opacity (~20 % difference) plus scrolling starfield (PAUSE only) +
  cyan heading vs red heading as orthogonal disambiguators. **PLAYER cyan heading confirmed**: opposite
  temperature from GAME_OVER's HP_RED; different hue from ENEMY magenta. Config constants block + draw recipe
  with CW arc math provided paste-ready (§V8.3.3/§V8.4). No new render layer — PAUSE slots into the existing
  state-overlay dispatch at layer 11.
- 2026-06-05 (v12): art_spec/v12.md added (§V12.1–§V12.10). **R-restart arc placement on PAUSE + GAME_OVER.**
  **Zero new palette / arc constants** — the R arc reuses the v8 Q arc verbatim (r=22, stroke 3, CW from
  12 o'clock, `HP_AMBER` fill / `HP_BACK` track) via the generalised `draw_hold_arc(...)`; only the two
  centres are new. **Placement rule = the Q-arc centre shifted 100 px LEFT, same y** → `PAUSE_RESTART_ARC_CENTER
  =(200,483)`, `GAMEOVER_RESTART_ARC_CENTER=(200,545)`. Chose a **horizontal** offset (not vertical) because the
  Q arc is locked centred at x=300 directly below each screen's text block, with no room to stack a second arc
  between the hints and the Q arc; shifting 100 px left drops the R arc into the **same open lower band** the Q
  arc already proved clear of all text, so it inherits that 25 px text clearance and only the new arc↔arc gap had
  to be solved — **56 px** of clear space between the two rings (> a full radius) on each screen, well distinct.
  Left (not right) so the R ring sits under the **restart** portion of the hint copy (PAUSE bottom hint /
  GAME_OVER key-list left clause), mirroring how the Q arc anchors the quit hint. **Idle-visibility matches the
  Q arc per screen** (GDD §V12.7.2): PAUSE R **track always-on** → PAUSE now shows two empty tracks side by side
  (sanctioned fallback to track-only-while-held recorded if a playtest finds it cluttered); GAME_OVER R **whole
  widget only-while-held**. Anti-collision proven in a table: each 44×44 R rect disjoint from the Q rect (56 px
  x-gap) AND every text rect (below them in y by 25 px, so any Writer hint-width change is safe). `HP_AMBER` reads
  in the lower band on both dims (α=110 / α=160). Coordinated the restart-hint slot with the Writer (each hint
  stays one line; arc clears any width).
- 2026-06-06 (v13): art_spec/v13.md added (§V13.1–§V13.7). **R-arc unified with the Q-arc.** Set
  the R-arc centre = the Q-arc centre per screen (`PAUSE_RESTART_ARC_CENTER (200,483)→(300,483)`,
  `GAMEOVER_RESTART_ARC_CENTER (200,545)→(300,545)`), **superseding v12 §V12.4**, and recolored the R
  **fill** violet `BONUS_BOMB #B464F5` (reused — no new palette; Q fill stays `HP_AMBER`). Chose to
  **reuse** the existing violet (palette's one saturated violet, luminance ≈140, reads over both dims;
  bomb pickup is PLAY-only so no in-frame clash) over a new constant — keeps the zero-new-colour rule.
  With both arcs co-located, the v12 §V12.5.1 R-vs-Q 56-px gap constraint is **dropped** (overlap
  human-approved); **render order locked R-after-Q so the violet R fill wins on dual-hold**. Co-located
  R inherits the Q arc's proven text clearance (no new anti-collision proof). Bonus: the two PAUSE
  always-on tracks now coincide into one ring (resolves v12's clutter note). Added a `fill_color` param
  to `draw_hold_arc` (defaults amber → Q unchanged; R passes violet). Hold timing/semantics untouched.
