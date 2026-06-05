# Story / UI Copy — "Starshard"

Owner: writer · Date: 2026-06-05 · Status: complete
Inputs: `workspace/design/gdd.md` (§9 HUD copy slots, §3 controls, §1 pitch), `workspace/art/art_spec.md`
(§4 font/color/position per text line), `workspace/requirements/requirements.md`, `workspace/shared/brief.md`.

> **Scope (non-goal guard, R/§5):** UI/flavor copy only — no cutscenes, no dialogue. Every string
> below maps 1:1 to a text slot the art_spec §4 already specced (font + color + centered position).
> The programmer should paste these **verbatim**; no copy needs to be invented. Strings are sized to
> fit their font and centered position on the 600 px-wide window.

---

## 1. Title & tagline

- **Title:** `STARSHARD`  *(art_spec §4.4 — FONT_BIG 64, color PLAYER cyan, centered y≈250)*
- **Tagline (the pitch line):** `Dodge the rocks. Gun the rest. Beat your best.`
  *(art_spec §4.4 — FONT_SMALL 22, color TEXT, centered y≈320; 46 chars — fits one line.)*

Theme note: a lone scout ship in an endless starfield (GDD §1). The voice is terse, arcade-cabinet,
all-caps where it's a heading — no lore dump, just the loop: dodge, shoot, score.

---

## 2. Start screen (R16) — exact strings, top to bottom

Maps to art_spec §4.4. Each line is centered horizontally.

| Slot | String (paste verbatim) | Font / color / y (from art_spec §4.4) |
|---|---|---|
| Title | `STARSHARD` | FONT_BIG, PLAYER, y≈250 |
| Pitch | `Dodge the rocks. Gun the rest. Beat your best.` | FONT_SMALL, TEXT, y≈320 |
| Controls line 1 | `MOVE  Arrows / WASD      FIRE  Space` | FONT_SMALL, TEXT_DIM, y≈470 |
| Controls line 2 | `QUIT  Esc` | FONT_SMALL, TEXT_DIM, y≈500 |
| Prompt | `Press any key to fly` | FONT_SMALL, TEXT, y≈560 (optional blink) |

---

## 3. HUD strings (PLAY — R10, R11) — GDD §9 copy slots

| Slot | Format string (paste verbatim) | Font / color / position (art_spec §4.2–4.3) |
|---|---|---|
| Score | `f"SCORE {score:05d}"` | FONT_HUD, TEXT, top-left (12, 10) |
| Health label *(optional, cut first)* | `f"HP {health}/100"` | FONT_SMALL, TEXT, right edge anchored x≈460 |

The health **bar** itself is drawn art (art_spec §4.3); the `HP n/100` text is the only optional HUD
label and may be dropped under the line budget without losing any required copy.

---

## 4. Game Over screen (R12, R19) — exact strings, top to bottom

Maps to art_spec §4.5. Each line is centered horizontally over the dimmed frozen field.

| Slot | String (paste verbatim) | Font / color / y (from art_spec §4.5) |
|---|---|---|
| Heading | `GAME OVER` | FONT_BIG, HP_RED, y≈300 |
| Score | `f"SCORE {score:05d}"` | FONT_MID, TEXT, y≈380 |
| Best *(R19, optional)* | `f"BEST {best:05d}"` | FONT_MID, TEXT_DIM, y≈420 |
| Restart / quit | `R  Restart      Esc  Quit` | FONT_SMALL, TEXT_DIM, y≈480 |

`SCORE` uses the same `:05d` zero-padding as the in-play HUD so the number reads consistently between
PLAY and GAME_OVER. If R19 (high score) is cut, simply omit the `BEST` line — nothing else changes.

---

## 5. String constants block (paste-ready for the programmer)

Drop these near the top of `main.py`. Two (`SCORE`, `BEST`) are f-string *templates* built at draw
time; the rest are fixed literals.

```python
# ── Start screen ───────────────────────────────────────────────
TITLE          = "STARSHARD"
PITCH          = "Dodge the rocks. Gun the rest. Beat your best."
CONTROLS_1     = "MOVE  Arrows / WASD      FIRE  Space"
CONTROLS_2     = "QUIT  Esc"
START_PROMPT   = "Press any key to fly"

# ── Game Over screen ───────────────────────────────────────────
GAMEOVER_TITLE = "GAME OVER"
GAMEOVER_KEYS  = "R  Restart      Esc  Quit"

# ── Format templates (built per-frame with the live values) ────
#   score line (HUD + Game Over):  f"SCORE {score:05d}"
#   best line  (Game Over, R19):   f"BEST {best:05d}"
#   hp label   (HUD, optional):    f"HP {health}/100"
```

---

## 6. Definition-of-done check (self-audit)

Every text slot art_spec §4 lists now has an exact string:
- Start: title ✓, pitch ✓, controls (2 lines) ✓, "press any key" prompt ✓ (§4.4)
- HUD: score label ✓, optional HP label ✓ (§4.2–4.3)
- Game Over: heading ✓, score ✓, best (R19 optional) ✓, restart/quit line ✓ (§4.5)

All copy is short enough for its font size + centered position, on-theme for Starshard, and UI-only
(no cutscenes/dialogue — non-goal respected). A programmer can render every text line from this file
without writing any copy.

— end of story (v1) —

---
---

