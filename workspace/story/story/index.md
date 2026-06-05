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

## Where is …? (topic → file)
- **Start-screen controls line (`CONTROLS_1`)** → `v1-base.md` → **rewritten in** `v6.md` (Z = fire · X = bomb)
- **Start-screen controls line (`CONTROLS_2`)** → `v1-base.md` → **rewritten in** `v8.md` (Esc pauses · hold Q quits)
- **Score / HP / Game-Over text** → `v1-base.md`
- **Bonus names + buff-pill letters** → `v2.md`
- **Enemy kind names** → `v5.md`
- **Bomb name / glyph / bomb-count label / "+1 BOMB" popup** → `v6.md`
- **Boss name / HUD label / WARNING intro / defeat line + reward popup** → `v7.md`
- **Pause-screen heading + hints / CONTROLS_2 + GAMEOVER_KEYS rewrites** → `v8.md`

## Updating this spec
- **New increment:** add `vN.md` (`# vN increment — …`) + a row + topic-map entry; flag any string it
  *rewrites* (like `CONTROLS_1`). One-line the why in `../history.md`.
- **Fix shipped copy:** edit that version's file **in place** and keep the string matching what's pasted
  in `workspace/game/` (config/view). Record the why in `../history.md`.
