# v2 increment — Bonus spawn economy + balance (appends to v1; v1 ramp UNCHANGED)

Owner: level-designer · Date: 2026-06-05 · Status: complete
Inputs: `workspace/design/gdd.md` (§V2.2 buff set, §V2.4 pickup entity, §V2.5 spawn defaults + smoke spec),
`workspace/requirements/requirements.md` (R23/R28/R33 MUST, AC13/AC20), `workspace/story/story.md` v2 (names + letters
`+ F R S 2`), v1 §1–§9 above (the QA-passed ramp), `workspace/shared/backlog.md`, `workspace/shared/handoffs.md`.
Implements: **R28** (bonus spawning numbers) + the **R33/AC20** smoke-reachability confirmation, balanced
so the v2 buff power spikes keep runs in the **1–3 min** band (**AC13**).

> **What I own (and only this):** the *spawn economy* of bonuses — **drip cadence, enemy-drop %,
> kind-selection weights, on-screen cap** — plus a smoke-seed confirmation and AC13 balance analysis.
> Buff *effects and durations* are LOCKED by GDD §V2.2 (Repair +40 instant; Fan 8 s; Rapid 8 s;
> Shield 5 s; Score×2 10 s) — I do **not** touch them. The **v1 pacing ramp (§3 above) is unchanged**;
> v2 adds bonuses *on top of* it. Where I keep a GDD §V2.5 default I say **CONFIRM** and give the
> balance reason; nothing here is overridden — the GDD defaults proved sound under the analysis in §V2.3.

Let `t` = seconds elapsed in the current PLAY run = `frames / 60` (same clock as v1 §3). All cadences
are in **frames @60 FPS**. Bonus pickups are **NOT** subject to the v1 hazard speed ramp (GDD §V2.4) —
they always drift at a flat **2.0 px/f** so they stay interceptable all run.

---

## V2.1 The bonus spawn numbers (the core deliverable) — all CONFIRM GDD §V2.5

| Lever | Value | Notes |
|---|---|---|
| **Drip cadence** | base **720 f (12 s)**, jitter **±120 f (±2 s)** → each interval drawn uniform in **[600, 840] f** | Primary spawn path. CONFIRM. |
| **Enemy-drop chance** | **15 %** (`0.15`) per enemy **destroyed by player fire** | Secondary path. CONFIRM. |
| **Kind weights** | **Repair 30 · Fan 20 · Rapid 20 · Shield 15 · Score×2 15** (sum 100) | One table, used by **both** paths. CONFIRM. |
| **On-screen cap** | **3** bonuses total (both paths combined) | CONFIRM. At cap → skip the spawn (no banking). |

### How the programmer implements each (programmer-ready)

- **Drip cadence.** Keep a `bonus_drip_timer` countdown. **Initialize it at run start** to a fresh draw
  `randint(600, 840)` so the **first bonus appears ~10–14 s in** (lands in the v1 "Warmup" band — an
  early, low-stakes treat to teach the collect mechanic). Each frame decrement; at 0, **attempt** a drip
  spawn and re-draw the timer `= randint(600, 840)` (reset **whether or not** the spawn happened — no
  banking). A drip spawn is **skipped** if `len(bonuses) >= 3` (the §V2.1 cap). Spawn position:
  `x` uniform in `[20, 580]`, `y = −13` (GDD §V2.5). Pick its kind by the weight table below.
- **Enemy-drop.** In the §V2.7 collision pipeline **step 2** (player-bullet kills an enemy), after
  awarding score, roll `random() < 0.15`. On success **and** if `len(bonuses) < 3`, spawn one bonus at
  the enemy's death point `(enemy.x, enemy.y)`; pick its kind by the same weight table. *(Ram-kills —
  enemy destroyed by colliding with the player, §V2.7 step 4 — do **not** drop: the player already paid
  HP for that, and a reward there would soften ramming's cost. Drops are a reward for **shooting**.)*
- **Kind weights (deterministic mapping).** Roll `r = randint(0, 99)` once per spawn (drip or drop):

  | `r` range | Kind | Letter (story.md) |
  |---|---|---|
  | `0–29`  | **Repair** | `+` |
  | `30–49` | **Fan**    | `F` |
  | `50–69` | **Rapid**  | `R` |
  | `70–84` | **Shield** | `S` |
  | `85–99` | **Score×2**| `2` |

  Both spawn paths share this one table (no per-path weighting). Cumulative thresholds are given so the
  pick is a single comparison ladder — no float weights needed.
- **On-screen cap (3).** Applies to the **total** live bonus pickups from both paths. When at 3, the
  drip is skipped and an enemy-drop is forfeited (GDD §V2.4: "enemy-drop still allowed up to the cap").
  Missed bonuses scroll off the bottom (`y − 13 > 800`) and are removed with **no penalty** (R23), which
  keeps the on-screen count self-draining so the cap is rarely the binding constraint.

---

## V2.2 Expected buff economy per run (what these numbers actually produce)

Modeled over a typical **~2 min (120 s)** run, to show the numbers are calibrated, not arbitrary:

- **Drip:** ~12 s cadence → ~**10 spawn opportunities**; minus the cap, scroll-offs, and the fact that
  grabbing one costs a dodge diversion, a typical player **collects ~3–5** of them.
- **Enemy-drop:** a player clearing enemies kills ~**10–15** fighters in 2 min (cap ramps 2→6); at 15%
  that's ~**1.5–2 extra bonuses**.
- **Total collected ≈ 5–7 bonuses/run.** By weight that's ~**1.5–2 Repairs**, ~**0.8–1 Shield**
  (≈4–5 s of invuln total), and the rest split across Fan/Rapid (offense) and Score×2.

This is a handful of **brief power spikes per run**, not a sustained transformation — exactly the
"quick risk/reward beat" the brief/GDD asked for, and small enough to keep AC13 (see §V2.3).

---

## V2.3 AC13 balance — why the buffs don't blow the 1–3 min target

The v1 QA flagged one non-blocking caveat: **expert pure-dodging can already exceed 3 min** (v1 §8
"too LONG" levers exist for it). Adding buffs *could* worsen the high tail — so I analyzed each buff's
effect on **run length**, not just on power:

1. **Repair is self-limiting and actually *compresses* the distribution.** It clamps at 100 HP with **no
   overheal, no stored charge** (GDD §V2.2). A skilled player who is at/near full HP gains **~0 survival**
   from a Repair (it clamps and is wasted). Repair only helps a player who is **already taking damage** —
   i.e. the weak/median/unlucky runs that currently end *short* of the band. Net effect: Repair **lifts
   the low tail toward 1–3 min** and **does not extend the expert tail**. As the highest-weighted pickup
   (30 %), this is a feature for AC13, not a risk — it pulls runs *into* the band from below.
2. **Shield is the only meaningful high-tail extender — and it's weighted low (15 %).** It's pure invuln
   regardless of HP, so it *does* extend skilled runs. But it's only **5 s**, second-lowest weight, so a
   typical run sees ~**4–5 s** of total shield — a few seconds, not a new survival floor. This is the
   single lever I watch for "runs too long" (see §V2.4).
3. **Fan / Rapid (offense, 40 % combined) cut incoming damage by clearing the field faster** — a mild
   survival aid — but they carry an **opportunity cost**: going to collect a bonus diverts the ship from
   optimal dodging, costing exposure. Net survival contribution is small and roughly self-paying.
4. **Score×2 (15 %) has zero survival effect** — it's the "press your luck while it's hot" score beat
   (R34), orthogonal to run length.

**Conclusion:** the dominant pickup (Repair) tightens the distribution toward the band, the only real
tail-extender (Shield) is short and low-weighted, and the rest are survival-neutral or self-paying. The
net shift to a typical run is **small and bounded** (low single-digit seconds of extra survival on
average). **Therefore I keep the QA-passed v1 ramp (§3) completely unchanged** — destabilizing a green
curve to pre-empt a bounded shift would be the wrong trade. If a human playtest shows the buffs push
runs past 3 min, the levers in §V2.4 (then v1 §8) bring it back. This honors the v1 QA recommendation:
*don't touch the ramp unless a playtest confirms.*

---

## V2.4 Tuning levers (for QA → programmer, if AC13 drifts WITH buffs active)

Apply one at a time, re-test. **These v2 economy levers come first** (they target the buff system
without touching the QA-passed core ramp); only if they're insufficient, fall back to v1 §8.

**Runs now too LONG (> ~3 min / experts never die):**
1. **Lower the Shield weight `15 → 10`** (give the 5 saved points to Score×2 → 20, the survival-neutral
   buff). Biggest single buff-economy lever on the high tail — directly trims the only real extender.
2. **Lengthen drip cadence `720 → 840 f` (12 → 14 s)** — fewer total spikes per run (~15 % fewer drips).
3. **Lower enemy-drop `15 % → 10 %`** — trims the secondary supply for players who clear lots of enemies.
4. Only if still long: apply v1 §8 "too LONG" levers (enemy_fire floor 55→50 / asteroid floor 22→19).

**Runs now too SHORT (< ~1 min / buffs feel pointless):**
1. **Shorten drip cadence `720 → 600 f` (12 → 10 s)** — more frequent recovery/power.
2. **Raise Repair weight `30 → 35`** (take 5 from Score×2) — more recovery for the players dying early.
   (Safe for the high tail: Repair self-limits per §V2.3.)
3. Raise the on-screen cap `3 → 4` (more banked at once) — last resort; watch HUD/clarity.

**Feels CLUTTERED / too many bonuses on screen:** lower the on-screen cap `3 → 2` (GDD allows it).

Do **not** change buff *durations or effects* here — those are GDD §V2.2's to own.

---

## V2.5 Smoke-seed confirmation (R28 / R33 / AC20) — CONFIRMED reachable + expirable in 120 f

GDD §V2.5 asks me to confirm the `--smoke-test` seed makes a bonus **collectible AND expirable** inside
120 frames. I worked the geometry against the v1 smoke harness (player force-spawned at `(300, 720)`,
scripted **slow left-right sweep + fire every frame**, fixed RNG seed). **Confirmed — it works.** Spec
for the programmer:

**Seed (frame ~2):** force-spawn **one Rapid pickup** at **`(300, 700)`** — i.e. the **player's x**,
**20 px directly above** the player — with its duration **forced to 60 f** for smoke mode only.

**Why it's collected (deterministic, sweep-independent):**
- Collision is circle–circle, player r=13 + pickup r=13 = **combined 26 px** (GDD §V2.4).
- Initial centre-distance is `720 − 700 = 20 px < 26` → the pickup is **already inside collect range at
  spawn**, so it collects on the **first collision check after seeding (~frame 2–3)** regardless of where
  the slow sweep has nudged the player's x (in 1–2 frames the sweep moves ≤10 px; `√(10² + 20²) = 22 < 26`
  — still in range).
- **Fallback robustness:** even if a frame is missed, the pickup drifts **down at 2.0 px/f** from y=700,
  so it stays within the player's y-band (≈700→726) for ~**13 frames**, and the sweep keeps the player
  near x=300 — the overlap window is wide. There is no way for it to slip past uncollected.

**Why apply AND expire are both observed:**
- Collect at ~frame 3 → **apply** Rapid (fire cooldown 12 f → 6 f). With the forced **60 f** duration the
  timer **expires at ~frame 63** → **revert** to 12 f cooldown. Both the applied state (~f3–63) and the
  post-expiry baseline (~f63–120) fall **well inside the 120-frame cap** → full
  **spawn → collect → apply → expire → revert** lifecycle verified headlessly (AC20).

**No interference:** the normal drip cadence is **720 f > 120 f**, so **no second drip fires** during
smoke — the seeded Rapid is the only drip bonus, keeping the lifecycle clean and attributable. (An
incidental 15 % enemy-drop from the seeded enemy is harmless — it stays under the cap of 3 — but the
**forced Rapid is the guaranteed lifecycle**; do not rely on the drop.) Keep the v1 fixed RNG seed for
determinism. *(Exact harness wiring is the programmer's; this confirms the seed geometry/timing is sound.)*

---

## V2.6 Traceability — every GDD §V2.5 default this spec resolves

| GDD §V2.5 default | This spec | Section |
|---|---|---|
| Drip cadence ≈ 12 s ±2 s | **CONFIRM** → `randint(600, 840) f`, first draw at run start | §V2.1 |
| Enemy-drop ≈ 15 % | **CONFIRM** → 0.15 on **bullet-kill** only (not ram-kill) | §V2.1 |
| Kind weights R30/F20/Ra20/S15/Sc15 | **CONFIRM** → cumulative `r∈[0,99]` ladder | §V2.1 |
| On-screen cap 3 | **CONFIRM** → total both paths; skip at cap, no banking | §V2.1 |
| Smoke seed reachable+expirable | **CONFIRM** → Rapid @(300,700), dur 60 f, collects ~f3, expires ~f63 | §V2.5 |
| Buff durations / effects (§V2.2) | **untouched** (GDD owns) | — |
| v1 pacing ramp (§3 above) | **untouched** (QA-passed; buffs ride on top) | §V2.3 |

Definition of done (per role): the programmer can implement bonus spawning entirely from §V2.1 (cadence,
drop %, weight ladder, cap) + the §V2.5 smoke seed, with the AC13 balance rationale in §V2.3 and the
lever order in §V2.4 — no spawn-economy guesswork remains.

---
---

