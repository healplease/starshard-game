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
v1–v12 shipped & passed QA — see `backlog.md` for the capability summary and the canonical specs in
each role folder. Closed-increment framings (v2, v5, v7–v12) are archived in
`../archive/brief-increments-*.md`.

## Current increment — v13: unify the restart hold-progress UI with quit

**Human's words:** holding **R** (restart) should use the **same progress bar position** as holding
**Q** (quit) — one UI element/location instead of two separate circle progresses. If R and Q are both
held they may overlap (drawing on the same spot) or only one shows; either is fine. **Hold behavior
does not change** — the only changes are (1) the restart progress arc's **position now matches the quit
arc's position** on each screen, and (2) the restart arc is **violet**.

**Lightly framed:** v12 placed the R-arc 100 px left of the Q-arc (`(200,…)` vs `(300,…)`). v13
collapses the R-arc onto the Q-arc centre (same x and y) and recolors it violet. PAUSE & GAME_OVER both
have a restart arc; START has only quit (no restart there — unchanged).

**Open question delegated to Artist:** pick the violet hex (a `BONUS_BOMB #B464F5`-style violet already
exists in the palette — reuse or pick a distinct violet) and confirm the two new R-arc centres = the
Q-arc centres. Note that with R & Q at the same centre, render order decides which arc shows on top when
both are held — that overlap is human-approved, so no anti-collision constraint between R and Q anymore.

**Scoped roles:** Artist → Programmer → QA (lazy pass). BA / Designer / Writer / Level-designer skipped
(no scope/timing/economy/copy change).
