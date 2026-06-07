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
v1–v14 shipped & passed QA — see `backlog.md` for the capability summary and the canonical specs in
each role folder. Closed-increment framings (v2, v5, v7–v14) are archived in
`../archive/brief-increments-*.md`.

## Current increment — v15: pytest test-suite + lint/type tooling (process hardening)

**Human's words:** programmer and tester spend too much time testing with one-off hand-crafted scripts;
replace that with a real **pytest suite** (a *set of files*, not one ~1000-line harness that "stuns
agents"). Set up **fixtures for end-to-end tests** (QA's lane) and **unit tests** (programmer's lane) so
both work faster. Add a **ruff / pyright lint+format autofixer**, and **tell the programmer they must run
the unit tests + lint-fix after finishing changes**.

This is a **process/tooling increment** — *no game-feature change* (like v9). The creative pipeline is
**skipped entirely** (BA, Designer, Artist, Writer, Level-designer = `skipped`).

**Decisions locked at kickoff (2026-06-06, via Q&A):**
- **Old harness:** *port all 75 checks, then delete.* Migrate every check in the 1,514-line
  `qa/regression_harness.py` into the new modular pytest suite (unit + e2e), prove parity (**≥75 tests
  pass**), then **delete the monolith**. Zero coverage loss is a hard requirement.
- **Lint/type bar:** ruff **format + check --fix** on every change; **pyright "basic"**. The Programmer
  *must run* them, but residual warnings are **non-blocking** (don't hard-fail the gate) — pragmatic for
  the existing codebase. The smoke gate + pytest staying green ARE blocking.
- **Role realignment:** *involve the Manager.* It owns `workspace/` structure, so it defines the `tests/`
  layout, the unit-vs-e2e split, the ruff/pyright config approach, and the new per-role testing process —
  and rewrites `roles/programmer.md`, `roles/qa-tester.md`, `CLAUDE.md`, `workspace/README.md`, and
  `qa/test_plan.md`. Programmer + QA then build against that contract.

**Work split delegated downstream:**
- **Manager (first):** design the `tests/` tree + `pyproject.toml` (pytest+ruff+pyright config) location,
  decide the **unit-vs-e2e boundary** (who ports which of the 75 checks), define the new testing process
  (Programmer runs `pytest` unit subset + `ruff --fix` + `pyright` before every handoff; QA runs the full
  suite as the regression gate), and realign all the role/process docs above. Does **not** build the suite.
- **Programmer:** scaffold `pyproject.toml`, create the `tests/` package + `conftest.py` with shared
  fixtures, port the **unit-level** checks (pure logic: physics, scoring, save serialization, spawn
  weights, string-widths) into `tests/unit/`, wire ruff/pyright, run them + smoke, keep everything green.
- **QA:** port the **e2e/behavioral AC** checks (driven through App/World pipeline, event scripts,
  render-smoke) into `tests/e2e/` with fixtures, prove parity (≥75 tests, no AC coverage lost), then
  **delete `qa/regression_harness.py`**. Smoke gate stays green.

**Smoke contract is untouched:** `main.py --smoke-test` (120 frames, simulated input, exit 0) stays the
first gate and must stay green across the whole refactor.

**Scoped roles:** Manager → Programmer → QA. **BA, Designer, Artist, Writer, Level-designer = skipped**
(no requirements/design/art/copy/economy change).
