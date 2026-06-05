# GDD — change log (lead-game-designer)

> Per-domain history. The current spec is `gdd.md` (canonical). This file holds the dated decision
> notes for this domain only. The cross-role story lives in `../shared/handoffs.md`.

- 2026-06-05 (v1): GDD.md created from R1–R14 — 600×800 @60fps, full master numbers table, ramp
  formula defaults, screen-state machine, entities & behaviors, HUD layout, collision order,
  smoke-test design. R20/R21 deferred for line budget; R19/R22 optional.
- 2026-06-05 (v2): GDD.md v2 section added. **Buff table LOCKED** — Repair `+40` HP instant
  (clamp 100, no overheal); Fan **3 beams** at −12°/0°/+12°, 8 s/480 f; Rapid cooldown **×0.5** (12→6 f),
  8 s/480 f; Shield **full invuln** 5 s/300 f reusing R18 blink (invulnerable if iframes OR shield);
  Score **×2** 10 s/600 f. **R34 IN, R35 OUT** (balance-swingy/instant-clear deferred). **Stacking** =
  independent per-type timers; same-type re-collect **hard-refreshes to full** (cap = one full duration,
  no accumulation, no effect doubling); Repair never stacks; restart wipes buff_timers + popup + pickups.
  **Pickup** = color-coded **diamond** (~26 px, collide r=13), drifts **2.0 px/f** down, no h-drift, NOT
  sped by ramp, on-screen **cap 3**, missed = no penalty. **Spawn** = BOTH timed drip (~12 s default) +
  enemy drop (~15% default) + kind weights (Repair30/Fan20/Rapid20/Shield15/Score15) — all level-designer
  defaults. **Smoke**: force-seed a Rapid pickup in the player's path ~frame 2 + shorten its duration to
  ~60 f so spawn→collect→apply→expire all fit in 120 f. **HUD** = buff-pill stack top-left under SCORE
  (14×14 letter box + 40×6 shrink bar, stable enum order) + transient green "+40" repair popup by HP bar.
  **Module map** specified: config / world(+enums) / input / entities(player,hazards,projectiles,bonus,fx)
  / systems(spawning,physics,combat,buffs,scoring) / view(render,hud) + **thin main.py**; dep direction +
  separation rules given (only systems/app mutate World; view read-only).
- 2026-06-05 (v5): GDD.md v5 section added — **3 enemy types, every §15 lever LOCKED.** Roster table
  (§V5.2): **REGULAR** = today's enemy carried forward verbatim (r=13, entry/strafe 2.0, descent 0.3,
  2 HP, +50, ram 40, red `EB_SPEED=4.5`) **+ one tweak**: aim cone **±12°**. **HEAVY** = r=18, entry 1.4 /
  strafe 1.2 / descent 0.3, **4 HP**, +80, ram 50, **green** pellet 4.5, fire **×1.6**, cone **±6°**.
  **SCOUT** = r=10, entry/strafe 3.0 / descent 0.4, **1 HP**, +60, ram 30, **cyan** **7.5** (high), fire
  **×1.4**, cone **±3°**. **Bullet dmg/radius flat 15/r=5 (`EB_DMG`/`EB_R`) for ALL enemy bullets** (green
  pellet, cyan, red children) so the §V2.7 collision path stays one uniform `EnemyBullet`; green pellet
  only *drawn* bigger (Artist), collision unchanged. **Aim** (§V5.3) = one routine, per-shot
  `uniform(−cone,+cone)` perturbation added to today's exact aim ⇒ **cone 0 == pre-v5 enemy** (R37/AC29
  regression guarantee); cones **monotone 12>6>3**. **Split** (§V5.4, the centerpiece) = **FIRE-TIME-frozen**
  heading `u` (incl. heavy's ±6°) + frozen distance `S = max(0.5·D, 60)`; implemented as a frozen
  **timer** `round(S/4.5)` (no live player re-read → not homing, guards the §16 "split at ≈0" risk).
  `SPLIT_FRACTION=0.5`, `SPLIT_MIN_DIST=60`. Children = **exactly 3** RED at offsets **(−18°,0°,+18°)**
  about `u` (**FAN_HALF_ANGLE=18°, center INCLUDED**), speed **4.5**, then ordinary terminal red bullets
  (no re-split). Surviving pellet **always** splits (even if player gone); destroyed/off-screen before the
  timer ⇒ no children. **Smoke** (§V5.6): seed a green pellet @~f3 `(300,300)` heading down with `S=60` ⇒
  splits ~f16, children update to 120 — guarantees the AC27 split runs in-budget (wiring = programmer,
  mirrors v2 `SMOKE_BONUS_*`). **Ramp INTENT only** (§V5.7, weights = level-designer/R41): REGULAR from
  t=0 (backbone, preserves R6/AC6), HEAVY gated ~20 s+ low weight, SCOUT gated ~45–60 s+ lowest — all draw
  the same `enemy_cap(t)` and HEAVY/SCOUT fire less often than REGULAR, so total bullet pressure stays
  within the QA-passed v1 §3 curve → AC13 holds. Fire cadence **ramps** (base `enemy_fire_interval(t)` ×
  per-kind mult). Placeholder bullet hex (green ~`(90,230,120)`, cyan ~`(90,230,255)`) — Artist finalizes.
- 2026-06-05 (v6): GDD.md v6 section added — **bombs / panic button, every §20 lever LOCKED.** **Charge
  pool**: start **2** (fixed by R45), **cap 4**, clamp [0,4], restart→2. **Activation** (X, key-down edge):
  −1 charge → **flush** the three hostile lists (all enemies + asteroids + **all enemy bullets incl. green
  pellets & red split children**) **before** the §V2.7 player-damage step; **SPARES** player bullets +
  all pickups (incl. the bomb pickup) + cosmetics. **FLUSH SCORE = NONE** (`BOMB_FLUSH_SCORE=0`, silent
  despawn, never hits scoring — confirms BA rec: survival tool, not a farming exploit). **Flash** (R50):
  Designer locks **duration `FLASH_FRAMES=18` (0.30 s) + linear fade**; Artist owns color (near-white) +
  peak alpha (~200, ~78%, *not* a full white-out). **One-press-one-bomb** = edge-trigger + **`BOMB_LOCKOUT=18`
  f** (== flash, so no strobe). **Bomb pickup** = **6th `BonusKind.BOMB`** in the v2 diamond framework
  (same diamond/r=13/2.0 px-f drift/cap 3/no-penalty-miss), **instant +1 clamped to cap, NO buff-pill**
  (exempt R29); **collect-at-full-cap = WASTED** (consumed, clamped — matches Repair-at-full, avoids a
  refused diamond starving the 3-slot cap); sole refill (no time/kill regen). **Keymap** (R52): **Z fire**
  (canonical, cooldown + Rapid/Fan modifiers intact — binding-only change), **X bomb**, move/start/R/Esc
  unchanged; Space dropped as taught fire key (silent alias = Programmer's option), all copy MUST teach
  **"Z = fire · X = bomb"** (AC35). **Bomb always usable when charges>0**, independent of i-frame/shield.
  **Activation-feel order**: flush runs at top of frame, ahead of §V2.7 step 4, so a panic bomb clears
  bullets before they hit. **Smoke** (§V6.10): scripted X key-down **~f20** (`SMOKE_BOMB_FRAME`), just
  after the v5 ~f16 split, so one flush clears the seeded enemy + asteroids + **the 3 red split children**
  — covers R48's hardest clause + AC30/AC32/AC33 free; **intentionally supersedes** the v5 "children to
  f120" obs (AC27 still ✓: children born ~f16 update f16–19 then flushed). Optional richer plan: presses
  20/45/70 → two activations + a 0-charge no-op (AC31/AC36). **DELEGATED**: Artist = pickup color/glyph +
  flash color/alpha + HUD readout placement; Writer = pickup name + glyph + `BOMBS` label + Z/X copy;
  Level-designer = bomb-pickup **weight (rarest, ~5–8% rec)** + optional **R55 lull (~30 f rec / 0)**, both
  bound by **AC13** (V6.8). New consts block in §V6.11 (`BOMB_START/CAP/LOCKOUT`, `FLASH_FRAMES/PEAK_ALPHA/
  COLOR`, `BOMB_FLUSH_SCORE`, `BOMB_SPAWN_LULL`, `SMOKE_BOMB_FRAME`).
- 2026-06-05 (v7): GDD `v7-bosses.md` added (§V7.1–V7.18) — **periodic Mothership boss, every §26 Designer
  lever LOCKED.** **★ The breakpoint-vs-AC13 decision (RECORDED, §V7.2):** metric = **TIME** (rejected points
  as too kill-variable, "both" as needless); **first boss @ 75 s** (frame 4500), then **every +90 s** (fixed
  absolute marks 75/165/255…), defer-not-drop if a boss is alive. **Chose option (a) lower the gate** — 75 s
  is mid-Squeeze, *before* the median ~120 s death, so median+skilled runs **reliably** see boss 1; bosses 2+
  become the deliberate **late/expert event of option (b)** for free (the periodic cadence gates them behind
  survival). **No AC13 re-tune (c).** Key sub-decision: **ONE run clock** — `t` **never pauses** during the
  fight, so the boss gives **no difficulty discount** (storm resumes escalated); the fight **replaces** ~15–25 s
  of storm rather than handing a safe breather → AC13 stays bounded. **Boss stats:** `BOSS_HP=120` hits
  (30× HEAVY; ~12–24 s fight = the LD's AC13 lever), collision **r=70** (always hittable, R60; Artist owns
  ~180×110-px silhouette), spawn **(300,−80)**, entrance **2.0 px/f** straight down to **rest y=400** (screen
  vertical centre), oscillate **±120 px @ 1.5 px/f** ping-pong; **NO attacks during entrance**, first step at
  settle+60 f. **Damage:** ram **60** (>HEAVY 50), bullets reuse **`EB_DMG`=15**; defeat reward **+1000** (flat,
  through `award` so Score×2 doubles it; surviving minions **persist**, no defeat-flush). **Moveset (R66):**
  fixed **1→2→3→4 loop**, `STEP_INTERVAL=150 f` (10 s/cycle). Steps 1–3 spawn **5 REGULAR / 2 HEAVY / 7 SCOUT**
  (ordinary v5 `Enemy`s, y=−24 / x∈[40,560]); **`MINION_CAP=14`** = one full wave, so the first cycle is never
  capped (AC49 sees exact 5/2/7) and later cycles self-throttle. **Minion SCORE on** (50/80/60) but **pickup
  drops + the v2 bonus drip FROZEN** during the fight (clean arena; LD confirms). **Step 4 (R68, §V7.12):**
  fan of **3 yellow** (±20°, telegraph, damaging in-flight) sharing a **frozen `YELLOW_SPLIT_DIST=200 px`**
  ("midway" boss→bottom; timer ≈44 f via the **v5 §V5.4 frozen split**), splitting into **exactly 12 RED** on
  the **even 30° 360° set** {0,…,330} (each yellow → 4 interleaved) at speed **4.5**, flat **15**, terminal/no
  re-split. Resolved the brief's loose "fan…→12 red total" by making the **even 12-red ring binding** (AC50)
  and the **plural yellow = telegraph**. **Arrival clear (R57):** reuse the **v6 flush+flash factored** as
  `trigger_flush(arm_flash=True)` — **no charge, no score**. **Bomb-vs-boss (R63):** clears minions+bullets,
  **boss IMMUNE** (`BOMB_BOSS_CHIP=0` — HP must be earned). **Smoke (R65/§V7.15):** force a boss **@~f40**
  (after the v5 f16 + v6 f20 seeds, so no regression; arrival costs **no charge** → smoke ends charge=1),
  boss spawned near rest **(300,360)** + **`SMOKE_BOSS_SPLIT_DIST=45`** → compressed moveset fires step 1
  (5 REGULAR) ~f55 and step 4 ~f70 → **12-red split ~f80**, updating to f120; boss not defeated; exits 0 / 120 f.
  Consts in §V7.16. **DELEGATED downstream:** Artist = Mothership shape + boss health bar + yellow/red hues;
  Writer = "MOTHERSHIP" name + HUD label + WARNING/defeat copy; Level-designer = re-confirm AC13 (first-mark /
  interval / `BOSS_HP` / reward) + the freeze/drop economy + smoke coexistence.
