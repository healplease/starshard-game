# v6 increment — Bomb-charge pickup spawn economy + post-bomb lull (appends to v1+v2+v5; v1 ramp + v2 economy UNCHANGED)

Owner: level-designer · Date: 2026-06-05 · Status: complete
Inputs: `workspace/design/gdd.md` (§V6.6 pickup = 6th v2 diamond, §V6.7 R55 lull intent, §V6.8 AC13 protection,
§V6.10 smoke seed, §V6.11 consts), `workspace/story/story.md` v6 (§V6.1 name `BOMB`/glyph `B`, §V6.3 popup),
`workspace/requirements/requirements.md` v6 (R51 pickup, R55 COULD lull, AC13/AC34/AC37), v2 §V2.1 economy +
v5 §V5.1 band weights above (both QA-passed), `workspace/shared/backlog.md`, `workspace/shared/handoffs.md`.
Implements: **R51 spawn weight/scarcity** (the bomb pickup's slot in the v2 kind table, set as the **rarest** kind)
+ the **R55 lull** decision, both tuned to protect **AC13** (runs ~1–3 min) and confirms the §V6.10 smoke bomb
activation still runs headlessly (**AC37**).

> **What I own (and only this):** the bomb pickup's **spawn weight** (its slice of the v2 kind-selection table) and
> the **R55 post-bomb lull** value. The pickup's *entity/effect* (6th `BonusKind.BOMB`, +1 charge clamped to cap 4,
> instant/no-pill, collect-at-full = WASTED, sole refill) is LOCKED by GDD §V6.6; its *name/glyph* (`BOMB`/`B`) by
> story §V6.1; its *color* (`#B464F5`) by art_spec §V6.1. I do **not** touch any of those.
>
> **The v2 spawn economy is UNCHANGED in volume.** Drip cadence (`randint(600,840) f`), enemy-drop chance (**15 %**
> on bullet-kills), and the on-screen **cap (3)** are all **CONFIRM** — bit-for-bit v2. The bomb pickup adds **no new
> spawn path and no extra pickup volume**: it **takes a slice of the existing kind-selection weight table**, and the
> other five kinds are **renormalized** so the table still sums to 100. This is exactly how v5 rebalanced enemy
> *kind* without touching enemy *count* — here the bomb changes *which* pickup a spawn becomes, never *how many*
> spawn. The **v1 §3 ramp and the v2 §V2.1 economy stay completely UNCHANGED** (AC13 bar). Same `t = frames/60` clock.

---

## V6.1 The bomb-pickup spawn weight (the core deliverable) — rarest kind, folded into the v2 table

The bomb pickup is the **6th kind** in the single v2 kind-selection table (§V2.1), set as the **rarest** kind at
**`BOMB = 6`** (a single-digit weight, inside the GDD §V6.6 ~5–8 % recommendation, and **clearly below** the current
lowest v2 weights — Shield/Score at 15). The 6 points come **out of** the existing table (Shield 15→12, Score×2
15→12); the other three kinds are untouched. The table still sums to **100**, so **total pickup volume is identical
to v2** — only the kind-mix shifts.

| Kind | v2 weight | **v6 weight** | Δ | Letter (story.md) |
|---|---:|---:|---:|---|
| **Repair** | 30 | **30** | — | `+` |
| **Fan**    | 20 | **20** | — | `F` |
| **Rapid**  | 20 | **20** | — | `R` |
| **Shield** | 15 | **12** | −3 | `S` |
| **Score×2**| 15 | **12** | −3 | `2` |
| **BOMB**   | — | **6** | **NEW** | `B` |
| **Sum** | 100 | **100** | 0 | |

### Why these source kinds (the −6 is AC13-aware, not arbitrary) — per the §V2.3 buff analysis
- **Repair (30) — untouched.** It's the low-tail *compressor* (§V2.3): it clamps at full HP, so it only helps
  players who are already taking damage → it lifts weak/unlucky runs *into* the band without extending experts.
  Cutting it would shorten the low tail (wrong direction), so I protect it.
- **Fan / Rapid (20 each) — untouched.** Self-paying offense (collecting one diverts from optimal dodging); their
  net survival contribution is small and roughly neutral. No reason to disturb them.
- **Shield (15 → 12), −3.** Shield is the **only real high-tail extender** (pure invuln, §V2.3) and is literally the
  **#1 "runs too long" lever** in §V2.4. Trimming it is the AC13-*helpful* direction, and it offsets the bomb's own
  mild survival benefit — a bomb-for-shield swap trades one survival aid for another, so the net effect on the high
  tail is ≈ a wash.
- **Score×2 (15 → 12), −3.** Survival-neutral (§V2.3: zero run-length effect), so giving up 3 of its points costs
  the balance nothing — the cleanest place to find the remaining points.

### Programmer-ready kind selection — the v2 §V2.1 ladder, extended to 6 kinds
Roll `r = randint(0, 99)` once per spawn (drip **or** enemy-drop — the **same one table** for both paths, exactly
as v2 §V2.1) and walk the cumulative ladder. Pure function of `r`; no per-kind banking, no new state.

| `r` range | Kind | Letter |
|---|---|---|
| `0–29`  | **Repair**  | `+` |
| `30–49` | **Fan**     | `F` |
| `50–69` | **Rapid**   | `R` |
| `70–81` | **Shield**  | `S` |
| `82–93` | **Score×2** | `2` |
| `94–99` | **BOMB**    | `B` |

This is the v2 ladder with two thresholds nudged (Shield `70–84`→`70–81`, Score `85–99`→`82–93`) and one 6-wide
band (`94–99`) appended for BOMB. **Both spawn paths share it** — no per-path weighting, no separate bomb table.

### Eligible for BOTH paths (drip + enemy-drop) — decision
The bomb pickup reaches the player through the **same drip + enemy-drop mechanisms** as every other kind (GDD §V6.6
left this to me). I keep it on **both** paths via the single shared table above — **not** drip-only — because:
1. **It's the cleanest "fold,"** honoring "no new spawn path / no extra volume": one shared 6-kind table for both
   paths is bit-for-bit the v2 design (§V2.1). Drip-only would force a *second* weight table (the 5 non-bomb kinds
   renormalized for the drop path) — more code, a deviation from "one table, both paths," for no balance need.
2. **6 % is already scarce enough** across both paths (see §V6.2) — drip-only would push refills below the intended
   feel for no AC13 gain.
3. **Tying refills to offense reads well:** enemy-drops fire only on **bullet-kills** (§V2.1), so the occasional
   bomb refill rewards *clearing threats* — thematically apt for a panic charge, and on the skilled-play path.

The §V2.1 **ram-kill exclusion still holds** (ram-kills don't drop — already paid in HP); the bomb is no exception.

---

## V6.2 Expected bomb economy per run (what 6 % actually produces) — scarce by design

Building on the §V2.2 model (~**5–7 bonuses collected** over a typical ~2 min run, both paths combined):

- **At 6 % weight → ~0.3–0.45 bomb pickups *collected* per ~2 min run.** In plain terms a refill lands roughly
  **once every ~2–3 runs**. A skilled ~3 min run sees ~**0.5–0.6** — still typically **under one** refill.
- **So most runs the player lives on the starting 2 charges** and rarely refills; **reaching cap 4 is uncommon**
  (it needs *two* collects from a start of 2) — which is exactly why the §V6.6 collect-at-full = WASTED rule almost
  never triggers. This matches the GDD §V6.8 intent: *"an expert sees at most a handful of flushes,"* *"hitting full
  cap is uncommon."*
- **The bomb is a scarce treasure, not a regular drop** (GDD §V6.6) — its rarity is the AC13 guarantee: the panic
  button can't become a sustained crutch, because the supply barely keeps up with use.

---

## V6.3 AC13 — why the bomb economy keeps runs in the 1–3 min band

The bomb is a survival tool, so its supply *could* lengthen runs. It does not meaningfully, for four reasons (this
extends GDD §V6.8 with the economy specifics):

1. **No added pickup volume.** The bomb **replaces** weight in the existing table; cadence/drop/cap are untouched
   (§V6.1). The number of pickups per run is **identical to v2** — the QA-passed economy's volume is preserved
   exactly. Only *which kind* a given spawn becomes changes.
2. **Buff supply slightly *decreases*, which is AC13-conservative.** The 6 % given to BOMB is taken from Shield (the
   high-tail extender) and Score×2 (survival-neutral). So per run the player now collects marginally **fewer**
   Shields — the one buff that extended expert runs — and the lost Score×2 share costs no balance. The mild survival
   value the bomb *adds* is roughly offset by the Shield share it *removes*: a near-wash on the high tail.
3. **Refills are rare (§V6.2).** ~0.3–0.6 bomb pickups/run means the panic button is fed about as fast as it's
   spent — it shortens *individual dangerous moments* but never accumulates into a standing survival buffer.
4. **No farming incentive.** Flush score = NONE (GDD §V6.3), so there's no reason to court a swarm to bomb it —
   runs aren't artificially prolonged for points; and the ramp **resumes** after a flush (R49), so the field
   repopulates on the unchanged v1 curve.

**Conclusion: the QA-passed v1 §3 ramp AND the v2 §V2.1 economy (cadence/drop/cap) stay completely UNCHANGED** — v6
only re-slices the kind table (volume-neutral) and the change is AC13-conservative on net. If a human playtest shows
drift, the §V6.4 lever (then §V2.4 / v1 §8) brings it back without destabilizing the green curve.

---

## V6.4 Post-bomb spawn lull (R55, COULD) — DECISION: `BOMB_SPAWN_LULL = 0` (no explicit lull)

GDD §V6.7 recommends ~30 f (~0.5 s) of paused spawning after a flush, **or 0**, and flags it as the **one lever in
v6 that could *lengthen* a run** (AC13-bound). **I set it to 0** — no explicit lull. Rationale:

- **The payoff already exists for free.** A flush instantly empties the screen; under R49 the ramp then refills at
  its **normal cadence** — which at the storm floor is ~22 f to the next asteroid and ~60–76 f to the next enemy
  spawn, *plus* that enemy's entry time (descend to `y ≥ 120`, GDD §6.4). So the freshly-cleared field already stays
  visibly calm for **~0.5–1.5 s naturally**, just from spawn cadence + entry. The cleared screen + the 18-f flash
  *are* the impact beat; an explicit lull would be largely **redundant**.
- **0 is the strictly AC13-safest choice.** The lull is the only v6 mechanic that pauses the ramp; at 0 the bomb can
  only ever *shorten* dangerous moments (by clearing threats), **never** suppress the spawn curve. v6 therefore adds
  **zero** run-lengthening from spawn suppression — the cleanest possible defense of the QA-passed band.
- **Simpler to build and verify.** No new spawn-suppression code path for the Programmer, no lull window for QA to
  reason about in the smoke run.

GDD §V6.7 explicitly says *"v6 passes without it,"* so 0 is fully spec-compliant. **It remains a tuning lever** (see
§V6.5): if a human playtest finds the flush feels flat, set `BOMB_SPAWN_LULL = 30` — but only after confirming the
extra ~0.5 s × a-handful-of-flushes (~1–2 s/run) still sits inside AC13 (it almost certainly does; it's bounded).

---

## V6.5 Tuning levers (for QA → programmer, if AC13 drifts WITH the bomb economy active)

Apply one at a time, re-test. **These v6 levers come first** (they retune the bomb economy without touching the
QA-passed core ramp or the v2 buff economy); only if insufficient, fall back to §V2.4 / v1 §8.

**Runs now too LONG (> ~3 min / experts never die):**
1. **Lower the BOMB weight `6 → 4`** (give the 2 points back to Score×2 → 14, survival-neutral). Fewer refills =
   fewer flushes = less escape value. Biggest single bomb-economy lever on the high tail. *(Keep BOMB the rarest
   kind — don't raise it above Shield's 12.)*
2. **Keep `BOMB_SPAWN_LULL = 0`** (it already is) — never *raise* the lull if runs are long.
3. **Make BOMB drip-only** (drop it from the enemy-drop roll) — trims the secondary supply for players who clear
   lots of enemies; requires the second (5-kind) table for the drop path noted in §V6.1.
4. Only if still long: apply §V2.4 "too LONG" levers (Shield weight 12→10) then v1 §8 (enemy_fire floor 55→50).

**Runs now too SHORT (< ~1 min / the bomb feels pointless / never refills):**
1. **Raise the BOMB weight `6 → 8`** (take the 2 from Score×2 → 10) — more frequent refills. *(Stays inside the
   §V6.6 5–8 % band and still ≤ Shield's 12, so it remains the rarest kind.)*
2. **Set `BOMB_SPAWN_LULL = 20–30`** — a short post-flush breather makes each bomb worth more (bounded ~0.5 s,
   §V6.4; re-confirm AC13 after).

Do **not** change the bomb *effect*, *cap*, or *collect-at-full rule* here — those are GDD §V6.6's to own. Do **not**
change drip cadence / drop % / on-screen cap for a bomb-scarcity problem — re-slice the kind weight first.

---

## V6.6 Smoke-seed re-confirmation (R54 / AC37) — the bomb activates headlessly, weight-independent

GDD §V6.10 has the Programmer script an **X key-down at ~frame 20** so one bomb flush clears the seeded enemy +
remaining asteroids + the 3 red split children (charge 2→1, flash f20→~f38). My job is only to confirm the **kind
weight does not interfere**. It does not — and by construction it *cannot*:

- **The smoke activation uses the *starting* 2 charges + a scripted X press — not a collected pickup.** So the
  flush fires regardless of any pickup spawn. My weight only affects which *kind* a pickup roll becomes; it has
  **zero** bearing on the seeded activation.
- **No pickup roll even occurs in the smoke window that could matter.** The drip cadence is `randint(600,840) f`
  **> 120 f**, so **no drip fires** in the 120-frame run (same as v2 §V2.5 / v5 §V5.5). An incidental 15 % enemy-drop
  from a smoke bullet-kill *might* roll the table, but (a) it's not the activation source, and (b) at BOMB 6 % it's
  unlikely and harmless under the cap of 3. The **scripted X press is the guaranteed lifecycle**, not any pickup.
- **Both prior smoke seeds are untouched:** the v2 forced-Rapid (§V2.5) and the v5 green-pellet split (§V5.5) both
  bypass the weight roll (one force-spawns a specific kind, the other is seeded directly), so re-slicing the table
  changes neither.

**Confirmed:** re-slicing the kind table for BOMB leaves the §V6.10 smoke bomb activation fully intact — the
scripted X @~f20 still flushes the live hostiles (incl. the v5 split children → AC32) and decrements 2→1 (AC30)
headlessly, and `--smoke-test` still exits 0 after exactly 120 frames. (Exact seed wiring is the Programmer's — this
only confirms the weighting leaves the smoke activation intact.)

---

## V6.7 Traceability — every R51/R55/AC this section resolves

| Lever / AC | This spec | Section |
|---|---|---|
| R51 bomb-pickup spawn weight (rarest kind) | **SET** → `BOMB = 6` (5–8 % band; < Shield/Score 15), in the shared table | §V6.1 |
| R51 folded into v2 economy, no new path/volume | **CONFIRM** → re-slice of the one kind table (Shield 15→12, Score 15→12); cadence/drop/cap untouched | §V6.1, §V6.3 |
| R51 reaches player via drip + enemy-drop | **DECIDE** → both paths, single shared 6-kind ladder (not drip-only) | §V6.1 |
| R55 post-bomb lull (COULD) | **DECIDE** → `BOMB_SPAWN_LULL = 0` (no lull; flush + cadence already pay off) | §V6.4 |
| AC13 runs ~1–3 min | **PROTECTED** → volume-neutral re-slice; buff supply slightly down; refills rare; lull 0 | §V6.2, §V6.3 |
| AC37 smoke bomb activation headless | **CONFIRM** → activation uses starting charges + scripted X, weight-independent | §V6.6 |
| Bomb effect / cap / collect-at-full / name / glyph / color | **untouched** (GDD §V6.6 / story §V6.1 / art_spec §V6.1 own) | — |
| Drip cadence / enemy-drop % / on-screen cap (volume) | **CONFIRM** — bit-for-bit v2 §V2.1 | §V6.1 |
| v1 pacing ramp (§3) + v2 economy (§V2.1) + v5 mix (§V5.1) | **untouched** (QA-passed; v6 rides on top, volume-neutral) | §V6.3 |

Definition of done (per role): the Programmer can set the bomb pickup's spawn weight entirely from the §V6.1 table +
6-kind ladder (one shared table, both paths) and the §V6.4 `BOMB_SPAWN_LULL = 0` decision, with the AC13 rationale in
§V6.2–§V6.3, the smoke re-confirmation in §V6.6, and the lever order in §V6.5 — no bomb-economy guesswork remains.
