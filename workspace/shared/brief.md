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

## Current increment — v14: save system + lifetime-stats screen

**Human's words:** add a **save system** — a single-file **JSON**-based store that currently persists:
(1) **highscore**, (2) **number of runs**, (3) **number of enemies killed**, (4) **number of asteroids
destroyed**, (5) **number of bosses killed**. File I/O is expensive, so **keep data in memory and write
to disk only occasionally**, not every change. The save file lives **somewhere in the user folder, in a
subfolder for the game**. Plus (confirmed via kickoff Q&A): **surface a lifetime-stats screen** showing
these values on-screen.

**Decisions locked at kickoff (2026-06-06):**
- **Display scope:** *Save + full stats screen* — persist all 5 values AND surface a lifetime-stats
  view (runs, enemies, asteroids, bosses + highscore). So this is NOT invisible persistence; it adds UI.
- **Write cadence:** *flush on GAME_OVER and on hold-Q quit.* Accumulate stats in memory during a run;
  write once when the run ends and once on quit. No per-event or timer writes (honors the "writes are
  expensive" constraint; a hard crash mid-run may lose that run's partial stats — accepted).
- **File location:** a per-user game subfolder (e.g. Windows `%APPDATA%\Starshard\`). Exact path +
  cross-platform choice delegated to the Programmer; schema should carry a version field for future migration.

**Open questions delegated downstream:**
- **BA:** lock the exact stat semantics — what counts as an "enemy killed" vs "asteroid destroyed" vs
  "boss killed" (do GREEN→RED split children count? do bombed/boss-cleared kills count? does a run that
  quits mid-game still increment "runs"?), the save-file schema (fields + version + corruption/missing-file
  fallback to zeros), and the flush trigger contract. These are persisted *counts*, so definitions must be exact.
- **Designer:** decide WHERE the stats screen lives in the state machine (new STATS state reachable from
  START? a panel on GAME_OVER? toggled by a key?) and how the player navigates to/from it — no new gameplay,
  just UX placement, keeping keyboard-only + single-screen constraints.
- **Artist:** layout/placement/colors for the stats screen (reuse existing panel/HUD palette + arc style;
  no new assets) and the highscore readout.
- **Writer:** the labels/copy for each stat row + screen title (short, fits the panel).

**Scoped roles:** BA → Designer → Artist → Writer → Programmer → QA. **Level-designer skipped** (no
spawn/wave/difficulty/economy change — stats only *observe* existing events).
