# v5 increment — Enemy-kind spawn mix + ramp gating (appends to v1+v2; v1 ramp UNCHANGED)

Owner: level-designer · Date: 2026-06-05 · Status: complete
Inputs: `workspace/design/gdd.md` (§V5.2 roster, §V5.5 constants/`fire_mult`, §V5.6 smoke seed, §V5.7 ramp intent),
`workspace/requirements/requirements.md` (R41 spawn mix, AC13, AC27, AC28), `workspace/story/story.md` (§V5.1 blessed
names REGULAR/HEAVY/SCOUT), v1 §3 ramp + §5 milestone bands above (the QA-passed pacing), `workspace/shared/backlog.md`,
`workspace/shared/handoffs.md`.
Implements: **R41** (per-kind spawn weighting + time-gating folded into the ramp) tuned to protect **AC13** (runs
~1–3 min) and **AC28** (all three kinds appear over a typical run), and confirms the §V5.6 smoke split still runs
headlessly (**AC27**).

> **What I own (and only this):** *which enemy kind* each spawned enemy is — the **per-kind weights** and the
> **time-gates** that introduce HEAVY then SCOUT. Names are LOCKED by story §V5.1 (`REGULAR`/`HEAVY`/`SCOUT`). All
> per-kind *stats* (size/speed/HP/bullet/cone/`fire_mult`, the split geometry, the smoke seed) are LOCKED by GDD
> §V5.2–§V5.6 — I do **not** touch them. **The v1 spawn machinery is UNCHANGED:** `enemy_spawn_interval(t)` and
> `enemy_cap(t)` (v1 §3) fire exactly as today; v5 only inserts a **kind choice** at the instant a spawn actually
> fires. No new spawn path, no extra enemies on top of `enemy_cap(t)` — variety **replaces** a fraction of REGULAR
> spawns, it does not add count (GDD §V5.7.2/.4). Same `t = frames/60` clock as v1 §3.

---

## V5.1 The spawn mix (the core deliverable) — per-kind weights by ramp band

When the existing v1 spawner decides to spawn an enemy (countdown hit 0 **and** alive count `< enemy_cap(t)`),
pick its **kind** from the band the run is currently in. Bands are keyed to `t` and aligned to the §5 milestone
bands so the texture-shift tracks the felt phases of a run.

| Band (t, s) | §5 phase | **REGULAR** | **HEAVY** | **SCOUT** | What the player meets |
|---|---|---:|---:|---:|---|
| `0 ≤ t < 20`  | Warmup  | **100** | 0  | 0  | Only the familiar fighter (now ±12° off-aim). Identical kind-mix to v1 — R6/AC6 hold before any new kind. |
| `20 ≤ t < 50` | Heat-up | **85**  | **15** | 0  | The slow green **lob** folds in at low weight — first taste of the split, no raw-volume spike. |
| `50 ≤ t < 90` | Squeeze | **60**  | **15** | **25** | The fast accurate cyan **sniper** enters mid-weight — the run's lethality step-up. |
| `t ≥ 90`      | Storm   | **55**  | **15** | **30** | Scout-leaning late mix; REGULAR still the plurality, HEAVY a constant area-denial presence. |

Weights are percentages summing to 100 within each band. Gates: **`HEAVY_GATE = 20 s`**, **`SCOUT_GATE = 50 s`**
(SCOUT chosen inside the GDD §V5.7.3 "~45–60 s+" window; HEAVY at the Heat-up boundary per §V5.7.2).

### Programmer-ready kind selection (deterministic ladder, mirrors the v2 §V2.1 pattern)

Roll one `r = rng.randint(0, 99)` per spawn and walk a cumulative ladder. Uses the same world RNG as every other
spawn (so `SMOKE_SEED` keeps it deterministic). Pure function of `t` and `r` — no per-kind banking, no state.

```python
def choose_enemy_kind(t, rng):
    # t = seconds elapsed this run (frames/60); rng = the world RNG (v1 §3 / SMOKE_SEED)
    if t < 20:                       # Warmup — REGULAR only (kind-mix identical to v1)
        return "REGULAR"
    r = rng.randint(0, 99)
    if t < 50:                       # Heat-up — R85 / H15
        return "HEAVY" if r < 15 else "REGULAR"
    if t < 90:                       # Squeeze — R60 / H15 / Sc25
        if r < 60:  return "REGULAR"
        if r < 75:  return "HEAVY"
        return "SCOUT"
    # Storm (t >= 90) — R55 / H15 / Sc30
    if r < 55:  return "REGULAR"
    if r < 70:  return "HEAVY"
    return "SCOUT"
```

**Spawn position/mechanism are UNCHANGED for all kinds** (v1 §4): spawn at `y = −24`, `x` uniform in `[40, 560]`,
then entry → strafe → fire per that kind's GDD §V5.2 stats. (HEAVY r=18 is comfortably inside `[40,560]`; its
strafe still clamps to `[20,580]` per GDD §6.4.) **The v2 enemy-drop economy is UNCHANGED too** (§V2.1): every
kind, including HEAVY/SCOUT, rolls the flat **15 %** bonus drop on a **bullet-kill** (R38: "like any enemy"); ram-kills
still don't drop. Variety does not touch the bonus supply.

---

## V5.2 Realized on-screen mix ≠ spawn weight (the fragility/dwell self-balance) — why these weights are safe

Spawn weight is not the same as **time-on-screen** presence, and that gap works *for* AC13:

- **HEAVY (4 HP, tanky)** lives longer per spawn than it is spawned → it is **over-represented** on screen relative
  to its 15 % weight. That's intended: it should feel like a persistent slow wall. 15 % spawn weight keeps its
  realized presence a felt-but-minority threat rather than a field of splitting pellets.
- **SCOUT (1 HP, fragile)** dies to a single hit → it is **under-represented** on screen relative to its 25–30 %
  weight (a player who prioritizes the deadliest target clears it fast). So the roster's most-lethal fire is
  **self-limiting** — its high spawn weight buys *appearance frequency*, not a standing wall of cyan. This is the
  key AC13 protection on the lethal kind.
- **REGULAR (2 HP)** sits between, and stays the **plurality of both spawns and presence** in every band — R6/AC6's
  "an enemy shoots back" is never diluted away.

Net: realized presence trends toward roughly **REGULAR plurality · HEAVY ~20 % · SCOUT ~20 %** in the Storm despite
the 55/15/30 *spawn* split — a balanced three-threat field, not a scout swarm.

---

## V5.3 AC13 — why the mix keeps runs in the 1–3 min band

The v1 ramp was QA-passed at ~1–3 min with **every** enemy a REGULAR (±12° loose, 4.5 px/f, `fire_mult ×1.0`).
v5 swaps a fraction of those slots for HEAVY/SCOUT **without changing `enemy_cap(t)` or `enemy_spawn_interval(t)`**,
so the *number* of enemies and the *spawn cadence* are bit-for-bit v1. Only the **per-slot fire texture** changes:

1. **HEAVY fires *less* often (×1.6 → 88 f floor) but its pellet splits ×3.** One surviving pellet → 1 slow green
   + 3 RED children fanned ±18° (GDD §V5.4). So a HEAVY slot can emit *more* bullets than a REGULAR slot, but they
   are **spread across a 36° fan and time-staggered** (pellet travels ~0.5·D before bursting), and the pellet must
   *survive* to split — it's area-denial, not a concentrated wall. At 15 % weight this is a flavor threat, not a
   volume driver.
2. **SCOUT fires *less* often (×1.4 → 77 f floor) and is single-shot** — fewer bullets/s than a REGULAR slot — but
   each is fast (7.5) and accurate (±3°), so per-bullet lethality is up. Its fragility (§V5.2) caps how many are
   ever on screen at once.
3. **The two effects roughly net out against the v1 curve.** Coarse Storm-floor estimate (cap 6, base 55 f):
   REGULAR slot ≈ 1.09 loose bullets/s; SCOUT slot ≈ 0.78 fast/accurate bullets/s; HEAVY slot ≈ 0.68 shots/s → up
   to ~2.0 spread bullets/s *if every pellet survives to split*. With the 55/15/30 storm weights over 6 slots the
   aggregate aimed-bullet pressure lands **near the v1 storm's ~6.5 bullets/s** — a touch higher in raw count
   (HEAVY's split) but **lower in concentration** (fan spread + SCOUT fragility). **Variety changes the *texture*
   of the threat — three distinct dodges — not its *volume* (AC28).**
4. **The small lethality bump is the *helpful* direction.** v1's one parked AC13 caveat was the **high tail**
   (expert pure-dodgers occasionally exceeding 3 min — see §8 / §V2.4). SCOUT's accuracy and HEAVY's split nudge
   the high tail *down* toward the band; the SCOUT gate (50 s) and Warmup REGULAR-only band protect the **low tail**
   (no fast-accurate cyan before ~50 s, so weak/early runs aren't ended cheaply). Net shift on a typical run is
   small and bounded.

**Conclusion: the QA-passed v1 §3 ramp (intervals, cap, speed, large-%) stays completely UNCHANGED** — v5 rides on
top exactly as v2's bonuses did. If a human playtest shows drift, the levers in §V5.4 (then v1 §8 / §V2.4) bring it
back without destabilizing the green curve.

**AC28 coverage over a typical run:** REGULAR from t=0, HEAVY from t=20 s, SCOUT from t=50 s. The §5 run model has
even weak/unlucky runs reaching **~60–90 s** and the median ~**110–130 s**, so essentially every non-fluke run
crosses all three gates and meets all three kinds. (A sub-50 s fluke death may miss SCOUT — acceptable under
AC28's "typically/over a run".)

---

## V5.4 Tuning levers (for QA → programmer, if AC13 drifts WITH the v5 mix active)

Apply one at a time, re-test. **These v5 mix levers come first** (they retune variety without touching the
QA-passed core ramp or the v2 bonus economy); only if insufficient, fall back to v1 §8 / §V2.4.

**Runs now too SHORT (< ~1 min / the three patterns feel like a wall):**
1. **Raise `SCOUT_GATE` 50 → 65 s** — delays the lethal accurate fire, directly protecting the low tail. Biggest
   single lever on early lethality.
2. **Lower the Storm SCOUT weight 30 → 20** (give it back to REGULAR) — fewer accurate snipers late.
3. **Lower HEAVY weight 15 → 10** in Squeeze/Storm — fewer splitting fans in the air at once.

**Runs now too LONG (> ~3 min / experts never die):**
1. **Lower `SCOUT_GATE` 50 → 40 s** and/or **raise Storm SCOUT weight 30 → 35** — more accurate pressure sooner.
2. **Raise HEAVY weight 15 → 20** in Storm — more splitting fans = more total bullets to thread.
3. Only if still long: apply v1 §8 "too LONG" levers (enemy_fire floor 55→50 / asteroid floor 22→19).

**Feels like a SCOUT swarm / too much cyan:** lower the Storm SCOUT weight (30 → 20) — note its on-screen presence
is already self-limited by 1-HP fragility (§V5.2), so this is rarely needed.

Do **not** change per-kind *stats* or the split geometry here — those are GDD §V5.2–§V5.4's to own. Do **not**
change `enemy_cap(t)`/`enemy_spawn_interval(t)` for a mix problem — fix the mix first.

---

## V5.5 Smoke-seed coexistence (R43 / AC27) — CONFIRMED: the split still runs headlessly

GDD §V5.6 has the Programmer seed one green pellet at ~frame 3 that splits at ~frame 16 (children update to f120).
My job is only to confirm the **kind-weighting does not interfere** with that seed. It does not, and in fact keeps
the smoke window clean:

- The 120-frame smoke run spans `t = 0 → 2 s`, which is entirely inside the **Warmup band (`t < 20`)** → the normal
  spawner's `choose_enemy_kind` returns **REGULAR only**. So **no HEAVY or SCOUT spawns naturally** during smoke,
  and the §V5.6-seeded green pellet is the **sole** split in the run — unambiguous and attributable, exactly like
  the v2 seeded-Rapid lifecycle. The §11 frame-1 force-seed (3 asteroids + 1 enemy) yields a REGULAR enemy under
  this band — harmless, expected.
- A single seeded pellet under the (untouched) v1 §3 curve is negligible to pacing. The v2 seeded-Rapid lifecycle
  (§V2.5) is unaffected — different system, different seed block.

**Confirmed:** the v5 mix coexists with the §V5.6 smoke seed; `--smoke-test` still exercises the full
green-pellet split lifecycle headlessly within 120 frames (AC27), and exits 0. (Exact seed wiring is the
Programmer's — this only confirms the weighting leaves the smoke split intact.)

---

## V5.6 Traceability — every R41/AC this section resolves

| Lever / AC | This spec | Section |
|---|---|---|
| R41 per-kind spawn weights | **SET** → Warmup R100 · Heat-up R85/H15 · Squeeze R60/H15/Sc25 · Storm R55/H15/Sc30 | §V5.1 |
| R41 time-gating | **SET** → `HEAVY_GATE = 20 s`, `SCOUT_GATE = 50 s` (within GDD §V5.7 windows) | §V5.1 |
| R41 folds into ramp, no regression | **CONFIRM** → kind chosen *within* the unchanged v1 `enemy_cap(t)`/`enemy_spawn_interval(t)` | §V5.1, §V5.3 |
| R41 REGULAR from t=0 (R6/AC6 hold) | **CONFIRM** → Warmup band is REGULAR-only | §V5.1 |
| AC13 runs ~1–3 min | **PROTECTED** → variety = texture not volume; fragility self-limits SCOUT; helps the high tail | §V5.2, §V5.3 |
| AC28 all three kinds over a run | **CONFIRM** → gates at 0/20/50 s vs the §5 run-length model | §V5.3 |
| AC27 split seeded headlessly | **CONFIRM** → Warmup = REGULAR-only, so the §V5.6 seed is the sole, clean split | §V5.5 |
| Per-kind stats / split geometry / `fire_mult` | **untouched** (GDD §V5.2–§V5.6 owns) | — |
| v2 enemy-drop economy (15 %/bullet-kill) | **untouched** — applies to all kinds (R38) | §V5.1 |
| v1 pacing ramp (§3) + v2 economy (§V2.1) | **untouched** (QA-passed; v5 mix rides on top) | §V5.3 |

Definition of done (per role): the Programmer can implement enemy-kind selection entirely from the §V5.1 band
table + ladder (folded into the existing v1 spawner), with the AC13 rationale in §V5.2–§V5.3, the smoke-coexistence
confirmation in §V5.5, and the lever order in §V5.4 — no spawn-mix guesswork remains.

---
---

