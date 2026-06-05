# v7 increment — Boss breakpoint cadence + spawn-freeze/resume + fight economy (appends to v1+v2+v5+v6; v1 ramp + all prior economy UNCHANGED)

Owner: level-designer · Date: 2026-06-05 · Status: complete
Inputs: GDD `design/gdd/v7-bosses.md` (§V7.2 breakpoint+AC13, §V7.3 run clock, §V7.4 `BOSS_HP`, §V7.6 freeze/drop/score
economy, §V7.9 `BOSS_KILL_SCORE`, §V7.15 smoke seed, §V7.16 consts, §V7.18 Level-designer asks), requirements
`requirements/requirements/v7.md` (§26 LD rows, R58/R62/R67, AC41/AC45), this folder's v1 §3 ramp + §5 milestone bands +
§8 levers, v2 §V2.1 economy + §V2.5 smoke, v5 §V5.5 smoke, v6 §V6.6 smoke (all QA-passed), `shared/handoffs.md` (entry 49).
Implements: **re-confirms** the Designer's locked boss-pacing values against **AC13** (runs ~1–3 min) and **owns** the
boss-fight **spawn economy** (drip freeze / minion-drop suppression / minion-score-on) + the **+1000 reward** balance, and
confirms the §V7.15 smoke boss seed (@~f40) **coexists** with the v5 split (f16) + v6 bomb (f20) seeds.

> **What I own (and only this):** the boss **breakpoint cadence** as it folds into the run/ramp, the **spawn-freeze +
> resume** rules (the exact gating semantics), the boss-fight **economy** (bonus-drip freeze, minion pickup-drops,
> minion score), and the **+1000 reward** balance — all tuned/confirmed against **AC13**. Every *effect/rule/geometry*
> (the boss entity, HP, moveset, flush/flash reuse, smoke wiring) is **LOCKED by GDD §V7.x**; I do **not** touch those.
>
> **No existing number is re-tuned.** The **v1 §3 ramp** and the **v2/v5/v6 spawn economy** (drip cadence
> `randint(600,840) f`, enemy-drop 15 %, kind weights, caps, the v5 kind mix, the v6 `BOMB=6` slice) are **bit-for-bit
> unchanged in normal play.** v7 only adds a **boss sub-state inside PLAY** that **pauses-and-resumes** those existing
> spawners (a gating condition, not a re-balance) and adds the **+1000** defeat reward + the boss-minion rules. Same
> `t = frames/60` clock as v1 §3 — and (decisive for AC13) **`t` never pauses during the fight** (GDD §V7.3).

---

## V7.1 The breakpoint cadence — CONFIRM the Designer's locked values, folded onto the run clock

The Designer locked the #1-decision (GDD §V7.2). From the pacing side I **CONFIRM** it — it reads cleanly off this
folder's existing run model and needs no ramp change.

| Lever (GDD §V7.2) | Value | LD verdict |
|---|---|---|
| Breakpoint **metric** | **TIME** (elapsed PLAY `t`), fixed interval | **CONFIRM.** A point gate would couple boss cadence to score (highly run-variable per v1 §7), firing 2–3× sooner for a farmer and never for a dodger; TIME maps 1:1 onto my §5 run-length bands. |
| **`BOSS_FIRST_MARK`** | **75 s** (frame 4500) | **CONFIRM.** Lands **mid-Squeeze** (§5: 60–90 s), **before** the median death (~110–130 s) and well before a skilled run ends → the median *and* skilled player reliably meet ≥1 boss. A sub-75 s death misses it, but that run was short by definition. |
| **`BOSS_INTERVAL`** | **90 s** (5400 f) → marks 75 / 165 / 255 / … | **CONFIRM.** Since the median run ends ~120 s, boss 2 (@165 s) is a skilled-run reward and boss 3 (@255 s) a rare-expert sight — the cadence gates later bosses behind survival skill *for free* (the deliberate late/expert event). |

**The AC13 reconciliation is RE-CONFIRMED, option (a)+(b).** Lowering the gate to 75 s makes the headline feature
reliably seen (option **a**); the periodic repeat then naturally *becomes* the late/expert event for bosses 2+ (option
**b**). **No AC13 re-tune (c) is needed** — see V7.5 for why the interlude doesn't blow the 3-min ceiling.

---

## V7.2 Spawn-freeze + resume — the gating contract (R58 / AC41), programmer-ready

The encounter manager runs a boss sub-state **ARRIVAL → ENTRANCE → ACTIVE → DEFEAT** inside PLAY (GDD §V7.3). While a
boss is active (ARRIVAL → DEFEAT inclusive) the normal spawners are **frozen**; on DEFEAT they **resume immediately**.

### Freeze (while `boss_active`) — gate the *fire-a-spawn* step, **skip-no-bank**
Gate each spawner's "actually emit" step on `not boss_active`. **Critically: the spawn-interval countdowns keep
free-running and just skip the emit — they do NOT bank a backlog** (identical to the existing at-cap rule, v1 §6 / §3
"reset the countdown either way, no banking"). This is the one freeze detail with an AC13 edge, so it is **specified,
not left open:**

| Spawner | Normal driver | While `boss_active` |
|---|---|---|
| **v1 asteroids** | `asteroid_spawn_interval(t)` (v1 §3) | timer free-runs; **emit skipped** (AC41) |
| **v5 enemies** | `enemy_spawn_interval(t)` + `enemy_cap(t)` + `choose_enemy_kind(t)` (v1 §3 / v5 §V5.1) | timer free-runs; **emit skipped** (AC41) |
| **v2 bonus drip** | `bonus_drip_timer` `randint(600,840) f` (v2 §V2.1) | timer free-runs; **emit skipped** (drip frozen — V7.3) |

- **Why skip-no-bank, not pause-and-dump:** if the countdowns were *paused* and then released at DEFEAT, a fight that
  spans several intervals would release a **backlog dump** — a wall of asteroids/enemies materialising on the resume
  frame, a sharp unfair difficulty spike right when the storm returns. Skip-no-bank means the **first** post-defeat
  spawn is at most one normal interval away — the storm resumes at its *normal* density, never a flood. (Either
  timer-implementation is fine **as long as no backlog accumulates**; skip-no-bank is the simplest that guarantees it.)
- **The only new hostiles during the fight are the boss's moveset minions** (V7.3 / GDD §V7.11) — they come from the
  boss, not these spawners, so they appear despite the freeze.

### Resume (on DEFEAT) — immediate, **no post-boss lull**
- All three spawners resume **on the DEFEAT frame**, under the **usual ramp at the current `t`** (AC41/AC45). Because
  `t` advanced through the whole fight (GDD §V7.3), the resumed storm is escalated to wherever the clock now is — **no
  difficulty discount**.
- **`BOSS_RESUME_LULL = 0` — there is no post-boss breather** (unlike v6's optional `BOMB_SPAWN_LULL`, also 0 — v6
  §V6.4). The storm comes straight back. Setting it to 0 keeps v7 strictly AC13-neutral on the lengthening side: the
  fight never hands out free calm time on either end beyond the brief entrance (V7.5). It remains a **lever** (V7.6) if
  a playtest finds the resume too abrupt.
- **Surviving minions persist** (GDD §V7.9): the resumed normal loop deals with any stragglers — a brief "mop up" beat.

---

## V7.3 The boss-fight economy — drip FROZEN, minion-drops SUPPRESSED, minion-score ON (R58/R67 §26 LD calls)

These three are explicitly mine to set (§26). I **CONFIRM** the Designer's recommended values; the rationale is
AC13-conservative throughout.

| Economy lever (§26) | LD decision | Why (AC13 + feel) |
|---|---|---|
| **Bonus drip during the fight** | **FROZEN** (V7.2) | A clean, self-contained arena (BA default-rec, R58). No *new* pickups appear mid-fight, so the fight injects **zero** survival/charge economy — it cannot become a refill window that lengthens the run. (Pickups already on the field at ARRIVAL **survive** the flush — GDD §V7.5 — and keep drifting/collectable; only *new* drip is paused.) |
| **Minion pickup-drops** | **SUPPRESSED** | Boss minions killed by player fire do **NOT** roll the v2 15 %-bullet-kill drop while `boss_active`. Consistent with the frozen drip (no new economy mid-fight) and it **prevents the fight becoming a bomb/buff farm** — a player can't grind boss-spawned minions for charges/Repairs. AC13-conservative: no economy injection. |
| **Minion SCORE** | **ON** (normal v5 award) | Minions **are** ordinary v5 enemies (R67), so a kill pays the normal v5 per-kind score through the usual `scoring.award` path (GDD §V5.2; the v7 GDD §V7.6 restates these as REGULAR 50 / HEAVY 80 / SCOUT 60). Score is intrinsic to the kill (always on); only the *economy* (pickups) freezes. |

**Why minion-score-on is AC13-orthogonal (the key point only the LD makes):** the breakpoint is **TIME-based, not
points** (V7.1). So minion score — and the +1000 reward (V7.4) — feed back into **nothing** about *when* the next boss
fires; they are pure reward, with zero effect on cadence or run length. And it isn't farmable: the boss spawns a
**bounded** number of minions (cap 14) on a **fixed** cadence (GDD §V7.11), so there is no infinite trickle to grind.
Score on / economy off is the clean split: the fight pays the **score-chase fantasy** (R11) without feeding the
**survival economy** that AC13 watches.

---

## V7.4 The +1000 defeat reward (R62) — CONFIRM `BOSS_KILL_SCORE = 1000`

I co-own this value (§26). **CONFIRM 1000**, flat, awarded through the normal `scoring.award` path.

- **"Big" beyond doubt:** **12.5×** the biggest normal kill (HEAVY 80), **20×** a REGULAR (50), **50×** a small
  asteroid (10) — and against the v1 §7 economy (~1.5k–2.5k pts in a typical 2-min run) it is **~40–65 % of an entire
  run's score in one defeat**. A run-defining payoff for surviving the fight (R62/AC45).
- **Score×2 (F31) doubles it → 2000** if active, because it flows through `award` like every point (no special case;
  `feature_inventory.md §F11`). Consistent and intended — surviving a boss *with* Score×2 banked is a deliberate
  high-roll.
- **AC13-orthogonal** (same argument as V7.3): the reward is **points, not HP/charge/survival**, and the breakpoint is
  time-based — so a big reward neither lengthens the run nor accelerates the next boss. It's a pure score beat.

---

## V7.5 AC13 — why the boss interlude keeps runs in the 1–3 min band (`BOSS_HP=120` is my fight-length lever)

The boss *fight* takes wall-clock time, so it *could* push runs past the 3-min ceiling. It does not meaningfully, for
four reasons — this is the pacing-side companion to GDD §V7.2.3:

1. **The run clock never pauses (the decisive guard).** `t` advances through ARRIVAL→DEFEAT (GDD §V7.3), so the ramp,
   the survival-tick, and the next mark all keep moving. The fight **replaces** ~12–24 s of storm with ~12–24 s of an
   **equally-dangerous boss arena** (bullet-hell 12-red ring + up to 14 minions + a 60-dmg ram), **not** a safe
   breather. When the boss dies the storm resumes already escalated to the current `t` — no difficulty discount.
2. **The economy is frozen, not gifted (V7.3).** No drip, no minion drops during the fight → the player banks **no new
   HP/charges** while fighting. The arena removes threats (the free arrival flush) but also removes the survival
   economy — the two roughly offset. The reward is points only (V7.4).
3. **The only "free" time is the brief entrance.** ENTRANCE (~4 s glide, GDD §V7.7) + the 60-f first-step delay (GDD
   §V7.8) is a ~5 s window with no boss attacks — genuinely calmer than the storm it replaces. This is the one mild
   run-lengthening pressure, and it is **bounded (~5 s) and one-shot for the median run** (only boss 1 @75 s fires
   before the ~120 s median death; bosses 2+ are expert-tail). ~5 s on a 1–3 min run is well inside the **small,
   bounded shift** that v2/v5/v6 each also introduced and that the §5 model absorbs.
4. **`BOSS_HP = 120` bounds the fight (CONFIRM).** At baseline fire (12-f cd, 5 shots/s) a perfectly-aimed single beam
   kills in 120/5 = 24 s; realistic dodging-and-firing ~18–22 s; Rapid (10/s) ~12 s; Fan grazes a centred boss
   ~15–20 s. So the fight is a bounded **~12–24 s** — long enough to read the moveset ~1.5–2.5× (10-s cycle), short
   enough to stay near the band. **`BOSS_HP` is my primary AC13 lever** (V7.6).

**Net: AC13 holds for the median run** — the boss interlude is a bounded, economy-frozen, clock-advancing swap of storm
for boss arena, with at most ~5 s of genuinely calmer entrance, once. **Therefore I keep the QA-passed v1 §3 ramp AND
the v2/v5/v6 economy completely UNCHANGED** — v7 only pauses-and-resumes them around a boss.

**Parked-caveat extension (non-blocking, honest):** the existing parked *"AC13 long runs — expert pure-dodging can
exceed 3 min"* watch-item (`backlog` Parked / `feature_inventory.md §4`) is **extended** to cover the boss interlude's
~5 s calm-entrance pressure × however many bosses an expert survives. It is bounded and clock-advancing, so it does not
*block* v7; if a human playtest shows runs drifting past 3 min *because of* the boss interludes, fix it with the V7.6
levers (cheapest first). This is the same "lock a number, own the playtest tuning" posture as v2/v5/v6.

---

## V7.6 Tuning levers (for QA → programmer, if AC13 drifts WITH bosses active)

Apply one at a time, re-test. **These v7 boss levers come first** (they retune the boss interlude without touching the
QA-passed core ramp or the v2/v5/v6 economy); only if insufficient, fall back to §V6.5 / §V2.4 / v1 §8.

**Runs now too LONG (> ~3 min / the boss interlude is lengthening expert runs):**
1. **Lower `BOSS_HP` `120 → 90`** — a shorter fight (~9–18 s) trims the interlude directly. **Biggest single lever**
   and the cleanest (it doesn't touch cadence). Keep it "large" (≥ ~60 = 15× HEAVY) so R60's big-HP fantasy holds.
2. **Raise `BOSS_FIRST_MARK` / `BOSS_INTERVAL`** (e.g. 75→90 / 90→120) — fewer interludes per run. Use *after* HP,
   since pushing the first mark past the ~120 s median death starts hiding the headline feature (re-check it's still
   reliably seen).
3. **Set `BOSS_RESUME_LULL` stays 0** — never *raise* the resume lull if runs are long (it would only add calm time).
4. Only if still long: apply the existing §V2.4 / v1 §8 "too LONG" storm levers (Shield weight 12→10, then
   `enemy_fire` floor 55→50).

**Runs now too SHORT (< ~1 min / the boss feels like a wall / players die in the fight):**
1. **Lower `BOSS_HP` is NOT the fix here** — instead **lower `BOSS_RAM_DMG` 60→45** or **trim the minion `MINION_CAP`
   14→10** (GDD owns these; flag to the Designer) so the arena is less lethal. *(These are Designer stats — I only flag
   the direction; I don't re-set them.)*
2. **Raise `BOSS_FIRST_MARK` 75→90 s** — give weaker players more warm-up before the first boss so it lands on a
   steadier player.

Do **not** change the breakpoint *metric* (time, not points — V7.1), the freeze *scope*, or the boss *moveset/stats*
here — those are GDD §V7.x's. The boss-economy levers I own are `BOSS_HP`-via-flag, the **marks**, and the **resume
lull**; re-tune those before reaching for the core ramp.

---

## V7.7 Smoke-seed coexistence (R65 / AC51) — the boss seed (@f40) composes with v5 (f16) + v6 (f20), weight/time-independent

GDD §V7.15 has the Programmer **force a boss @~`SMOKE_BOSS_FRAME=40`** (near-rest spawn + a compressed moveset so
arrival-clear + entrance + step 1 + the yellow→12-red split all run in 120 f). My job is to confirm the **breakpoint
cadence + the freeze do not interfere** with the existing v5/v6 smoke observations. They do not — by construction:

- **The natural TIME breakpoint never fires in smoke.** `BOSS_FIRST_MARK = 75 s = f4500 ≫ 120 f`, so the cadence
  trigger (V7.1) **cannot** fire in the 120-f run — exactly as the v2 drip (`randint(600,840) f > 120`) never fires
  (v2 §V2.5). The **only** boss in smoke is the **forced seed @f40**, which bypasses the time gate (like the v5
  green-pellet seed bypasses the kind roll and the v6 X-press bypasses the pickup roll). Clean and attributable.
- **The boss seed starts strictly AFTER the prior seeds** (f40 > the v5 split @~f16 > the v6 bomb @f20), so both
  earlier lifecycles are **observed first and untouched:** the v5 green pellet still splits ~f16 into 3 red children
  (AC27), and the v6 scripted **X @f20** still flushes them + the seeded enemy/asteroids, decrementing charge **2→1**
  (AC30/32/33). Re-confirmed coexistent — the same chained-seed timeline v6 §V6.6 already verified, now with the boss
  appended after.
- **The free arrival flush @f40 spends NO charge (R57), so smoke ends with charge = 1.** The v6 bomb left it at 1; the
  boss arrival is free (GDD §V7.5), so QA can assert "boss arrival cost no charge" directly off the residual **1**
  (AC40). The f40 arrival flash is a *second*, free flash overlay — distinct from the v6 bomb flash (f20→38).
- **During the smoke fight (f40→120) my freeze (V7.2) is exercised headlessly:** the v1 asteroid + v5 enemy spawners
  emit **nothing** except the boss's own step-1 wave (5 REGULAR ~f55), so AC41's freeze is observed in-budget. No drip
  fires (cadence > 120 f), so the frozen-drip rule is vacuously satisfied — nothing to suppress, nothing leaks.
- **The boss is NOT defeated in 120 f** (HP 120 stands), so DEFEAT/resume aren't exercised in smoke — fine; the MUST is
  arrival-clear + entrance + ≥1 attack step, all covered. The run still **exits 0 after exactly 120 frames** (R14).

**Confirmed:** the v7 breakpoint cadence + spawn-freeze leave the §V7.15 smoke boss seed fully coherent with the v1
warmup, the v5 split seed (f16), and the v6 bomb seed (f20) — all four compose in one 120-f run. (Exact seed wiring is
the Programmer's, GDD §V7.15; this only confirms the cadence/freeze/economy leave the smoke timeline intact.)

---

## V7.8 Traceability — every §26 LD lever / AC this section resolves

| Lever / AC | This spec | Section |
|---|---|---|
| ★ Breakpoint metric + value (reconcile AC13) | **CONFIRM** → TIME; `BOSS_FIRST_MARK=75 s`, `BOSS_INTERVAL=90 s`; option (a)+(b), no AC13 re-tune | §V7.1, §V7.5 |
| R58 spawn-freeze (v1 asteroids + v5 enemies) | **SET** → gate emit on `not boss_active`, **skip-no-bank** (no backlog dump) | §V7.2 |
| R58/R62 resume on defeat | **SET** → all 3 spawners resume on DEFEAT at current `t`; `BOSS_RESUME_LULL = 0` (no lull) | §V7.2 |
| R58 bonus-drip frozen during fight | **CONFIRM** → drip timer free-runs, emit skipped while `boss_active` | §V7.2, §V7.3 |
| R67 minion pickup-drops | **SET** → **SUPPRESSED** during the fight (no 15 % bullet-kill roll for minions) — no farm | §V7.3 |
| R67 minion score | **SET** → **ON**, normal v5 award (50/80/60 per GDD §V5.2/§V7.6); AC13-orthogonal (time gate) | §V7.3 |
| R62 defeat reward (big, flat) | **CONFIRM** → `BOSS_KILL_SCORE = 1000` (12.5× HEAVY; Score×2 → 2000); points-only, AC13-orthogonal | §V7.4 |
| `BOSS_HP` (fight-length lever) | **CONFIRM** → 120 → bounded ~12–24 s fight; my primary AC13 lever | §V7.5, §V7.6 |
| AC13 runs ~1–3 min | **HELD (median)** → clock never pauses, economy frozen, ~5 s entrance bounded/one-shot; parked caveat **extended** | §V7.5 |
| AC41 freeze + resume | **SET** → skip-no-bank freeze; immediate resume, no lull | §V7.2 |
| AC45 big reward + resume | **CONFIRM** → +1000 + spawners resume at current `t` | §V7.2, §V7.4 |
| AC51 smoke boss seed coexists | **CONFIRM** → forced @f40 (time gate never fires in 120 f); after v5 f16 + v6 f20; freeze exercised; exits 0 | §V7.7 |
| Boss entity / HP / moveset / flush-flash reuse / smoke wiring | **untouched** (GDD §V7.x owns) | — |
| v1 §3 ramp + v2/v5/v6 economy | **untouched** (QA-passed; v7 only pauses-and-resumes them around a boss) | §V7.2, §V7.5 |

Definition of done (per role): the Programmer can implement the breakpoint cadence (§V7.1), the freeze/resume gating
(§V7.2 — skip-no-bank, `BOSS_RESUME_LULL=0`), and the fight economy (§V7.3 — drip frozen, minion-drops suppressed,
minion-score-on) from this file, with the +1000 reward confirmed (§V7.4), the AC13 rationale + lever order in §V7.5–§V7.6,
and the smoke coexistence in §V7.7 — no boss-pacing/economy guesswork remains. All numbers reference GDD §V7.16 consts.

---
---
