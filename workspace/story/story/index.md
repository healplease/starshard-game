# Story / UI Copy — index / navigation

> All on-screen text + naming for "Starshard" (owner: **writer**) — titles, HUD labels, names, controls
> copy, paste-ready string constants. Split by increment. **All files are live, code-matching contract**
> (the strings are pasted verbatim into `workspace/game/`). Cross-increment *why* → `../history.md`.

## Files (in build order)
| File | Increment | Covers | Status |
|------|-----------|--------|--------|
| `v1-base.md` | v1 base | Start screen (title/pitch/**controls**/prompt) · HUD (score/HP) · Game Over (heading/score/best/restart-quit) · paste-ready constants | shipped ✅ |
| `v2.md` | v2 | 5 bonus names (REPAIR/FAN/RAPID/SHIELD/SCORE×2) · pill letters `+ F R S 2` · "+40" repair popup · config block | shipped ✅ |
| `v5.md` | v5 | Enemy kind names REGULAR/HEAVY/SCOUT (R44) + **UI-copy decision: none needed** (no new strings) | shipped ✅ |
| `v6.md` | v6 | Bomb pickup name `BOMB` + glyph `B` · HUD `×N` bomb-count label · **`CONTROLS_1` rewrite "Z = fire · X = bomb"** (drops stale "Space") · "+1 BOMB" popup | shipped ✅ |
| `v7.md` | v7 | Boss name `MOTHERSHIP` · boss-bar HUD label (`boss_label_text`) · optional arrival `WARNING`/`MOTHERSHIP INBOUND` · defeat `MOTHERSHIP DOWN` + `+{points}` popup | shipped ✅ |
| `v8.md` | v8 | `PAUSE_TITLE` "PAUSED" · `PAUSE_HINT_RESUME` "Esc  Resume" · `PAUSE_HINT_QUIT` "Hold Q  Quit" · `PAUSE_HINT_RESTART` "R  Restart" · **`CONTROLS_2` rewrite** (Esc now pauses) · **`GAMEOVER_KEYS` rewrite** (Esc clause removed) | shipped ✅ |
| `v10.md` | v10 | NEW `START_QUIT_HINT` "Hold Q  Quit" (START line, top-y 600, arc-anchored) · **`GAMEOVER_KEYS` rewrite** (append "Hold Q  Quit", R77) · **`CONTROLS_2` rewrite** (drop duplicate quit clause → "Esc  Pause") · START prompt kept | shipped ✅ |
| `v12.md` | v12 | **`PAUSE_HINT_RESTART` rewrite** "Hold R  Restart" · **`GAMEOVER_KEYS` rewrite** (R clause → "Hold R  Restart", Q clause kept) — teach the hold-R-to-restart gesture (R85) | spec ready |
| `v14.md` | v14 | STATS screen: `STATS_TITLE` "LIFETIME STATS" · 5 row labels `STATS_LBL_HIGHSCORE/RUNS/ENEMIES/ASTEROIDS/BOSSES` (single-noun, ≤260 px) · `STATS_HINT` "Tab / Esc  Back" · NEW START `START_STATS_HINT` "Tab  Stats" hint line | spec ready |
| `v16-second-boss.md` | v16 | Second boss copy: name/HUD label `NOVA` (`NOVA_NAME`/`NOVA_LABEL_TEXT`) · arrival `WARNING`/`NOVA INBOUND` · defeat `NOVA DOWN` + `+{points}` popup — mirrors the v7 Mothership set | spec ready |
| `v18.md` | v18 | Two new bonus names `OVERDRIVE`/`RAILGUN` + pill letters `O`/`V` · **`RAPID` name + `R` letter removed** (R108/R109) · no popup (timed buffs) · config block | spec ready |
| `v19.md` | v19 | **`CONTROLS_1` ⚠ REWRITE** — add `Hold Shift  Focus` (the held-SHIFT precise mode) next to MOVE (R114); 462 px, fits · no new HUD label/popup/screen (red hitbox circle is the on-screen indicator) · everything else unchanged | spec ready |

## Where is …? (topic → file)
- **Start-screen controls line (`CONTROLS_1`)** → `v1-base.md` → **rewritten in** `v6.md` (Z = fire · X = bomb) → **rewritten in** `v19.md` (add `Hold Shift  Focus`)
- **Start-screen controls line (`CONTROLS_2`)** → `v1-base.md` → **rewritten in** `v8.md` (Esc pauses · hold Q quits) → **rewritten in** `v10.md` (→ "Esc  Pause"; quit clause moved to the dedicated line)
- **Start-screen quit-hint line (`START_QUIT_HINT`)** → `v10.md` (NEW; "Hold Q  Quit", arc-anchored at top-y 600)
- **Game-Over key list (`GAMEOVER_KEYS`)** → `v1-base.md` → **rewritten in** `v8.md` (Esc clause removed) → **rewritten in** `v10.md` (append "Hold Q  Quit", R77) → **rewritten in** `v12.md` (R clause → "Hold R  Restart", R85)
- **PAUSE restart hint (`PAUSE_HINT_RESTART`)** → `v8.md` ("R  Restart") → **rewritten in** `v12.md` ("Hold R  Restart", R85)
- **Score / HP / Game-Over text** → `v1-base.md`
- **Bonus names + buff-pill letters** → `v2.md` → **OVERDRIVE/RAILGUN added, RAPID removed in** `v18.md`
- **Enemy kind names** → `v5.md`
- **Bomb name / glyph / bomb-count label / "+1 BOMB" popup** → `v6.md`
- **Boss name / HUD label / WARNING intro / defeat line + reward popup** → `v7.md` (Mothership); `v16-second-boss.md` (NOVA, second boss)
- **Pause-screen heading + hints / CONTROLS_2 + GAMEOVER_KEYS rewrites** → `v8.md`
- **START quit-hint line + GAME_OVER/CONTROLS_2 quit-hint rewrites (Q-hold-to-quit copy)** → `v10.md`
- **STATS-screen strings (title / 5 row labels / back hint) + START `Tab  Stats` hint line** → `v14.md`

## Copy-surface map (string → screen/state → render site)  *(added 2026-06-05 retro)*

Every UI string and **where it is actually drawn**, so a control-scheme change can find every literal it
invalidates and QA can confirm each is on screen. Keep this current when you add/rewrite a string.

| Constant(s) | Screen / state | Render site |
|-------------|----------------|-------------|
| `TITLE`, `PITCH`, `CONTROLS_1`, `CONTROLS_2`, `START_STATS_HINT`, start prompt, `START_QUIT_HINT` | START | `view/hud.py` `draw_start()` (`START_STATS_HINT` y≈530; `START_QUIT_HINT` at top-y 600, above the v10 Q-hold arc) |
| `STATS_TITLE`, `STATS_LBL_HIGHSCORE/RUNS/ENEMIES/ASTEROIDS/BOSSES`, `STATS_HINT` | STATS | `view/hud.py` `draw_stats()` (art_spec §V14a.5; title y130, 5 rows, back hint y712) |
| score / HP readout, bomb `×N`, active buff pills | PLAY HUD | `view/hud.py` |
| boss label / `WARNING` / `MOTHERSHIP DOWN` / `NOVA DOWN` + reward popup | PLAY (boss) | `view/hud.py` |
| `PAUSE_TITLE` + 3 pause hints (resume/quit/restart) | PAUSE | `view/hud.py` `draw_pause()` |
| Game-Over heading / score / best, `GAMEOVER_KEYS` | GAME_OVER | `view/hud.py` |
| collect popups (`+40`, `+1 BOMB`, `+{points}`) | PLAY (transient) | `view/hud.py` / fx |

> **No in-game controls overlay exists** (PLAY HUD = score + HP + bomb readout only) — recorded so nobody
> re-derives it per increment. Mark any string that **replaces** a shipped one with `⚠ REWRITE` (delete the
> old literal in place, don't append).

## Updating this spec
- **New increment:** add `vN.md` (`# vN increment — …`) + a row + topic-map entry; flag any string it
  *rewrites* (like `CONTROLS_1`) with `⚠ REWRITE`, and update the copy-surface map above. One-line the why
  in `../history.md`.
- **Fix shipped copy:** edit that version's file **in place** and keep the string matching what's pasted
  in `workspace/game/` (config/view). Record the why in `../history.md`.
