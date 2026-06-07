# v16 increment — second boss (NOVA) + the random extensible boss pool

Owner: lead-game-designer · Date: 2026-06-07 · Status: complete
Inputs: `workspace/requirements/requirements/v16.md` (R99–R105, AC86–AC93, §V16.3 Open values),
`workspace/shared/brief.md` (v16 section), GDD `v7-bosses.md` (the encounter loop + the Mothership —
**reused verbatim**, only *which* boss + its per-boss values differ), `workspace/shared/handoffs.md` (117–119).
Implements the Designer-owned §V16.3 levers: the **new boss's identity/theme, moveset/attack patterns
(projectile-only, R103), HP, reward, defeat behaviour**, the **deadlier-than-Mothership lever + concrete
numbers (R104)**, and the **uniform-random extensible-pool concept (R99/R100)**.

> This section **appends** to v1–v15 and **supersedes nothing**. It adds **one new Boss spec (NOVA)** to a
> **boss pool/registry** and a **selection step** in front of the v7 encounter loop. The **Mothership keeps
> its v7 numbers verbatim** (`v7-bosses.md` unchanged). Everything in the v7 loop — ARRIVAL field-clear,
> spawn-freeze, slow entrance → centre → oscillation, big HP + always-hittable, ram + bullet damage, big
> flat reward + resume, bomb-vs-boss, HUD bar — **runs identically for NOVA** (R101); only the per-boss
> values below differ. Frames @60 FPS; angles in degrees; speeds px/f. NOVA's name + HUD/banner copy are the
> **Writer's** (R102); its shapes/palette/bullet hues are the **Artist's** (R102); final balance tuning
> (HP / spacing / cadence confirm) is the **Level-designer's** (R104) — on top of the concrete values I lock.

## V16.1 Feature in one line
Every boss-spawn still runs the identical v7 loop on the identical cadence (75 s, then +90 s) — but the game
now **rolls a die** over a boss pool and may instead drop the **NOVA**: a compact, radiant energy-weapon core
that **spawns no ships at all** and kills purely through a **faster, denser, higher-damage** barrage than the
Mothership — built so a **third boss is one registry entry away**.

---

## V16.2 The boss pool + uniform-random selection (R99/R100) — the concept I own

The encounter machinery is unchanged; v16 inserts **one selection step** at the V7.2 breakpoint.

- **A boss POOL / registry** holds the eligible boss **specs** (one entry per boss type). Today, exactly two,
  **in this order: `[MOTHERSHIP, NOVA]`**. It is the **single** source of the roster — nothing downstream
  hard-codes "two bosses." *(Exact registry data-shape is the Programmer's, §V16.3; the **concept** is: an
  ordered list of boss specs the loop iterates/indexes, never a hard-coded pair.)*
- **A boss SPEC = the per-boss values the v7 loop reads** instead of hard-coded Mothership numbers:
  `hp`, collision `r`, `ram_dmg`, `kill_score`, the **moveset function** `(step_index, boss, world) → fires
  that boss's pattern`, plus its **visual key** (Artist) and **name/HUD-label key** (Writer). Entrance / rest-y
  / oscillation **default to the shared v7 framing** (R101) — NOVA reuses them verbatim (§V16.3), so a spec
  only *overrides* what differs. The Mothership spec = its existing v7 numbers, untouched.
- **Selection = uniform i.i.d. at each spawn event (R100).** When the V7.2 breakpoint fires (mark reached,
  no boss active), pick **one** spec **uniformly at random** (probability **1/N**; today ½/½). **Independent
  per event — repeats allowed** (no no-repeat/shuffle-bag). The pick happens **once, at ARRIVAL**, and fixes
  which boss runs that whole fight. The selection layer chooses **only the spec**; the ARRIVAL→ENTRANCE→
  ACTIVE→DEFEAT loop (V7.3) is byte-for-byte the same regardless of pick.
- **Extensible — boss #3 = one entry (R99).** Append one more spec to the pool. Selection (still uniform 1/N)
  and the v7 loop need **zero** edits — N is read from the pool length. (AC86's one-entry test.)
- **Seedable/overridable RNG (R100/R105).** The pick must be forceable so smoke + pytest can pin a specific
  boss deterministically (a `SMOKE_BOSS_TYPE`-style override / seeded RNG, mirroring the v7 `SMOKE_BOSS_*`
  hook). Programmer + QA own the exact hook (§V16.3); the **requirement** is: random in play, forceable in tests.

---

## V16.3 NOVA — identity / theme (R102)

A **pure energy-weapon platform** — deliberately the Mothership's opposite. The Mothership is a blocky
**carrier** whose threat is the **ships it launches**; NOVA is a compact, radiant **artillery core / pulsar**
with **no hangar and no ships** — its entire threat is its **own** dense projectile fire. Read: *"a star that
shoots."* Distinct in silhouette, colour, name, and attacks (AC90).

- **Working concept name: NOVA** (an energy/artillery core). The **canonical on-screen name + WARNING/banner/
  defeat copy + HUD label are the Writer's** (R102) — "NOVA" is my design handle, not the locked display string.
- **Silhouette intent (Artist owns the px/shape/palette, R102):** a compact, radiant, many-emitter core — e.g.
  a spiked star / prism / ringed reactor — **clearly distinct** from the Mothership carrier, the v5 enemies,
  the player, the pickups, and the buff pills. Drawn body ≥ the `r=60` collision circle (still huge).

---

## V16.4 NOVA stats — reuses the v7 entrance framing; only these differ (R101, R102)

NOVA reuses the **v7 entrance/rest/oscillation framing verbatim** (spawn `(300,−80)`, entry `2.0` px/f, rest
`y=400`, oscillate `±120` @ `1.5` px/f, no-attack-during-entrance, first step at `settle+60 f`). Only the
values below differ from the Mothership.

| Lever | NOVA (LOCKED) | Mothership (v7) | Note |
|---|---|---|---|
| **HP** (`NOVA_HP`) | **120** | 120 | Same "large" pool (R60). **Deadlier via ATTACKS, not HP-sponge** (R104) — a fair, learnable target, not a bigger bullet-sponge. LD confirms vs fight length. |
| **Collision r** (`NOVA_R`) | **60** | 70 | Still huge → "always hittable" (R60) trivially holds. Slightly tighter than the carrier = a compact-core read; offsets the no-minion focus-fire so fight length stays in the v7 ~12–24 s band. |
| **Ram damage** (`NOVA_RAM_DMG`) | **80** | 60 | **Deadlier lever** — body contact hurts more. Still **< 100 HP** (survivable, not a one-shot); routes the §V2.7 player-damage step, honours i-frames/shield as usual. |
| **Defeat reward** (`NOVA_KILL_SCORE`) | **1500** | 1000 | Bigger flat payout for the harder fight (R62 — "may differ"). Flat via `scoring.award` → **Score×2 doubles it** (→3000). LD co-owns. |

---

## V16.5 NOVA moveset — projectile-only, DEADLIER than the Mothership (R103, R104) — LOCKED

**Structure reused from v7:** exactly **4 steps**, **fixed order `1→2→3→4→1…` looping until defeat**, fired on
a step interval, first step at `settle+60 f`, **no attacks during ENTRANCE**. **What differs:** every step is a
**projectile pattern** — NOVA has **NO spawn step and never touches any minion/enemy-spawn path** (R103); the
v1/v5 spawners stay frozen (V7.6) and the **only** hostiles on screen are NOVA's own bullets (AC91). The
patterns are denser, faster, higher-damage, and mostly **aimed** — the boss must threaten through fire alone.

- **Faster cadence (fire-rate lever):** `NOVA_STEP_INTERVAL = 90 f (1.5 s)` — **< Mothership 150 f**. Full
  4-step cycle = **360 f = 6 s** (vs the Mothership's 10 s): **1.67× more attack events per second.**
- **NOVA bullets** are ordinary `EnemyBullet`s on the existing enemy-bullet × player path (no new collision
  code) but with **`NOVA_BULLET_DMG = 25`** (> Mothership `EB_DMG = 15`) and **`NOVA_BULLET_SPEED = 5.5`**
  (> 4.5) — a **NOVA colour** (Artist) — **terminal** (never split). The step-3 lance uses
  `NOVA_LANCE_SPEED = 6.0` (fastest).

| Step | Pattern (projectile-only) | Bullets | Headings | Threat / lever |
|---|---|---|---|---|
| **1 — RAKE** (aimed spread) | tight aimed fan | **5** | boss→player heading at fire time **± {0, 15, 30}°** (60°-wide) | aim — read-and-sidestep; tighter & denser than the Mothership's 3-bullet ±20° fan |
| **2 — NOVA BURST** (dense ring) | full 360° ring | **24** | `k·15° + ring_phase` (k=0..23) | density — **double** the Mothership's 12-red ring (30°→15°); find-the-gap |
| **3 — LANCE** (aimed rapid stream) | fast straight burst | **4** | boss→player heading at fire time, launched on frames **f, f+4, f+8, f+12** | fire-rate — punishes standing still; fastest bullets (6.0) |
| **4 — ARC WALL** (aimed wide wall) | aimed 120° arc | **9** | boss→player heading **± {0,15,30,45,60}°** | aim + density — a wide wall; dodge around its edge |

- **`ring_phase`** is a stored offset that advances **`+9° (NOVA_RING_PHASE_STEP)` every step**, so the ring
  (step 2) **precesses** — never the identical safe-gap twice. A small accumulator on the boss; no new system.
- **No-recursion / no-split** (§27 stands): NOVA bullets are flat terminal `EnemyBullet`s — no yellow→red split
  (that's the Mothership's). One HP pool, one repeating moveset (no phases/enrage, v16 non-goal).

### Why this is measurably DEADLIER than the Mothership (R104 / AC92) — headline lever + the numbers

The **headline, simplest-to-verify lever is damage per hit: `NOVA_BULLET_DMG = 25 > EB_DMG = 15`** (and
`NOVA_RAM_DMG = 80 > 60`). It is reinforced on **every** other axis — all recorded so QA can compare directly:

| Axis | NOVA | Mothership | Deadlier? |
|---|---|---|---|
| Bullet damage / hit | **25** | 15 | **+67 %** |
| Ram damage | **80** | 60 | **+33 %** |
| Bullet speed | **5.5–6.0** | 4.5 | **faster → harder to dodge** |
| Step cadence | **90 f** | 150 f | **1.67× more often** |
| Boss-bullets / cycle | **42** (5+24+4+9) / 6 s = **7 / s** | 3+12 = 15 / 10 s = 1.5 / s | **~4.7× denser** |
| Aimed patterns | 3 of 4 (RAKE/LANCE/ARC) | mostly fixed fan/ring | **harder to dodge** |

*(The Mothership's *other* threat is its minion waves — forbidden to NOVA by R103 — so NOVA replaces "adds"
with a barrage that is strictly worse on damage, density, speed, cadence, and aim. Per-hit damage 25>15 is the
one-line check; the table is the full evidence.)*

- **Still survivable / dodgeable (R104 caveat — winnable, not unfair).** Steps are **1.5 s apart** and each
  resolves before the next is dangerous: the 24-ring at 5.5 px/f clears ~600 px in ~110 f (~1.8 s), so it has
  largely swept past a bottom-screen player by the next step — intense but navigable. Every pattern has a
  **defined safe response**: RAKE/ARC → step to the un-aimed side; NOVA BURST → hold a 15° gap and ride it out;
  LANCE → keep moving laterally. No minions compete for the player's attention, so the whole screen is dodge
  room. **Final spacing/cadence/HP tuning is the Level-designer's** (R104) — if a playtest shows it unwinnable,
  cheapest levers (in order): widen `NOVA_STEP_INTERVAL`, then drop `NOVA_RING_COUNT`, then lower bullet speed.

---

## V16.6 NOVA defeat behaviour (R62, R101) — LOCKED

Identical to the v7 DEFEAT phase, with no minions to consider:
- **On `NOVA_HP ≤ 0`:** award **`NOVA_KILL_SCORE = 1500`** through the normal `scoring.award` path (Score×2
  doubles it); **lift the spawn-freeze** → the v1 asteroid + v5 enemy spawners + v2 bonus drip resume at the
  current `t` (no post-boss lull); **remove the boss HUD bar**; the run continues to the next breakpoint mark.
- **In-flight NOVA bullets PERSIST** (no defeat-flush) — mirroring the Mothership's "surviving minions persist"
  rule (V7.9): a brief "dodge the last volley" beat. The **only** flushes in the game stay the player bomb (R63)
  and the boss-arrival clear (V7.5). NOVA has **no** minions to leave behind (R103).
- **Bomb-vs-NOVA = same as v7 (R63/V7.14):** a player bomb mid-fight clears all NOVA bullets (full §V6.3 scope)
  but **NOVA itself is IMMUNE** (`BOMB_BOSS_CHIP = 0`, reused) — its HP is earned with shots only.

---

## V16.7 Smoke + tests (R105) — force NOVA headlessly

Selection is random, so smoke/pytest **force** a boss (the seed/override above). The existing v7 boss-smoke
geometry (`v7-bosses.md` §V7.15: boss @ ~f40 near rest, compressed moveset, exits 0 at 120 f) is **reused** —
with `SMOKE_BOSS_TYPE = "NOVA"` it drives NOVA instead: arrival flush+flash (free, no charge) → short entrance
→ settle → **≥1 NOVA attack step** (e.g. step 1 RAKE ~f55, step 2 NOVA BURST ~f70), boss alive at f120 (HP 120
stands; defeat not required). The headless run thereby exercises (a) NOVA's arrival-clear + entrance + ≥1
attack and (b) **zero ships spawned** across the fight (R103/AC91). pytest grows with checks for: the pool +
one-entry extensibility (R99/AC86), uniform-random selection (R100/AC87), NOVA's **no-ship** moveset
(R103/AC91), and the **deadlier values** `NOVA_BULLET_DMG=25 > 15` etc. (R104/AC92) — Mothership parity
(AC39–AC52) and AC1–AC85 untouched (AC93). Exact frame seeds/asserts are the Programmer's + QA's.

---

## V16.8 New tuning constants (programmer-ready — add to `config.py`)

Names are suggestions; **values are the spec.** NOVA reuses the v7 entrance/rest/osc + arrival-clear + bomb-
immunity constants **verbatim** (not redefined) — only the deltas below are new.

```
# ── v16 second boss — NOVA (energy-weapon core; projectile-only) — GDD §V16.x ──
# Boss pool / selection (R99/R100). Programmer owns the registry data-shape (§V16.2).
#   BOSS_POOL = ordered list of boss specs; today [MOTHERSHIP, NOVA]. Pick ONE uniformly (1/N),
#   independent per spawn event (repeats allowed), at ARRIVAL. +1 entry adds a boss; loop unchanged.
#   RNG seedable/overridable so tests force a specific boss.

# NOVA stats — reuse v7 entrance(300,-80)/2.0, rest y=400, osc ±120@1.5, settle+60 VERBATIM. Only these differ:
NOVA_HP            = 120     # = Mothership; "large" (R60). Deadlier via ATTACKS, not HP-sponge (R104). LD confirms.
NOVA_R             = 60      # collision circle (huge → always hittable R60); compact-core silhouette intent
NOVA_RAM_DMG       = 80      # body contact (> Mothership 60) — deadlier lever; still < 100 HP (survivable)
NOVA_KILL_SCORE    = 1500    # flat defeat reward (> Mothership 1000); via scoring.award (Score×2 doubles). LD co-owns.

# NOVA bullets — ordinary EnemyBullets (existing enemy-bullet × player path), NOVA colour (Artist), terminal.
NOVA_BULLET_DMG    = 25      # > Mothership EB_DMG 15 — HEADLINE deadlier lever (AC92)
NOVA_BULLET_SPEED  = 5.5     # > Mothership 4.5 — faster, harder to dodge
NOVA_LANCE_SPEED   = 6.0     # px/f, step-3 LANCE (fastest)

# Moveset (R66 structure reused) — 4 steps, fixed order 1→2→3→4 loop. PROJECTILE-ONLY (R103) — NO spawn step.
NOVA_STEP_INTERVAL = 90      # f (1.5 s) between steps (< Mothership 150) — deadlier fire-rate; cycle 360 f (6 s)
NOVA_FIRST_STEP_DELAY = 60   # f after settle before step 1 (reuse v7 BOSS_FIRST_STEP_DELAY)
NOVA_RING_PHASE_STEP = 9     # deg; ring start-angle advances each step → ring precesses (never identical)
# step 1 RAKE  — aimed spread : boss->player ± {0,15,30}      -> 5 bullets @ NOVA_BULLET_SPEED
# step 2 BURST — dense ring   : k*15 + ring_phase (k=0..23)   -> 24 bullets @ NOVA_BULLET_SPEED
# step 3 LANCE — aimed stream : boss->player; bullets on f,f+4,f+8,f+12 -> 4 bullets @ NOVA_LANCE_SPEED
# step 4 ARC   — aimed wall   : boss->player ± {0,15,30,45,60}-> 9 bullets @ NOVA_BULLET_SPEED
NOVA_SPREAD_COUNT  = 5
NOVA_SPREAD_STEP_DEG = 15    # spread bullets at ±15, ±30 about the aim
NOVA_RING_COUNT    = 24
NOVA_RING_STEP_DEG = 15      # 360/24
NOVA_LANCE_COUNT   = 4
NOVA_LANCE_GAP_F   = 4       # frames between LANCE bullets
NOVA_ARC_COUNT     = 9
NOVA_ARC_STEP_DEG  = 15      # 9 bullets over ±60 = 120-deg arc, centred on the player

# Smoke / tests — force a specific boss (mirror v7 SMOKE_BOSS_* geometry, §V16.7)
SMOKE_BOSS_TYPE    = "NOVA"  # override the random pick to force NOVA headlessly (R105). Seedable RNG.
```

## V16.9 v16 requirement coverage map
| Req | Where realized |
|---|---|
| R99 extensible boss pool/registry (one-entry add) | §V16.2 |
| R100 uniform-random pick per spawn (1/N, i.i.d., seedable) | §V16.2 |
| R101 v7 cadence + encounter framing unchanged for every boss | §V16.2, §V16.4 (NOVA reuses entrance/rest/osc verbatim) |
| R102 second boss = new content, distinct identity/shape/name/attacks | §V16.3, §V16.5 |
| R103 HARD: NOVA spawns NO ships/minions (projectile-only) | §V16.5 (no spawn step; only its bullets are hostile) |
| R104 HARD: NOVA attacks DEADLIER than Mothership (concrete numbers) | §V16.5 (damage 25>15, ram 80>60, faster/denser/faster-cadence/aimed; full table) |
| R105 smoke green + force-a-boss + suite grows (pool/selection/no-ship/deadlier) | §V16.7 |

## V16.10 Handoffs to downstream roles
- **Artist (next):** NOVA's **silhouette** (compact radiant energy-core, shapes-only C2, distinct from the
  Mothership carrier + v5 enemies + player + pickups; body ≥ r=60 circle); a **NOVA bullet hue** distinct from
  the v5 RED/GREEN/CYAN and the Mothership's yellow; and a **NOVA HUD bar + label frame** (R64) — reuse the
  Mothership's bar treatment but visually tell the two bosses apart (tracks `NOVA_HP` 120→0). Arrival flash =
  the existing v6 `FLASH_*`, nothing new.
- **Writer:** NOVA's **canonical name** ("NOVA" is my design handle) + **WARNING/banner/defeat** copy + **HUD
  label**, matching the Mothership's treatment (R102/R64).
- **Level-designer:** **own the pool-selection rule + extensibility** statement and **confirm the boss cadence
  is unchanged** (75 s / +90 s); **re-confirm/finalize** the deadlier numbers (`NOVA_BULLET_DMG=25`,
  `NOVA_RAM_DMG=80`, `NOVA_STEP_INTERVAL=90`, densities) and `NOVA_HP=120` against AC13/fight-length — cheapest
  tuning levers in §V16.5. Add the v16 pool/selection + NOVA balance rows to `level_spec`.
- **Programmer:** no blocking unknowns — every Designer lever is a concrete number (§V16.8). Key reuse: NOVA
  plugs into the **unchanged v7 loop** as a **boss spec** read from the pool (§V16.2); the selection layer only
  picks the spec (uniform 1/N, seedable). NOVA bullets are **ordinary `EnemyBullet`s** with `NOVA_BULLET_DMG`/
  speed/colour (no new collision code); the moveset is **projectile-only — no minion/enemy-spawn path touched**
  (R103). `ring_phase` is one stored accumulator. Force-a-boss seed mirrors the v7 `SMOKE_BOSS_*` hook.

---
---
</content>
</invoke>
