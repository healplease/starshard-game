# Art Spec — index / navigation

> Placeholder visuals for "Starshard" (owner: **artist**) — palette, shapes/geometry, HUD layout,
> render order. Shapes + text only, **no external assets**. Split by increment; **every file is live,
> code-matching contract** (later "supersedes" wins). Cross-increment *why* → `../history.md`.

## Files (in build order)
| File | Increment | Covers (sections) | Status |
|------|-----------|-------------------|--------|
| `v1-base.md` | v1 base | §1 **palette** · §2 per-entity visuals (+ §2.1 vertex math) · §3 starfield · §4 HUD & text (font, score, **§4.3 health-bar thresholds**, start, game-over) · §5 particles · §6 polish · **§7 render order** · §8 DoD | shipped ✅ |
| `v2-bonus-pickups.md` | v2 | §V2.1 bonus palette · §V2.2 diamond pickup · §V2.3 buff-pill stack · §V2.4 "+40" repair popup · §V2.5 shield blink/ring · **§V2.6 render order (supersedes §7)** · DoD | shipped ✅ |
| `v5-enemy-bullets.md` | v5 | **§V5.1 three enemy bodies** (octagon/chevron/dart + vertex math) · **§V5.2 RED/GREEN/CYAN bullet palette** · §V5.3 bullet shapes · §V5.4 optional split burst · §V5.5 render order · DoD | shipped ✅ |
| `v6-bomb-flash.md` | v6 | §V6.1 bomb palette (`BONUS_BOMB #B464F5`) · §V6.2 violet diamond · **§V6.3 bomb-count HUD readout** (`×N`, top-right) · §V6.4 "+1 BOMB" popup · **§V6.5 activation flash** (`FLASH_TINT #F0F8FF`, alpha 200, 18-f fade) · §V6.6 render order · DoD | shipped ✅ |
| `v7-bosses.md` | v7 | §V7.1 boss palette (`BOSS_HULL #342C4A`, `EB_COLOR_YELLOW #FFEA00`) · **§V7.2 Mothership silhouette** (~180×152, vertices, r=70 coverage) · **§V7.3 boss health bar + label** (center-top, magenta, anti-collision) · §V7.4 yellow fan + red children hues · §V7.5 arrival flash (reuse v6) · §V7.6 render order · DoD | spec ✅ |
| `v8-pause.md` | v8 | **§V8.1 no new palette** (all reused) · **§V8.2 three design confirmations** (HP_AMBER arc color, alpha=110 dim, PLAYER cyan heading) · **§V8.3 exact pixel layout** (heading y=290, hints y=358/388/418, `pause_panel_y=427`, arc center y=483) · §V8.4 draw recipe (pygame.draw.arc CW from 12 o'clock) · §V8.5 anti-collision · §V8.6 render order | spec ✅ |
| `v10.md` | v10 | **§V10.2 no new palette** (reuse v8 arc verbatim) · **§V10.3 idle visibility** (track+fill drawn only while Q held; `draw_pause` untouched) · **§V10.4 the two arc centres** (`START_ARC_CENTER=(300,665)`, `GAMEOVER_ARC_CENTER=(300,545)`, each +56 below its quit-hint) · **§V10.5 anti-collision proof** (both 44×44 rects clear every text rect) · §V10.8 config · §V10.9 draw recipe (`draw_quit_arc` helper) | spec ✅ |
| `v11.md` | v11 | **§V11.2 alpha levers** (`INVULN_ALPHA_FLOOR=128`/~50%, `INVULN_ALPHA_CEIL=255`, `INVULN_PULSE_PERIOD=30 f`) · **§V11.3 cosine curve recipe** (phase→alpha off `blink_timer`) · **§V11.4 Shield ring stays SOLID** (does not pulse; amends §V2.5) · §V11.5 render-mechanism note (per-sprite alpha surface, SRCALPHA `set_alpha` gotcha) · §V11.6 render order unchanged · **no new palette** | spec ✅ |
| `v12.md` | v12 | **§V12.2 no new palette** (reuse v8 arc verbatim for the R gesture) · **§V12.3 idle visibility** (R matches Q per screen: PAUSE track always-on → two empty tracks; GAME_OVER only-while-held) · ~~**§V12.4 R-arc centres** (`(200,483)`/`(200,545)`, 100 px left)~~ **→ superseded by v13** · ~~§V12.5 R-vs-Q anti-collision~~ **→ void (v13)** · §V12.8 config · §V12.9 draw recipe (`draw_hold_arc` helper) | spec ✅ |
| `v14.md` | v14 | **§V14a.1 five ledger rows** (= R92 fields) · **§V14a.2 no new palette** (8 reused) · **§V14a.4 exact pixel layout** (title y130, rules y204/304, rows cy 264/344/404/464/524, hint y712; label rail x100 / value rail x500) · §V14a.5 `draw_stats` recipe · §V14a.6 config · **§V14a.7 render order** (STATS over starfield, no dim/arc/in-run HUD) · §V14a.8 render-smoke rects | spec ✅ |
| `v16-second-boss.md` | v16 | **§V16.1 blue pulsar palette** (`NOVA_BODY`/`NOVA_RAY`/`NOVA_BULLET` + bar colors) · **§V16.2 NOVA silhouette** (disc r=62 + 12 spikes, paste-ready, r=60 coverage) · §V16.3 plasma-azure bullets · **§V16.4 NOVA boss bar** (reuse v7 geometry, recolor blue) · §V16.5 render order · DoD | spec ✅ |
| `v13.md` | v13 | **§V13.2 R-arc centres = Q-arc centres** (`PAUSE_RESTART_ARC_CENTER=(300,483)`, `GAMEOVER_RESTART_ARC_CENTER=(300,545)`; co-located, supersedes §V12.4) · **§V13.3 R fill recolored violet `BONUS_BOMB #B464F5`** (reused, no new palette; Q stays amber) · **§V13.4 overlap + render order** (R drawn after Q → violet on top; §V12.5 R-vs-Q constraint dropped, human-approved) · §V13.5 config · §V13.6 draw recipe (`fill_color` param) | spec ✅ |
| `v17-hp-feedback-bullet-clarity.md` | v17 | **§V17.1 HP-bar green→amber→red gradient** (`hp_bar_color()`, anchors HP 100/50/0, **supersedes v1-base §4.3**) · **§V17.2 low-HP red vignette** (`#E63C3C`, health<25, edge-only radial falloff + slow pulse) · **§V17.3 HEAVY pellet `#8CF03C`→`#D230DC`** purple (`EB_COLOR_GREEN→EB_COLOR_PURPLE`, **supersedes v5 §V5.2 GREEN**) + anti-clash proof · §V17.4 render order · DoD | spec ✅ |
| `v18.md` | v18 | **§V18.1 two new bonus styles** — Overdrive `O` electric-lime `#A6F03C` (NEW) + Railgun `V` cyan `#50DCFF` (reuses freed Rapid/`PLAYER`); anti-clash table vs live palette · **§V18.2 reuse v2 diamond + pill verbatim** (only fill+letter change) · **§V18.3 registry deltas** (drop all `RAPID` visuals; `TIMED_ORDER` Fan→Overdrive→Railgun→Shield→Score; 5-pill stack ends y≈122) · §V18.4 render order unchanged · DoD | spec ✅ |
| `v19.md` | v19 | **§V19a.1 one new color** `HITBOX_RED #FF2840` (+ alpha 128) · **§V19a.2 SHIFT red hitbox indicator** (filled disc @128 + 1-px opaque rim, radius = LD's `P_HITBOX_R`, straight-alpha SRCALPHA, centered on ship, PLAY + SHIFT-held only) · **§V19a.3 ~50%-larger bullets + the draw==collision invariant** (retires the old draw≠collision flourishes; `EB_R 5→8` all enemy/boss families, player bullet `6×18`, CYAN tail 18; draws bound to LD's collision) · **§V19a.4 render order — new top world layer** (indicator after particles, appends §V2.6) · §V19a.5 ship unchanged + DoD | spec ✅ |

## Where is …? (topic → file)
- **Palette / named colors** → `v1-base.md` §1 (+ extensions: `v2…` §V2.1, `v5…` §V5.2, `v6…` §V6.1)
- **Health-bar fill color** → ~~`v1-base.md` §4.3 (stepped ≥40/<40/<20)~~ **superseded by** `v17-hp-feedback-bullet-clarity.md` §V17.1 (continuous green→amber→red gradient)
- **Low-HP red vignette (edge glow, health<25)** → `v17-hp-feedback-bullet-clarity.md` §V17.2
- **Render order (layering)** → `v1-base.md` §7 → **superseded by** `v2-bonus-pickups.md` §V2.6 (extended in §V5.5, §V6.6)
- **Bonus diamond pickups + buff pills + repair popup** → `v2-bonus-pickups.md`
- **Enemy body silhouettes (HEAVY/REGULAR/SCOUT) + bullet hues** → `v5-enemy-bullets.md` §V5.1–V5.2 (**HEAVY pellet hue superseded:** `#8CF03C` lime → `#D230DC` purple in `v17-hp-feedback-bullet-clarity.md` §V17.3)
- **Bomb pickup color/glyph, bomb-count HUD, full-screen flash** → `v6-bomb-flash.md`
- **Mothership silhouette/hull color, boss health bar + label, yellow-fan + red-child bullet hues** → `v7-bosses.md`
- **Pause overlay dim + text block + Q-hold arc, `pause_panel_y` resolution** → `v8-pause.md`
- **Q-hold-to-quit arc centres on START + GAME_OVER (only-while-held)** → `v10.md`
- **Invuln alpha pulse (floor 128 / ceil 255 / 30-f cosine), Shield-ring-stays-solid rule** → `v11.md` (amends §V2.5 blink)
- **Hold-R-to-restart arc centres on PAUSE + GAME_OVER (reuse the Q arc, two-arc placement)** → `v12.md` (centres + R-vs-Q gap **superseded by `v13.md`**)
- **R-arc co-located with the Q arc (same centre) + R fill recolored violet `BONUS_BOMB`** → `v13.md`
- **STATS lifetime-stats screen layout (5-row ledger, pixel coords, no new palette/dim/arc)** → `v14.md`
- **NOVA (2nd boss) silhouette/blue palette, plasma-azure bullets, blue NOVA boss bar (vs the magenta Mothership)** → `v16-second-boss.md`
- **v18 bonus rebalance — Overdrive (lime `O`) + Railgun (cyan `V`) pickup styles, Rapid visual dropped, registry/`TIMED_ORDER` deltas** → `v18.md` (reuses the `v2-bonus-pickups.md` diamond + pill)
- **v19 precise controls — SHIFT red hitbox-indicator circle (`HITBOX_RED #FF2840`, alpha 128, disc+opaque rim, radius=`P_HITBOX_R`, PLAY+SHIFT-only, after-particles slot) / ~50%-larger bullets + draw==collision invariant (`EB_R 5→8`, player bullet `6×18`, retires `PELLET_DRAW_R`/`NOVA_BULLET_DRAW_R`/hardcoded yellow draws) / ship draw unchanged** → `v19.md` (render order appends `v2-bonus-pickups.md` §V2.6)

## Updating this spec
- **New increment:** add `vN-<topic>.md` (`# vN increment — …`) + a row + topic-map entry; flag any
  *superseded* render-order/section. One-line the why in `../history.md`.
- **Fix a shipped visual:** edit that version's file **in place** (keep it matching `workspace/game/view/`)
  and note the why in `../history.md`. Hex values + geometry are the contract.
