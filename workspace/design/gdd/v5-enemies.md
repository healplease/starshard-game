# v5 increment — Three enemy types (varied movement, fire & bullet behaviors)

Owner: lead-game-designer · Date: 2026-06-05 · Status: complete
Inputs: `workspace/requirements/requirements.md` v5 §13–§17 (R36–R44, AC22–AC29, **§15 Open-values table**),
`workspace/shared/brief.md` v5 increment, `workspace/levels/level_spec.md` (v1 §3 ramp / AC13), GDD v1+v2 above
(baseline enemy & bullet numbers), and the **shipped code** (`config.py` `EB_SPEED=4.5`, `EN_R/EN_HP`,
`enemy_fire_interval(t)`, `entities/hazards.py` `Enemy`, `entities/projectiles.py` `make_enemy_bullet`).
Implements: **R36–R44 (MUST)** — locks every §15 lever (per-kind size/speed/HP, bullet speeds, fire
cadences, both deviation cones, the split fraction + fan geometry + child speed). **Spawn weighting /
time-gating is deliberately NOT set here — that is the level-designer's (R41); I state only the ramp
*intent* so AC13 holds.**

> This section **appends** to v1+v2; all prior numbers still hold. The REGULAR enemy is the **existing**
> v1 fighter (GDD §6.4) **unchanged except** for the new aim-deviation cone — every other regular number
> (r=13, 2 HP, +50, 40 ram dmg, entry 2 / strafe 2 / descent 0.3, red bullet at `EB_SPEED`) is carried
> forward verbatim, so with the regular cone at 0 the behavior is **bit-for-bit today's enemy** (R37/AC29).
> All angles are degrees; all speeds px/f @60 FPS; "medium/high" are **relative to today's `EB_SPEED=4.5`**.

## V5.1 Feature in one line
Three readable threats: the **REGULAR** sprays red a little *off* your exact spot; a fat slow **HEAVY**
lobs a **green** pellet that **bursts at the midway point into a 3-red fan** along its frozen heading; a
small fast **SCOUT** snipes **fast accurate cyan** — each demands a different dodge.

## V5.2 The enemy roster (the core table) — every §15 number LOCKED

Per-kind stats. **REGULAR** values equal today's `config.py` (carried forward); **HEAVY**/**SCOUT** are
new. Collision is the listed circle radius `r`; body px is the Artist's to finalize (R42) — sizes given
as intent so the three read apart at a glance (HEAVY **>** REGULAR **>** SCOUT).

| Lever (§15) | **REGULAR** (existing) | **HEAVY** (new) | **SCOUT** (new) |
|---|---|---|---|
| Internal kind (R44, Writer blesses) | `REGULAR` | `HEAVY` | `SCOUT` |
| Collision radius `r` | **13** (unchanged) | **18** | **10** |
| Body size intent (Artist owns px) | ~26×24 chevron | ~36×32 (bigger/blockier) | ~20×18 (small/darty) |
| **Move speed** — entry (phase A) | **2.0** (unchanged) | **1.4** (slower) | **3.0** (faster) |
| **Move speed** — strafe (phase B) | **2.0** (unchanged) | **1.2** (slower) | **3.0** (faster) |
| **Move speed** — descent (phase B) | **0.3** (unchanged) | **0.3** | **0.4** |
| **HP** (player-bullet hits) | **2** (unchanged) | **4** (tanky) | **1** (fragile) |
| Score on kill | **50** (unchanged) | **80** | **60** |
| Ram damage (contact) | **40** (unchanged) | **50** | **30** |
| **Bullet color** | RED | GREEN (pellet) → RED children | CYAN |
| **Bullet speed** | **4.5** `=EB_SPEED` (medium) | **4.5** (medium) | **7.5** (high, ≈1.67× red) |
| Bullet damage / radius (collision) | 15 / r=5 (`EB_DMG`/`EB_R`) | 15 / r=5 | 15 / r=5 |
| **Fire cadence** (× the ramp base) | **×1.0** | **×1.6** (slow heavy weapon) | **×1.4** (throttled sniper) |
| **Aim-deviation cone** (half-angle) | **±12°** (moderate) | **±6°** (slight) | **±3°** (tight, < regular) |
| Projectile behavior | single aimed red | **splitting green** (V5.4) | single aimed cyan |

**Notes on the choices**
- **Sizes/speeds** give the brief's silhouette story directly: HEAVY is the big slow wall, SCOUT the
  small fast pest, REGULAR the familiar middle. Collision radii (18 / 13 / 10) keep HEAVY easy to hit
  (it's slow and tanky) and SCOUT hard to clip (it's fast and fragile — reward for landing the 1 hit).
- **HP / score / ram** track threat: HEAVY soaks **4** hits (commit fire) and pays **80**; SCOUT dies to
  **1** hit but is the deadliest fire, so it pays **60** to reward prioritizing it; REGULAR unchanged.
- **Bullet damage is a flat 15 (`EB_DMG`) and collision radius a flat 5 (`EB_R`) for ALL enemy bullets**
  — green pellet, cyan, and red children alike — so the v2 §V2.7 collision pipeline stays uniform (one
  `EnemyBullet` path, one radius). The green pellet is drawn **visually larger** (Artist, R42); that is a
  render-only choice and does **not** change its collision radius. This keeps R39.4 literally true:
  children **are** ordinary red enemy bullets.

## V5.3 Aim deviation — one mechanism, three cones (R37, R40)

All three kinds fire through **one** aim routine; only the cone constant differs. This generalizes
today's `make_enemy_bullet` (`entities/projectiles.py`) by adding a per-shot angular perturbation:

```
# heading toward the player's CURRENT position at fire time, then perturbed:
base = atan2(py - ey, px - ex)
theta = base + rng.uniform(-cone, +cone)          # cone in radians; per-shot random
v = (cos(theta), sin(theta)) * bullet_speed        # bullet_speed per kind (V5.2)
```

- **Per-shot random, not a fixed offset** (R37): each shot independently rolls `uniform(−cone, +cone)`.
- **cone = 0 ⇒ exact aim** — the perturbation is purely additive, so a zero cone reduces **identically**
  to today's dead-on shot (`make_enemy_bullet`). REGULAR with cone 0 == the pre-v5 enemy → R6/AC6/AC29
  preserved. (REGULAR ships at **±12°**, but the zero-equivalence is the regression guarantee.)
- **Cones (half-angles): REGULAR ±12° > HEAVY ±6° > SCOUT ±3°.** Monotone: SCOUT is the near-perfect
  sniper (tight; R40 allows 0 — ±3° keeps it organic rather than robotic while staying *visibly* tighter
  and faster than REGULAR per AC26), HEAVY lobs with a slight wobble, REGULAR sprays the "general area."
  At a typical ~400 px engagement, ±12° ≈ ±85 px of lateral scatter — clearly off-dead-on yet dodgeable.
- For the **HEAVY**, the perturbed heading computed here is exactly the heading that gets **frozen** for
  the split (V5.4) — i.e. the green pellet commits to its ±6°-perturbed fire-time direction.

## V5.4 The splitting green pellet (HEAVY's projectile) — R39, the centerpiece

The green pellet's full lifecycle, specified as a **FIRE-TIME-frozen distance along its own heading** (no
live player re-read), per R39.2 / risk §16:

**1 — Fire (freeze the reference).** When the HEAVY fires, compute, **once**, from the enemy position
`(ex, ey)` and the player's position `(px, py)` **at that instant**:
- the heading `u = unit(angle)` where `angle = atan2(py−ey, px−ex) + rng.uniform(−6°, +6°)` (V5.3), and
- the fire-time distance `D = hypot(px−ex, py−ey)`.

The pellet stores **`u`** and a **frozen split travel distance**
`S = max(SPLIT_FRACTION · D, SPLIT_MIN_DIST)` — **nothing about the player is read again.** It then
travels straight at `u · 4.5` px/f as an ordinary damaging enemy projectile (contact = 15 dmg, R9).

- **`SPLIT_FRACTION = 0.5`** — literal "midway" (R39.2).
- **`SPLIT_MIN_DIST = 60` px** — a floor so a point-blank HEAVY (tiny `D`) still flies a **readable**
  stretch before bursting instead of splitting on its own muzzle. Guards the §16 "split at distance ≈0"
  failure mode deterministically.

**2 — Split trigger (frozen, unconditional).** Implement as the equivalent **frozen timer**
`split_timer = round(S / 4.5)` frames (distance ÷ pellet speed, per R39.2's "or an equivalent timer").
Decrement each frame; when `split_timer ≤ 0` the pellet **is removed and replaced by its children** —
**regardless of where the player now is** (even if the player is dead/gone). It does **not** re-home.
- **Edge cases (R39):** if the pellet **hits the player** (damages + is consumed) or **leaves the screen**
  **before** `split_timer` reaches 0, it is removed by the normal bullet rules and **produces no children**
  — only a *surviving* pellet splits. (Enemy bullets are never shot down by the player — `combat.py` does
  not test player-bullets × enemy-bullets — so "destroyed before split" means *hit the player* or *off
  screen*.)

**3 — Children (exactly 3 RED, fanned about `u`).** On split, spawn **exactly 3** RED `EnemyBullet`s at
the pellet's current position, velocities = `u` **rotated** by the fan offsets, each at the child speed:
- **`FAN_HALF_ANGLE = 18°`**, **center child INCLUDED** ⇒ offsets **`(−18°, 0°, +18°)`** → one along the
  frozen heading and one to each side; **total fan 36°**; **count is exactly 3** (R39.3, AC25).
- **Child speed = 4.5** (the ordinary RED `EB_SPEED`, = the pellet's own speed) — R39.4 child-speed value.

**4 — Children are ordinary red bullets (terminal).** Each child is a plain `EnemyBullet` (RED, r=5,
15 dmg, despawns off-screen like any enemy bullet) and **never splits again** (no recursion — non-goal).
They reuse the **existing enemy-bullet update/collision path** verbatim (AC29).

> Why frozen-distance and not a live midpoint: a live re-read of the player's position would make the
> pellet feel **homing** and could collapse the split to distance ≈0 if the player closed in (§16, the
> top v5 risk). Freezing `u` and `S` at fire time makes the burst point a property of the **shot**, not
> of the player's later movement — exactly R39.2.

## V5.5 New tuning constants (programmer-ready — add to `config.py`)

All numbers above, gathered for the single-source-of-truth config. Names are suggestions; values are the
spec. Per-kind values are best expressed as a small **table keyed by kind** so spawn/render/fire branch
on `enemy.kind` (R36/AC29).

```
# ── v5 enemy roster (GDD §V5.2) ──────────────────────────────────────────────
# Per-kind: collision r, entry/strafe/descent speed, HP, score, ram dmg,
#           bullet color key, bullet speed, fire-cadence multiplier, aim cone (deg).
ENEMY_KINDS = {
  "REGULAR": dict(r=13, entry=2.0, strafe=2.0, descent=0.3, hp=2, score=50,
                  ram=40, bullet="RED",  bspeed=4.5, fire_mult=1.0, cone_deg=12),
  "HEAVY":   dict(r=18, entry=1.4, strafe=1.2, descent=0.3, hp=4, score=80,
                  ram=50, bullet="GREEN",bspeed=4.5, fire_mult=1.6, cone_deg=6),
  "SCOUT":   dict(r=10, entry=3.0, strafe=3.0, descent=0.4, hp=1, score=60,
                  ram=30, bullet="CYAN", bspeed=7.5, fire_mult=1.4, cone_deg=3),
}
# per-enemy fire cooldown = round(enemy_fire_interval(t) * fire_mult)   # ramps with t (level_spec §3)

# Splitting green pellet (GDD §V5.4)
SPLIT_FRACTION   = 0.5     # "midway": fraction of fire-time pellet→player distance
SPLIT_MIN_DIST   = 60      # px floor so a point-blank pellet still flies a readable stretch
FAN_HALF_ANGLE   = 18      # deg; children at (-18, 0, +18) → exactly 3, center included
CHILD_SPEED      = 4.5     # red child speed (= EB_SPEED / pellet speed)

# Bullet colors (Artist owns final hex, art_spec) — RED reuses today's BULLET_E
EB_COLOR_RED  = BULLET_E              # regular + split children (existing orange-red, art may retint)
EB_COLOR_GREEN = (90, 230, 120)      # heavy pellet  — Artist finalizes
EB_COLOR_CYAN  = (90, 230, 255)      # scout bullet  — Artist finalizes
```

- **Fire cadence ramps**: keep the existing `enemy_fire_interval(t) = max(55, 95−0.35·t)` as the **base**
  and scale per kind by `fire_mult`. So at t=0: REGULAR ~95 f (1.58 s), HEAVY ~152 f (2.53 s), SCOUT
  ~133 f (2.22 s); at the floor (t≳114 s): 55 / 88 / 77 f. The whole roster still gets faster late
  (level_spec §3 escalation), preserving the v1 pacing shape — HEAVY/SCOUT just fire **less often** than
  REGULAR at every `t`, which is what keeps three simultaneous patterns fair (AC28).
- **Bullet color is a render concern** (Artist, R42); the **green** RGB above is a placeholder so the
  smoke/play path has *a* color — the Artist's `art_spec` hex wins. RED children reuse the existing
  enemy-bullet color so they are indistinguishable from REGULAR's fire (intended: "they become ordinary
  red bullets").

## V5.6 Smoke-test design for the split (R43 / AC27) — must run headlessly

The 120-frame `--smoke-test` must **exercise one full green-pellet split lifecycle** (Heavy fires →
pellet reaches split point → 3-red fan → children update) without raising. 120 frames will **not**
reliably spawn a Heavy and let its pellet mature, so the smoke path **seeds** it (mechanism = programmer's
choice, R43). Design intent + recommended deterministic seed:

- On smoke frame ~**3**, seed **one green pellet** already in flight (or force-spawn a HEAVY that fires
  immediately) heading **downward toward the player**, with a **short frozen split distance** so the burst
  fires **early**: e.g. spawn at `(300, 300)`, `u=(0, 1)` (straight down at the player column), and force
  `S = SPLIT_MIN_DIST = 60` ⇒ `split_timer = round(60/4.5) ≈ 13` → **splits at ~frame 16**.
- After the split, the **3 red children** update from ~frame 16 through 120 (≈104 frames of ordinary-bullet
  life) — so **fire → travel → split → children-update** are *all* observed well inside the 120-f cap.
- Keep the existing fixed RNG seed (`SMOKE_SEED`) for determinism; the v2 seeded-Rapid lifecycle is
  unaffected (different system). Exact wiring (a `SMOKE_SPLIT_*` constant block + an `app.py` seed hook,
  mirroring the v2 `SMOKE_BONUS_*` pattern) is the **Programmer's**; this section fixes the geometry/timing
  so the seed is guaranteed to split in-budget. The **level-designer** need only confirm the seed coexists
  with the normal ramp (it will — a single seeded pellet under the §3 curve is negligible).

## V5.7 Ramp INTENT (so AC13 holds) — final weights/gating are the LEVEL-DESIGNER's (R41)

I do **not** set spawn weights or time-gates here (that's R41 / `level_spec`). I state only the **intent**
the numbers above are balanced for, so the level-designer can fold the roster into the v1 §3 ramp without
breaking AC13 (runs still ~1–3 min):

1. **REGULAR spawns from t=0** and stays the **backbone** of the mix all run — this preserves R6/AC6
   (an enemy shoots back) even before the new kinds appear, and keeps early pressure identical to v1.
2. **HEAVY folds in after the Warmup** (~the level_spec "Heat-up" band, ~20 s+) at a **low weight**: it is
   slow, tanky, and fires the *least* often (×1.6) — a low-frequency "area-denial lob" that the split makes
   scary without adding much raw bullet volume. Its presence should *replace* a fraction of REGULAR spawns,
   not add on top, so total enemy count still obeys `enemy_cap(t)`.
3. **SCOUT is the latest/most-gated** (suggest ~the "Squeeze" band, ~45–60 s+) and **lowest early weight**:
   fast accurate cyan (7.5 px/f) is the roster's most lethal fire, so introducing it later protects the
   early game and the AC13 low tail. Its ×1.4 cadence throttles volume so accuracy ≠ an unavoidable wall.
4. **Net:** because all three draw from the **same ramping `enemy_cap(t)`** and HEAVY/SCOUT fire *less*
   often than REGULAR, the **total aimed-bullet pressure stays within the v1 §3 curve** the QA-passed
   pacing was tuned to. Variety changes the *texture* of the threat (three dodges), not its *volume* —
   so AC13/AC28 should hold. The level-designer owns the final weight table + gate thresholds and
   re-confirms run length; if it drifts long/short, the level_spec §8/§V2.4 levers (and a HEAVY/SCOUT
   weight tweak) bring it back.

## V5.8 v5 requirement coverage map
| Req | Where realized |
|---|---|
| R36 typed roster (REGULAR/HEAVY/SCOUT, branchable kind) | §V5.2 table; `ENEMY_KINDS` (§V5.5) |
| R37 regular + per-shot aim deviation (0 ⇒ exact aim) | §V5.3 (±12°, additive perturbation) |
| R38 heavy (bigger/slower, green medium pellet) | §V5.2 (r=18, 1.4/1.2, 4 HP); §V5.4 |
| R39 splitting green pellet (frozen midway → 3-red fan) | §V5.4 (SPLIT_FRACTION 0.5, MIN 60, fan ±18°, 3 children) |
| R40 scout (faster/fragile, fast accurate cyan) | §V5.2 (r=10, 3.0, 1 HP, cyan 7.5); §V5.3 (±3°) |
| R41 spawn mix folds into ramp, keeps AC13 | §V5.7 **intent only** — values = level-designer |
| R42 visual distinguishability (shapes + colors) | §V5.2 size intent; §V5.5 RED/GREEN/CYAN — Artist finalizes |
| R43 smoke gate + split seeded headlessly | §V5.6 (seed @~f3, splits ~f16, children to 120) |
| R44 internal kind names | §V5.2 (`REGULAR`/`HEAVY`/`SCOUT`) — Writer blesses |

## V5.9 Open questions / handoffs to downstream roles
- **Artist (next):** finalize the three **enemy body shapes/sizes** so HEAVY (~36×32, big/blocky),
  REGULAR (~26×24 chevron, unchanged), SCOUT (~20×18, small/darty) read apart at a glance (R42, AC22);
  and the three **bullet hex**: **RED** (reuse/retint today's enemy-bullet `BULLET_E`), **GREEN** pellet
  (drawn **larger** than a normal bullet though collision stays r=5), **CYAN** (suggest small/streaky).
  Avoid clashing with the magenta enemy body, cyan player/Rapid pickup, and the green Repair/HP color —
  pick a GREEN/CYAN that stay distinct from those (a brief split "burst" is optional, not required).
- **Writer:** **bless the internal kind names** `REGULAR` / `HEAVY` / `SCOUT` (R44) for consistent use in
  code/specs/QA; no UI bestiary is required this scope.
- **Level-designer:** own the **spawn weighting + time-gating** per kind (R41) folded into the v1 §3 ramp —
  keep REGULAR from t=0, gate HEAVY/SCOUT per §V5.7 intent, **protect AC13** (1–3 min) and re-confirm the
  smoke seed coexists with the ramp (R43).
- **Programmer:** no blocking unknowns — every §15 lever is a concrete number above (§V5.2/§V5.4/§V5.5);
  the split is a frozen distance/timer along the pellet's own heading; the smoke seed geometry (§V5.6)
  guarantees an in-budget split.

---
---

