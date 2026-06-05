# v2 increment — Pickup bonuses + modular MVC refactor

Owner: lead-game-designer · Date: 2026-06-05 · Status: complete
Inputs: `workspace/requirements/requirements.md` v2 §8–§12 (R23–R35, AC14–AC21), `workspace/shared/brief.md` v2 increment,
`CLAUDE.md` v2 ground rules, GDD v1 above (baseline numbers).
Implements: R23–R33 (MUST) + **R34 Score-multiplier (IN)**. **R35 Screen-clear: OUT** (see §V2.8).

> This section **appends** to v1; all v1 numbers (player 100 HP, fire cooldown 12 f, i-frames 60 f,
> bullet 10 px/f, 600×800 @60 FPS) still hold and are the baseline buffs modify. Frames are @60 FPS;
> seconds shown alongside. Values here are the **design source of truth**; the **level-designer** owns
> the spawn *rates/weights/balance* (§V2.5), the **Artist** owns exact glyphs/hex, the **Writer** owns
> buff names + HUD labels.

## V2.1 Feature in one line
Occasionally a **diamond bonus pickup** drifts down the field; fly over it to grab a buff — instant
hull repair, or a timed gun/shield/score upgrade — a quick risk/reward "go get it" beat per run.

## V2.2 The buff set (final) — kind, type, value, duration

Five bonus kinds. **Repair** is an *instant one-shot*; the other four are *timed buffs* with HUD timers.

| # | Kind | Letter | Type | Effect (exact) | Duration |
|---|------|--------|------|----------------|----------|
| R24 | **Repair** | `+` | instant | `hp = min(100, hp + 40)` — **+40 HP, clamp to max, no overheal, no stored charge** | — (instant) |
| R25 | **Spread / Fan** | `F` | timed | Fire **3 beams** per shot at **−12° / 0° / +12°** from straight up; each beam is a normal player bullet, speed **10 px/f**, same 1-hit damage. Replaces the single shot; reverts on expiry. | **8 s / 480 f** |
| R26 | **Rapid** | `R` | timed | Fire-cooldown **× 0.5** → **12 f → 6 f** (~5/s → ~10/s). Reverts to 12 f on expiry. | **8 s / 480 f** |
| R27 | **Shield** | `S` | timed | **Full invulnerability**: no damage from asteroids, debris, enemy contact, or enemy bullets. Reuses the **R18 blink** visual for the whole window. Reverts to vulnerable on expiry. | **5 s / 300 f** |
| R34 | **Score ×2** | `2` | timed | All score gains (asteroid/enemy/time bonus) **× 2** while active. | **10 s / 600 f** |

Notes / rationale:
- **Spread fan geometry:** centre beam velocity `(0, −10)`; side beams `(±10·sin12°, −10·cos12°) ≈ (±2.08, −9.78)` px/f. 24° total fan widens the kill lane while staying mostly upward. **Locked at 3 beams** (modest bullet count, cheap collisions); programmer may bump to 5 only if trivially cheap — 3 is the spec.
- **Rapid × Spread combine** (different types coexist): a 3-beam fan every 6 frames. Strong but both are short and timed — intended power spike, not a permanent state.
- **Shield vs. R18 i-frames:** player is invulnerable if **either** `iframes > 0` (brief post-hit, R18) **or** `shield > 0` (R27). Both drive the same blink. Artist *may* add a faint steady ring to distinguish shield from the brief blink, but reusing the blink alone satisfies R27.
- **Repair value** = +40 (two small-asteroid hits / one enemy ram). Meaningful but not a full reset.

## V2.3 Stacking & refresh model (R30, R31) — deterministic

- **Different timed types coexist.** Spread, Rapid, Shield, Score each carry an **independent countdown**
  on the player (`buff_timers: {kind: frames_remaining}`). They never interfere.
- **Re-collecting an active timed buff = hard refresh.** Set `frames_remaining = full duration`
  (**reset, not add**). This is also the **refresh cap**: remaining can never exceed one full duration,
  so spam-collecting cannot bank unbounded time. Effects **do not multiply** (two Spreads = one fan,
  not a double-fan; two Score×2 = ×2, not ×4).
- **Repair never stacks.** It is applied immediately and discarded (clamp to 100, no overheal, no
  charges). Two Repairs the same frame each just clamp — never exceeds 100.
- **Same-frame multi-pickup is safe:** apply collected bonuses in a deterministic order (BonusKind enum
  order), each independently — no contradictory state possible.
- **Expiry → clean revert (R31):** at `frames_remaining == 0` the buff is removed and the player returns
  to baseline (single forward shot, 12 f cooldown, vulnerable, ×1 score). The timer entry is deleted.
- **Restart resets everything (R31/AC19):** restart clears `buff_timers`, the repair-popup timer, and
  all on-screen bonus pickups along with the rest of the world — zero leak into the next run.

## V2.4 Bonus pickup entity (R23) — shape, motion, collision

- **Shape:** a **diamond** (square rotated 45°), ~**26 px** point-to-point, 1 px outline, with the
  **kind letter centred** (table V2.2). Diamond reads as "collectible" — distinct from round asteroids,
  triangular ship/enemy. Color-coded per kind (Artist finalizes hex; intent below).
- **Collision:** circle, **radius 13** (forgiving — easy to scoop while dodging).
- **Motion:** drifts **straight down at 2.0 px/f**, **no horizontal drift**, and is **NOT** affected by
  the hazard speed-ramp bonus (§7.2) — so a bonus is always slow enough to intercept. No rotation needed.
- **Collect:** ship circle (r=13) overlaps bonus circle (r=13) → remove pickup, apply effect, brief
  collect feedback. Collection is **never** blocked by i-frames/shield (buffs are good to grab anytime).
- **Missed:** scrolls off the bottom (`y − 13 > 800`) → removed silently, **no penalty** (R23).
- **On-screen cap:** **max 3 bonuses** at once (skip a drip spawn if at cap; enemy-drop still allowed
  up to the cap). Level-designer may lower this but not the spec's purpose.
- **Color intent** (Artist owns hex): Repair = green · Fan = amber/orange · Rapid = cyan · Shield =
  pale blue/white · Score×2 = gold.

## V2.5 Spawn approach (R28) — **both** mechanisms; rates handed to level-designer

Mechanism is fixed here; **all numbers below are level-designer-owned defaults** to tune in `level_spec`.

1. **Timed drip** (primary): a bonus appears on a cadence. **Default ≈ one every 12 s (720 f)** with a
   small jitter (±2 s), subject to the §V2.4 on-screen cap of 3. Spawn x uniform in `[20, 580]`,
   `y = −13`.
2. **Enemy drop** (secondary, flavor/reward): a destroyed enemy fighter has a **default ≈ 15 % chance**
   to leave a bonus at its death point.
3. **Kind-selection weighting** (default, level-designer tunes): Repair **30 %**, Fan **20 %**,
   Rapid **20 %**, Shield **15 %**, Score×2 **15 %**. (Repair weighted highest as the "safety" pickup.)

**Smoke reachability (R28/R33/AC20) — REQUIRED:** the `--smoke-test` path must exercise a *full*
spawn→collect→apply→expire lifecycle inside 120 frames. Spec for the programmer + level-designer:
- On smoke frame ~2, **force-spawn one bonus directly in the player's path** (e.g. a **Rapid** pickup at
  the player's x, a little above it) so the scripted sweep collects it within ~15–25 frames.
- In smoke mode, **shorten that buff's duration to ~60 f** (or seed it already near expiry) so it
  **expires by ~frame 90** — guaranteeing apply *and* expire are both observed before the 120-f cap.
- Keep it deterministic (fixed RNG seed, as v1 §11). Exact seeding wiring: programmer; the level-designer
  confirms the smoke seed makes a bonus reachable.

## V2.6 Active-buff HUD indication (R29) — layout intent

Drawn during PLAY (frozen on GAME_OVER). Artist owns exact px/hex; Writer owns letters/labels.

- **Buff pill stack:** a **vertical stack at top-left, under the SCORE text.** SCORE sits at `(12,10)`;
  pills start at `(12, 36)`, each row ~**18 px** tall, stacked downward. Max 4 timed buffs → stack ends
  ~`y=108`, clear of the play area.
- **One pill per active timed buff** = `[colored 14×14 box with the kind letter] [shrinking bar 40×6]`.
  The bar fills `frames_remaining / full_duration` and drains left-to-right as it counts down; bar color
  matches the buff. A tiny seconds number is optional (Writer's call).
- **Stable order:** pills are ordered by **BonusKind enum order (Fan, Rapid, Shield, Score)** and a pill
  only shows while its timer > 0 — so pills never reorder/jump as buffs come and go.
- **Repair has NO pill** (it's instant, R29): instead show a **transient green "+40" popup** near the HP
  bar (top-right) for ~**30 f**, and the HP bar visibly jumps. Writer owns the popup text.
- Keep it compact — HUD-clutter is a named v2 risk; 4 small pills + a transient popup is the ceiling.

## V2.7 Updated collision/order rules (supersedes §8 for v2)

Per frame, after movement, resolve in this order (skip anything already destroyed this frame):
1. **Player bullets × asteroids** → bullet removed; asteroid −1 hit; if ≤0 destroy + score(×mult) + particles.
2. **Player bullets × enemies** → bullet removed; enemy HP −1; if ≤0 destroy + score(×mult) + particles
   + **roll enemy-drop** (§V2.5).
3. **Player × bonus pickups** → collect: remove pickup, apply buff (§V2.2/V2.3), collect feedback.
   *(Always allowed — independent of invulnerability.)*
4. **(player vulnerable: `iframes==0` AND `shield==0`) Player × {asteroid, enemy, enemy-bullet}** →
   apply that source's damage, remove the source, start R18 i-frames. First hit wins (one source/frame).
   **If Shield is active, this whole step is skipped (no damage taken).**
5. **Tick buff timers** (decrement each `frames_remaining`; on reaching 0, revert to baseline §V2.3).
6. If `health ≤ 0` → GAME_OVER.

Score with multiplier: `score += base_points × (2 if score_mult active else 1)` at each award site.

## V2.8 R34 / R35 decision
- **R34 Score ×2 — IN.** Trivial once the timed-buff framework exists (one multiplier at the award
  sites + one HUD pill). Adds a fun "press your luck while it's hot" beat. Specced above.
- **R35 Screen-clear / bomb — OUT (deferred).** It's an instant effect that swings balance (can trivialize
  dense fields / the difficulty ramp) and needs its own clear+score-attribution rules. Out of v2 scope to
  keep the increment focused; revisit in a later pass if desired. Its absence does not fail v2 (COULD).

## V2.9 Module map — the MVC-ish refactor target (R32, AC21)

Refactor the single `workspace/game/main.py` into the package below. **No line cap** (C3 retired) —
optimize for clarity; each module earns its place. `main.py` stays the **thin entry point** and keeps
the `--smoke-test` contract (R33).

```
workspace/game/
├─ __init__.py        # marks the package
├─ main.py            # THIN entry: parse --smoke-test, set dummy SDL env (if smoke), build App, run, exit
├─ config.py          # ALL tuning constants — v1 numbers (§7.3) + v2 buffs (V2.2) + spawn defaults
│                     #   + the PALETTE (Artist's hex). Single source of truth; imports nothing game-side.
├─ app.py             # App/Game class: state machine (START/PLAY/GAME_OVER[/PAUSED]), the run loop,
│                     #   the --smoke-test harness (120-frame headless branch + smoke seeding hooks).
├─ world.py           # World/state container (entity lists, player ref, score, ramp timer, RNG) +
│                     #   enums: GameState, BonusKind. Plain data; no pygame, no rendering.
├─ input.py           # Input layer: real keyboard → an InputState (move dx/dy, fire, start, restart,
│                     #   quit); plus the SCRIPTED smoke provider — same InputState shape both paths.
├─ entities/
│  ├─ __init__.py
│  ├─ player.py       # Player model: pos, hp, iframes, shield, fire cooldown, buff_timers dict.
│  ├─ hazards.py      # Asteroid (small/large) + Enemy fighter models & their movement/fire data.
│  ├─ projectiles.py  # Player bullet + enemy bullet models/factories (incl. spread-fan factory).
│  ├─ bonus.py        # Bonus pickup model + the buff REGISTRY (kind → type/value/duration/letter/color).
│  └─ fx.py           # Particles + starfield (cosmetic models).
├─ systems/           # pure-ish update logic over World; no rendering
│  ├─ __init__.py
│  ├─ spawning.py     # spawn timers + difficulty ramp; bonus drip + enemy-drop; smoke seeding.
│  ├─ physics.py      # integrate motion, scroll starfield, clamp player, despawn off-screen.
│  ├─ combat.py       # the §V2.7 collision pipeline: hits, damage, i-frames/shield, bonus collect.
│  ├─ buffs.py        # apply-on-collect, tick timers, expiry→revert, restart reset (R30/R31).
│  └─ scoring.py      # award points (with score×2 mult), survival tick, session high score.
└─ view/             # READ-ONLY rendering; reads World+config, mutates nothing
   ├─ __init__.py
   ├─ render.py       # draw the scene per state (starfield, entities, particles, bonuses).
   └─ hud.py          # score, health bar, BUFF PILLS (V2.6), repair popup, start/game-over text.
```

**Separation rules (the point of the refactor):**
- **Dependency direction:** `config` ← `entities` ← `systems` ← `app` → `view`. `input` feeds `app`.
  `view` and `systems` read `world`/`config`; **only `systems` (+ `app`) mutate `world`**; `view` never mutates.
- **entities** = data + tiny self-contained behavior only (no `pygame.draw`, no globals).
- **systems** = the verbs (spawn/move/collide/buff/score); operate on a `World` passed in.
- **view** = the nouns drawn; pure render from state.
- **config** = numbers + palette; **app** = orchestration, the loop, and the smoke harness.
- Programmer may merge a *trivially tiny* pair (e.g. fold `fx.py` together, or `__init__` re-exports) but
  must keep the config / entities / systems / view / input / thin-main separation — that's what AC21 checks.

## V2.10 v2 requirement coverage map
| Req | Where realized |
|---|---|
| R23 bonus pickup entity | §V2.4; `entities/bonus.py`, `systems/spawning.py`, `systems/combat.py` |
| R24 repair (instant) | §V2.2; `systems/buffs.py` |
| R25 spread/fan (timed) | §V2.2; `entities/projectiles.py`, `systems/buffs.py` |
| R26 rapid (timed) | §V2.2; `entities/player.py`, `systems/buffs.py` |
| R27 shield/invuln (timed) | §V2.2, §V2.7; `entities/player.py`, `systems/combat.py` |
| R28 spawning (drip + drop) | §V2.5; `systems/spawning.py` |
| R29 active-buff HUD | §V2.6; `view/hud.py` |
| R30 stacking & refresh | §V2.3; `systems/buffs.py` |
| R31 expiry & restart cleanup | §V2.3; `systems/buffs.py`, `app.py` |
| R32 modular MVC refactor | §V2.9 (whole package) |
| R33 smoke gate preserved | §V2.5 smoke seeding; `app.py`, `input.py` |
| R34 score ×2 (IN) | §V2.2, §V2.7; `systems/scoring.py`, `view/hud.py` |
| R35 screen-clear | **OUT** (§V2.8) |

## V2.11 Open questions / handoffs to downstream roles
- **Artist (next):** finalize the **diamond pickup** hex per kind (§V2.4 color intent) + the letter glyph
  rendering; design the **buff-pill** look (14×14 letter box + 40×6 shrink bar) and the **green "+40"
  repair popup** (§V2.6); confirm shield's blink (and optional distinguishing ring) reads clearly.
- **Writer:** name the five bonuses and provide the **HUD letters/short labels** (table V2.2 letters are
  placeholders) and the repair-popup text.
- **Level-designer:** own the **spawn numbers** (§V2.5) — drip cadence, enemy-drop %, kind weights,
  on-screen cap — balanced for 1–3 min runs; **confirm the smoke seed** makes a bonus reachable+expirable
  in 120 f; sanity-check that the buff power spikes don't break the AC13 run-length target.
- No blocking unknowns for the programmer — every buff value, the stacking model, and the module map are
  concrete above.

---
---

