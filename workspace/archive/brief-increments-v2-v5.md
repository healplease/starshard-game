# Brief — closed-increment framings (archived)

Frozen. These are the orchestrator's **kickoff framings** for the closed increments **v2** (bonuses +
modular refactor) and **v5** (three enemy types), moved out of the active `../shared/brief.md` to keep
it to the theme + the *current* increment. The features they describe all shipped and passed QA; the
canonical spec for each lives in the per-domain spec files (requirements/ design/ art/ story/ levels/),
and the closeout story is in `../shared/history.md` + `handoffs-v2-v5.md`.

---

## v2 increment (added 2026-06-05) — Bonuses / power-ups + modular refactor

> v1 ("Starshard") shipped and passed QA. The human asked for a new feature plus an architecture
> change. This is the next pipeline run (BA → … → programmer → QA), building on the existing specs.

### Feature: pickup bonuses (power-ups)
Occasionally a **bonus object** spawns on-screen (drifting with the scroll, like a hazard). Flying
the ship over it **collects** it and grants a buff. Proposed buff kinds (the BA/Designer finalize the
exact set, values, durations, and balance — and may add more):
- **Repair** — restore ship HP (note: this is an *instant* one-shot effect, not a timed buff).
- **Spread/fan fire** — fire 3 or 5 beams at once in a fan, for a limited time.
- **Rapid fire** — increased fire rate, for a limited time.
- **Shield / invulnerability** — temporary invulnerability, for a limited time (reuse the existing
  i-frame/blink machinery from R18 where sensible).
- *(open to more — e.g. score multiplier, slow-time, screen-clear — designer's call within scope.)*

### Design questions for the BA & Designer to nail down
- Spawn cadence & how a bonus appears (timed drip? drop from destroyed enemies? both?).
- Buff **durations** and on-screen indication (HUD timer/icons — coordinate with Artist + Writer).
- **Stacking rules**: can two timed buffs run at once? Does picking up the same buff refresh/extend?
- Keep everything renderable as **shapes + text** and inside the single-screen, keyboard-only scope.
- AC: bonuses spawn, are collectible, apply the correct effect, expire correctly, and the
  `--smoke-test` gate still passes after the modular refactor.

### Architecture: retire the line cap, go modular
Per the human: drop the "dumb 500-line limit." Programmer refactors the single `main.py` into a
small MVC-ish module set under `workspace/game/` (config/tuning, entities/models, systems/update,
view/render, input, thin `main.py` entry). The refactor and the bonus feature land in the same
programmer pass; QA re-verifies the full requirement set + smoke gate afterward.

### Notes for the BA & Designer
Turn this into concrete requirements and a GDD. Keep the feature set minimal but fun: player ship,
scrolling background, asteroids/debris as hazards, at least one enemy type that shoots back,
player weapon, collision + health/lives, score, and a game-over/restart flow. Everything renderable
as shapes.

---

## v5 increment (added 2026-06-05) — Three enemy types (varied movement, fire & bullet behaviors)

> v1/v2 shipped & passed QA; v3 reorganized the KB; v4 added standing QA docs. The human now wants
> **enemy variety**: keep the existing enemy (with one tweak) and add two new kinds, each with its
> own size, speed, bullet color, velocity, accuracy, and a distinct projectile behavior. This is the
> next build run (BA → Designer → Artist → Writer → Level-designer → Programmer → QA).

### Feature: 3 enemy types (human's words, lightly framed)
1. **Regular enemy (existing — one tweak).** Already fires **red** bullets at **medium** velocity,
   aimed at the player's current position. **Change:** add **aim deviation** — fire at the *general
   area* of the player rather than dead-on (an inaccuracy cone, not perfect tracking).
2. **Heavy enemy (new).** **Slightly bigger**, **moves slower**. Fires **green** bullets at the
   player at **medium** velocity. The green pellet is a **splitting** projectile: **midway** to the
   player it **disappears** and becomes **3 red bullets** that **preserve the green pellet's heading**
   and **spread in a fan**. (After splitting, the children behave like ordinary red bullets.)
3. **Scout enemy (new).** **Slightly faster** (moves faster). Fires **cyan** bullets at **high**
   velocity toward the player with **high accuracy** (little/no deviation).

### Design questions for the BA & Designer to nail down (delegate values)
- Exact numbers: per-type **size**, **move speed**, **bullet speed** (red medium / green medium /
  cyan high), **fire cadence**, and the **aim-deviation cones** (regular = moderate spread, scout =
  tight/none). Define "midway" for the green split (fraction of pellet→player distance, or a timer/
  distance fallback if the player has moved) and the **fan spread angle** of the 3 red children.
- **Spawn mix / weighting & difficulty:** how often each type appears and how it folds into the
  existing level ramp (`levels/level_spec.md`) without breaking AC13 (1–3 min runs) or the v1 ramp.
- **Art:** the three enemy bodies as distinguishable **shapes/sizes** + bullet colors
  (red `#…`, green, cyan) — placeholder shapes only, coordinate with the existing palette.
- **Writer:** any names/labels if surfaced in UI (likely minimal — internal kind names at least).
- Keep everything renderable as **shapes + text**, single-screen, keyboard-only.
- **AC:** all three enemies spawn and move per spec; regular fires with deviation; heavy's green
  pellet splits midway into a 3-red fan preserving heading; scout fires fast/accurate cyan; the
  `--smoke-test` gate still exits 0 (seed at least one split so the lifecycle is exercised headlessly).

### Notes
- Builds on the existing enemy/projectile code — likely `entities/hazards.py` (enemies),
  `entities/projectiles.py` (bullets, incl. a new **splitting** behavior), `systems/combat.py`
  (firing/aim), `systems/spawning.py` (type mix), `view/render.py` (shapes/colors), `config.py`
  (tuning). The Programmer owns the actual module touch-list; this is just orientation.
