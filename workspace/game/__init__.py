"""Starshard — a tiny top-down arcade space shooter (modular pygame-ce package).

Built to the studio blackboard specs (GDD / requirements / art_spec / story /
level_spec). Shapes + text only, keyboard only, one fixed 600×800 screen, 60 FPS.

Layout (MVC-ish, GDD §V2.9):
  config   — all tuning numbers, palette, strings (data only)
  world    — state container + enums (GameState, BonusKind)
  input    — keyboard / scripted-smoke → InputState
  entities — data models (player, hazards, projectiles, bonus, fx)
  systems  — verbs over the World (spawning, physics, combat, buffs, scoring)
  view     — read-only rendering (render, hud)
  app      — state machine, run loop, smoke harness
  main     — thin entry point (`--smoke-test`)
"""

__version__ = "2.0"
