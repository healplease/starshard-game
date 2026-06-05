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
