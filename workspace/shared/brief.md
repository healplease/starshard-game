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

## Current increment
_None open._ The Orchestrator writes the next increment's framing here when the human gives a new
feature or theme — **theme + the human's words, lightly framed + the open questions to delegate**, then
scopes which roles it actually needs (see `roles/orchestrator.md`). Keep this section to the *latest*
increment; archive the prior framing when a new one opens.
