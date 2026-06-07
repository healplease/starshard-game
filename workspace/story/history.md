# Story / UI Copy — change log (writer)

> Per-domain history. The current spec is `story.md` (canonical). This file holds the dated
> decision notes for this domain only. The cross-role story lives in `../shared/handoffs.md`.

- 2026-06-05 (v1): story.md created — verbatim Start/HUD/Game Over strings + a paste-ready constants
  block for every art_spec §4 text slot. UI-only per non-goals.
- 2026-06-05 (v2): story.md v2 section added. **5 display names** — REPAIR · FAN · RAPID · SHIELD ·
  SCORE ×2. **HUD pill letters `+ F R S 2` ALL CONFIRMED, none overridden** (each single-glyph, fits the 14×14
  box / 26 px diamond, mnemonic: +=heal, F=Fan, R=Rapid, S=Shield, 2=×2; matches art_spec BONUS_STYLE + GDD
  §V2.2). FAN chosen over "Spread" so name↔letter stay in sync (S is Shield's). **Repair popup text confirmed
  `+40`** — built from `REPAIR_POPUP_TEXT = f"+{REPAIR_HP}"` so it auto-tracks the heal value and can't drift;
  no "HP" suffix (green + position by the bar already read as health, keeps it narrow). Paste-ready config block
  (BONUS_NAMES, BONUS_LETTERS, REPAIR_HP/REPAIR_POPUP_TEXT). UI-only per non-goals; full names are NOT drawn on
  the HUD (pills show only the letter); v1 strings untouched.
- 2026-06-05 (v7): story/v7.md added (bosses). **Boss name = `MOTHERSHIP`** — the brief's name, blessed
  verbatim like the v5 kind names (no synonym). **HUD label = `MOTHERSHIP` (not overridden)** — deliberately
  kept identical to the art_spec §V7.3 `boss_label_text` placeholder so the §V7.3.1 **AC47** anti-collision
  envelope (x≈[225,375] = 10 chars @ FONT_HUD 28) stays valid; a longer label would risk the proven clearance,
  hence the ≤~12-char rule. **Arrival WARNING/intro** `WARNING` / `MOTHERSHIP INBOUND` made **optional/cuttable**
  (juice; the field-clear+glide-in+bar already announce the fight), two-line to dodge a separator glyph, shown
  ARRIVAL→ENTRANCE and fading before the boss settles; placement deferred to the Artist (art_spec §V7.3 specced
  only bar+label). **Defeat copy** `MOTHERSHIP DOWN` + a points popup built as `f"+{points}"` from the **actual
  awarded value** — chosen over a hardcoded `+1000` because GDD §V7.9 routes the reward through `scoring.award`,
  so **Score×2 doubles it to 2000**; a literal would lie (same single-source-of-truth discipline as v2 `+40` /
  v6 `+1 BOMB`). UI-only (C2); all v1/v2/v5/v6 strings untouched.
- 2026-06-05 (v10): story/v10.md added (Q-hold-to-quit copy on START + GAME_OVER, R78). **New
  `START_QUIT_HINT = "Hold Q  Quit"`** — the v8 `PAUSE_HINT_QUIT` wording **verbatim** so the gesture
  reads identically wherever it's now active (START/PAUSE/GAME_OVER, one mental model); placed on the
  Artist's locked START slot (top-y 600, the arc sits 56 px below at `(300,665)`). **`GAMEOVER_KEYS`
  rewritten** `"R  Restart"` → `"R  Restart      Hold Q  Quit"` (restores the v8 two-entry key-list
  shape, second entry now the honest gesture since Q-hold quits from GAME_OVER in v10, R77); **no "Esc"**
  so AC59 + v8 R73 still hold. **`CONTROLS_2` rewritten** `"Esc  Pause · hold Q  Quit"` → `"Esc  Pause"`
  — the quit clause was a v8 *preview* (gesture wasn't START-active then); now the dedicated arc-anchored
  line owns it, so dropping the duplicate avoids "hold Q Quit" appearing twice on START (still has
  Esc+Pause for AC59). **`START_PROMPT` KEPT** `"Press any key to fly"` (Designer-blessed §V10.5: Q is
  carved out of "any key starts" but a Q-tap does nothing and starting via Q is vanishingly rare; the
  new quit hint below disambiguates Q — chose iconic v1 copy over hedging a 0.0001 % edge). Widths
  **measured** (live small font, budget W=600): START_QUIT_HINT 89 px, CONTROLS_2 77 px, GAMEOVER_KEYS
  184 px — all safe. Flagged for QA/Programmer: add `START_QUIT_HINT` to the `string_widths` budget list.
  UI-only (C2); all other v1–v8 strings untouched.
- 2026-06-07 (v18): story/v18.md added (two new bonus kinds, RAPID retired — R108/R109). **Blessed the GDD
  design handles `OVERDRIVE` / `RAILGUN` as final display names** (verbatim, like MOTHERSHIP/NOVA — no synonym).
  **Confirmed the artist's pill letters `O` (Overdrive) / `V` (Railgun), none overridden.** `O` = first letter
  (name↔letter sync, cf. FAN→F). **Kept `V` over the freed `R` for Railgun** because Railgun **reuses Rapid's
  cyan** (`BONUS_RAILGUN = PLAYER`): cyan **+** `R` would render identically to the retired Rapid pill while
  behaving differently — the same stale-read trap v12 fixed for the hold-R copy. `V` = velocity (its axis) also
  stays distinct from neighbour Shield's `S`. **No popup/pickup text** — both are timed buffs (pill only, drain
  over 480 f), exactly like old Rapid/Fan/Shield/Score; only Repair (+40) and Bomb (+1 BOMB) get collect text.
  Config: removed the `RAPID` row from `BONUS_NAMES` **and** `BONUS_LETTERS`, added the two kinds. Display names
  aren't drawn on the HUD (letters only), so no width budget concern. UI-only (C2); all v1–v17 strings untouched.
- 2026-06-05 (v12): story/v12.md added (hold-R-to-restart hint copy, R85). **`PAUSE_HINT_RESTART`
  rewritten** `"R  Restart"` → `"Hold R  Restart"` and the **R clause of `GAMEOVER_KEYS`** rewritten
  → `"Hold R  Restart      Hold Q  Quit"` (only the restart clause changed; the v10 `"Hold Q  Quit"`
  clause kept byte-for-byte). Chose `"Hold R  Restart"` = the v8/v10 `"Hold Q  Quit"` **wording shape
  verbatim** (capital "Hold", key, two spaces, action) so restart + quit read as one symmetric hold
  pair — the brief's explicit goal. Both stale instant-press strings are gone (the §46 risk: a tap no
  longer restarts after GDD §V12.5, so "R  Restart" would mislead). Both stay **one FONT_SMALL line at
  their locked y** (PAUSE 418, GAME_OVER 480) — growth is horizontal only, so the Artist's two R arcs
  (`(200,483)` / `(200,545)`) keep their 25 px vertical clearance at any width (art_spec §V12.5/§V12.6);
  GAME_OVER reads left=restart / right=quit, matching the two arcs left→right. Widths **measured** (live
  small font, budget W=600): PAUSE_HINT_RESTART 108 px, GAMEOVER_KEYS 221 px — both safe; no new
  `string_widths` row needed (both already listed). No "Esc" reintroduced (AC59 / v8 R73). UI-only (C2);
  all other v1–v11 strings untouched, Q gesture wording not touched.
