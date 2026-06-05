# Test Plan — "Starshard" (v1 + v2)

Owner: qa-tester · Date: 2026-06-05 · Status: complete · Type: standing doc (not a per-run verdict)
Companion to: `feature_inventory.md` (Feature IDs F1–F32 are the shared key). Verdicts go in `qa_report/`.

> **What this is.** The reusable procedures for verifying Starshard: a **smoke-test plan** (the headless
> 120-frame gate), a **regression-test plan** (re-verify all v1+v2 features after any change), and
> **per-feature checklists** with concrete, observable pass/fail steps. Run the smoke gate on *every*
> change; run the full regression suite before declaring a version done or after any non-trivial edit.
>
> **How to record a run.** Don't edit this plan with results — open a new dated section in `qa_report/`
> (PASS/FAIL per AC + evidence). This plan is the *method*; `qa_report/` is the *log*.

---

## 0. Setup (do this once per session)

```powershell
# From the repo root (c:\Users\olhav\Documents\MultiAgentApproach)
$env:SDL_VIDEODRIVER="dummy"; $env:SDL_AUDIODRIVER="dummy"   # headless drivers (smoke/regression-by-logic)
```
- Interpreter: `.\.venv\Scripts\python.exe` (Python 3.14.3 · pygame-ce 2.5.7 / SDL 2.32.10).
- For **[Play]** checks needing a real window, run WITHOUT the dummy drivers (or in a new shell):
  `.\.venv\Scripts\python.exe workspace\game\main.py`.
- **Note on headless QA:** a live human-driven window can't be observed from the headless CI environment.
  This repo's standing practice (see `qa_report/`) is to verify [Play] behaviours by **driving the real
  logic/view code directly** — import the real `World`/systems, assert behaviour, and draw to a dummy SDL
  surface. Each checklist below states the observable, regardless of whether a human or a harness drives it.

---

## 1. SMOKE-TEST PLAN — the headless gate (R14, R33 / AC1, AC2, AC20)

**Purpose.** A fast, deterministic, no-human gate proving the game initializes, runs, and shuts down
cleanly — and (v2) that a **full bonus lifecycle** runs inside the cap. This is the first thing to run
after *any* code change.

### 1.1 How to run
```powershell
$env:SDL_VIDEODRIVER="dummy"; $env:SDL_AUDIODRIVER="dummy"
.\.venv\Scripts\python.exe workspace\game\main.py --smoke-test ; Write-Output "EXIT=$LASTEXITCODE"
.\.venv\Scripts\python.exe -m game.main --smoke-test          ; Write-Output "EXIT=$LASTEXITCODE"  # package-importable
.\.venv\Scripts\python.exe -m compileall -q workspace\game                                          # no syntax/import errs
```

### 1.2 Expected result
- **Exit code 0**, both invocations. (Last confirmed: **2026-06-05, exit 0.**)
- Banner `pygame-ce 2.5.7 (SDL 2.32.10, Python 3.14.3)` prints; **no traceback**, **no window**, **no
  audio device**, **no hang** (hard 120-frame cap → `sys.exit(0)`).
- Runs in ~2–3 s. Repeat **3×** — exit 0 every time (determinism; fixed RNG seed `1234`).
- `compileall` prints nothing / exits 0.

### 1.3 What the smoke run actually exercises (so "exit 0" means something)
The smoke branch (`app.run` + `systems/spawning.seed_smoke*`, `input.smoke_input`) deterministically:
1. Forces **PLAY** immediately and seeds **3 asteroids + 1 enemy** on frame 1 (`seed_smoke`) → spawning,
   movement, enemy AI/fire, player firing, and the full collision pipeline all execute.
2. Drives **scripted input** — a slow left-right sweep, firing every frame (cooldown still gates shots).
3. On **frame 2** seeds a short-duration **Rapid** pickup at `(300, 700)` — the player's x, 20 px above —
   inside the 26 px collect range (`seed_smoke_bonus`, dur forced to 60 f).
4. Runs exactly **120 frames**, then exits 0.

**The seeded bonus lifecycle it exercises (AC20):**
| Phase | ~Frame | Observable in instrumentation |
|---|---|---|
| spawn | 2 | a Rapid `Bonus` appears in `world.bonuses` at (300,700) |
| collect | ~2–3 | overlap (centre-dist 20 < 26) → pickup removed, `buff_timers[RAPID]` set |
| apply | ~3–62 | `player.fire_cooldown == 6` (12→6) while active |
| expire | ~62–63 | `buff_timers[RAPID]` deleted → cooldown reverts to 12 |
| baseline | 63–120 | run continues at baseline; exits 0 at 120 |
(Prior runs measured collect @f2, expire @f61 — both well inside 120. The exact frame may shift ±2 with
harness changes; what matters is **apply AND expire both observed before frame 120**.)

### 1.4 Smoke PASS criteria (all required)
- [ ] `main.py --smoke-test` exits **0**, 3× stable, no traceback/window/audio/hang. *(AC1, AC2)*
- [ ] `-m game.main --smoke-test` exits **0** (package importable as the entry point). *(AC21)*
- [ ] `compileall` clean (no syntax/import warnings). *(AC21)*
- [ ] The seeded Rapid bonus completes **spawn→collect→apply→expire** within 120 f without raising.
      *(AC20 — verify with the §1.5 instrumented harness when in doubt.)*

> **FAIL → route to programmer** with the traceback / the lifecycle phase that didn't happen. A non-zero
> exit, a hang, or a missing lifecycle phase is a hard fail (these are MUST-tier R14/R33).

### 1.5 Optional lifecycle probe (when "exit 0" isn't enough evidence)
To *prove* the lifecycle (not just exit 0), drive the real smoke loop with `buffs.apply`/`buffs.tick`
instrumented and assert `collected_frame`, the cooldown seen while active (`== 6`), and `expired_frame`.
Build it as a scratch harness, run it, record the numbers in `qa_report/`, then delete it (don't commit
scratch). This is how the v2 report produced `{'collected_frame': 2, 'expired_frame': 61, 'rapid_seen': True}`.

---

## 2. REGRESSION-TEST PLAN — full re-verify after any change

**Purpose.** After *any* code change (a fix, a tuning pass, a refactor), confirm nothing in v1 **or** v2
broke. Use this before declaring a version done or routing a PASS to the orchestrator.

### 2.1 Order of operations
1. **Smoke gate first** (§1). If it fails, stop and route to programmer — no point regressing further.
2. **Code-shape checks** (fast, [Code]): F29 (modular, imports clean), shapes/text-only (no asset files).
3. **v1 MUST suite** (F1–F14): every MUST must pass — a v1 MUST failure blocks the release.
4. **v1 SHOULD/COULD** (F15–F19): acceptance-checked because implemented; a failure is logged, and is
   blocking only if it's actually a regression of previously-passing behaviour.
5. **v2 MUST suite** (F20–F30): every MUST must pass.
6. **v2 COULD** (F31 Score×2): verify because implemented. (F32 screen-clear stays OUT — confirm absence
   is still intentional, not an accidental half-build.)
7. **Targeted re-check** of whatever the change touched (use `feature_inventory.md` module column to find
   the affected F#s) + its immediate neighbours.

### 2.2 Pass bar (from `requirements/requirements/`)
- **v1 ships only if R1–R14 all pass** (SHOULD/COULD don't block). **v2 is done when R23–R33 pass AND
  AC14–AC21 pass AND no v1 regression.** R34 is bonus-verify; R35 is intentionally absent.
- Record one dated verdict section in `qa_report/` with a per-AC PASS/FAIL table + evidence.

### 2.3 Regression coverage map (run every checklist in §3)
| Suite | Features | Gate |
|---|---|---|
| Smoke + code-shape | F14, F29, F30 | AC1, AC2, AC20, AC21 — **must pass** |
| v1 MUST | F1–F13 | AC3–AC12 — **must pass** |
| v1 SHOULD/COULD | F15–F19 | AC13 + observation — log; block only on true regression |
| v2 MUST | F20–F28 | AC14–AC19 — **must pass** |
| v2 COULD (IN) | F31 | AC16/17/18 — verify (present) |
| v2 deferred (OUT) | F32 | confirm still intentionally absent |

### 2.4 Known non-blocking item to re-confirm (not re-litigate)
- **AC13** (F15) long-run caveat: confirm runs still terminate and the ramp still escalates. Do **not**
  re-fail it for expert-dodger length — that's the documented, parked caveat (`feature_inventory §4`).

---

## 3. PER-FEATURE CHECKLISTS

Each: **what to do → what you must observe to PASS**. `[Smoke]` checks ride the gate in §1; `[Play]`
checks need a run or a logic/render harness; `[Code]` checks are inspection. Module references are in
`feature_inventory.md`.

### v1 — base game

**F1 — Fixed window (R1) [Play]**
- Launch the game. **PASS:** a single non-resizable **600×800** window titled "Starshard"; the *world*
  (starfield, hazards) scrolls downward while the camera stays fixed. No second screen, no scroll camera.

**F2 — Player ship (R2) [Play]**
- Observe the ship at run start. **PASS:** a cyan upward-pointing **triangle** sits near **bottom-centre**
  (~`(300,720)`) with a small bright core dot.

**F3 — Movement + clamp (R3 / AC3) [Play]**
- Hold arrows, then WASD, including diagonals; then shove hard into each edge for several seconds.
- **PASS:** ship moves on both axes (additive, diagonals work); the **whole triangle stays on-screen** —
  it clamps to `x∈[14,586]`, `y∈[15,785]` and never shows past any edge.

**F4 — Auto-scroll starfield (R4 / AC4) [Play]**
- Touch **no** keys for several seconds; also watch on START and GAME_OVER.
- **PASS:** stars drift **downward continuously with zero input**, in 3 visibly different parallax speeds,
  wrapping at the bottom. Scrolling runs in every state (screen never feels dead).

**F5 — Asteroids + contact damage (R5, R9 / AC5) [Play]**
- Watch the top; let an asteroid touch the ship (outside i-frames/shield).
- **PASS:** small + large rocks spawn at the top and descend (varying speed/size); contact **reduces HP**
  (−20 small / −30 large) and consumes the rock.

**F6 — Enemy that shoots (R6, R9 / AC6) [Play]**
- Let an enemy enter and reach its strafe band; let one of its bullets hit you.
- **PASS:** a magenta chevron descends, then strafes side-to-side, and **fires bullets aimed at the ship**;
  an enemy bullet on contact **reduces HP** (−15). Ramming an enemy deals −40 and destroys it.

**F7 — Player weapon + cooldown (R7 / AC7) [Play]**
- Hold Space. **PASS:** cyan bullets travel straight **up** at a **limited rate** (~5/s baseline — not one
  per frame, no continuous laser). Bullets despawn off the top.

**F8 — Combat collisions/removal (R8 / AC7) [Play]**
- Shoot an asteroid (small=1 hit, large=2) and an enemy (2 hits).
- **PASS:** the player bullet is consumed on hit; small rock dies in 1 hit, large in 2 (flashes white on
  surviving the first), enemy dies in 2; destroyed objects are **removed** and emit a particle burst.

**F9 — Damage collisions, first-hit-wins (R9 / AC9) [Play]**
- Engineer a frame where two hazards overlap the ship at once.
- **PASS:** exactly **one** damage source applies that frame (first hit wins), the source is removed, and
  i-frames start. HP never double-deducts in one frame.

**F10 — Health + HP bar (R10 / AC9) [Play]**
- Watch the top-right bar as you take hits. **PASS:** starts full (100); the bar shrinks proportionally and
  changes colour **green → amber (<40) → red (<20)**.

**F11 — Score + display (R11 / AC8) [Play]**
- Destroy rocks/enemies and survive several seconds. **PASS:** `SCORE nnnnn` (top-left, 5-digit) **rises**
  by +10/+20/+50 on kills and **+1 per full second** survived; visible at all times during PLAY.

**F12 — Game over (R12 / AC10) [Play]**
- Take lethal damage. **PASS:** at HP≤0 play **freezes and dims**, and a centred **GAME OVER** + final
  `SCORE` (+ `BEST`) appears.

**F13 — Restart + quit (R13 / AC11) [Play]**
- From START press any key (→PLAY). Die, press **`R`**. Then press **`Esc`** / close the window.
- **PASS:** any key starts; `R` begins a **fully reset** run (score 0, HP full, all entities/timers/buffs
  cleared, ship re-centred) **without relaunching**; `Esc`/close exits cleanly with no traceback.

**F14 — Smoke test (R14 / AC1, AC2) [Smoke]** — see §1. **PASS:** exit 0 after exactly 120 frames, dummy
drivers, simulated input, no hang, 3× stable.

**F15 — Difficulty ramp (R15 / AC13) [Play]**
- Play (or simulate) a long run; sample density over time.
- **PASS:** spawn rate / enemy count / enemy fire rate / hazard speed / large-rock share **increase over
  time** per `level_spec §3` (asteroid interval `max(22,64−0.47t)`, enemy cap `min(6,2+t//20)`, etc.); the
  field is clearly denser/faster by ~90 s and **every run terminates**. *(Non-blocking caveat: expert
  pure-dodging may exceed 3 min — `feature_inventory §4`; don't re-fail on that.)*

**F16 — Start screen (R16) [Play]**
- Launch; observe before pressing a key. **PASS:** centred **STARSHARD** title, pitch line, control hints,
  and a **blinking** "Press any key to fly", starfield scrolling behind.

**F17 — Hit/destroy feedback (R17) [Play]**
- Hit a large rock once (don't kill it); then kill any object. **PASS:** large rock **flashes white** for
  a few frames when it survives a hit; on any destroy, a **6-particle burst** appears at the death point.

**F18 — I-frames + blink (R18) [Play]**
- Take a hit; immediately try to take another within ~1 s.
- **PASS:** for **60 frames** after a hit the ship is invulnerable (a second contact deals **0**), and the
  ship **blinks** (visible on alternate ~6-frame intervals) for the window.

**F19 — Session high score (R19 / AC10) [Play]**
- Finish a run, restart, beat it, finish again. **PASS:** GAME_OVER shows **`BEST nnnnn`**; it holds the
  session max across restarts (and resets only when the process exits).

### v2 — bonuses + refactor

**F20 — Bonus pickup entity (R23 / AC14) [Play]**
- Watch for a diamond; fly over one; let another scroll past uncollected.
- **PASS:** a colour-coded **diamond + kind letter** drifts straight down at a steady slow speed; flying
  the ship over it **removes it and applies its effect** (+ a small collect burst); a **missed** bonus
  leaves the bottom with **no penalty** (HP/score unchanged, no buff). Max **3** on screen at once.

**F21 — Repair, no overheal (R24 / AC15) [Play]**
- Collect a `+` Repair at partial HP, then again at/near full HP.
- **PASS:** HP rises by **+40** (e.g. 30→70); from ≥60 it **clamps to 100** (no overheal, no stored
  charge); a transient green **"+40"** popup shows by the HP bar; **no persistent pill** appears.

**F22 — Spread/Fan (R25 / AC16) [Play]**
- Collect `F`; fire; wait 8 s for expiry; fire again.
- **PASS:** while active each shot is a **3-beam fan** (−12/0/+12°); on expiry it **reverts to a single
  forward shot**.

**F23 — Rapid (R26 / AC16) [Play]**
- Collect `R`; hold fire; wait for expiry.
- **PASS:** fire rate **visibly doubles** (cooldown 12→6 f) while active; **reverts** to baseline on expiry.

**F24 — Shield (R27 / AC16) [Play]**
- Collect `S`; ram an asteroid / sit in bullets while active; wait for expiry; take a hit.
- **PASS:** while active the ship takes **zero damage** from all sources, shows the **blink + a bubble
  ring**; on expiry it becomes **vulnerable** again (ring gone). Invuln holds if **either** shield or
  post-hit i-frames are active.

**F25 — Bonus spawning (R28 / AC14, AC20) [Play]/[Smoke]**
- Play a couple of minutes; also kill many enemies with bullets.
- **PASS:** bonuses appear via **timed drip** (~every 10–14 s, first one ~10–14 s in) **and** as a ~**15%
  drop from bullet-killed enemies** (ram-kills never drop); kinds follow the weight mix (Repair most
  common); never more than 3 on screen. *(Smoke path proves spawn is reachable headlessly — §1.)*

**F26 — Active-buff HUD (R29 / AC17) [Play]**
- Hold several timed buffs at once; watch the top-left under SCORE.
- **PASS:** one **pill per active timed buff** = coloured letter box + a **shrinking timer bar** draining
  left→right; pills in **stable order F, R, S, 2** (never reorder); a pill vanishes when its timer hits 0.
  **Repair shows no pill** (only the transient popup).

**F27 — Stacking & refresh (R30 / AC18) [Play]**
- Collect Fan; before it expires collect Fan again; also hold Fan+Rapid+Shield+Score together; collect two
  Repairs near full HP.
- **PASS:** re-collecting **refreshes to full** (timer bar jumps back to full, **not** added beyond full);
  effect does **not** double (still 3 beams, not 6); different timed buffs **coexist** independently;
  Repair **never stacks** (just clamps to 100).

**F28 — Expiry + restart cleanup (R31 / AC16, AC19) [Play]/[Smoke]**
- Let buffs expire (revert to baseline). Then, with buffs/bonuses live, die and press `R`.
- **PASS:** each buff reverts cleanly at 0 (single shot / cd 12 / vulnerable / ×1 score). After restart:
  `buff_timers=={}`, `bonuses==[]`, `repair_popup_timer==0`, HP/score/i-frames at baseline — **no buff,
  timer, or pickup leaks** into the new run.

**F29 — Modular architecture (R32 / AC21) [Code]**
- Inspect `game/` and run the import checks.
- **PASS:** multiple focused MVC-ish modules (config / entities / systems / view / input + **thin
  `main.py`**); the package **imports cleanly** as a script, via `-m game.main`, and under `compileall`;
  **no single-file line cap** enforced (C3 retired); rendering only via `pygame.draw.*` + `SysFont` text —
  **no external image/sound/asset files referenced** (also satisfies C2/AC12 for the shapes-only rule).

**F30 — Smoke gate + lifecycle (R33 / AC20) [Smoke]** — see §1. **PASS:** exit 0 after exactly 120 frames
post-refactor **and** the seeded Rapid completes spawn→collect→apply→expire without raising.

**F31 — Score×2 (R34 / AC16, AC17, AC18) [Play]**
- Collect `2`; destroy something and survive a few seconds while active; watch its pill; wait for expiry.
- **PASS:** all score gains (kills **and** the survival tick) **double** while active (e.g. enemy 50→100);
  it has its **own HUD pill** with a timer; **reverts to ×1** on expiry; re-collect refreshes (no ×4).

**F32 — Screen-clear / bomb (R35) — OUT [Code]**
- **PASS (intentional absence):** no screen-clear pickup exists — `R35` is deferred (GDD §V2.8), not in the
  `BonusKind` enum, no HUD/effect. Confirm it's **still** intentionally absent (not an accidental
  half-build). Its absence does **not** fail v2.

---

## 4. Quick command reference

```powershell
# Smoke gate (run on every change)
$env:SDL_VIDEODRIVER="dummy"; $env:SDL_AUDIODRIVER="dummy"
.\.venv\Scripts\python.exe workspace\game\main.py --smoke-test ; "EXIT=$LASTEXITCODE"
.\.venv\Scripts\python.exe -m game.main --smoke-test          ; "EXIT=$LASTEXITCODE"
.\.venv\Scripts\python.exe -m compileall -q workspace\game

# Play the game (real window — for [Play] checks; run without the dummy drivers)
.\.venv\Scripts\python.exe workspace\game\main.py
```

*Maintenance: when `feature_inventory.md` gains/loses a feature, add/remove its checklist here in the same
change. This plan stays method-only; record outcomes in `qa_report/`.*
