# Brief — archived increment framings (v7–v12)

Frozen 2026-06-06 when the studio turned a new page. These are the Orchestrator's kickoff framings for
the v7–v12 increments, moved out of `../shared/brief.md` so that file holds only the theme + the
*current* increment. All of these shipped & passed QA; their final specs are canonical in each role
folder. Earlier framings (v2, v5) are in `brief-increments-v2-v5.md`.

---

## v7 increment (added 2026-06-05) — Bosses (periodic mothership boss fights)

> v1/v2/v5/v6 shipped & passed QA; v3 reorganized the KB; v4 added standing QA docs. The human now
> wants **bosses**: large-health-pool enemies with **learnable attack patterns** that interrupt the
> normal run on a **periodic breakpoint**. This is a big increment — it touches every role. Full build
> run (BA → Designer → Artist → Writer → Level-designer → Programmer → QA).

### Feature: bosses (human's words, lightly framed)
**The boss-fight loop:**
1. **Breakpoint trigger.** Every now and then a boss arrives. The trigger is **time- or point-based** —
   human's examples: *every 5 minutes* or *every 5000 points*. Designer/Level-designer pick **which
   metric and the exact value(s)**, and whether it repeats on a fixed interval or scales.
2. **Field clears + spawns freeze.** When the breakpoint fires, the **field clears fully** — reuse the
   **v6 bomb flush + flash visual** (the screen-covering flash) so it reads the same, but **this is a
   system-initiated clear: it does NOT consume a player bomb charge** and is not a player action. While
   the boss is active, **all regular enemy and asteroid spawns are disabled**.
3. **Boss entrance + movement.** A **slow-moving boss enemy appears**, travels in, and **settles at the
   vertical center of the screen**, then **moves slowly left and right** (oscillates) to make dodging
   harder. Bosses have a **large health pool** and a **moveset** (see Mothership below).
4. **Defeat + resume.** When the boss is defeated, the player is awarded a **big amount of points**, and
   the **normal loop resumes** — asteroids and regular enemies start spawning again — **until the next
   breakpoint** brings the next boss.

**First boss — the Mothership.** Large, slow, central-oscillating. Its moveset (a repeating attack
cycle — Designer locks order, timing, and whether it loops 1→2→3→4→1):
1. **Spawn 5 regular enemies** (the v5 REGULAR type).
2. **Spawn 2 heavy enemies** (the v5 HEAVY type).
3. **Spawn 7 scout enemies** (the v5 SCOUT type).
4. **Fire a fan of yellow bullets** that **midway split into 12 red bullets** flying outward **in all
   directions** (≈30° apart for an even 360° burst — Designer confirms counts/angles/split point).

### Design questions for the BA & Designer to nail down (delegate values — DO NOT assume)
- **Breakpoint:** time **vs** points **vs** both? Exact value(s)? Fixed interval or scaling per boss?
  First-boss timing. **Reconcile with AC13** (runs are typically 1–3 min): a 5-min/5000-pt gate may
  mean most runs never see a boss — Designer/Level-designer decide whether to lower it for this game's
  pace or accept bosses as a late-run event. **This is the #1 thing to resolve.**
- **Boss stats:** health pool (how many player hits), size/shape (Mothership = large geometry),
  entrance path + speed, the central oscillation amplitude + speed, vertical resting position.
- **Field-clear semantics on boss arrival:** reuse the v6 flush — confirm exactly what it clears
  (enemies / asteroids / enemy bullets) and what it spares (player bullets? pickups? cosmetics?), and
  that it awards **no score** and **costs no charge** (it's the system, not the player).
- **Spawn suppression:** while the boss is alive, freeze the v1 asteroid spawner + the v5 enemy spawner
  (and bonus-pickup drip? boss-minion drops?). Boss-spawned minions are the exception. How/when normal
  spawning re-enables after the kill.
- **Moveset cadence:** intervals between the 4 attacks, the order, looping, and whether the boss can
  attack during its entrance. Minion caps (does step 1 re-spawn 5 even if the last 5 are alive?).
- **Attack-4 detail:** yellow-fan count + spread; the **split trigger** ("midway" = screen midpoint?
  after N frames/distance?); the 12 red children's directions (even 360°?) + their speed/damage.

---

## v8 increment (added 2026-06-05) — Pause / Unpause + Q-hold to quit

> v7 shipped & passed QA. The human now wants a **pause system** and a **hold-to-quit gesture**.
> This is a moderate increment — it primarily touches the Programmer and the flow/HUD, but the full
> pipeline runs because controls and UX copy need to be specced, and the smoke-gate plan needs
> updating. Build run: BA → Designer → Writer → Programmer → QA (Artist is light; Level-designer
> likely no-op — Orchestrator will skip them if the BA/Designer confirm no economy impact).

### Feature: pause / unpause (human's words, lightly framed)

**Pause behaviour (Esc key)**
- **Esc now pauses/unpauses** instead of quitting. Pressing Esc while playing freezes all objects
  (player, bullets, enemies, asteroids, particles, boss) and all timers (buff durations, spawn
  timers, boss timers, flash timer, bomb lockout timer, popup timers, buff tick, run clock) in place.
- **Unpausing (Esc again)** resumes from the **exact same state** — all velocities, directions,
  and timer values exactly as they were when paused. Nothing expires during the pause.

**Pause screen**
- While paused, a screen **similar to the start screen** covers the game scene (semi-transparent
  overlay over the frozen game world). It shows hints: how to **unpause**, how to **restart**, and
  how to **quit** (using the Q-hold gesture).

**Q-hold to quit (any time)**
- **Q key held for ~0.5 s (≈ 30 frames @60 FPS)** quits the application from *any* state (START,
  PLAY, PAUSE, GAME_OVER).
- While Q is being held, a **round progress arc** appears in a corner of the screen — it fills as
  the hold progresses; releasing Q before the threshold cancels it cleanly.
- Old Esc-to-quit behavior is **removed**; Q-hold is the sole quit path.

### Design questions for the BA & Designer to nail down
- **What exactly freezes during pause?** Enumerate every timer/system: run frame counter, spawn
  timers, buff timers, boss moveset timer, boss osc, flash timer, bomb lockout, popup timers,
  survival-score tick, starfield scroll. Some (starfield) may be fine to keep running.
- **Does pressing Esc on START or GAME_OVER do anything?** (Pausing is only meaningful in PLAY.)
- **Q-hold threshold:** ~30 f (0.5 s) is the human's spec — confirm or adjust. Does Q-hold cancel
  a pause (i.e., does it work while paused too)?
- **Progress arc:** corner, size, color, whether it's always visible when Q is held regardless of
  game state, behavior if Q is released mid-hold.
- **Restart from the pause screen:** pressing R while paused — does it restart directly or unpause
  first? (Simplest: restart directly, no extra confirm step.)
- **Smoke-gate plan:** the smoke test must still exit 0 in 120 f. Pause is player-triggered
  (KEYDOWN Esc); the scripted smoke path never issues that key, so pause is a no-op for the smoke
  run. Verify nothing regresses. The Q-hold threshold also requires the Q key to be held, which the
  smoke path won't do — no change needed there either.
- **Boss damage model:** does the boss collide-damage the player (ram)? boss-bullet damage. Is the
  **boss immune to the player's bomb flush**, or does the flush chip it / clear only its minions+bullets?
  (Edge case: player bombs mid-boss-fight.) Can the player's shots always hit the boss?
- **Reward:** the "big amount of points" on defeat (flat value); do boss-spawned minions award normal
  score / drop pickups?
- **Boss HUD:** a boss health bar + label (Artist/Writer) — distinct from the player HP bar.
- **Smoke-test plan:** the headless `--smoke-test` (120 f) must stay green AND **exercise a boss** —
  seed/force a boss spawn early in the headless run so the field-clear + entrance + at least one attack
  step fire within 120 frames (QA/Programmer design the seed, like the v6 bomb seed). Keep AC1–AC38
  regression-clean.
- Keep everything renderable as **shapes + text**, single-screen, keyboard-only, no external assets.

### Notes (orientation only — Programmer owns the real touch-list)
- Likely touches: `config.py` (breakpoint value, boss HP/size/speed, oscillation, fan/split counts,
  reward), `entities/` (a Boss model + boss-state, reuse v5 enemy + green-split-style bullet logic for
  the yellow→red split), `systems/` (a boss/encounter manager that watches the breakpoint, runs the
  field-clear, gates the v1 asteroid + v5 enemy spawners, drives the moveset, awards points), `view/`
  (boss shape + boss health bar + yellow/red boss bullets; the flush flash already exists from v6),
  `input.py` unchanged. The **yellow→red split** strongly resembles the **v5 green→red splitting
  pellet** — reuse that machinery. The **field-clear flash** reuses the **v6 bomb flush/flash** —
  factor it so the boss manager can trigger it without a charge.

## v10 increment (added 2026-06-05) — Q-hold-to-quit on the START + GAME_OVER screens

> v8 shipped pause/unpause + a **Q-hold-to-quit gesture with a progress arc**. The v8 brief intended
> Q-hold to quit "from *any* state (START, PLAY, PAUSE, GAME_OVER)", but the shipped build only wired
> the gesture (and its arc) into **PAUSE**. The human now wants the **same gesture available on the
> START (game-start) screen and the GAME_OVER screen**. This is a **small extension** — it reuses the
> v8 mechanic verbatim; the work is enabling it in two more states + showing the quit hint there.

### Feature: Q-hold-to-quit on START + GAME_OVER (human's words, lightly framed)
- Holding **Q** for the v8 threshold (`PAUSE_QUIT_FRAMES = 30 f / 0.5 s`) on the **START screen** and on
  the **GAME_OVER screen** quits the application — exactly as it already does from PAUSE.
- The same **round progress arc** must appear while Q is held on these screens, filling toward the
  threshold and **cancelling cleanly on release before it completes** (reuse the v8 arc + reset logic).
- The **on-screen hint** for the gesture must be visible on both screens (the START screen should teach
  "hold Q  Quit"; the GAME_OVER key list — currently `R  Restart` with no quit hint — should add it).

### Design questions for the BA & Designer to nail down (delegate values — DO NOT assume)
- **Arc position on START / GAME_OVER.** In PLAY/PAUSE the arc is centered at `(300, 483)` under the
  pause panel. On START / GAME_OVER there's no pause panel — does the arc reuse the same center, sit by
  the relevant hint line, or go in a fixed corner? Artist owns the exact placement so it doesn't collide
  with existing START/GAME_OVER text.
- **Hold-state bookkeeping per state.** The Q-hold counter must arm/reset correctly when entering and
  leaving START and GAME_OVER (e.g. a partial hold carried across a restart must not instantly quit).
  Programmer confirms one shared hold counter is reset on every state transition.
- **Copy.** START quit hint + the GAME_OVER key-list quit hint (Writer; keep both width-safe at the
  established fonts). Confirm there's no stale "Esc Quit" text reintroduced.
- **Smoke gate.** Q-hold needs the Q key actually held, which the headless smoke path never does, so this
  stays a no-op for the smoke run — but the new render paths (arc drawn on START/GAME_OVER) must pass the
  v9 render-smoke (no draw raises + key rects don't overlap). QA confirms.

### Notes (orientation only — Programmer owns the real touch-list)
- Likely touches: `input.py`/the event handler (route Q key-down/up + the hold counter in START and
  GAME_OVER, not just PAUSE), `view/`/`hud.py` (draw the v8 arc on the START + GAME_OVER screens), and
  `story/` copy for the two hints. The arc draw + threshold + reset all **already exist from v8** — this
  is wiring them into two more states, not new mechanics. **Economy no-op** (Level-designer likely skip).

## v11 increment (added 2026-06-05) — Softer invulnerability blink (raise the alpha floor + smooth it)

> v10 shipped & passed QA. The human reports the **invulnerability animation is hard on the eyes**: the
> player ship currently **strobes between full opacity and fully invisible** (it skips drawing the ship on
> alternate 6-frame intervals — `view/render.py` `_draw_player`, gated on `p.invulnerable` + `p.blink_timer`).
> This is a **tiny, art-only visual tweak** — no gameplay, requirements, economy, or copy change. The
> i-frame/Shield mechanic, its duration, and its gameplay tell are all unchanged; only the *rendering* of
> the tell softens. Build run: **Artist → Programmer → QA** (BA / Designer / Writer / Level-designer SKIPPED —
> no requirements, design-number, copy, or economy impact).

### Feature: softer invulnerability blink (human's words, lightly framed)
1. **Raise the alpha floor.** Instead of oscillating between **100% and 0%** alpha (full → invisible), the
   ship should oscillate between **max (100%) and ~50%** alpha — it never fully disappears, so the strobe is
   far gentler on the eyes while still clearly reading as "invulnerable / flashing."
2. **Smooth the transition.** Rather than a hard on/off snap every 6 frames, the alpha should **change smoothly**
   (interpolated — e.g. a sine/triangle ease between the floor and the ceiling) across the invulnerability
   period, so it pulses rather than blinks.

### Decisions to nail down (Artist owns the alpha levers; Programmer owns the render mechanism)
- **Artist:** the exact **alpha floor** (the human said ~50% → ~128/255; confirm or set the precise value),
  the **pulse period** (today the half-cycle is 6 frames; pick the cycle length that reads as a smooth pulse,
  not a flicker), and the **interpolation curve** (sine vs triangle). Confirm the **Shield bubble ring**
  behaviour during the pulse (does the ring fade with the ship or stay solid as the distinct Shield tell?
  — it's the thing that separates a brief i-frame flash from the 5 s Shield, §V2.5). No new palette colours.
- **Programmer:** the current `_draw_player` draws polygons **straight to the screen**, so a partial alpha
  needs a **per-sprite alpha surface** (draw the ship onto a small `SRCALPHA` temp surface, `set_alpha`/per-pixel
  alpha, then blit) instead of an early-`return`. Keep it cheap (no per-frame surface alloc if avoidable —
  size once like the v6 flash surface). Drive the alpha from `p.blink_timer` so the phase still tracks the
  remaining i-frames/Shield. **Must not** regress the smoke gate, the v9 **render-smoke** (no draw raises),
  or any AC.
- **QA:** verify the ship is **never fully invisible** during invulnerability (floor respected), the pulse is
  smooth (alpha varies across frames, not a 2-state snap), invulnerability still ends correctly (ship returns
  to solid), Shield ring behaves per the Artist's call, and **no v1–v10 regression** + render-smoke + smoke gate green.

## v12 increment (added 2026-06-05) — Hold-R-to-restart (mirror the Q-hold gesture on PAUSE + GAME_OVER)

> v11 shipped & passed QA. The human now wants the **Restart (R)** action to require a **hold (~0.5 s)**,
> exactly like the v8/v10 Q-hold-to-quit gesture (with the same winding-up progress arc). Restart is only
> offered on the **PAUSE** and **GAME_OVER** screens, so the hold-R gesture is scoped to those two states.
> This is a **small extension that reuses the v8/v10 hold-gesture machinery** (threshold + arc + cancel-on-
> release + reset-on-transition) — but with a new twist the Q-only work never hit: on PAUSE and GAME_OVER
> **two** hold gestures (Q-quit and R-restart) now coexist on the same screen, so they need **independent
> hold counters** and **two non-overlapping arcs**. Build run: BA → Designer → Artist → Writer →
> Level-designer (likely no-op) → Programmer → QA — same shape as v10.

### Feature: hold-R-to-restart (human's words, lightly framed)
- On the **PAUSE** and **GAME_OVER** screens, the **R / Restart** action no longer fires on a single key
  press — it now **winds up while R is held** and only restarts once the hold reaches the threshold
  (reuse the v8 `PAUSE_QUIT_FRAMES = 30 f / 0.5 s` so quit and restart feel identical), then runs the same
  `reset_run()` → PLAY it does today.
- While R is held, a **round progress arc** appears (reuse the v8/v10 arc visual) and fills toward the
  threshold; **releasing R before it completes cancels cleanly** (no restart, counter resets).
- **START is excluded** (no Restart action there — START already starts on any key). PLAY is unaffected.
- The on-screen **hints** that currently read "R  Restart" (PAUSE pause-screen + the GAME_OVER key list)
  must teach the new gesture (e.g. "hold R  Restart"), staying width-safe and with no stale instant-restart copy.

### Design questions for the BA & Designer to nail down (delegate values — DO NOT assume)
- **Threshold reuse.** Confirm hold-R reuses `PAUSE_QUIT_FRAMES = 30 f` (or set a distinct restart threshold).
  Recommend reuse so the two gestures are symmetric.
- **Two coexisting gestures.** Q and R can both be held on PAUSE / GAME_OVER. There must be **two independent
  hold counters** (holding R must not fill the quit arc and vice-versa), and **both** counters reset on every
  state transition (so a partial R-hold can't survive a restart and instantly re-trigger). Programmer confirms
  the counter model; Designer confirms the reset-on-transition rule extends to the R counter.
- **Arc placement (Artist, the #1 layout risk).** A second arc now shares PAUSE and GAME_OVER with the existing
  Q-quit arc (`(300,483)` on PAUSE, `GAMEOVER_ARC_CENTER=(300,545)`). Place the R-restart arc so it **doesn't
  overlap the Q arc or any text rect** (anchored to its own "hold R Restart" hint line), and passes the v9
  render-smoke anti-collision check on both screens.
- **Copy (Writer).** Rewrite the PAUSE restart hint (`PAUSE_HINT_RESTART`) and the GAME_OVER key list
  (`GAMEOVER_KEYS`) restart clause to teach the hold gesture; keep width-safe; no stale "R Restart" (instant) text.
- **Smoke gate.** Hold-R needs R actually held, which the headless smoke path never does, so restart stays a
  no-op for the smoke run — but the new arc render paths must pass the v9 render-smoke (no draw raises + rects
  don't overlap). QA confirms; economy is a no-op (Level-designer likely skip).

### Notes (orientation only — Programmer owns the real touch-list)
- Likely touches: the event handler / hold-counter logic (a second `r_hold_frames` counter alongside
  `q_hold_frames`, armed in PAUSE + GAME_OVER, R key-down/up + threshold → `reset_run()`; both counters reset
  on all state transitions), `view/`/`hud.py` (draw the reusable arc for the R gesture on PAUSE + GAME_OVER —
  the `hud.draw_quit_arc` factored in v10 can likely be generalised to a `draw_hold_arc(center, frac)` used by
  both), and `story/` copy for the two restart hints. The threshold + arc + cancel + reset all **already exist
  from v8/v10** — this is adding a parallel counter + a second arc + scoping it to PAUSE/GAME_OVER, not new
  mechanics. **Economy no-op** (Level-designer likely skip). **Do not let R-hold leak into START or PLAY.**
