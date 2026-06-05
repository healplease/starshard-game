# v7 increment — Bosses (periodic mothership boss fights)

Owner: lead-game-designer · Date: 2026-06-05 · Status: complete
Inputs: `workspace/requirements/requirements/v7.md` (R56–R68, AC39–AC52, **§26 Open-values table**),
`workspace/shared/brief.md` v7 increment, `workspace/shared/handoffs.md` (entry 46), GDD `v5-enemies.md`
(the REGULAR/HEAVY/SCOUT roster §V5.2 + the green→red splitting pellet §V5.4 — **reused, not changed**),
GDD `v6-bombs.md` (the flush §V6.3 + the activation flash §V6.5 — **factored & reused**), and
`workspace/levels/level_spec/v1-base.md` (§3 difficulty curve / §5 milestones / AC13 1–3 min band).
Implements: **R56–R68 (MUST)** — locks every §26 lever the Designer owns (breakpoint metric+value &
the AC13 reconciliation, boss HP/size-intent/entrance/rest/oscillation, attack-during-entrance, moveset
cadence/order/loop, minion cap/respawn + score/drop rule, attack-4 fan count+spread+split+12-red, boss
ram+bullet damage, bomb-vs-boss rule, big reward, bonus-drip freeze, and the smoke-seed geometry/timing).

> This section **appends** to v1+v2+v5+v6 and **supersedes nothing** — every prior number still holds. It
> adds an **encounter manager + a Boss entity**, reusing existing machinery: the **v6 flush/flash** for the
> arrival clear (factored so it spends NO charge), the **v5 enemy roster** for the moveset minions, and the
> **v5 green→red frozen split** (§V5.4) for attack-4's yellow→red burst. Frames are @60 FPS; seconds shown
> alongside. All angles in degrees, speeds in px/f. Boss visuals (silhouette px, health-bar look, yellow/red
> hues) are the **Artist's** (§26); the boss name + WARNING/defeat/HUD copy are the **Writer's** (§26);
> final breakpoint-vs-AC13 *tuning* + the freeze/drop economy are the **Level-designer's** to confirm (§26),
> on top of the concrete design values I lock below (same Designer-sets-number / LD-tunes pattern as v5/v6).

## V7.1 Feature in one line
At a fixed time mark the run pauses — the field is swept clean (free flush+flash), normal spawns freeze, and
a huge slow **Mothership** glides to screen-centre and oscillates while cycling a learnable 4-step moveset
(spawn 5 REGULAR → 2 HEAVY → 7 SCOUT → a yellow fan that bursts into a 12-red 360° ring); out-shoot its big
HP pool to bank **+1000** and resume the run until the next mark.

---

## V7.2 ★ THE BREAKPOINT + the AC13 reconciliation (R56) — the #1 decision, LOCKED & RECORDED

This is the delegated decision the whole increment hangs on (§26 top row, §28 headline risk). **Decided and
recorded here.**

### V7.2.1 Metric — TIME, not points, not both
- **LOCKED: the breakpoint is TIME-based** (elapsed PLAY time), **fixed interval**, not point-based and not
  both.
- **Why time over points:** a "periodic" boss must appear *reliably*, decoupled from how good a player is at
  farming. Score is highly variable run-to-run — at the v1 economy (enemy 50 / asteroid 10–20 / +1 pt-per-sec,
  `level_spec §7`) a 2-min run banks roughly **1.5k–2.5k pts** depending almost entirely on kill count, so a
  point gate fires 2–3× sooner for an aggressive player than a pure-dodger and **never** for a timid one.
  Time is monotonic, predictable, and maps directly onto the `level_spec §5` run-length bands, so "every N
  seconds" gives a *dependable* cadence. **Both** (time AND/OR points) only adds a second tunable with no
  payoff for one boss. Rejected.

### V7.2.2 Value — first boss at **75 s**, then every **+90 s** (fixed marks 75 / 165 / 255 / …)
- **LOCKED: `BOSS_FIRST_MARK = 75 s` (frame 4500); `BOSS_INTERVAL = 90 s` (5400 f).** Breakpoint marks are
  **absolute** on the run clock `t`: **t = 75, 165, 255, … s**. The boss is **the same Mothership each time**
  (one boss this increment, §27 — no scaling/roster; the *cadence* is what repeats, R56).
- **One concrete trigger rule (programmer-ready):** the encounter manager fires a boss when `t` first reaches
  the next unfired mark **AND** no boss is currently active. If a mark is crossed while a boss is still alive
  (cannot happen at these numbers — see below — but make it deterministic), the trigger is **deferred** until
  the boss resolves, then fires immediately; marks are never dropped or doubled-up.

### V7.2.3 The AC13 reconciliation — **chose (a) lower the gate**, blending into (b) for later bosses
Per requirements §26/§28 I had to consciously pick **(a) lower the gate so a boss reliably appears in a 1–3
min run**, **(b) accept a late/expert-run event**, or **(c) re-tune AC13**. **DECISION: (a)** for the first
boss; the periodic structure then **naturally becomes (b)** for bosses 2+. No AC13 re-tune (c) is needed.

Against the `level_spec §5` model (Warmup 0–20 s · Heat-up 20–60 s · Squeeze 60–90 s · Storm 90 s+; deaths:
weak ~60–90 s, **median ~110–130 s**, skilled ~2.5–3.5 min):

- **First boss @ 75 s (mid-Squeeze) is reliably seen.** It lands *before* the median death (~120 s) and well
  before a skilled run ends, so the **median and skilled player reliably meet at least one boss** — the
  headline feature is no longer rare (the 5-min/5000-pt example would have hidden it from nearly everyone).
  A weak sub-75 s death misses it, but that run was short by definition. 75 s is also a strong *beat*: the
  player has lived the full Heat-up and is into real dodging when the field suddenly clears and the Mothership
  glides in.
- **Bosses 2+ (@ 165 s, 255 s, …) are exactly the deliberate late/expert event of option (b).** Since the
  median run ends ~120 s, boss 2 is a skilled-run reward and boss 3 a rare-expert sight — the periodic cadence
  gates later bosses behind survival skill *for free*, with no extra logic. So (a) and (b) coexist: reliable
  first boss, escalating-rarity repeats.
- **The fight does NOT discount difficulty (this protects the 3-min ceiling).** The run clock `t` **keeps
  advancing during the boss fight** (one clock; see V7.3) — the ramp does not pause. So when the boss dies and
  the storm resumes, it has escalated to wherever `t` now is. The boss fight therefore **replaces** ~15–25 s
  of storm with ~15–25 s of an equally-dangerous boss arena (bullet-hell + minions + ram), rather than handing
  out a safe ~20 s breather. Net effect on run length is small and bounded; the distribution stays in/near the
  1–3 min band.
- **The reward is points, not survival** (V7.9: +1000, no HP/charge gift), so beating a boss does not
  artificially lengthen the run either.

**Carried watch-item (non-blocking, handed to the Level-designer):** the exact first mark (75 s) and interval
(90 s) and the boss HP (V7.4, the fight-length lever) are the Level-designer's to **re-confirm against a human
playtest** — same as the v5/v6 pattern where I lock a concrete number and the LD owns final AC13 tuning. If
playtests show runs drifting past 3 min *because of* the boss interlude, the cheapest levers (in order) are:
lower `BOSS_HP` (shorter fight), then raise `BOSS_FIRST_MARK`/`BOSS_INTERVAL` (fewer interludes), then the
existing `level_spec §8` storm levers. This extends the existing parked "AC13 long runs" caveat
(`feature_inventory.md §4`); it does not block v7.

---

## V7.3 The boss-fight loop (R56–R62) — states & the run clock

The encounter manager adds a **boss sub-state** *inside* PLAY (not a new top-level `GameState`; the §V2.7
pipeline and HUD keep running). One boss is active at a time (§27).

| Phase | Trigger | What runs |
|---|---|---|
| **ARRIVAL** (1 frame) | breakpoint mark reached, no boss active | free flush+flash (V7.5); freeze spawners (V7.6); spawn the boss off-screen-top; HUD bar appears |
| **ENTRANCE** | after ARRIVAL | boss descends to centre (V7.7); **no attacks** (V7.8); player may shoot it |
| **ACTIVE** | boss settled | oscillation (V7.7) + the 4-step moveset loops (V7.10–V7.12); boss damages player (V7.9); player whittles HP |
| **DEFEAT** (1 frame) | boss HP ≤ 0 | award +1000 (V7.9); lift the freeze → normal loop resumes (V7.6); HUD bar removed; surviving minions persist |

- **ONE run clock (R56/AC13 decision).** `t = PLAY frames / 60` (the existing `level_spec` clock) **never
  pauses** — it advances through ARRIVAL/ENTRANCE/ACTIVE/DEFEAT. The difficulty ramp, the survival-tick score,
  and the next breakpoint mark all read this same `t`. (Rationale in V7.2.3: no difficulty discount.) No
  separate "boss clock" exists.
- **Spacing is collision-free.** Fight length is bounded to ~15–25 s (V7.4) and the interval is 90 s, so the
  boss always resolves with ~65–75 s of normal play before the next mark — the deferred-trigger guard (V7.2.2)
  is belt-and-suspenders, never actually exercised at these numbers.

---

## V7.4 Boss health pool (R60) — LOCKED

| Lever (§26) | Value (LOCKED) | Rationale |
|---|---|---|
| **`BOSS_HP`** | **120** (player-bullet hits) | "Large" beyond doubt — **30×** a HEAVY (4 HP), **60×** a REGULAR (2 HP), the tankiest thing in the game by far. Yet bounded: see fight-length below. Explicit integer (AC52). |
| Damage per player bullet | **1 hit** | Each player bullet that overlaps the boss removes the bullet and subtracts 1 from `BOSS_HP`. No per-bullet variance. |

- **Always defeatable, never invulnerable (R60/AC43, BA ruling).** The boss is added to the **player-bullet ×
  hostile** collision step (V7.13) so **Z fire — including v2 Rapid (cd 6) and Fan (3 beams) — always damages
  it** via the normal path; bullets are **consumed on hit** as usual. There is no shot-immunity phase.
- **Fight length (the AC13 lever).** Baseline fire is 12-f cooldown = 5 shots/s; the boss is a big easy target
  (V7.7, collision r=70). Perfect single-beam fire = 120 / 5 = **24 s**; realistic dodging-and-firing ~**18–22
  s**; **Rapid** (10/s) ~**12 s**; **Fan** adds side beams that mostly graze a centred boss, so ~**15–20 s**.
  So the fight runs **~12–24 s** depending on buffs/aim — long enough to watch the 4-step moveset cycle **~1.5–
  2.5×** (a 10-s cycle, V7.10) so the pattern is *learnable*, short enough to keep runs near the band (V7.2.3).
  `BOSS_HP` is the Level-designer's primary AC13 lever if a playtest disagrees (V7.2.3).

---

## V7.5 Boss-arrival field-clear (R57) — reuse the v6 flush+flash, FREE & SILENT

The instant a boss encounter begins (ARRIVAL frame), the field is cleared by **reusing the v6 bomb flush
(§V6.3) and activation flash (§V6.5)** so it reads **identically** to a player bomb — **but driven by the
encounter manager, not a player press.**

- **Clears (exactly the §V6.3/R48 scope):** all enemies (REGULAR/HEAVY/SCOUT), all asteroids/debris, and **all
  enemy projectiles** — explicitly **including in-flight HEAVY green pellets and already-split RED children**,
  plus SCOUT cyan and REGULAR red.
- **Spares (§V6.3 scope):** **player bullets** (keep flying), **all pickups** (the 5 v2 diamonds + the bomb
  pickup), and **cosmetics** (particles / hit-feedback / starfield).
- **FREE — consumes NO bomb charge (BA ruling, R57).** The player's charge count is **untouched** (AC40). The
  Programmer **factors** the v6 bomb routine so the encounter manager can call the **flush + flash** path
  *without* the `charges -= 1` / `BOMB_LOCKOUT` decrement-and-lockout path. Suggested factoring: a
  `trigger_flush(arm_flash=True)` core that both the player-bomb path (after it spends a charge + arms the
  lockout) and the boss-arrival path (charge/lockout untouched) call. The flash itself is the **identical**
  `FLASH_FRAMES=18` near-white linear-fade overlay (§V6.5) — same look, no charge.
- **SILENT — awards NO score (BA ruling, R57).** Like the v6 flush, this is a silent despawn that does **not**
  route through `systems/scoring.py` (`BOMB_FLUSH_SCORE=0` applies equally). Score is identical the frame
  before and after the arrival clear (AC40).
- **The boss is not flushed by its own arrival.** Ordering on the ARRIVAL frame: **flush first**, **then**
  spawn the boss off-screen-top — so the new boss never appears in the cleared lists.

---

## V7.6 Spawn freeze + resume (R58) — LOCKED, plus the bonus-drip & minion-drop economy

- **Freeze (while a boss is active — ARRIVAL→DEFEAT):** the **v1 asteroid/debris spawner** and the **v5 enemy
  spawner** produce **nothing** (AC41). The encounter manager gates both spawners' "fire a spawn" step on
  "no boss active." The ramp clock `t` keeps advancing (V7.3) but no asteroid/enemy is emitted.
- **The only new hostiles during the fight are the boss's moveset minions (V7.11)** — they come from the boss,
  not the spawner, so they appear despite the freeze.
- **Bonus drip — FROZEN during the fight (Designer value; Level-designer confirms, §26).** The v2 timed
  bonus-pickup drip (`randint(600,840) f`) is **also paused** while a boss is active, matching the BA
  default-rec (R58): a **clean, self-contained arena**. No *new* pickups appear during the fight. (Pickups
  already on the field at ARRIVAL **survive** the flush, per V7.5, and keep drifting/collectable.)
- **Minion pickup-drops — SUPPRESSED during the fight (Designer value; Level-designer confirms, §26).** Boss
  minions killed by player bullets do **NOT** roll the v2 15%-enemy-drop while a boss is active. Rationale:
  consistent with the frozen drip (no new economy mid-fight) and prevents the fight becoming a bomb/buff farm.
- **Minion SCORE — awarded normally (Designer value).** Minions **are** ordinary v5 enemies (R67), so killing
  them pays the **normal v5 score (REGULAR 50 / HEAVY 80 / SCOUT 60)** through the usual `scoring.award` path.
  Score is intrinsic to the kill (always on); only the *economy* (pickups) is frozen. This is not farmable —
  the boss spawns a **bounded** number on a **fixed** cadence (V7.11, cap 14), so there is no infinite trickle.
- **Resume (on DEFEAT, R62):** the freeze **lifts immediately** — the v1 asteroid spawner, the v5 enemy
  spawner, and the v2 bonus drip all **resume** under the usual ramp at the current `t` (AC41/AC45). There is
  **no post-boss lull** (unlike the optional v6 `BOMB_SPAWN_LULL`); the storm comes straight back.

---

## V7.7 Boss entrance, resting position & oscillation (R59) — LOCKED

| Lever (§26) | Value (LOCKED) | Notes |
|---|---|---|
| Spawn (ARRIVAL) | **(300, −80)** | Centred horizontally (x=300), just above the screen so the whole silhouette is off-screen at spawn. |
| **Entrance path + speed** | straight down at **2.0 px/f** | Slow, grand glide-in. ~ (400−(−80))/2 = **240 f ≈ 4.0 s** to reach centre. (Player entry is 2.0; this *feels* slower because the boss is huge.) No horizontal movement during entrance. |
| **Resting vertical position** | **y = 400** (= H/2, the screen vertical centre) | Required by R59 ("settles at the vertical centre"). The Mothership hovers mid-screen and rains fire on the player below (player sits ~y=720, ~320 px of dodge room + the whole screen to manoeuvre). |
| Settle test | when boss `y ≥ 400`, snap to 400 and switch ENTRANCE→ACTIVE | Deterministic; no overshoot. |
| **Oscillation amplitude** | **±120 px** about x=300 ⇒ **x ∈ [180, 420]** | A wide, readable left-right sweep. With a ~180-px silhouette (V7.7-size) the boss edges reach x∈[90, 510] — comfortably inside the 600-px window (≥90-px margins). |
| **Oscillation speed** | **1.5 px/f**, constant-speed **ping-pong** (reverse at the bounds) | Slow. Full L→R→L cycle = 4·120/1.5 = **320 f ≈ 5.3 s**. Begins **only after** settle. (A `x = 300 + 120·sin(2π·f/320)` sinusoid is an acceptable equivalent if the Programmer prefers eased turns — same amplitude/period.) |
| **Boss size intent** | silhouette **~180 px wide × ~110 px tall**; **collision = circle r = 70** | Designer owns the **collision** (r=70 — huge, so R60 "always hittable" is trivially satisfied); the **Artist owns the visible silhouette px/shape/colour** (§26), intent "biggest thing on screen, unmistakably a Mothership, distinct from the v5 enemies," with the drawn body ≥ the r=70 collision circle. |

---

## V7.8 Attack-during-entrance rule (R59/R66) — LOCKED: NO

- **The boss does NOT attack during ENTRANCE.** The 4-step moveset begins only **after** it settles at y=400.
- **First step fires at `settle + 60 f` (1.0 s)** — a one-beat pause so the player can read the boss before
  the pattern starts.
- **Why:** a clean "here it comes → it's in position → now it attacks" rhythm; avoids minions/bullets emitting
  from a still-moving, off-centre boss; and makes the smoke timing deterministic (V7.14).

---

## V7.9 Boss damage to the player + the defeat reward (R61, R62) — LOCKED

- **Ram / body contact — `BOSS_RAM_DMG = 60`.** The player colliding with the boss body (player circle ×
  boss r=70 circle) costs **60 HP**. Threat-ranked above HEAVY (50) and REGULAR (40) — the boss is the
  scariest thing to touch — but **not** a one-shot (player has 100 HP), so a single ram is survivable and the
  i-frames (R18) prevent an instant second tick. Routes through the **§V2.7 player-damage step** (first-hit-
  wins, honours i-frames R18 / shield R27) (AC44).
- **Moveset bullets — reuse `EB_DMG = 15`** (BA "may reuse `EB_DMG`"). Both the **yellow fan bullets** and the
  **12 red children** (V7.12) are ordinary enemy bullets dealing the flat **15** via the same §V2.7 step
  (honouring i-frames/shield) (AC44). No new damage value.
- **Defeat reward — `BOSS_KILL_SCORE = 1000`** (flat). "Big" beyond doubt: **12.5×** a HEAVY, **20×** a
  REGULAR, and roughly **half a typical 2-min run's entire score** — a run-defining payoff for surviving the
  fight (R62/AC45). Awarded as a flat add through the normal `scoring.award` path, so **Score×2 (F31) doubles
  it if active** (→ 2000) — consistent with "every point flows through `award`" (`feature_inventory.md §F11`),
  not a special case. (Level-designer co-owns this value per §26; 1000 is the locked design value to confirm.)
- **Surviving minions on defeat (Designer call, §26): they PERSIST.** Any boss minions still alive when the
  boss dies are **not** cleared — they remain as ordinary v5 enemies and the resumed normal loop (V7.6) deals
  with them (a brief "mop up the stragglers" beat). No defeat-flush. The **only** flushes in the game stay the
  player bomb (R63) and the boss arrival (V7.5).

---

## V7.10 Mothership moveset — cadence, order & loop (R66) — LOCKED

- **Exactly 4 steps, fixed order `1 → 2 → 3 → 4 → 1 → …`, looping until the boss is defeated** (R66/AC48).
- **`STEP_INTERVAL = 150 f (2.5 s)` between steps.** Full 4-step cycle = **600 f = 10 s**.
- **First step at `settle + 60 f`** (V7.8). Then step 2 at +150 f, step 3 at +300 f, step 4 at +450 f, back to
  step 1 at +600 f, etc.
- A ~12–24 s fight (V7.4) therefore shows the player **~1.5–2.5 full cycles** — enough to *learn* the pattern.
- The 2.5-s gap lets each step's threat resolve before the next: step-4's 12-red ring (V7.12) at ~4.5 px/f
  clears the ~600–800-px screen well within the 10-s gap before step 4 comes round again — no bullet pile-up.

| Step | Action | Spec |
|---|---|---|
| **1** | Spawn **5 REGULAR** | V7.11 |
| **2** | Spawn **2 HEAVY** | V7.11 |
| **3** | Spawn **7 SCOUT** | V7.11 |
| **4** | Yellow fan → 12-red 360° ring | V7.12 |

---

## V7.11 Moveset steps 1–3 — spawn waves of v5 enemies (R67) — LOCKED

Steps 1–3 spawn reinforcements that are **exactly the v5 enemy kinds** (§V5.2), in the counts the brief/req
fix: **Step 1 = 5 REGULAR, Step 2 = 2 HEAVY, Step 3 = 7 SCOUT** (R67/AC49). Once spawned they **are ordinary
v5 enemies** — they move, fire (REGULAR red / HEAVY green splitting pellet / SCOUT cyan), take damage, score,
and die exactly per §V5.2–§V5.4 / R36–R40 — and they appear **despite the frozen spawner** (V7.6).

- **Spawn positions (Designer value).** Each minion spawns at `y = −24` (same as the v5 enemy spawn, so they
  enter from the top with the normal entry behaviour), `x` **uniform in [40, 560]** (the v5 enemy spawn band,
  `level_spec §4`). The wave's members spawn **on the same frame** the step fires (a "drop" of the whole wave),
  each with an independent random x. They then run the standard v5 entry→strafe→fire AI. *(No formation/scripted
  pattern — §27 non-goal; uniform-x keeps it simple and reuses the v5 spawn path verbatim.)*
- **Minion cap / re-spawn rule (Designer value, §26) — `MINION_CAP = 14` alive boss-minions.**
  - A step, when it fires, spawns its **full** wave (5 / 2 / 7) **provided that keeps alive boss-minions ≤ 14**.
    If the full wave would exceed 14, the step spawns only `max(0, 14 − alive)` of its kind (no banking); if
    already at/over 14, it spawns **none** that step. **No "is the previous identical wave still alive?" check**
    — a step re-spawns freely each cycle, gated **only** by the global 14-cap.
  - **Why 14:** it equals **one full moveset's worth** of minions (5+2+7). So the **first** time each step
    fires after the arrival-clear (the field is empty, alive = 0) the cap **never bites** — step 1 spawns all
    5, step 2 all 2, step 3 all 7 — which is exactly what **AC49 checks** (the clean opening cycle spawns
    precisely 5/2/7). The cap only throttles *later* cycles if the player has ignored minions, bounding the
    arena at 14 enemies (vs the normal `enemy_cap(t)` max of 6) — fair, since during the fight minions are the
    *only* spawned threat besides the boss.
- **Frame-budget note (no change to existing caps).** The global **enemy-bullet cap stays 40** and the
  **asteroid cap stays 16** (`level_spec §6`); boss minions count toward the enemy-bullet cap normally but
  **bypass the enemy *spawn* cap** (they're boss-driven). Worst case ≈ 14 minions + boss + ≤40 enemy bullets +
  the 12-red ring — still well inside the `level_spec §6` shape budget (~80–142 shapes) for 60 FPS.
- **Score / drops:** normal v5 score **on**, pickup drops **suppressed** during the fight — see V7.6.

---

## V7.12 Moveset step 4 — yellow fan → 12-red 360° ring (R68) — LOCKED, reuses the v5 frozen split

The centrepiece attack. It **reuses the v5 green→red splitting-pellet machinery (§V5.4)**: a fire-time-frozen
split distance along each bullet's heading, then a removal-and-replace into RED children that are **ordinary
red enemy bullets** (terminal, never re-split).

**1 — Fire the yellow fan (the telegraph).** The boss fires a **fan of 3 YELLOW bullets** from its centre,
aimed downward at the player: the **centre** bullet on the boss→player heading **at fire time**, the two
**flanks at ±20°** (a clearly-readable **40°-wide** yellow fan). All three travel at **`YELLOW_SPEED = 4.5`
px/f** (= `EB_SPEED`, the v5 pellet speed) and are **damaging enemy bullets while in flight** (flat
`EB_DMG = 15`, collision r=5 — the uniform `EnemyBullet` path).

**2 — Frozen "midway" split trigger (recommended v5 frozen-distance, LOCKED).** Each yellow bullet stores, at
fire time, a **frozen split distance `YELLOW_SPLIT_DIST = 200 px`** — literally "midway" between the boss
(y=400) and the bottom of the play area (y=800), a fixed 200-px drop. Implemented as the v5 **frozen timer**
`split_timer = round(200 / 4.5) ≈ 44 f`; decrement each frame, split at ≤0 — **no live player re-read** (so it
cannot home or collapse to a 0-distance burst — the §V5.4/§16 guard). Because the boss y is fixed, this
distance is constant and even more deterministic than the v5 player-relative `S`.
- **Edge cases (reuse §V5.4 verbatim):** a yellow bullet that **hits the player** (deals 15, consumed) or
  **leaves the screen** *before* its `split_timer` reaches 0 is removed by the normal bullet rules and
  **produces no children** — only a *surviving* yellow bullet splits.

**3 — Split into exactly 12 RED children, an even 360° ring (LOCKED).** When the volley's bullets reach the
split point they are **removed and replaced** by **exactly 12 RED `EnemyBullet`s total**, whose headings are
**evenly spaced every 30° over a full 360°** — the set `{0°, 30°, 60°, …, 330°}` (12 directions, "flying
outward in all directions," AC50). Each of the 3 yellow bullets contributes **4** of the 12 (so "each split
into red bullets" is literally true), using **interleaved** 30°-spaced headings so the 12 together form the
even ring — e.g. centre→{0,90,180,270}, left-flank→{30,120,210,300}, right-flank→{60,150,240,330}. *(The
binding invariant QA checks is the 12 outgoing headings = the even 30° set; the partition is the Programmer's
— spawning all 12 from the centre bullet's split position is an acceptable equivalent. The yellow flanks
spread only ±20° over 200 px, so the three split origins sit close together and the burst reads as one clean
12-ray ring.)*
- **Resolving the brief's wording:** "*a fan of yellow bullets … midway split into 12 red bullets … all
  directions … ≈30° apart*" is loose where the yellow-plurality (3) meets the red total (12). The **binding,
  QA-checked** constraint (AC50) is the **red layer: exactly 12, even 360°, 30° apart** — only cleanly
  satisfiable as a single even ring. I keep a genuine **plural yellow fan (3, the telegraph)** *and* the exact
  12-red even ring by having the three yellows each burst into an **interleaved quarter** of the ring. This
  honours both clauses without ever producing 12×N reds.

**4 — Children are ordinary RED bullets (terminal).** Each child: RED, **speed `RED_CHILD_SPEED = 4.5`** (=
`CHILD_SPEED`/`EB_SPEED`), **flat `EB_DMG = 15`**, collision r=5, despawns off-screen, and **never splits
again** (no recursion — §27 non-goal). They reuse the **existing enemy-bullet update/collision path verbatim**
(AC50/AC52) — identical to the v5 red children.

---

## V7.13 Boss collision integration (R60, R61) — how the boss plugs into §V2.7

The boss is one extra collidable; it does **not** change the §V2.7 step order, only adds the boss as a target/
source:
- **Player-bullet × boss** (folded into §V2.7 step 2, the player-bullet × enemy step): on overlap (player
  bullet vs boss r=70 circle), **remove the bullet** and **`BOSS_HP -= 1`**; if `BOSS_HP ≤ 0` → DEFEAT (V7.9).
  The boss is **not** an `Enemy` in the v5 roster (no kind-table entry, no v5 score on hit) — it's its own
  entity with its own HP and the +1000 defeat reward.
- **Player × boss body** (folded into §V2.7 step 4, player-damage): overlap costs `BOSS_RAM_DMG = 60`,
  first-hit-wins with i-frames/shield as usual.
- **Boss bullets × player** (the yellow fan + 12 red children) are **ordinary `EnemyBullet`s** — they're
  already in the enemy-bullet × player path (§V2.7 step 4), no new code.
- **Bomb-vs-boss** — see V7.14.

---

## V7.14 Bomb-vs-boss rule (R63) — LOCKED: boss IMMUNE to the flush

The player's bomb (X) **remains usable during a boss fight** (R46 unchanged) and **costs a charge as normal**
(it IS a player action, unlike the free arrival clear V7.5).

- **A player bomb mid-fight clears the boss's minions + all boss/enemy bullets** — the full §V6.3 flush scope:
  all minions (REGULAR/HEAVY/SCOUT), the **yellow fan bullets**, and the **12 red children** (and any v5
  green pellets/cyan in flight). It is a legitimate "clear the adds + panic the bullet-wall" tool (AC46).
- **The boss itself is IMMUNE — `BOMB_BOSS_CHIP = 0` (no chip).** A bomb does **not** subtract any `BOSS_HP`
  (AC46). **Why immune (BA-recommended default):** the big HP pool **must be earned with shots** — a chip
  would let a player carrying up to 4 charges burst a fixed chunk (4 × chip) off the boss, undermining the
  "large health pool" fantasy and the fight-length/AC13 balance. Clean, deterministic, trivial to verify
  (boss HP is identical the frame before and after a bomb). Consistent with the arrival clear (V7.5) also not
  touching the boss.
- The flush still **awards no score** and **spares** player bullets + pickups + cosmetics (§V6.3), exactly as
  in v6 — only the *minions* and *bullets* clear; the boss stands.

---

## V7.15 Smoke-test design (R65 / AC51) — seed a boss headlessly, in-budget

A natural 120-f run reaches no breakpoint (first mark is 75 s = f4500), so the smoke path **must seed/force a
boss** so the **arrival clear (R57), the entrance (R59), and ≥1 moveset attack step (R67/R68)** all run within
120 f without raising — composing with the existing **v5 split seed** (@f3, splits ~f16) and **v6 bomb seed**
(@f20) so none of those regress. The wiring (a `SMOKE_BOSS_*` constant block + an `app.py`/`world` hook,
mirroring `SMOKE_SPLIT_*` and `SMOKE_BOMB_*`) is the **Programmer's choice**; this section fixes the
**geometry/timing** so the boss loop is guaranteed in-budget and maximally covering.

**Recommended deterministic seed (composes with v5 @f16 + v6 @f20):**

| Smoke frame | Event | Covers |
|---|---|---|
| f1 | v1 seed: 3 asteroids + 1 enemy | (existing) |
| f3 | v5 seed: green pellet → splits ~f16 into 3 red children | AC27 (existing) |
| f20 | v6 seed: scripted **X bomb** → flushes enemy + asteroids + the 3 red children; charge **2→1** | AC30/32/33 (existing) |
| **~f38** | (optional) seed a token asteroid/enemy so the arrival clear has a visible target | guarantees AC40 has something to clear |
| **`SMOKE_BOSS_FRAME ≈ 40`** | **Force the boss encounter:** free arrival **flush+flash** (R57 — **NO charge**, stays at 1), freeze the spawners, spawn the boss **already near rest at (300, 360)** (not (300,−80) — a short entrance to fit the budget) | **AC40** (free clear, no charge), **AC41** (freeze) |
| **~f50** | Boss reaches y=400 → ENTRANCE→ACTIVE (descends 360→400 at 2.0 px/f ≈ 20 f) | **AC42** (entrance→settle) |
| **~f55** | **Smoke moveset step 1: spawn 5 REGULAR** (the wave drop) | **AC49 / R67** (a spawn step) |
| **~f70** | **Smoke moveset step 4: fire the yellow fan**, but with a **shortened `SMOKE_BOSS_SPLIT_DIST ≈ 45 px`** → `split_timer ≈ round(45/4.5) = 10 f` | sets up the split in-budget |
| **~f80** | Yellow fan **splits into 12 red** (even 360° ring); children update f80→120 | **AC50 / R68** (the split) |
| f120 | smoke **exits 0** (boss still alive — HP 120 stands; defeat is *not* required) | **AC51 / R14** preserved |

- **Why compress in smoke (mirrors v5).** Just as v5 smoke forced a short split distance (`S=60`, split ~f16)
  to fit the lifecycle in 120 f, the boss smoke (a) spawns the boss near its rest position (short entrance)
  and (b) uses a short `SMOKE_BOSS_SPLIT_DIST` so the **hardest clause — the yellow→12-red split (R68/AC50) —
  is observed headlessly**. In smoke the moveset is driven on a **compressed timeline** (step 1 ~f55, step 4
  ~f70) rather than the play `STEP_INTERVAL=150 f`, so **both** a spawn step (R67) and the split (R68) fire
  in-budget — exceeding the "≥1 attack step" MUST.
- **No v5/v6 regression.** The boss seed starts at **f40**, strictly **after** the v5 split (f16) and the v6
  bomb (f20), so those observations are untouched. Crucially, the arrival flush at f40 is **free** (R57): the
  v6 charge ended at **1** after the f20 bomb and the boss arrival spends **none**, so the smoke still ends
  with **charge = 1** — QA can assert "boss arrival cost no charge" directly (AC40). The arrival flush+flash
  at f40 is a *second* flash overlay (the boss's free one) — distinct from the v6 bomb flash (f20→38) and
  demonstrating R57's "reads like a bomb, but free."
- **During the smoke fight (f40→120) the spawners are frozen (V7.6)** — no new asteroids/enemies except the 5
  REGULAR minions at f55, exercising AC41's freeze headlessly. The boss is **not** defeated (no DEFEAT/resume
  in-budget) — that's fine; the MUST is arrival-clear + entrance + ≥1 attack, all covered.

---

## V7.16 New tuning constants (programmer-ready — add to `config.py`)

All v7 numbers gathered for the single-source-of-truth config. Names are suggestions; **values are the spec.**

```
# ── v7 bosses / periodic Mothership (GDD §V7.x) ─────────────────────────────
# Breakpoint (R56) — TIME-based, fixed marks; reconciled with AC13 (§V7.2)
BOSS_FIRST_MARK   = 75      # seconds of PLAY before the FIRST boss (frame 4500)
BOSS_INTERVAL     = 90      # seconds between subsequent bosses (marks 75, 165, 255, …)
#   trigger when t reaches the next mark AND no boss active; defer (never drop) if a boss is alive.
#   ONE run clock: t never pauses during the fight (no difficulty discount — §V7.2.3 / §V7.3).

# Boss stats (R59, R60, R61)
BOSS_HP           = 120     # player-bullet hits; 1 dmg/bullet; ~12–24 s fight (AC13 lever, §V7.4)
BOSS_R            = 70      # collision circle radius (huge → always hittable, R60). Artist owns silhouette px (~180×110).
BOSS_SPAWN        = (300, -80)   # ARRIVAL spawn (off-screen top, centred)
BOSS_ENTRY_SPEED  = 2.0     # px/f straight-down entrance; ~240 f (~4 s) to y=400
BOSS_REST_Y       = 400     # settles at the screen vertical centre (H/2), R59
BOSS_OSC_AMP      = 120     # px; oscillate x in [180, 420] about x=300
BOSS_OSC_SPEED    = 1.5     # px/f constant ping-pong (reverse at bounds); ~320 f (~5.3 s) full cycle
#   no attacks during ENTRANCE; first step at settle + BOSS_FIRST_STEP_DELAY (§V7.8)
BOSS_FIRST_STEP_DELAY = 60  # f after settle before moveset step 1
BOSS_RAM_DMG      = 60      # body-contact damage (>HEAVY 50 >REGULAR 40; not a one-shot vs 100 HP)
#   boss bullets (yellow fan + red children) reuse EB_DMG = 15 (R61)

# Moveset (R66) — fixed order 1→2→3→4 looping until defeat
BOSS_STEP_INTERVAL = 150    # f between steps (2.5 s); full 4-step cycle = 600 f = 10 s
MINION_CAP        = 14      # max alive boss-minions (= one full 5+2+7 wave; AC49 first cycle never capped)
BOSS_WAVE = {               # step -> (kind, count)  — exact counts (R67/AC49)
  1: ("REGULAR", 5),
  2: ("HEAVY",   2),
  3: ("SCOUT",   7),
}
#   minions spawn at y=-24, x uniform in [40,560]; ordinary v5 enemies thereafter (§V5.2).
#   minion SCORE on (normal v5: 50/80/60); minion pickup-DROPS + bonus drip FROZEN during fight (§V7.6).

# Attack-4: yellow fan → 12-red 360° ring (R68) — reuses the v5 frozen split (§V5.4)
YELLOW_FAN_COUNT  = 3       # yellow bullets in the fan (telegraph)
YELLOW_FAN_SPREAD = 20      # deg; flanks at ±20° about the boss->player heading (40° wide)
YELLOW_SPEED      = 4.5     # px/f (= EB_SPEED); yellow bullets are damaging in flight (EB_DMG=15)
YELLOW_SPLIT_DIST = 200     # px frozen "midway" (boss y=400 -> bottom 800); split_timer = round(200/4.5) ≈ 44 f
RED_RING_COUNT    = 12      # red children total, even 360° ring (headings k*30°, k=0..11)
RED_RING_STEP_DEG = 30      # 360 / 12; "all directions, ≈30° apart" (AC50)
RED_CHILD_SPEED   = 4.5     # px/f (= CHILD_SPEED/EB_SPEED); flat EB_DMG=15; terminal, never re-split

# Reward + bomb rule (R62, R63)
BOSS_KILL_SCORE   = 1000    # flat defeat reward (through scoring.award; Score×2 doubles it). Big: 12.5× HEAVY.
BOMB_BOSS_CHIP    = 0       # player bomb during fight: clears minions+bullets, boss IMMUNE (no chip), §V7.14

# Arrival clear (R57) — reuse the v6 flush+flash, NO charge, NO score (§V7.5)
#   factor the v6 bomb so the encounter manager calls trigger_flush(arm_flash=True) WITHOUT charges-=1/lockout.
#   FLASH_FRAMES=18 / FLASH_PEAK_ALPHA / FLASH_COLOR / BOMB_FLUSH_SCORE=0 all reused from §V6.11.

# Smoke seed (GDD §V7.15) — force a boss @ ~f40, AFTER the v5 (f16) + v6 (f20) seeds
SMOKE_BOSS_FRAME       = 40   # force arrival flush+flash (NO charge) + spawn boss near rest
SMOKE_BOSS_SPAWN       = (300, 360)  # short entrance so it settles (~f50) in-budget
SMOKE_BOSS_SPLIT_DIST  = 45   # px shortened "midway" → split_timer ≈ 10 f, so the yellow fan splits ~f80
#   compressed smoke moveset: step 1 (5 REGULAR) ~f55, step 4 (yellow fan) ~f70 -> 12-red ~f80 update to 120.
#   boss NOT defeated in 120 f (HP 120 stands); smoke still exits 0 / exactly 120 f (R14).
```

- Reuse, don't duplicate: `EB_DMG`, `EB_R`, `EB_SPEED`, `CHILD_SPEED`, `FLASH_FRAMES`/`FLASH_PEAK_ALPHA`/
  `FLASH_COLOR`, `BOMB_FLUSH_SCORE`, and the `ENEMY_KINDS` table (§V5.5) are **existing** — v7 references them,
  it does not redefine them. `BOSS_HP` is the explicit integer health AC52 checks.

## V7.17 v7 requirement coverage map
| Req | Where realized |
|---|---|
| R56 periodic breakpoint trigger (repeats) | §V7.2 (TIME, first 75 s, every +90 s, fixed marks; AC13 reconciled) ; §V7.3 |
| R57 free/silent arrival flush+flash (reuse v6, no charge, no score) | §V7.5 |
| R58 spawn-freeze (v1 asteroids + v5 enemies; drip + minion drops) + resume | §V7.6 |
| R59 entrance → vertical-centre → oscillation; attack-during-entrance | §V7.7, §V7.8 |
| R60 large HP, always hittable (Z/Rapid/Fan) | §V7.4, §V7.13 |
| R61 ram + bullet damage (§V2.7 step) | §V7.9, §V7.13 |
| R62 big defeat reward + normal-loop resume; surviving minions persist | §V7.9, §V7.6 |
| R63 bomb-vs-boss (minions+bullets cleared, boss immune) | §V7.14 |
| R64 boss HUD (bar + label) | downstream — **Artist** (bar look/placement) + **Writer** (label); driven by `BOSS_HP` (§V7.4) |
| R65 smoke gate + seeded boss (arrival+entrance+≥1 attack in 120 f) | §V7.15 |
| R66 Mothership repeating 4-step moveset (order/cadence/loop) | §V7.10 |
| R67 steps 1–3 spawn 5 REGULAR / 2 HEAVY / 7 SCOUT (v5 kinds) + cap/score/drop | §V7.11, §V7.6 |
| R68 step 4 yellow fan → midway → 12-red 360° ring (reuse v5 split) | §V7.12 |

## V7.18 Open questions / handoffs to downstream roles
- **Artist (next):** owns (a) the **Mothership silhouette** — a large (~180×110-px intent, ≥ the r=70
  collision circle) blocky/menacing shape, **shapes only (C2)**, **distinct** from the v5 enemies, the player
  cyan, the pickups, and the buff pills; (b) the **boss health bar + label frame** (R64) — tracks `BOSS_HP`
  (120→0), **visually distinct** from the player HP bar (R10), the v2 buff pills (R29) and the v6 bomb readout,
  and **placed so it does not collide** with any of them (AC47), appearing on ARRIVAL and removed on DEFEAT;
  (c) the **yellow fan + red-child bullet hues** — a **yellow** distinct from the v5 GREEN pellet / CYAN scout
  / amber Fan-pickup, and the **red children** reuse the existing RED enemy-bullet colour (`EB_COLOR_RED`) like
  the v5 split children. The **arrival flash reuses the v6 `FLASH_TINT`/peak-alpha verbatim** — nothing new to
  pick there.
- **Writer:** the **boss name** (the brief's "**MOTHERSHIP**"), the **HUD label text** (e.g. `MOTHERSHIP`), an
  optional **WARNING/intro line** on arrival and a **defeat line** on the +1000 (R64) — shapes+text only.
- **Level-designer:** **re-confirm AC13** with these design values — `BOSS_FIRST_MARK=75 s`, `BOSS_INTERVAL=90
  s`, `BOSS_HP=120` (the fight-length lever), `BOSS_KILL_SCORE=1000` — and **own the final tuning** if a
  human playtest shows runs drifting past 3 min (levers in §V7.2.3, cheapest-first). Confirm the **bonus-drip
  freeze + minion-drop suppression + minion-score-on** economy (§V7.6) and that the **v7 smoke boss seed (@f40)
  coexists** with the v1 ramp, the v5 split seed (f16) and the v6 bomb seed (f20) — it will (the boss seed
  starts strictly after both). Add the v7 spawn-freeze/resume + breakpoint rows to `level_spec`.
- **Programmer:** no blocking unknowns — every §26 Designer lever is a concrete number above (§V7.16 consts).
  Key reuse: **factor the v6 bomb** into a `trigger_flush(arm_flash=True)` core so the **arrival clear runs
  without** the charge-decrement/lockout path (§V7.5); the **yellow→12-red split reuses the v5 frozen
  distance/timer** (§V5.4) with `YELLOW_SPLIT_DIST=200` (smoke: 45); minions are **ordinary v5 `Enemy`s** from
  the `ENEMY_KINDS` table; the boss is its **own entity** (own HP + the +1000 reward), folded into §V2.7
  steps 2 (player-bullet × boss → −1 HP) and 4 (player × boss body → 60 ram); the breakpoint uses the existing
  run clock `t` (never paused); the smoke seed (§V7.15) forces a boss @~f40 so arrival-clear + entrance + a
  spawn step + the yellow→12-red split all run in-budget.

---
---
