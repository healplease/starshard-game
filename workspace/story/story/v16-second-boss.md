# v16 increment — Second boss copy: name NOVA + HUD label + arrival WARNING + defeat line

Owner: writer · Date: 2026-06-07 · Status: complete
Inputs: `workspace/design/gdd/v16-second-boss.md` (§V16.3 identity / "NOVA" design handle, §V16.10 Writer ask,
R102), `workspace/art/art_spec/v16-second-boss.md` (§V16.4 boss bar/label — `boss_label_text`, FONT_HUD, NOVA
blue, centered midbottom above the bar), `workspace/story/story/v7.md` (the Mothership copy — **treatment
matched verbatim**), `workspace/shared/handoffs.md` (120–121).

> **Scope (non-goal guard, same as v7):** UI-only copy — shapes + text, no cutscenes/dialogue (C2). This
> **appends**; every prior string is unchanged. v16 adds exactly four NOVA strings, **structurally identical to
> the v7 Mothership set** (§V7.1–V7.4): (1) the **boss name / display string**, (2) the **HUD bar label text**
> (`boss_label_text`), (3) an **optional arrival WARNING/intro** banner, (4) a **boss-defeat line** + the live
> reward popup. NOVA is the second entry in the boss pool (GDD §V16.2); only one boss is active at a time, so
> NOVA's copy occupies the **same HUD slots** as the Mothership's — never both at once.

---

## V16.1 Boss name — **NOVA** (blessed; the Designer's handle = the final display string)

I **bless `NOVA`** as the canonical, final on-screen name — all-caps, used **verbatim** across code (`NOVA_NAME`),
specs, backlog, handoffs, and QA, exactly like `MOTHERSHIP` (v7) and the v5 kind names. The Designer's working
handle "NOVA" (GDD §V16.3 — *"a star that shoots"*) is self-explanatory, on-theme (a radiant electric-blue
pulsar core, art_spec §V16.2), and contrasts the Mothership cleanly. **No override, no synonym** (not "Pulsar",
"Star Core", "Reactor"). The word the Designer gave **is** the name.

---

## V16.2 HUD bar label text — **`NOVA`** (the art_spec §V16.4 `boss_label_text` render-target; width-safe)

The art_spec §V16.4 boss bar renders the label as
`FONT_HUD.render(boss_label_text, True, NOVA_BAR_FILL)` centered `midbottom=(300, BOSS_BAR_RECT.y - 2)`
(FONT_HUD 28 pt, NOVA blue `#4A7CFF`, centered just above the shared center-top bar) — the **identical recipe
and slot** as the Mothership's magenta label; only the color + literal differ.

**Writer's pick: `NOVA` verbatim — do NOT override.**
- **Name↔label unity:** the bar label and the boss name are one string, exactly as in v7. The player reads
  "NOVA" on the blue bar and that is what the boss is called everywhere.
- **Width budget honored.** v7 set the rule: **≤ ~12 chars at FONT_HUD 28** to stay inside the §V7.3.1 AC47
  label envelope (`MOTHERSHIP` = 10 chars defined the widest proven box; the NOVA bar reuses that geometry
  verbatim, art_spec §V16.4, so AC47 carries over). **`NOVA` = 4 chars ≪ 10** → comfortably inside the proven
  envelope, narrower than the Mothership label — no clearance risk.
- **All-caps** matches the arcade-heading voice (`STARSHARD`, `GAME OVER`, `MOTHERSHIP`).

---

## V16.3 Arrival WARNING / intro banner (R102, **optional/cuttable**) — same klaxon as the Mothership

Mirrors the v7 §V7.3 transient two-line "incoming boss" banner exactly — the klaxon heading + the name reveal,
shown on **ARRIVAL→ENTRANCE** and fading before NOVA settles to ACTIVE:

| Line | Text (paste verbatim) | Role |
|---|---|---|
| 1 | `WARNING` | klaxon heading — **reused verbatim** from the Mothership banner (shared, boss-agnostic) |
| 2 | `NOVA INBOUND` | intro + name reveal (12 chars) — *what* is warning you; parallels `MOTHERSHIP INBOUND` |

- **Optional / cuttable juice** — the arrival field-clear + the blue star gliding in + the blue bar appearing
  already announce the fight. If the line budget is tight, **drop it**; nothing downstream depends on it.
- **When/placement** = same as v7 (Artist's to formalize): centred (x≈300), centre-screen (y≈400, where NOVA is
  *not yet* during ARRIVAL — still up top), fades before the boss reaches rest. Color the **NOVA blue**
  (`NOVA_BAR_FILL`/`NOVA_RAY`) so the warning matches *which* boss is coming (vs the Mothership's magenta) —
  Artist's final call.
- **Single-line degrade** (if one slot): `WARNING — NOVA INBOUND` (ASCII: `WARNING - NOVA INBOUND`). Two-line is
  canonical.

---

## V16.4 Boss-defeat line + the +1500 reward popup (R62, GDD §V16.6) — mirrors v7 §V7.4

On defeat (`NOVA_HP ≤ 0`, the `NOVA_KILL_SCORE = 1500` award) — same transient pattern as `MOTHERSHIP DOWN`:

| Element | Text (paste verbatim) | Notes |
|---|---|---|
| **Defeat line** | `NOVA DOWN` | terse arcade kill-confirm (9 chars); fixed literal, parallels `MOTHERSHIP DOWN` |
| **Points popup** | `f"+{points}"` | the reward, **built from the actual awarded amount** — **not** a hardcoded `+1500` |

- **Why the popup reads the live award:** GDD §V16.6 routes the reward through `scoring.award`, so **Score×2
  doubles it to 3000** if active. `f"+{points}"` (where `points` is the value actually added — 1500, or 3000
  under Score×2) stays honest; single source of truth is `NOVA_KILL_SCORE = 1500` in config. Same rule as the
  Mothership's `+{points}`.
- **When/placement** = same as v7: centre-screen where NOVA died (~y=400), fades ~1 s as the loop resumes; the
  blue bar + label are removed on the same frame (art_spec §V16.4). Flavor line cuttable; `+{points}` is the
  points read. Artist's keep/placement call; text verbatim either way.

---

## V16.5 String / label constants block (paste-ready for the programmer)

Drop into `config.py` alongside the v7 boss block. Writer **owns these literals**; the Artist owns the bar/label
geometry + colors (art_spec §V16.4). **Data-driven:** these are NOVA's name/label keys in its **pool spec**
(GDD §V16.2 / art_spec §V16.4) — the HUD reads the active boss's strings, not a hard-coded `if`. Boss #3 supplies
its own the same way.

```python
# ── v16 second boss: NOVA — name + HUD bar label (art_spec §V16.4 `boss_label_text` render-target) ──
NOVA_NAME        = "NOVA"        # canonical boss name (code/docs/QA); the Designer's handle, blessed verbatim
NOVA_LABEL_TEXT  = NOVA_NAME     # drawn on the NOVA bar: FONT_HUD 28, NOVA blue #4A7CFF, centered midbottom=(300, 50)
#   Width-safe: "NOVA" (4 chars) ≪ "MOTHERSHIP" (10) — well inside the v7 §V7.3.1 AC47 label envelope (≤ ~12 chars).

# ── v16 NOVA arrival WARNING / intro (OPTIONAL transient; ARRIVAL→ENTRANCE, fades before the boss settles) ──
NOVA_WARN_1      = "WARNING"        # klaxon heading — reuse the v7 BOSS_WARN_1 literal (boss-agnostic)
NOVA_WARN_2      = "NOVA INBOUND"   # intro + name reveal (12 chars, fits one centered FONT_MID line)
#   Single-line degrade (if one slot):  "WARNING — NOVA INBOUND"  (ASCII: "WARNING - NOVA INBOUND")
#   Cuttable juice — the arrival clear + glide-in + blue bar already announce the fight. Placement = Artist's.

# ── v16 NOVA defeat copy (transient; shown on DEFEAT + the +1500 award, fades ~1 s as the loop resumes) ──
NOVA_DEFEAT_TEXT = "NOVA DOWN"      # defeat flavor line (kill-confirm), parallels BOSS_DEFEAT_TEXT
#   Points popup tracks the ACTUAL awarded amount (1500, or 3000 under Score×2 F31) — NOT a hardcoded literal:
#     popup_s = FONT_MID.render(f"+{points}", True, TEXT)     # points = the value scoring.award actually added
#   Single source of truth for the base reward: NOVA_KILL_SCORE = 1500 (GDD §V16.4). Flavor line cuttable.
```

---

## V16.6 Definition-of-done check (v16 self-audit)
- **Boss name blessed:** `NOVA` — final, the Designer's handle, verbatim everywhere, no synonym/override; mirrors
  the v7 `MOTHERSHIP` discipline ✓ (V16.1).
- **HUD bar label set:** `NOVA` — **matches the art_spec §V16.4 `boss_label_text` render-target**; 4 chars ≪ the
  10-char `MOTHERSHIP` budget → inside the AC47 envelope (geometry reused from v7); name↔label unity ✓ (V16.2).
- **Arrival WARNING/intro written (optional):** `WARNING` / `NOVA INBOUND` (two-line, single-line degrade noted),
  ARRIVAL→ENTRANCE, fading before settle; NOVA-blue; cuttable; placement deferred to the Artist ✓ (V16.3).
- **Defeat copy written:** `NOVA DOWN` + an honest `f"+{points}"` popup tracking the real award (1500, or 3000
  under Score×2) rather than a hardcoded literal; mirrors v7 §V7.4 ✓ (V16.4).
- Paste-ready **constants block** (name/label, WARNING lines, defeat line + popup template) ✓ (V16.5).
- Non-goal respected: UI-only, shapes+text (C2); all prior copy intact; no lore/dialogue/per-step captions; the
  only new on-screen-name string is the width-safe `NOVA` ✓.

— end of story (v16) —
