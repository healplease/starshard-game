# Requirements — change log (business-analyst)

> Per-domain history. The current spec is `requirements.md` (canonical). This file holds the dated
> decision notes for this domain only — read it if you need *why*, not *what*. The cross-role story
> lives in `../shared/handoffs.md`.

- 2026-06-05 (v1): requirements.md created — R1–R22 MoSCoW, non-goals, constraints, AC1–AC13.
  MUST = R1–R14; SHOULD = R15–R18; COULD = R19; R20/R21/R22 won't-have (line budget). Aim: 1–3 min runs.
- 2026-06-05 (v2): requirements.md v2 section added. **R23–R33 MUST** — R23 bonus pickup entity
  (drifts down, collide-to-collect, no penalty if missed); R24 repair (instant, no overheal); R25
  spread/fan fire, R26 rapid fire, R27 shield/invuln (timed, reuses R18 blink); R28 spawning (timed
  drip and/or enemy drop, must be reachable in smoke seed); R29 HUD buff identifier + remaining-time;
  R30 stacking/refresh (different types coexist, same type refreshes-not-doubles, repair never stacks);
  R31 expiry + restart cleanup (no state leak); R32 modular MVC refactor (**C3 line cap RETIRED**);
  R33 smoke gate preserved + exercises a full bonus lifecycle. **R34/R35 COULD** (score-mult,
  screen-clear). **AC14–AC21**. Concrete values (durations, fan count, fire-rate, cadence, drop %)
  delegated to designer/level-designer.
- 2026-06-05 (v5): requirements.md v5 section added (§13–§17). **R36–R44 MUST** — R36 typed roster
  (REGULAR/HEAVY/SCOUT, kind is an explicit branchable property); R37 regular + per-shot aim-deviation
  cone (additive perturbation on the existing aim vector, so zero-cone == today's exact aim → R6/AC6
  preserved, no regression); R38 heavy (bigger/slower) firing a GREEN medium pellet; **R39 the split
  lifecycle** — the crux: travel → split at "midway" → exactly 3 RED children fanned about the pellet's
  heading → children are ordinary red bullets (terminal, no re-split). Two deliberate guardrails written
  into R39 to forestall the obvious mis-implementations: (a) **"midway" is a FIRE-TIME-frozen reference**
  (fraction of the pellet→player distance captured at fire, realized as a fixed distance/position along
  the pellet's own heading or an equiv. timer) — **not** a live re-read of the player's position, else it
  reads as homing and can split at ≈0 distance once the player closes in; (b) the split is
  **unconditional on the player** (a surviving pellet always splits, even if the player is gone), while a
  pellet destroyed/off-screen **before** the split point yields **no children**. R40 scout (faster, likely
  fragile) firing fast accurate CYAN (tight/zero cone < regular cone); R41 spawn mix folds into the ramp
  and must keep AC13; R42 visual distinguishability (distinct shapes/sizes; red/green/cyan bullets;
  shapes+text only); R43 smoke gate preserved **+ a split SEEDED so it runs headless** (120 f may not
  naturally spawn a Heavy + let its pellet reach the split point); R44 internal kind names (Writer
  blesses; no UI surface required). **AC22–AC29.** Every number — sizes, move speeds, HP, bullet speeds,
  fire cadences, the two deviation cone half-angles, split fraction, fan half-angle + center-child rule,
  child speed, spawn weighting — is **delegated** via the §15 Open-values table (Designer + Level-designer
  own them); examples in the spec are illustrative, not final tuning.
- 2026-06-05 (v7): `requirements/v7.md` added (§24–§29). **R56–R68 MUST** (no COULD this increment),
  **AC39–AC52**. Two requirement blocks: **A the boss-fight loop** (R56 periodic breakpoint; R57
  system arrival field-clear reusing the v6 flush+flash but **no charge / no score**; R58 freeze the v1
  asteroid + v5 enemy spawners while the boss lives, minions excepted, resume on defeat; R59 slow entrance
  → vertical-centre → L/R oscillation; R60 large HP + always-hittable; R61 ram + bullet damage; R62 big
  flat reward + resume; R63 bomb-vs-boss; R64 boss HUD bar+label; R65 smoke seeds a boss) and **B the
  Mothership** (R66 identity + repeating 4-step moveset; R67 steps 1–3 spawn **5 REGULAR / 2 HEAVY / 7
  SCOUT** — the v5 kinds; R68 step 4 yellow fan → **midway split into 12 red, all directions**, reusing
  the v5 green→red split machinery). **Key BA design decisions / why:** (1) **The #1 routed-downstream
  tension is the breakpoint cadence vs AC13** — the human's "every 5 min / 5000 pts" against 1–3 min runs
  means most runs never reach a boss; I refused to assume a value and instead wrote R56 + §26-top-row + §28
  to FORCE the Designer/Level-designer to consciously choose: lower the gate, accept a late-run event, or
  re-tune AC13. This is the spine of the increment. (2) **Reuse over reinvention** — R57/R68 explicitly
  bind the boss to the *already-shipped* v6 flush/flash and v5 split so the Programmer factors existing
  code rather than writing new systems (cheaper + AC52 checks it). (3) **BA rulings made (not delegated)
  to remove ambiguity the brief left open:** the arrival clear is free + silent (system, not player); the
  player's weapon always hits the boss (else unwinnable); a player bomb mid-fight clears minions+bullets
  but the **boss is immune by default** (you can't bomb-kill a boss — recommended, with an optional chip
  left to the Designer); attack-4 children are terminal (no recursion, like v5). (4) **Everything numeric
  delegated** via the §26 table — breakpoint, boss HP/size/speed/oscillation, moveset cadence, fan/split
  counts+angles, reward, damage — examples are illustrative, not tuning. The run-length watch-item now
  cuts both ways: a boss fight *itself* costs time and could push runs past 3 min, so the chosen cadence +
  HP + reward must be balanced (or AC13 redefined) — flagged in §28.
- 2026-06-05 (v10): `requirements/v10.md` added (§36–§41). **R76–R82 MUST**, **AC61–AC68**. Extends the
  v8 Q-hold-to-quit gesture (R72) — previously **PAUSE-only** — to **START + GAME_OVER**, and surfaces
  the quit hint on both. **Key BA stance: freeze by reuse.** The threshold (`PAUSE_QUIT_FRAMES=30`),
  the arc visual, and the cancel-on-release/no-accumulation semantics are **reused verbatim from v8** —
  v10 invents no new mechanic; it only changes *which states* run the gesture and *where* the hint/arc
  sit. **This increment explicitly amends v8 R72's "PAUSE-only" ruling + v8 §33 non-goal #1** (the
  deferral this resolves). **BA rulings (not delegated):** active states become START/PAUSE/GAME_OVER
  but **NOT PLAY** (R81 — keeps a stray Q from ending a run; mid-run quit still via PAUSE); one shared
  hold counter **reset to zero on every state transition** (R79 — the correctness spine: a partial hold
  must never carry across a death/restart into an instant quit). **Delegated (§38):** arc pixel
  placement on each of START + GAME_OVER → Artist (criterion: visible + no text-rect overlap, the v9
  render-smoke key-rect check is the gate); the two quit-hint strings → Writer (width-safe, no stale
  "Esc Quit"); economy = confirmed no-op (Level-designer confirm/skip). Smoke stays a no-op (Q never
  held headlessly) — the real new-code gate is the v9 **render-smoke** on START+GAME_OVER (AC68).
- 2026-06-07 (v16): `requirements/v16.md` added. **R99–R105 MUST**, **AC86–AC93**. Second boss + a
  **uniform-random pick from an extensible boss pool** at each boss-spawn event, under **two non-negotiable
  human constraints**. **Key BA stances:** (1) **Extend, don't reinvent** — R101 binds *every* boss to the
  already-shipped v7 encounter contract (R57–R64) verbatim; v16 adds only a **selection step + one new Boss
  type**, not a new system. Cadence (~75 s then +90 s) and the arrival-clear/freeze/reward framing are
  **explicitly locked unchanged** — only *which* boss appears is randomized. (2) **The two hard constraints
  are the spine** and I wrote them as standalone MUSTs that **override** any conflicting v7 default: **R103
  no ship/minion spawns of any kind** (a per-boss override of v7 R67, which is Mothership-*only* by
  definition — adds stay the Mothership's exclusive gimmick), **R104 strictly deadlier attacks** (and I
  forced "deadlier" to be **concrete with recorded numbers** vs the Mothership so AC92 is measurable, not
  cosmetic; still must stay winnable/dodgeable). (3) **Selection = pure uniform i.i.d.** (R100) — equal
  prob, independent per event, **repeats allowed**; explicitly ruled **out** weighted/no-repeat/shuffle-bag
  as a non-goal. (4) **Testability ruling** — R100/R105 require a **seedable RNG / force-a-boss hook** so
  smoke + pytest can deterministically exercise the new boss + the no-ship check (random runs may never pick
  it). (5) **Extensibility is a checked AC** (AC86: adding a 3rd boss = one registry entry, no logic edit) so
  "the pool must be trivially extensible" doesn't get lost. **Everything creative delegated** via §V16.3:
  identity/moveset/HP/reward → Designer; shapes/palette/projectiles → Artist; name/copy → Writer; the
  deadlier-lever numbers + cadence-unchanged confirm → Level-designer; registry shape + seed hook →
  Programmer. (Also flipped v14 index status to shipped ✅ — v1–v15 are shipped per the backlog.)

- 2026-06-07 (v18): `requirements/v18.md` added. **R106–R113 MUST**, **AC94–AC101**. Bonus rebalance:
  Fan side-beam nerf + Rapid → two fire/speed kinds. **Key BA stances:** (1) **Amend, don't reinvent** —
  R106 amends R25 (Fan side beams now fire at HALF the center cadence; wrote the contract as a **2:1
  center:side firing-rate ratio**, mechanism delegated to Programmer, geometry/angles/colors untouched);
  R26 (Rapid) **RETIRED** by R108, replaced by R109's two kinds — both reuse the v2 timed-buff shape
  (R29 HUD, R30 refresh, R31 expiry/restart) verbatim, so this adds two BonusKinds + a Fan rule, not a
  new system. (2) **The weight-sharing contract is the spine** — R111: the two new kinds' **combined**
  weight **= old Rapid weight (20)**, split delegated (default even 10/10); combined with R107 (Fan
  rarer, freed weight redistributed), the **full roll-0–99 ladder MUST stay non-overlapping and sum to
  100** across the post-v18 **7 kinds** (Repair·Fan·fire-rate·velocity·Shield·Score·Bomb). Made
  sums-to-100 a hard, AC-checked gate (AC99) — the #1 footgun of touching three ladder slots at once.
  (3) **Locked the two effects' semantics, delegated magnitudes** — (a) fire-rate kind = cooldown halved
  *exactly as old Rapid* (FIRE_CD//2) **+** bullet speed up a bit; (b) velocity kind = bullet speed up a
  lot **+** fire rate up a bit (< the (a) halving). Introduced **R110: bullet speed becomes a buffable
  stat** off a single base constant (today fixed) — the levers the two kinds move; reverts on expiry. All
  "a bit"/"a lot" numbers + base speed → Level-designer. (4) **Stacking ruling (R112)** — the new kinds
  both touch fire-cooldown AND bullet-speed, and per R30 different types coexist, so they can be active at
  once on the **same** stats; required the per-stat resolution to be **deterministic, bounded, clean-
  reverting** (no ≤0 cooldown, no stuck stat) — recommended strongest-wins, but the choice is the
  Designer's as long as it's specified + testable. (5) **Testability** — R113: smoke seed
  `SMOKE_BONUS_KIND="RAPID"` MUST be repointed to a valid post-v18 kind (ideally a new one); suite grows
  with 2:1 cadence / Fan-weight / Rapid-gone / each new effect / sums-to-100 / clean-stacking checks. All
  creative delegated via §V18.3: identity/feel/durations/stacking → Designer; pill letter+color → Artist;
  name → Writer; every magnitude + all ladder weights + split → Level-designer; Fan mechanism + smoke
  seed → Programmer. (Also flipped v16 index status to shipped ✅ — v1–v17 are shipped per the backlog.)

- 2026-06-07 (v19): `requirements/v19.md` added. **R114–R119 MUST**, **AC102–AC108**. Precise controls
  = focus mode + circular player hitbox + larger bullets. **Key BA stances:** (1) **Amend, don't
  reinvent** — R114 amends R3 (hold SHIFT → ×0.5 move, PLAY-only, **held modifier not toggle**,
  firing/hitbox untouched); R115 amends the R16–R18 collision *radius* only. No new system/screen — an
  input modifier + a radius change + a size scale + one overlay. (2) **Hitbox-is-always-small is the
  spine, and it's confirmed with the human** — I asked the load-bearing question at kickoff (always-on
  vs precise-only) and the human said **always-on**; SHIFT only *reveals* (R117) and *slows* (R114), it
  does **not** resize the hitbox. Wrote R115 to force the Programmer to **decouple the draw constant from
  the collision radius** (today `P_R=13` is both) so the visible ship stays full-size while the hitbox
  becomes a circle ≈50% of it. (3) **"All bullets larger" made exhaustive + two-sided** — R116 requires
  **every** projectile family (player, `EB_R`, pellet, child, NOVA, boss) enlarged in **BOTH draw and
  collision** so visuals stay matched; flagged tunneling/cull as the risk. Bullet **speed** explicitly
  unchanged (v18 R110 untouched) — size only. (4) **Indicator is render-only** — R117 forbids the red
  circle from touching any collision/movement (pure readout of R115), SHIFT-and-PLAY-only. (5) **Enemy
  hitboxes fenced off** — R118 keeps asteroid/enemy/boss *body* radii unchanged (only their bullets grow
  via R116). (6) **One nuance surfaced, not silently decided** — bonus-pickup collection *also* uses `P_R`
  today; whether it shrinks with the damage hitbox or stays generous is delegated to the Designer
  (default: pickup stays generous, only the *damage* hitbox shrinks) so bonuses don't quietly get harder
  to grab. **Everything numeric delegated** via §V19.3: ×0.5 multiplier + hitbox px + per-family bullet
  sizes → Level-designer; precise-mode/indicator feel + the pickup-radius call → Designer; red
  hue/alpha/slot → Artist; optional SHIFT hint → Writer; smoke-path SHIFT+shrunk-hitbox proof →
  Programmer. (Also flipped v18 index status to shipped ✅ — v1–v18 are shipped per the backlog.)

- 2026-06-06 (v14): `requirements/v14.md` added. **R92–R98 MUST/SHOULD**, **AC78–AC85**. One-file JSON
  save (versioned schema, per-user folder) + 5 lifetime counts + flush-only-on-GAME_OVER/quit + corrupt
  fallback + lifetime-stats screen. **Key BA stance — one governing principle anchors all five counts:**
  *a kill/destroy counts only at the exact code site that already calls `scoring.award` for that entity*
  (combat.py `a.hits<=0` / `e.hp<=0`, encounter.py `on_defeat`). That one rule resolves every kickoff
  edge question by reading the live code, not by inventing policy: GREEN→RED split children **don't
  count** (they're enemy *bullets*, not ships — never reach a destroy site); **bomb-flush and
  boss-arrival clears don't count** (silent `.clear()`, no award); **ram-consumes don't count** (player
  takes damage, no award); **boss minions DO count** as enemies (they're scored v5 Enemies); boss defeat
  counts toward `bosses_killed` only (its own entity, never `enemies_killed`); large asteroid = 1 (per
  entity, not per hit). **Rulings made (not delegated):** (1) **runs increments the instant a run
  begins** (fresh-world PLAY entry) — fires on initial start + each hold-R restart, NOT on resume/launch/
  game-over; so a quit-or-restarted-mid-game run still counts because it was counted at its *start*.
  (2) **Counting is decoupled from writing** — counters tick at event sites; the file writes only at a
  flush. This is the correctness spine: multiple flushes (GAME_OVER then quit-from-GAME_OVER) never
  double-count, and restart resets the world but NOT the process-lifetime counters (R94). (3) **highscore
  = max(stored, world.score) refreshed at every flush** — captures the run high-water mark, reflects the
  baked-in Score×2, never decreases. (4) **Fallback is per-field defensive** (R96): missing file →
  zeros; unparseable/non-object/unknown-version → all-zeros; otherwise coerce any missing/non-int/
  negative field to 0 — never crash, next flush overwrites. (5) **Smoke must not touch the real save
  file** (R98) — path overridable for headless. **Delegated:** stats-screen state placement+nav →
  Designer; layout/colors → Artist; labels+title → Writer; file path/atomic-write/counter wiring →
  Programmer. (Also flipped v12 index status to shipped ✅ — v1–v13 are shipped per the backlog.)
