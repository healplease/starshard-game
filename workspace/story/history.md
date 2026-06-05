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
