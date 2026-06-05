# v6 increment — Bombs (panic button) + control remap (Z fire / X bomb)

Owner: lead-game-designer · Date: 2026-06-05 · Status: complete
Inputs: `workspace/requirements/requirements.md` v6 §18–§23 (R45–R55, AC30–AC38, **§20 Open-values table**),
`workspace/shared/brief.md` v6 increment, `workspace/shared/handoffs.md` (entries 34–36), GDD v2 above
(the diamond pickup economy §V2.2/§V2.4/§V2.5, the §V2.7 collision pipeline, the buff-pill HUD §V2.6),
GDD v5 above (it is **extended, not replaced** — the roster + split stay exactly as specced).
Implements: **R45–R54 (MUST)** — locks every §20 lever (charge **max cap**, collect-at-full rule, **flush
score rule**, inter-bomb lockout, flash **duration**, the full post-remap keymap, the bomb-pickup economy
slot, and the `--smoke-test` activation seed). **R55 (post-bomb spawn lull) is COULD/Level-designer-owned —
I state intent + a recommended default, the number is theirs.** Flash **color/opacity** and the bomb-pickup
**shape/glyph** are the **Artist's** (§20); spawn **weight/scarcity** is the **Level-designer's** (§20).

> This section **appends** to v1+v2+v5; all prior numbers still hold. The bomb is the long-deferred v2
> **R35** "screen-clear" idea (GDD §V2.8 marked it OUT for v2) — now promoted, **charge-gated**, and fully
> specified. Frames are @60 FPS; seconds shown alongside. The bomb pickup is a **6th kind in the existing
> v2 diamond framework** — it reuses that entity/collision/drift/cap machinery verbatim, so no new spawn
> path or pickup geometry is introduced.

## V6.1 Feature in one line
When the screen is about to bury you, slam **X**: a brief white **flash** flushes every hostile off the
field — but you carry only **2 charges** (cap **4**), refilled solely by a **rare diamond pickup**, so a
bomb is a hard, deliberate choice, never a crutch.

## V6.2 The bomb charge pool (R45) — every §20 number LOCKED

| Lever (§20) | Value (LOCKED) | Rationale |
|---|---|---|
| **Start count** (given by R45) | **2** | Fixed by the requirement; not a design lever. |
| **Max cap** | **4** | ≥2 per R45. Cap 4 lets the rare pickup build a small 2-bomb reserve (panic + one held spare) without ever letting the player hoard enough to trivialize the ramp. Start 2 ⇒ exactly **two** pickups to top off. |
| **Clamp** | `charges = clamp(charges, 0, 4)` | Never < 0 (R47 guard) and never > 4 (R51 pickup clamp). Integer state. |
| **Restart (R13)** | resets to **2** | Extends R31's restart-cleanup: no charge, flash, or lockout state leaks between runs (AC36). |

- The count changes **only** by **−1 on a successful activation (R46)** and **+1 on a bomb-pickup collect
  (R51)** — each by exactly 1. No time-based or kill-based regen (non-goal).
- **HUD readout** of the current count is required at all times during PLAY (R45). Style (icons ×N vs a
  `BOMBS: N` label) is **Artist + Writer** (§20); I only fix that it shows the integer 0–4 and updates
  the same frame the count changes (decrement on bomb, increment on pickup). It belongs with the other
  top-of-screen HUD furniture (SCORE top-left, HP bar top-right, buff pills under SCORE) — Artist places
  it so it does **not** collide with the §V2.6 buff-pill stack.

## V6.3 Bomb activation & the flush (R46, R48, R49) — what one press does

On a **key-down edge** of **X** during PLAY, **if `charges > 0`** and **not within the inter-bomb lockout
(V6.4)**: in this exact order, on that one frame —
1. **Decrement:** `charges -= 1` (so the HUD readout drops by 1 — AC30).
2. **Flush (R48):** bulk-clear the **live hostile entity lists** at this instant:
   - **all enemies** (REGULAR / HEAVY / SCOUT) — cleared;
   - **all asteroids / debris** — cleared;
   - **all enemy projectiles** — cleared, explicitly **including in-flight HEAVY green splitting pellets
     and any already-split RED child bullets**, plus SCOUT cyan and REGULAR red.
   - **SPARED (BA rulings, §R48 — restated as design law):** **player bullets** (keep flying), **all
     pickups** (the 5 v2 diamonds **+ the bomb pickup** — never flush a bomb pickup, that is
     self-defeating), and **particles / hit-feedback / starfield** (cosmetic). The flush touches **only**
     the three hostile lists.
3. **Flash (R50):** start the full-screen activation flash (V6.5). Tied **1:1** to this successful
   activation — the 0-charge no-op (R47) and a lockout-blocked press produce **no flush and no flash**.
4. **Arm the lockout (V6.4).**

- **FLUSH SCORE RULE (§20) — LOCKED: NONE.** Destroying entities via the bomb flush awards **zero score**
  (confirming the BA's non-binding recommendation, R48). The bomb is a **survival tool, not a farming
  exploit** — letting it bank points would invert the risk/reward (you'd *want* to be swarmed so you could
  bomb for points). Concretely: the flush removes entities **without** routing them through the
  `systems/scoring.py` award sites — it is a silent despawn, not a "kill." The R11 score display is
  untouched (no flicker, no negative). Deterministic and trivial to verify (score is identical the frame
  before and after a bomb). *(Player bullets already in flight that subsequently hit a — now-cleared —
  target simply find nothing; they award nothing because their targets are gone. No special-casing.)*
- **Flush is "now," spawning resumes (R49):** the clear acts on what is alive **this instant**; it is **not**
  a suppression field. The normal spawner (v1 ramp + v5 kind-mix + v2 bonus economy) resumes on the very
  next frame unless the optional R55 lull is built (V6.7).
- **Activation-feel edge case (BA §22) — LOCKED intent:** the bomb is **always usable when `charges > 0`,
  independent of i-frame / shield state** (R18 / R27). It can be fired while invulnerable, on the same
  frame the player takes damage, mid-blink — none of that gates it. The bomb touches **only** the hostile
  lists + charge count + flash; it grants **no** i-frames and does **not** interact with the player's
  damage/shield resolution. (If a bomb and a lethal hit land the same frame, the §V2.7 collision step still
  resolves the player's damage as usual — the bomb does not retroactively save the player from a hit that
  already connected before the clear. Order: process input/bomb-flush **before** the §V2.7 player-damage
  step so a panic bomb on the key-down frame clears the bullets *before* they can hit — the intuitive
  "I bombed in time" feel. Programmer places the flush at the top of the frame's resolution, ahead of
  §V2.7 step 4.)

## V6.4 One-press-one-bomb + inter-bomb lockout (R53) — LOCKED

- **Edge-trigger is the primary guarantee:** a bomb fires only on the **key-down transition** of X (X
  down **this** frame, up **last** frame). Holding X drains **no** further charges across frames. This
  alone satisfies R53.
- **Inter-bomb lockout = `BOMB_LOCKOUT = 18 frames` (0.30 s)** — belt-and-suspenders. After a successful
  activation, X is ignored for 18 frames even on a fresh key-down. Two reasons: (a) hardens against any
  edge-detection slip, and (b) it equals the flash duration (V6.5), so the screen visually **settles before
  another bomb can fire** — you can't stack two white-outs into an unreadable strobe. 18 f is well below
  any human double-tap intent for a deliberate panic button, and with cap 4 + rare refills, chaining bombs
  is already a rare extreme. The lockout ticks down each frame and resets nothing on its own (a blocked
  press is a complete no-op, like R47).

## V6.5 Activation flash (R50) — Designer locks the TIMING, Artist owns color/opacity

- **Duration (Designer-owned timing, §20) — LOCKED: `FLASH_FRAMES = 18` (0.30 s).** A brief, snappy
  pop-and-fade — long enough to read as "something big happened," short enough not to blind the player
  during the very moment they panic-bombed (they need to see the now-clear field immediately).
- **Shape/overlay only (C2):** a single screen-covering rectangle (the full 600×800 window) drawn **on top
  of** the scene, **after** all entities/HUD, every frame the flash is active. No asset, no extra surface
  cost beyond one `draw.rect` with alpha.
- **Fade curve (Designer intent; Artist finalizes the exact alpha):** **linear fade-out** from a peak on
  the activation frame to fully transparent at frame 18. `alpha(f) = peak · (1 − f/18)` for `f` in `[0,18)`.
- **Intensity intent (Artist owns the final hex + peak alpha, §20):** a **bright near-white** flash; my
  design intent is a **peak opacity around ~75–80% (≈ alpha 190–205 / 255), NOT a full white-out** — the
  player should still faintly see the field clear *through* the flash, so the bomb reads as "everything got
  wiped" rather than "the screen blanked." Artist: confirm a white/very-pale-cyan tint that pops against the
  near-black space-blue background and is distinct from the cyan player-bullet / pale-blue Shield visuals.
  **Coordination note to Artist:** I've fixed **duration = 18 f** and **linear fade**; you own **color + peak
  alpha** — if you want a different peak or a 2-stage (flash-up then fade) curve, keep total duration at 18 f
  so it stays in lockstep with `BOMB_LOCKOUT` (V6.4).

## V6.6 The bomb-charge pickup (R51) — the v2 economy slot it occupies

The bomb pickup is a **6th kind added to the v2 diamond pickup framework** (GDD §V2.2/§V2.4/§V2.5) — it is
**not** a new spawn path. It inherits **all** v2 pickup mechanics verbatim:

| Property | Value (inherited from v2 §V2.4 unless noted) |
|---|---|
| `BonusKind` enum entry | **`BOMB`** — appended as the 6th kind (after Repair, Fan, Rapid, Shield, Score). |
| Entity / shape | **Diamond**, ~26 px point-to-point, 1 px outline + centered glyph — same as the 5 v2 pickups (Artist sets a **distinct color + glyph**, §20; Writer names it, suggest letter **`B`** or a bomb glyph). |
| Collision | circle **r = 13** (same forgiving scoop radius). |
| Motion | drifts **straight down 2.0 px/f**, no h-drift, **NOT** sped by the hazard ramp (same as v2). |
| On-screen cap | shares the v2 **cap of 3** simultaneous pickups. |
| Missed | scrolls off the bottom → removed silently, **no penalty**. |
| Collect | ship circle overlaps pickup circle → remove pickup, apply effect. **Always allowed** (independent of i-frames/shield), same as v2. |
| **Effect** | **`charges = min(4, charges + 1)`** — restores **exactly +1** bomb charge, **clamped to the cap** (R51). |
| **Type** | **Instant, one-shot** (like Repair R24): **no timer, no buff-pill** — it is **exempt from the R29 active-buff-timer HUD** and only changes the V6.2 charge readout. It may reuse the **transient collect-popup** style (e.g. a brief "+1 BOMB" near the charge readout — Writer's text, Artist's look), mirroring Repair's "+40" popup. |

- **COLLECT-AT-FULL-CAP RULE (§20) — LOCKED: WASTED (consumed, no effect).** Collecting a bomb pickup while
  already at cap 4 **consumes the pickup** (it is removed from play) and the count **stays at 4** — the +1
  is simply clamped away. **Not "refused."** Rationale: "refused / left in play" would leave an
  uncollectible diamond drifting through the ship and **occupying one of the 3 on-screen pickup slots** until
  it scrolls off — confusing ("why won't it pick up?") and it starves the other pickups. "Wasted" matches
  the existing v2 semantics exactly: **Repair at full HP** already clamps and is consumed (§V2.2/V2.3), so
  BOMB-at-full-cap behaves identically — one consistent "instant pickup at the ceiling = consumed, clamped"
  rule across the whole economy. Either way the count never exceeds the cap (R51). Because the pickup is the
  **rarest** kind and cap 4 needs two collects from a start of 2, hitting full cap is uncommon anyway.
- **Sole replenishment (R51):** this pickup is the **only** way to gain charges — no time/kill regen.
- **DELEGATED to the Level-designer (§20):** the bomb pickup's **spawn weight / scarcity** in the v2 kind-
  selection table. Design **intent** (the level-designer owns the final number, mirroring how I left the v5
  weights to them): the bomb pickup must be the **rarest** kind — **clearly below** the current lowest v2
  weights (Shield/Score at 15% each, GDD §V2.5). A bomb is meant to be a scarce treasure, not a regular drop.
  **Recommended starting point: a single-digit weight (~5–8%)**, with the other five kinds' weights
  renormalized around it — but the Level-designer sets and balances the final value against AC13 (V6.8). It
  should reach the player via the **same drip + enemy-drop mechanisms** as the other pickups (no special
  path); whether it is eligible for the enemy-drop roll or drip-only is the Level-designer's call (drip-only
  would make it even scarcer — acceptable).

## V6.7 Post-bomb spawn lull (R55, COULD) — intent only; the number is the Level-designer's

R55 (a brief spawn lull right after a bomb to make the flush feel impactful) is **COULD-grade and the
Level-designer's value** (§20). My design **intent**, should they build it: a **short** breather of about
**30 frames (~0.5 s)** of paused/reduced spawning immediately after an activation — just enough that the
freshly-cleared screen stays clear for a beat (the payoff for spending a charge) before the ramp
repopulates. **It must be small and is the one lever here that could *lengthen* a run, so it is explicitly
bound by AC13** (V6.8) — if a lull pushes runs past 3 min, shorten or drop it. Absent the lull, R49 governs:
spawning simply resumes next frame. This is optional; v6 passes without it.

## V6.8 AC13 protection (1–3 min runs) — explicit

The bomb's net effect on run length is **small and bounded**, so **AC13 holds**:
- **Few activations per run.** Start **2** + cap **4**, refilled only by the **rarest** pickup → an expert
  sees at most a **handful** of flushes in a 1–3 min run. The bomb shortens individual *dangerous moments*;
  it does **not** alter the v1 §3 ramp, the v5 kind-mix, or the spawn rates (R49 — spawning resumes).
- **No farming incentive.** Flush score = **NONE** (V6.3), so there is no reason to court a swarm to bomb it
  — runs aren't artificially prolonged for points.
- **The only lengthening lever is the optional R55 lull**, which is **bounded** (~0.5 s, V6.7) and is the
  Level-designer's to keep inside the band. A handful of half-second lulls per run is negligible against the
  1–3 min target.
- **The pickup respects the economy:** it shares the v2 on-screen cap (3) and drift speed, adds no new
  entities to the frame budget beyond an occasional diamond, and **replaces** weight in the existing kind
  table (V6.6) rather than adding a new spawn stream — so it does not increase pickup volume.

→ Net: the bomb changes the *texture* of survival (a panic escape valve), not the ramp's *shape*. The
Level-designer re-confirms run length after setting the pickup weight + any R55 lull (V6.8 is the bar).

## V6.9 Control remap — the full post-remap keymap (R52) — LOCKED

The complete keymap after the remap (movement/start/restart/quit **unchanged** from GDD §3; only fire moves
and bomb is added):

| Action | Key(s) | Notes |
|---|---|---|
| Move | `←/→/↑/↓` **and** `A/D/W/S` | **Unchanged** (R3). 4-directional, additive, ship clamped on-screen. |
| **Fire** | **`Z`** | **Canonical fire key** (R52). Replaces v1 Space-fire for R7/R8. **Still cooldown-gated** (12 f baseline) and **still honors v2 Rapid ×0.5 and Fan 3-beam modifiers** (R25/R26) — the remap is *key-binding only*, the weapon logic is untouched. |
| **Bomb** | **`X`** | **New** (R46). Edge-triggered key-down; activates only with `charges > 0` and outside the 18-f lockout (V6.4). |
| Start run | any key | **Unchanged** (R16) — from the Start screen, any key begins. |
| Restart | `R` | **Unchanged** (R13) — from Game Over; resets charges to 2 (V6.2). |
| Quit | `Esc` (+ window close) | **Unchanged** (R13). |
| Pause *(optional, R22)* | `P` | **Unchanged** if present; the bomb is **not** usable while paused (R46). |

- **Space (old fire key):** the canonical fire key is **Z**, and **all on-screen copy MUST teach Z** (R52 /
  AC35) — a stale "press Space to fire" string is a defect. Whether Space is retained as a **silent
  secondary alias** for fire is the **Programmer's discretion** (R52); if kept, it is **not advertised**
  anywhere in the copy. My recommendation: **drop Space as the fire key** for clarity (Z is the only taught
  fire key), but a silent Space alias is harmless if the Programmer prefers it. (Note: Space may still act as
  an "any key" to *start* a run from the Start screen — that's the R16 start binding, not firing.)
- **Copy update (Writer, R52/AC35):** the **Start-screen instructions** and any **in-game controls text**
  must show **"Z = fire · X = bomb"** (plus the unchanged Move / R restart / Esc quit). Final wording =
  Writer; this is a MUST for AC35.

## V6.10 --smoke-test design for the bomb (R54 / AC37) — must run headlessly

The 120-frame `--smoke-test` must **exercise one full bomb-activation lifecycle** (charge > 0 → X activates
→ flush clears the live hostile lists → flash appears/fades → charge decrements) **without raising** (R54).
A natural 120-f run won't reliably present a charge + a well-timed press, so the smoke path **seeds** the
activation (wiring = Programmer's choice, mirroring the v2 `SMOKE_BONUS_*` and v5 `SMOKE_SPLIT_*` patterns).
The run starts with **2 charges** by default (R45), so no charge seeding is needed — only a **scripted X
key-down on a known frame**. Design intent + recommended deterministic seed:

- **Compose with the existing v5 split seed for maximum coverage.** The v5 smoke seed (§V5.6) already puts a
  green pellet at `(300,300)` that **splits ~frame 16** into **3 red children**, and the v1 smoke seed puts
  **3 asteroids + 1 enemy** on frame 1. So if the smoke harness simulates an **X key-down at frame ~20**
  (just after the split), that **single** bomb flush clears, in one shot: the **seeded enemy**, the
  **remaining asteroids**, **and the 3 red split children** — directly exercising R48's hardest clause
  ("flush clears already-split red children") **for free**, headlessly. Charge goes **2 → 1**; the flash
  runs frames ~20→~38 then play continues to 120.
- **Recommended seed frame: `SMOKE_BOMB_FRAME ≈ 20`** (any frame in ~`[18, 30]` works — the requirement is
  only that **hostiles are on-screen** at the press so the flush has targets and that it lands **after** the
  v5 split so the children-clear path is covered). The Programmer wires the scripted X press; this section
  fixes the **timing** so the activation is guaranteed in-budget and maximally covering.
- **Coordination note to QA (important — this *intentionally* updates the v5 smoke observation):** firing
  the bomb at ~f20 **flushes the v5 split children**, which the v5 smoke section (§V5.6) previously expected
  to "update to f120." This is **deliberate and strictly better coverage**: the children are still observed
  **born at ~f16 and updating for frames ~16–19** (so v5 **AC27** — split lifecycle pellet→3-fan→children-
  update — is still satisfied), and then the **v6 bomb at ~f20 clears them**, exercising v6 **AC32** (flush
  removes split children) in the same run. QA should assert, in order: (a) the green pellet splits into
  exactly 3 red children ~f16 that update for ≥1 frame (AC27 ✓), (b) at ~f20 the X press flushes **all**
  enemies/asteroids/enemy-bullets (incl. those children) while **player bullets + any pickups survive**
  (AC32 ✓), (c) the charge readout dropped **2 → 1** (AC30 ✓), and (d) a flash overlay was active post-f20
  and faded (AC33 ✓). The smoke still **exits 0 after exactly 120 frames** (R14/R33/R43 preserved).
- **OPTIONAL richer seed (Programmer's discretion — strengthens AC31/AC36 headlessly, not required):** drive
  X-key-downs at **~f20** (2→1) and **~f45** (1→0) for **two** successful activations, then a **third X at
  ~f70 while charges == 0** to exercise the **R47/AC31 no-op** (no flush, no flash, no decrement, stays 0)
  in the headless path. (Each activation must respect the 18-f lockout, so space the presses ≥18 f apart —
  20/45/70 satisfy that.) The MUST is one full activation (~f20); the extra presses are a cheap way to also
  prove the 0-guard and one-press-one-bomb without a human.

## V6.11 New tuning constants (programmer-ready — add to `config.py`)

All v6 numbers gathered for the single-source-of-truth config. Names are suggestions; values are the spec.

```
# ── v6 bombs / panic button (GDD §V6.x) ─────────────────────────────────────
BOMB_START        = 2      # charges at run start / after restart (R45; fixed by req)
BOMB_CAP          = 4      # max charges; clamp [0, BOMB_CAP] (R45)
BOMB_LOCKOUT      = 18     # frames X is ignored after a successful activation (R53; == FLASH_FRAMES)
FLASH_FRAMES      = 18     # full-screen activation flash duration, 0.30 s (R50)
FLASH_PEAK_ALPHA  = 200    # ~78% peak opacity; linear fade to 0 over FLASH_FRAMES (Artist finalizes)
FLASH_COLOR       = (255, 255, 255)   # near-white; Artist owns final tint (art_spec wins)
BOMB_FLUSH_SCORE  = 0      # flush awards NO score (R48 ruling, §20)
# Post-bomb spawn lull (R55, COULD) — Level-designer owns the value; 0 = no lull
BOMB_SPAWN_LULL   = 30     # frames of paused/reduced spawning after a bomb (~0.5 s); level_spec may set/zero

# Bomb-charge pickup = 6th kind in the v2 diamond framework (GDD §V6.6 / §V2.4)
#   BonusKind.BOMB : instant, +1 charge clamped to BOMB_CAP, collect-at-full = WASTED, NO buff-pill.
#   color + glyph = Artist (art_spec); spawn weight/scarcity = level-designer (rarest kind, ~5-8% rec).

# Smoke seed (GDD §V6.10) — scripted X key-down(s); start charges already = BOMB_START
SMOKE_BOMB_FRAME  = 20     # simulate X key-down ~f20 (after the v5 ~f16 split) → flush clears the
                           #   enemy + asteroids + the 3 red split children; charge 2->1; flash f20->~f38
# (optional richer plan: presses at 20 / 45 / 70 → two activations then a 0-charge no-op; see §V6.10)
```

- `BOMB_FLUSH_SCORE = 0` is a constant rather than inline so QA can see the "none" ruling at a glance and the
  flush stays a **silent despawn** (it must **not** call the scoring award path — V6.3).
- The flash is **one `draw.rect` with per-frame alpha** over the full window, drawn **after** entities + HUD
  (V6.5). `BOMB_LOCKOUT == FLASH_FRAMES` by design (V6.4) — keep them equal if either is retuned.

## V6.12 v6 requirement coverage map
| Req | Where realized |
|---|---|
| R45 charge pool (start 2, cap 4, clamp, restart→2, HUD) | §V6.2 |
| R46 bomb activation (X, edge, −1, flush+flash) | §V6.3, §V6.4 |
| R47 0-charge no-op | §V6.3 (guard), §V6.4 |
| R48 screen-flush (clears enemies/asteroids/enemy-bullets incl. split children; spares pickups + player bullets; **score NONE**) | §V6.3 |
| R49 flush = on-screen-now, spawning resumes | §V6.3, §V6.7 |
| R50 activation flash (brief full-screen fade, shapes-only, 1:1 with success) | §V6.5 |
| R51 bomb pickup (6th v2 kind, +1 clamped, instant/no-pill, collect-at-full=WASTED, sole refill) | §V6.6 |
| R52 control remap (Z fire w/ cooldown+Rapid/Fan intact, X bomb, copy updated) | §V6.9 |
| R53 one-press-one-bomb (edge + 18-f lockout) | §V6.4 |
| R54 smoke gate + bomb activation seeded | §V6.10 (seed @~f20, clears the v5 split children) |
| R55 post-bomb lull (COULD) | §V6.7 (intent + ~30 f rec; Level-designer owns) |

## V6.13 Open questions / handoffs to downstream roles
- **Artist (next):** owns (a) the **bomb-pickup diamond** — a **distinct color + glyph** vs the 5 v2 diamonds
  (Repair-green / Fan-amber / Rapid-cyan / Shield-pale-blue / Score-gold) and vs the enemy/bullet hues
  (R51/R42); suggest a glyph reading as "bomb" (Writer names it, likely letter **`B`**); (b) the **HUD
  bomb-count readout** (icons ×N or `BOMBS: N`) placed clear of the §V2.6 buff-pill stack; (c) the
  **full-screen flash** — I've **locked duration = 18 f and a linear fade**; you own the **color (near-white
  intent) + peak alpha (~190–205 rec, NOT a full white-out)** and may use a 2-stage curve as long as total
  duration stays 18 f (it's in lockstep with the lockout). Optional: a small "+1 BOMB" collect popup style
  mirroring Repair's "+40".
- **Writer:** the **bomb-pickup name**, its **diamond glyph/letter** (suggest `B`), the **HUD bomb-count
  label** (e.g. `BOMBS`), and the **updated controls copy** — Start-screen + in-game must show **"Z = fire ·
  X = bomb"** (drop any stale Space-fire text) — this is a **MUST** for AC35 (R52).
- **Level-designer:** owns the **bomb-pickup spawn weight / scarcity** in the v2 kind table — make it the
  **rarest** kind (clearly below the 15% Shield/Score floor; **~5–8% recommended**, renormalize the others),
  via the existing drip/enemy-drop mechanisms; and the optional **R55 post-bomb lull** value (~30 f rec, or
  0). **Re-confirm AC13** (1–3 min) after setting both (V6.8 is the bar) and that the bomb pickup + the v6
  smoke X-press coexist with the ramp + the v5 split seed (they will — one rare diamond + one scripted press).
- **Programmer:** no blocking unknowns — every §20 lever is a concrete number above (§V6.2/§V6.4/§V6.5/
  §V6.6 + the §V6.11 constants). The flush is a bulk clear of the three hostile lists **before** the §V2.7
  player-damage step, awards **no** score, spares pickups + player bullets; X is **edge-triggered** with an
  18-f lockout; the bomb pickup is a **6th `BonusKind`** reusing the v2 diamond path; the smoke seed (§V6.10)
  scripts an X key-down ~f20 so the activation (and the split-children clear) runs in-budget.
