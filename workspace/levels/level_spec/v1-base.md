# Level / Difficulty Spec — "Starshard"

Owner: level-designer · Date: 2026-06-05 · Status: complete
Inputs: `workspace/design/gdd.md` (§5 caps, §6 entities, §7 scoring/ramp/master table), `workspace/requirements/requirements.md`
(R15 difficulty ramp, AC13 / §3 session length 1–3 min), `workspace/shared/backlog.md`, `workspace/shared/handoffs.md`
Implements: **R15** (difficulty ramp) tuned to satisfy **AC13** (typical run ~1–3 min).

> This file is the **single source of truth for pacing**. Every number below is programmer-ready.
> Where it differs from GDD §7.2 / §7.3 I say **OVERRIDE** and give the reason; where it keeps a GDD
> value I say **CONFIRM**. All other GDD numbers (entity sizes, damage, HP, speeds, i-frames, etc.)
> are unchanged — this spec only touches **pacing, spawn mix, caps, and one scoring tweak**.

Let `t` = seconds elapsed in the current PLAY run = `frames / 60`. `t` resets to 0 on restart (R13).
All intervals are in **frames at 60 FPS**. Use these formulas verbatim each frame.

---

## 1. Why the GDD defaults needed tuning (the two structural fixes)

1. **The enemy threat saturated instantly instead of ramping.** GDD enemies descend at only
   `0.3 px/f` in strafe, so each one lives ~39 s (700 px ÷ 0.3). With a **flat cap of 6** and a 2.5 s
   spawn, the screen pins to 6 enemies within ~15 s and stays there all run. Six enemies firing every
   75 f = **4.8 aimed bullets/s, flat, from ~15 s onward** — punishing *early*, with *no escalation*
   *late*. **Fix:** ramp the enemy **cap (2→6)** and **fire interval (1.58 s→0.92 s)** so the bullet
   hail grows over the run instead of arriving all at once.
2. **The storm capped too soft for skilled players.** Once intervals hit their floors (~88 s) the
   game stopped getting harder, so a good player who reaches steady-state could survive past 3 min.
   **Fix:** push the asteroid floor and large-rock share a little harder so the storm reliably closes
   runs near the top of the 1–3 min band.

Validated by simulating the curve (see §3 table): bullet pressure climbs smoothly **1.3/s → 6.5/s**
and on-screen asteroids **~4 → ~7**, monotonic, no early spikes.

---

## 2. Starting state (run reset values — R13)

| State | Value |
|---|---|
| Score | 0 |
| Health | 100 / 100 (single life) |
| Run timer `t` | 0 (frame counter resets) |
| Player position | `(300, 720)`, re-centered (GDD §6.1) |
| All entity lists | cleared (asteroids, enemies, all bullets, particles) |
| Time-bonus accumulator | 0 (see §7) |

No spawns on frame 0 in normal play — the first asteroid lands ~1 s in, the warmup is deliberately
empty so the player orients. **(Smoke-test mode is exempt: per GDD §11 it force-seeds 3 asteroids + 1
enemy on frame 1 for coverage; all caps in §6 still apply.)**

---

## 3. Difficulty curve (formulas — the core deliverable)

```
asteroid_spawn_interval(t) = max(22, 64 − 0.47·t)      # frames   [OVERRIDE §7.3]
enemy_spawn_interval(t)    = max(60, 130 − 0.60·t)      # frames   [OVERRIDE §7.3]
enemy_fire_interval(t)     = max(55,  95 − 0.35·t)      # frames   [OVERRIDE §7.3]
enemy_cap(t)               = min(6, 2 + int(t // 20))   # count    [OVERRIDE §7.3]
hazard_speed_bonus(t)      = min(2.0, 0.020·t)          # px/f     [CONFIRM §7.3]
large_asteroid_chance(t)   = min(0.40, 0.25 + 0.0017·t) # prob.    [OVERRIDE §7.3]
```

Sampled values (what the programmer/QA should observe):

| t (s) | ast interval | ast/s | enemy cap | enemy spawn int | fire interval | bullets/s @cap | speed bonus | large % | ~asteroids on-screen |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0   | 64.0 f | 0.94 | 2 | 130 f | 95.0 f | 1.3 | +0.00 | 25% | ~3.8 |
| 15  | 57.0 f | 1.05 | 2 | 121 f | 89.8 f | 1.3 | +0.30 | 28% | ~4.0 |
| 30  | 49.9 f | 1.20 | 3 | 112 f | 84.5 f | 2.1 | +0.60 | 30% | ~4.2 |
| 45  | 42.9 f | 1.40 | 4 | 103 f | 79.2 f | 3.0 | +0.90 | 33% | ~4.5 |
| 60  | 35.8 f | 1.68 | 5 |  94 f | 74.0 f | 4.1 | +1.20 | 35% | ~5.0 |
| 75  | 28.8 f | 2.09 | 5 |  85 f | 68.8 f | 4.4 | +1.50 | 38% | ~5.9 |
| 90  | 22.0 f | 2.73 | 6 |  76 f | 63.5 f | 5.7 | +1.80 | 40% | ~7.2 |
| 120 | 22.0 f | 2.73 | 6 |  60 f | 55.0 f | 6.5 | +2.00 | 40% | ~6.9 |
| 180 | 22.0 f | 2.73 | 6 |  60 f | 55.0 f | 6.5 | +2.00 | 40% | ~6.9 |

Floor-hit times: asteroid interval ~89 s · enemy fire ~114 s · enemy spawn ~117 s · speed bonus 100 s ·
large% ~88 s · enemy cap maxes at 80 s.

### How to read each formula
- **`asteroid_spawn_interval`** — frames between asteroid spawns. Maintain a countdown; when it hits 0,
  spawn one asteroid (subject to the §6 asteroid cap) and reset it to the current interval value.
  *(OVERRIDE: GDD `max(25, 60−0.40·t)`. Gentler open — 1.07 s vs 1.0 s — for a fair warmup; denser
  storm floor — 22 f / 2.73-per-sec vs 25 f / 2.4 — so skilled runs don't outlast 3 min.)*
- **`enemy_spawn_interval`** — frames between enemy spawn *attempts*. On fire, spawn one enemy **only
  if** the current alive-enemy count `< enemy_cap(t)`; otherwise skip (no banking). Reset countdown
  either way. *(OVERRIDE: GDD `max(70, 150−0.90·t)`. Retuned to refill the new ramping cap.)*
- **`enemy_fire_interval`** — per-enemy fire cooldown (each enemy keeps its own timer, fires only in
  Phase B per GDD §6.4). *(OVERRIDE: GDD flat 75 f. Now ramps 1.58 s→0.92 s: fairer early, harder late
  — this is the main lever that converts the flat enemy hail into a real escalation.)*
- **`enemy_cap`** — max enemies alive at once, by 20-second steps: **2** (0–20 s) → **3** (20–40 s) →
  **4** (40–60 s) → **5** (60–80 s) → **6** (80 s+). *(OVERRIDE: GDD flat 6. Ramping the cap is the
  other half of fixing the instant-saturation problem; it also makes early enemy kills feel like
  real progress.)*
- **`hazard_speed_bonus`** — added to **every asteroid's** downward speed (GDD §6.3 base 2.5–4.0 small
  / 1.5–2.8 large). *(CONFIRM: identical to GDD. Speed is the "feel" of escalation; +2.0 keeps small
  rocks ≤6.2 px/f → still ~2.1 s to cross the screen, reaction-able but clearly faster.)*
- **`large_asteroid_chance`** — probability a newly spawned asteroid is **large** (else small). Roll at
  spawn time. *(OVERRIDE: GDD flat 70/30. Drifts 75/25 → 60/40: late game gets more 2-hit, 30-damage,
  screen-blocking rocks — cheap, durable late-game pressure that asks the player to commit fire.)*

---

## 4. Spawn rules / patterns (positions & weighting)

Positions and per-entity behavior are unchanged from GDD §6 — restated here so the programmer can
implement spawning from this file alone.

- **Asteroids.** On each asteroid spawn: roll `large_asteroid_chance(t)` for size. Spawn at
  `y = −radius`, `x` uniform in `[radius, 600 − radius]`. Assign downward speed = random in the size's
  GDD range **+ `hazard_speed_bonus(t)`**, plus the GDD h-drift (±0.5 small / ±0.4 large). No safe-gap
  logic — uniform-x with the natural cooldown keeps gaps fair; **do not** spawn an asteroid whose x is
  within 1 player-width (28 px) of the player's current x on the *first* 1.5 s of the run only
  (optional anti-cheap-shot; skip if it costs lines).
- **Enemies.** On each enemy spawn attempt (if under `enemy_cap(t)`): spawn at `y = −24`,
  `x` uniform in `[40, 560]`. Entry/strafe/fire behavior per GDD §6.4 (entry to `y≥120`, then strafe
  ±2 px/f, slow descent 0.3 px/f, fire per `enemy_fire_interval(t)` aimed at the player).
- **Bullets / particles.** Unchanged (GDD §6.2, §6.5, §6.7).

There are **no discrete waves or scripted formations** — this is a continuous endless arena (per
non-goals). The "waves" are the milestone bands in §5.

---

## 5. Milestones (the felt phases of a run)

Pure consequence of §3 — no extra code, just the narrative the curve produces. Useful for QA to
sanity-check "does it feel like this?".

| Band | Name | What the player feels |
|---|---|---|
| 0–20 s | **Warmup** | Sparse. ~4 asteroids, 2 enemies, ~1.3 bullets/s. Learn the controls, get a few easy kills. |
| 20–60 s | **Heat-up** | Density and enemy count climb every ~20 s; bullets reach ~4/s. First real dodging. |
| 60–90 s | **Squeeze** | Rocks speed up, 5→6 enemies, large rocks more common. HP starts dropping for most. |
| 90 s+ | **Storm (steady-state)** | ~7 fast asteroids, 6 enemies, ~6.5 aimed bullets/s, 40% large. Survival is the goal; most runs end here. |

**Expected run length (the AC13 justification).** Player has 100 HP and 1 s i-frames per hit (GDD
§6.1), so deaths require sustained pressure, not one fluke. Modeled outcomes:
- *Weak/unlucky:* dies in Heat-up/Squeeze → **~60–90 s**.
- *Median:* enters the Storm with low HP, dies within ~20–40 s of it → **~110–130 s (≈2 min)**.
- *Skilled:* clears enemies to suppress bullets, survives deep into the Storm → **~2.5–3.5 min**, with
  rare exceptional runs just over 3 min.

That centers the distribution squarely in the **1–3 min** target (R15 / §3 / AC13). The Storm being a
true ceiling (cap 6 refilling on a 1 s fire interval + 22 f rock spawns) is what prevents runaway runs.

---

## 6. Entity caps (FPS / line-budget guard — confirms GDD §5)

Hard caps; when at cap, **skip the spawn** (don't queue). Per-frame counts stay modest so collision
loops and draws stay cheap (shapes only, easily 60 FPS).

| Entity | Cap | Source |
|---|---|---|
| Asteroids alive | **16** | **NEW** — GDD gave no explicit number; storm naturally sits ~7, 16 is headroom + safety. |
| Enemies alive | **`enemy_cap(t)`, max 6** | OVERRIDE §7.3 (was flat 6) — see §3. |
| Enemy bullets | **40** (oldest despawns first if exceeded) | CONFIRM GDD §6.5. |
| Player bullets | **~20** (natural via 12 f cooldown; no hard enforce) | CONFIRM GDD §6.2. |
| Particles | **60** (first-to-expire dropped; whole system cuttable) | CONFIRM GDD §6.7. |

Worst-case concurrent total ≈ 16 + 6 + 40 + 20 + 60 = **142** simple shapes; realistic steady-state is
~80–100. Comfortably within 60 FPS for `pygame-ce` shape drawing. If FPS ever dips on a weak machine,
drop the particle cap first (it's decorative), then enemy-bullet cap to 30.

---

## 7. Scoring tweak — small per-second survival bonus (ADD)

GDD §7.1 explicitly leaves this to the level-designer. **Decision: add it, small.**

- **+1 point for every full second survived in PLAY** (i.e. `+1` each time the run frame counter
  crosses a multiple of 60). Accumulate into the same `score` shown top-left (GDD §9). Reset with the
  run (§2).
- **Why small:** kills dominate (small 10 / large 20 / **enemy 50**, GDD §7.1) — a single enemy kill
  outscores ~50 s of survival, so this **cannot** incentivize turtling; offense always pays far more.
  Over a full 3-min run it adds only ~180 pts. What it buys: (a) a non-zero, "you got *somewhere*"
  score even on an unlucky early death — softens the retry loop; (b) rewards pushing **deeper** into
  the Storm, reinforcing the score-chase fantasy (R11). It keeps scoring legible: combat is still the
  story, time is a quiet bonus.
- **No combo/popup (R20)** — out for line budget per GDD §7.3 / §13; not reintroducing it here.

---

## 8. Tuning notes (levers for QA → programmer if AC13 fails)

If QA's smoke test passes but **playtest run length is off**, adjust in this order (cheapest, most
effective first). One lever at a time; re-test.

**Runs end too FAST (< ~1 min typical):**
1. Raise `enemy_fire_interval` floor `55 → 65` (less bullet pressure late) — biggest single lever.
2. Lower `large_asteroid_chance` cap `0.40 → 0.32`, or slow its slope.
3. Soften the asteroid floor `22 → 26` (fewer rocks in the Storm).
4. Slow the `enemy_cap` ramp: `2 + int(t // 30)` (reach 6 at 120 s instead of 80 s).

**Runs run too LONG (> ~3 min typical / skilled players never die):**
1. Lower `enemy_fire_interval` floor `55 → 50`, and/or steepen slope `0.35 → 0.45`.
2. Tighten asteroid floor `22 → 19` (denser Storm).
3. Steepen `enemy_spawn_interval` so a killed enemy is replaced faster (slope `0.60 → 0.75`).
4. Raise `hazard_speed_bonus` cap `2.0 → 2.4` (faster rocks = less reaction time). Watch it stays
   dodgeable: small-rock top speed = `4.0 + cap`; keep ≤ ~6.5 px/f.

**Feels UNFAIR rather than hard** (cheap deaths, not skill deaths):
- Confirm i-frames are actually 60 f (GDD §6.1) — most "unfair" reports are an i-frame bug.
- Enable the optional first-1.5 s no-spawn-on-player-x rule in §4.
- Reduce simultaneous *crossfire*: lower `enemy_cap` max `6 → 5`.

Leave entity-size, damage, HP, speed, i-frame, and cooldown numbers to the GDD — this spec should be
the only thing touched for pacing.

---

## 9. Traceability — every GDD §7.3 row this spec touches

| GDD §7.3 row | This spec | Section |
|---|---|---|
| Asteroid spawn interval `max(25, 60−0.40·t)` | **OVERRIDE** → `max(22, 64−0.47·t)` | §3 |
| Enemy spawn interval `max(70, 150−0.90·t)` | **OVERRIDE** → `max(60, 130−0.60·t)` | §3 |
| Enemy fire interval `75 f` (flat) | **OVERRIDE** → `max(55, 95−0.35·t)` (ramps) | §3 |
| Enemy cap `6` (flat) | **OVERRIDE** → `min(6, 2 + int(t//20))` (ramps) | §3, §6 |
| Hazard speed bonus `min(2.0, 0.02·t)` | **CONFIRM** (unchanged) | §3 |
| Asteroid mix `70% / 30%` (flat) | **OVERRIDE** → `large = min(0.40, 0.25+0.0017·t)` | §3 |
| Scoring (no time bonus; LD may add) | **ADD** → +1 pt / second survived | §7 |
| (none — no explicit asteroid cap) | **NEW** → asteroids alive ≤ 16 | §6 |
| Enemy bullet cap 40 / player bullet ~20 / particles 60 | **CONFIRM** | §6 |
| All entity sizes, damage, HP, speeds, i-frames, cooldowns | **untouched** (GDD owns) | — |

Definition of done (per role): the programmer can implement spawning and the full difficulty ramp from
the §3 formulas, §4 spawn rules, §6 caps, and §7 scoring tweak — no pacing guesswork remains.

---
---

