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

## Where is …? (topic → file)
- **Palette / named colors** → `v1-base.md` §1 (+ extensions: `v2…` §V2.1, `v5…` §V5.2, `v6…` §V6.1)
- **Health-bar green/amber/red thresholds** → `v1-base.md` §4.3
- **Render order (layering)** → `v1-base.md` §7 → **superseded by** `v2-bonus-pickups.md` §V2.6 (extended in §V5.5, §V6.6)
- **Bonus diamond pickups + buff pills + repair popup** → `v2-bonus-pickups.md`
- **Enemy body silhouettes (HEAVY/REGULAR/SCOUT) + bullet hues** → `v5-enemy-bullets.md` §V5.1–V5.2
- **Bomb pickup color/glyph, bomb-count HUD, full-screen flash** → `v6-bomb-flash.md`
- **Mothership silhouette/hull color, boss health bar + label, yellow-fan + red-child bullet hues** → `v7-bosses.md`
- **Pause overlay dim + text block + Q-hold arc, `pause_panel_y` resolution** → `v8-pause.md`

## Updating this spec
- **New increment:** add `vN-<topic>.md` (`# vN increment — …`) + a row + topic-map entry; flag any
  *superseded* render-order/section. One-line the why in `../history.md`.
- **Fix a shipped visual:** edit that version's file **in place** (keep it matching `workspace/game/view/`)
  and note the why in `../history.md`. Hex values + geometry are the contract.
