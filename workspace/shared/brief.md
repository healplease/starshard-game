# Project Brief

## Theme (from the human)
> A top-down auto-scrolling 2D space shooter. A little spaceship flies through the cosmos,
> avoiding debris and asteroids while fighting enemy ships.

## One-line pitch (Orchestrator's framing)
"**Starshard**" — pilot a lone scout ship through an endless scrolling starfield; dodge drifting
asteroids/debris and blast enemy fighters to rack up a score before your ship is destroyed.

## Genre & shape
- **Genre:** top-down vertical auto-scroller / arcade shoot-'em-up (shmup).
- **Camera:** fixed single screen; the world scrolls past the player (starfield + hazards move
  downward, ship moves within the screen).
- **Win/lose:** arcade-style — survive and score as high as possible; lose when health runs out.

## Hard constraints (from CLAUDE.md — every role respect these)
- One single screen, keyboard-only, 2D.
- Placeholder art ONLY: colored shapes + on-screen text, no external image/sound files.
- Code is modular; `main.py` stays the entry point and supports `--smoke-test` (120 frames, simulated
  input, exits 0). Keep the smoke gate green.
- Python 3.14 + `pygame-ce` from the `.venv`.

## Current state & where the detail lives
v1–v16 shipped & passed QA — see `backlog.md` for the capability summary and the canonical specs in
each role folder. Closed-increment framings (v2, v5, v7–v16) are archived in
`../archive/brief-increments-*.md`.

## Current increment — v17: HP-feedback + bullet-clarity polish (UI/UX, render-only)

**Human's words:** three UI/UX improvements — (1) make the **HP bar change color from green to red
gradually** as HP lowers (not the current stepped thresholds); (2) **slightly flash the screen with a
red vignette when HP < 25%**, kept subtle / **not distracting**; (3) the **green enemy bullets are too
easily confused with the HP bonus** — pick another (non-green) color for them (the **HEAVY** enemy
shoots them).

This is a **render-only polish increment** — no new mechanic, economy, or copy. The **creative
pipeline is skipped**; it runs **Artist → Programmer → QA** (like v13).

**Decisions locked at kickoff (2026-06-07):**
- **(1) HP bar = continuous gradient**, replacing the stepped `≥40 green / <40 amber / <20 red`
  thresholds in art_spec `v1-base.md` §4.3. Artist owns the interpolation rule (endpoints + curve);
  numbers/thresholds elsewhere are unchanged — this is purely how the bar's *fill color* is computed.
- **(2) Low-HP red vignette** triggers at **HP < 25 %** (a render trigger, not a balance number).
  Must be **subtle and non-distracting** — Artist defines the tint, max alpha, edge falloff, and any
  gentle pulse so it reads as "danger" without obscuring play. Independent of the existing v6 bomb flash.
- **(3) Recolor the HEAVY green pellet** (`EB_COLOR_GREEN #8CF03C`, art_spec `v5-enemy-bullets.md`
  §V5.2). The human's playtest shows it still clashes with the **Repair/HP green `#3CD25A`** — the
  Artist must pick a genuinely **non-green** hue and **re-verify** it stays clear of every other entity
  (the RED split-children it becomes, magenta enemy body, player cyan, CYAN scout bullet, the bonus
  palette, violet bomb). Shape/size/collision unchanged — color only.

**Out of scope / unchanged:** all gameplay numbers, HP thresholds for damage/death, the bomb flash,
boss bars, every other entity color, and all on-screen copy. No new R#/AC# expected (render polish);
QA verifies against the existing contract + the three new visual behaviors.

**Smoke + test contract untouched:** `main.py --smoke-test` (120 frames, exit 0) stays the first gate;
the pytest suite (91) stays green (grows only if a clean render-smoke assertion fits the new visuals).

**Scoped roles:** **Artist → Programmer → QA**. Skipped (no impact): BA, Designer, Writer, Level-designer.
