# v16 increment — boss-pool selection rule + extensibility + NOVA balance (appends to v7; v1 ramp + all prior economy UNCHANGED)

Owner: level-designer · Date: 2026-06-07 · Status: complete
Inputs: GDD `design/gdd/v16-second-boss.md` (§V16.2 pool/selection, §V16.4 NOVA stats, §V16.5 moveset/deadlier table, §V16.10 LD ask),
requirements `requirements/requirements/v16.md` (R99–R105, AC86–AC93), story `story/v16-second-boss.md` (NOVA copy),
this folder's `v7-bosses.md` (§V7.1 cadence + §V7.5 `BOSS_HP` fight-length model — the reused contract), `shared/handoffs.md` (119–122).
Implements the LD-owned §V16.10 levers: **own** the uniform-random pool-selection rule + one-entry extensibility, **CONFIRM**
the boss cadence is unchanged (75 s / +90 s), and **finalize/lock** NOVA's deadlier numbers + `NOVA_HP=120` against AC13/fight-length.

> **What I own (and only this):** the **pool-selection rule** (uniform i.i.d. 1/N per spawn event) + the **extensibility**
> statement, the **cadence-unchanged** confirm, and the **balance lock** on NOVA's numbers vs AC13/fight-length. The boss
> *entity / moveset / patterns / stats themselves* are **LOCKED by GDD §V16.x** — I confirm them, I do not re-design them.
> The **registry data-shape** is the Programmer's (§V16.2); I own the *rule* it must satisfy.
>
> **No existing number is re-tuned.** The **v1 §3 ramp**, the **v2/v5/v6 economy**, and the **Mothership's v7 values** are
> **bit-for-bit unchanged**. v16 inserts **one selection step** in front of the unchanged v7 loop and adds **NOVA** as a
> second pool entry. Same TIME breakpoint, same freeze/resume, same `t`-never-pauses guard as `v7-bosses.md` — both bosses
> run the identical loop; only *which* spec it reads differs.

---

## V16.1 The pool-selection rule + extensibility (R99/R100) — the rule I own

The encounter machinery (`v7-bosses.md` §V7.2) is unchanged. v16 adds **one selection step** at the V7.2 breakpoint, governed by:

- **Uniform i.i.d. per spawn event.** When the breakpoint fires (mark reached, no boss active), pick **one** boss spec from
  the pool **uniformly at random** — probability **1/N** for N entries (today **½ Mothership / ½ NOVA**). The draw is
  **independent per event**: consecutive bosses **may repeat** — no no-repeat / shuffle-bag / weighting this increment (R100;
  non-goal v16.4). Pure i.i.d. uniform.
- **Picked once, at ARRIVAL; fixes the whole fight.** The selection layer chooses **only the spec**; the
  ARRIVAL→ENTRANCE→ACTIVE→DEFEAT loop runs byte-for-byte the same regardless of pick. One boss at a time (v7 §27 stands).
- **Extensible — boss #3 = one entry (R99/AC86).** Append one more spec to the pool. **N is read from the pool length**, so
  selection (still uniform 1/N) and the v7 loop need **zero** edits. Nothing downstream may hard-code "two bosses."
- **Seedable / forceable (R100/R105).** The pick must be overridable so smoke + pytest pin a specific boss deterministically
  (the `SMOKE_BOSS_TYPE`-style hook, mirroring the v7 `SMOKE_BOSS_*`). Random in play, forceable in tests. *(Exact hook =
  Programmer + QA; the rule is: uniform-random in play, deterministic under override.)*

**Balance note — selection is AC13-orthogonal.** Both pool entries are fixed-cadence (V16.2) and bounded to the same
~12–24 s fight band (V16.4), so the run-length distribution is **independent of which boss the die rolls** — the pool adds
variety, not pacing drift.

---

## V16.2 Cadence UNCHANGED — CONFIRM 75 s / +90 s (R101 / AC88)

The boss-appearance cadence is **identical to v7** — selection rides on top of the existing breakpoint, it does **not**
move it.

| Lever | Value | LD verdict |
|---|---|---|
| Breakpoint **metric** | **TIME** (elapsed PLAY `t`) | **CONFIRM, unchanged** (`v7-bosses.md` §V7.1). Selection consumes the breakpoint; it adds no new timing. |
| **`BOSS_FIRST_MARK`** | **75 s** (f4500) | **CONFIRM, unchanged.** Marks 75 / 165 / 255 / … fire exactly as v7 regardless of which boss is drawn. |
| **`BOSS_INTERVAL`** | **90 s** (5400 f) | **CONFIRM, unchanged.** NOVA reuses the v7 entrance/rest/osc framing verbatim (GDD §V16.4), so cadence is literally the same marks. |

No new cadence number is introduced this increment. The §V7.1 reasoning (TIME-gate decouples cadence from score; first
mark lands mid-Squeeze before the ~120 s median death) carries over verbatim.

---

## V16.3 NOVA balance — FINALIZE / LOCK the deadlier numbers + HP (R104 / AC92)

I **confirm and lock** every Designer-set NOVA number from the balance side. All reference GDD §V16.8 consts; the
Mothership column is its untouched v7 value.

| Lever | NOVA (LOCKED) | Mothership (v7) | LD balance verdict |
|---|---|---|---|
| **`NOVA_HP`** | **120** | 120 | **CONFIRM.** Same "large" pool (R60). Deadlier via attacks, **not** HP-sponge. My fight-length lever (V16.4). |
| **`NOVA_R`** | **60** | 70 | **CONFIRM.** Still huge → "always hittable" (R60) trivially holds. Tighter target is **offset** by no-minion focus-fire (V16.4), so fight stays in band. |
| **`NOVA_RAM_DMG`** | **80** | 60 | **CONFIRM (deadlier, +33 %).** Still **< 100** player HP → survivable, not a one-shot; routes the normal §V2.7 damage step + i-frames/shield. |
| **`NOVA_KILL_SCORE`** | **1500** | 1000 | **CONFIRM (co-owned).** 1.5× the Mothership; flat via `scoring.award` → Score×2 doubles to 3000. AC13-orthogonal (points, time-gate — V16.4). |
| **`NOVA_BULLET_DMG`** | **25** | 15 (`EB_DMG`) | **CONFIRM — HEADLINE deadlier lever (+67 %).** 4 hits from full HP; i-frames gate dense patterns to one hit/window → survivable. |
| **`NOVA_BULLET_SPEED`** | **5.5** | 4.5 | **CONFIRM (faster → harder to dodge).** |
| **`NOVA_LANCE_SPEED`** | **6.0** | — | **CONFIRM** (step-3 LANCE, fastest). |
| **`NOVA_STEP_INTERVAL`** | **90 f** | 150 f | **CONFIRM (deadlier fire-rate, 1.67× more often).** Full cycle 360 f = 6 s (vs 10 s). |
| **Pattern densities** | RAKE 5 · BURST 24 · LANCE 4 · ARC 9 | fan 3 · ring 12 | **CONFIRM.** 42 bullets/cycle = ~7/s (vs 1.5/s) → ~4.7× denser; ring precesses `+9°/step` (no repeat safe-gap). |

**Deadlier is concrete (AC92), every axis worse, none cosmetic:** dmg 25>15, ram 80>60, speed 5.5–6.0>4.5, cadence
90<150 f, density ~7/s>1.5/s, 3-of-4 patterns aimed. The one-line check is per-hit damage **25 > 15**; the full evidence
table is GDD §V16.5.

---

## V16.4 AC13 / fight-length reconciliation — NOVA holds the 1–3 min band (LOCK)

NOVA reuses the v7 fight-length model (`v7-bosses.md` §V7.5). It holds for the same reasons, with two NOVA-specific notes:

1. **Same HP, same bounded fight.** `NOVA_HP = 120 = BOSS_HP`, so the §V7.5 kill-time math is unchanged: perfectly-aimed
   ~24 s, realistic dodge-and-fire ~18–22 s, Rapid ~12 s → bounded **~12–24 s**, same band as the Mothership.
2. **Tighter `r=60` is offset by no-minion focus-fire.** A slightly smaller target costs a few stray shots, but NOVA spawns
   **no minions** (R103) competing for the player's fire/attention — so the player lands a **higher fraction** of shots on
   the boss than in the Mothership fight. The two roughly cancel → fight length stays in the band, not longer.
3. **Deadlier attacks bound run length on the SHORT side, never the long side.** Higher damage/density makes the player
   **more** likely to die *during* the fight — that ends a run sooner, which AC13's lengthening watch doesn't care about; it
   never extends a run. R104's "still winnable" caveat (GDD §V16.5: 1.5 s between steps, each pattern has a defined safe
   response, whole screen is dodge room) keeps it fair.
4. **Cadence + reward are AC13-orthogonal** (time-gate, points-only — §V7.1/§V7.4): the +1500 reward and the boss choice
   feed back into **nothing** about *when* the next boss fires or how long the run lasts.

**Net: AC13 holds for the median run, unchanged from v7.** No ramp/economy re-tune. The parked *"expert pure-dodging can
exceed 3 min"* caveat is **unchanged in scope** — NOVA replaces ~12–24 s of storm with an equally-bounded boss arena, same
as the Mothership, so it adds no new lengthening pressure beyond the existing v7 entrance window.

---

## V16.5 Tuning levers — if a playtest shows NOVA unwinnable (deadliest-first) or AC13 drifts

NOVA is **balanced to be intense-but-winnable**; if a human playtest disproves that, apply one lever at a time, re-test.

**NOVA feels UNFAIR / unwinnable (R104 caveat fails — too deadly to dodge):** — order per GDD §V16.5
1. **Widen `NOVA_STEP_INTERVAL` 90 → 110 f** — more breathing room between patterns. Biggest readability win; keeps every
   number's *relative* deadliness vs the Mothership intact (still < 150 f).
2. **Drop `NOVA_RING_COUNT` 24 → 18** (step-2 BURST) — wider safe-gaps in the dense ring. Still > the Mothership's 12.
3. **Lower `NOVA_BULLET_SPEED` 5.5 → 5.0** (and `NOVA_LANCE_SPEED` 6.0 → 5.5) — easier to read/dodge; still > 4.5.
4. Only if still unfair: trim `NOVA_RAM_DMG` 80 → 70 (still > 60, still deadlier). **Do NOT drop `NOVA_BULLET_DMG` below 16**
   — 25 > 15 is the headline AC92 lever; lose it and "deadlier" degrades to "different."

**Runs drift too LONG with NOVA active (> ~3 min):** lower `NOVA_HP` 120 → 90 (shorter fight; keep ≥ ~60 for the big-HP
fantasy) — the same primary lever as the Mothership's `BOSS_HP` (§V7.6). Never *raise* the entrance/first-step delays.

**Runs too SHORT (players die in the NOVA fight):** the §V16.5 "unwinnable" levers above (widen interval, thin the ring)
also fix this — they reduce in-fight lethality. Raising `BOSS_FIRST_MARK` (§V7.6) gives weaker players more warm-up.

Do **not** change the breakpoint *metric* (TIME), the selection *rule* (uniform 1/N), or the moveset *structure* here —
those are GDD §V16.x / this spec's §V16.1. The balance knobs I own are NOVA's per-hit/density/HP numbers and the marks.

---

## V16.6 Smoke + test confirmation (R105 / AC93) — no cadence/economy interference

The v16 selection + NOVA balance leave the v7 smoke timeline intact:

- **The TIME breakpoint never fires in smoke** (`BOSS_FIRST_MARK = f4500 ≫ 120 f`), exactly as v7 §V7.7. The only boss is
  the **forced seed** (`SMOKE_BOSS_TYPE="NOVA"`, §V16.1) — the uniform draw is bypassed deterministically, like the v7
  forced seed. Selection randomness is therefore **never** exercised by the natural gate in-budget; it is unit-tested via
  the seedable hook (R100/AC87).
- **The freeze/resume contract is NOVA-unchanged** (`v7-bosses.md` §V7.2): NOVA spawns **no minions** (R103), so during its
  fight the v1/v5/v6 spawners emit **nothing at all** — a *stricter* freeze than the Mothership's (whose minions appear). No
  drip fires (cadence > 120 f). Zero-ship is observable headlessly (AC91).
- **NOVA's higher numbers don't touch cadence/economy** — they're per-hit/ram/density values on the existing
  enemy-bullet × player path; the breakpoint, freeze, and `t`-never-pauses guard are byte-for-byte v7.

pytest grows (Programmer/QA own asserts) with: pool + one-entry extensibility (R99/AC86), uniform-random selection
(R100/AC87), NOVA no-ship (R103/AC91), deadlier values `NOVA_BULLET_DMG=25>15` etc. (R104/AC92) — Mothership parity
(AC39–AC52) and AC1–AC85 untouched (AC93).

---

## V16.7 Traceability — every §V16.10 LD lever / AC this section resolves

| Lever / AC | This spec | Section |
|---|---|---|
| R99 extensible pool — boss #3 = one entry, N from pool length | **OWN** → uniform 1/N reads N from length; zero loop/selection edits | §V16.1 |
| R100 uniform i.i.d. pick per spawn (1/N, repeats, seedable) | **OWN** → the selection rule + forceable-in-tests requirement | §V16.1 |
| R101 cadence + framing unchanged | **CONFIRM** → TIME 75 s / +90 s unchanged; selection rides the existing breakpoint | §V16.2 |
| R104 deadlier numbers (dmg/ram/cadence/density) | **FINALIZE/LOCK** → 25>15, 80>60, 90<150 f, ~4.7× density — all confirmed vs balance | §V16.3 |
| `NOVA_HP=120` vs AC13/fight-length | **LOCK** → bounded ~12–24 s; tighter r offset by no-minion focus-fire | §V16.3, §V16.4 |
| `NOVA_KILL_SCORE=1500` (co-owned reward) | **CONFIRM** → flat via `scoring.award`; Score×2→3000; AC13-orthogonal | §V16.3, §V16.4 |
| AC13 runs ~1–3 min with NOVA | **HELD (median)** → same HP/band as Mothership; deadlier bounds short side only | §V16.4 |
| AC88 cadence unchanged | **CONFIRM** → 75 s / +90 s regardless of pick | §V16.2 |
| AC92 deadlier concrete + winnable | **LOCK** → every axis > Mothership; winnable per R104 caveat; levers if not | §V16.3, §V16.5 |
| AC86/AC87/AC91/AC93 smoke + suite | **CONFIRM** → forced seed, stricter freeze, no cadence/economy change | §V16.6 |
| NOVA entity / moveset / patterns / silhouette / copy | **untouched** (GDD §V16.x / art_spec / story own) | — |
| v1 §3 ramp + v2/v5/v6 economy + Mothership v7 values | **untouched** (QA-passed; v16 only inserts a selection step + a pool entry) | §V16.1, §V16.4 |

Definition of done (per role): the Programmer can implement the **selection rule** (§V16.1 — uniform 1/N i.i.d., N from
pool length, seedable) on top of the **unchanged v7 cadence/freeze** (§V16.2), reading NOVA's **locked balance numbers**
(§V16.3) — with AC13/fight-length reconciled (§V16.4), the tuning-lever order on hand (§V16.5), and smoke coexistence
confirmed (§V16.6). No pool/selection/balance guesswork remains.

---
---
</content>
</invoke>
