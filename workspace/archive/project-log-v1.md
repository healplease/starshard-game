# Project log — v1 (archived, frozen)

The original `backlog.md` "Status summary" prose for v1, kept verbatim for the record. Not needed to
work the project — the live board is `../shared/backlog.md`; per-domain detail is each folder's
`history.md`. This exists so the full v1 narrative is never lost.

---

## v1 status summary (verbatim, 2026-06-05)

- Theme captured. Requirements done (R1–R22 MoSCoW, non-goals, AC1–AC13). GDD done: 600×800 @60fps,
  full numbers table, ramp formulas, screen states, HUD, smoke-test design. R20/R21 deferred for line
  budget; R19/R22 optional. Art spec done: 12-color palette (RGB+hex), per-entity shapes/geometry,
  triangle/chevron vertex math, health-bar green/amber/red (<40/<20), particles, fonts, render order.
  Writer done: story.md gives verbatim strings + a paste-ready constants block for every art_spec §4
  text slot (Start, HUD, Game Over), UI-only per non-goals.
  Level-designer done: level_spec.md tunes the ramp for 1–3 min runs (AC13). Key OVERRIDES of GDD §7.2/§7.3:
  asteroid spawn `max(22,64−0.47·t)`; enemy threat now RAMPS (fixed GDD's instant-saturation) via cap
  `min(6,2+t//20)` (2→6) and fire interval `max(55,95−0.35·t)`; enemy spawn `max(60,130−0.60·t)`;
  large-rock chance drifts 25→40%; speed bonus CONFIRMED at +2.0. NEW asteroid cap 16. ADDED +1 pt/sec
  survival bonus (kills still dominate). Tuning levers in §8 if QA finds it off.
  Programmer done: workspace/game/main.py implemented (499 lines, shapes/text only, no asset files).
  All MUST R1–R14 built; SHOULD R15 (full level_spec ramp), R16 (start screen), R17 (large-rock flash +
  6-particle death bursts), R18 (60 f blinking i-frames) built; COULD R19 (in-session BEST) built.
  R20/R21/R22 deferred for line budget per GDD §13. `--smoke-test` exits 0 after exactly 120 frames
  headless (dummy SDL drivers, seed 3 asteroids+1 enemy, simulated sweep+fire, fixed RNG seed) — verified
  3× stable, compiles warning-free on Python 3.14 / pygame-ce 2.5.7.
  QA done: VERDICT **PASS**. Smoke gate green (exit 0 / 120 f / 3× stable, ~2.3 s, no hang). All MUST
  R1–R14 verified by driving the real game logic + render paths headlessly (live window not observable
  in this env). AC1–AC12 all PASS; SHOULD R15–R18 + COULD R19 work. AC13 PASS with a non-blocking tuning
  caveat: ramp is functional and every run terminates (none hit the 8-min cap), but run length is
  skill-sensitive — non-dodgers die <30 s, a near-optimal dodge-bot survives ~2.7–5.7 min (median 260 s),
  so expert pure-dodging can exceed 3 min; recommend level_spec §8 "too LONG" levers IF a human playtest
  confirms (lower enemy_fire_interval floor 55→50 / steepen slope, then asteroid floor 22→19). Details +
  evidence in qa_report.md.
  Orchestrator done: project **DONE / shipped v1** (2026-06-05). All MUST R1–R14 verified; SHOULD
  R15–R18 + COULD R19 work; smoke gate green. No FAIL → no route-back. One non-blocking polish item
  carried forward for a future tuning pass: AC13 expert pure-dodging can exceed 3 min — apply
  level_spec §8 "too LONG" levers (enemy_fire_interval floor 55→50 / steepen slope, then asteroid
  floor 22→19) IF a human playtest confirms long runs. Play with:
  `.\.venv\Scripts\python.exe workspace\game\main.py`.
  **v1 complete.**
