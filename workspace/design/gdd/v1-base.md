# Game Design Document — "Starshard"

Owner: lead-game-designer · Date: 2026-06-05 · Status: complete
Inputs: `workspace/requirements/requirements.md` (R1–R22, AC1–AC13), `workspace/shared/brief.md`, `CLAUDE.md`
Implements: every MUST (R1–R14). SHOULD items R15–R18 are specced as build-now. COULD items
R19–R22 are specced as optional and clearly marked so they can be cut to protect the line budget.

> Everything here is shapes-only, keyboard-only, single fixed screen, target **60 FPS**. All
> numbers are in pixels-per-frame (px/f) at 60 FPS unless noted. Numbers are tuned starting points;
> the **level-designer** owns final difficulty values (R15) and may override the ramp table.

---

## 1. Title & pitch
- **Title:** Starshard
- **Pitch:** Pilot a lone scout ship through an endless scrolling starfield — dodge asteroids,
  gun down enemy fighters, and push your score as high as you can before the ship is destroyed.

## 2. Core loop
The 1–3 second moment, repeated for a 1–3 minute run:

1. **Read** the descending field of asteroids and enemy fighters.
2. **Weave** the ship between hazards (arrow/WASD movement, clamped to screen).
3. **Shoot** upward (Space) to clear asteroids and kill fighters before they reach/shoot you.
4. **Score** ticks up per kill; **difficulty ramps** so the field gets denser/faster.
5. **Take damage** → health drops → eventually **die** → **Game Over** shows score → **press R** to
   instantly retry and try to beat it.

Why it's fun: tight dodge-vs-shoot tension, a visible score to beat, instant restart keeps the
play→die→retry loop frictionless. One satisfying loop, no menus.

## 3. Controls (keyboard only)
| Action | Keys | Notes |
|---|---|---|
| Move | `←/→/↑/↓` **and** `A/D/W/S` | 4-directional, additive; diagonals allowed. Ship clamped on-screen (R3). |
| Fire | `Space` | Cooldown-gated (R7); holding fires at the fire-rate, not every frame. |
| Start run | any key / `Space` | From Start screen (R16). |
| Restart | `R` | From Game Over only (R13). |
| Quit | `Esc` (also window close) | Clean exit from any state (R13). |
| Pause *(optional, R22)* | `P` | Toggles a PAUSED overlay; ignore if cut. |

## 4. Screen states (state machine)
```
            any key                health<=0                 R
   START ─────────────► PLAY ───────────────► GAME_OVER ─────────► PLAY (full reset)
     ▲                   │  P (optional)          │ Esc
     │                   ▼                        ▼
     └────────────── PAUSED (optional)          quit
```
- **START (R16):** title, one-line pitch, control hints, "Press any key". Starfield scrolls behind.
- **PLAY:** the game. Spawns, movement, firing, collisions, scoring, difficulty ramp all active.
- **GAME_OVER (R12):** freeze the field, dim it, show **final score** + **high score** (R19, optional)
  + "Press R to restart, Esc to quit".
- **PAUSED (optional, R22):** halt updates, draw "PAUSED" overlay, `P` resumes.
- **Reset on restart (R13):** score=0, health=full, all entity lists cleared, ramp timer=0, player
  re-centered at start position. No process relaunch.

## 5. Window, world & coordinate conventions
- **Window:** 600 × 800 px, fixed, non-resizable (R1). Origin top-left, +y points **down**.
- **Forward flight** = world scrolls **downward** past a player that sits near the bottom (R4).
- Frame budget assumes ≤ ~120 active entities total (caps below) to protect FPS and the line budget.

---

## 6. Entities & behaviors

### 6.1 Player ship (R2, R3)
- **Shape:** upward-pointing triangle, ~**28 px** wide × **30 px** tall. Collision: circle, radius **13**.
- **Start position:** centered horizontally, near bottom — `(x=300, y=720)`.
- **Movement:** `speed = 5 px/f` per axis (≈300 px/s). Add per pressed direction; **clamp** the
  ship's bounding box fully inside the window (R3) — never off-screen.
- **Health (R10):** `100 HP`, single life (health pool model). Reaches 0 → GAME_OVER.
- **I-frames (R18):** on taking damage, **60 frames (1.0 s)** of invulnerability; ship **blinks**
  (visible every other ~6-frame interval). No damage can apply during i-frames.
- **Firing (R7):** Space spawns a player bullet from the nose; **cooldown 12 frames** (≈5 shots/s).
  Holding Space auto-fires at that rate — no per-frame stream.

### 6.2 Player bullet (R7, R8)
- **Shape:** small rect **4 × 12 px** (cyan). Collision: its bounding rect.
- **Velocity:** straight up, `10 px/f`.
- **Lifetime:** despawn when `y < -12` (off top).
- **Effect:** on hitting an asteroid or enemy, the bullet is removed and applies **1 hit** of damage
  to the target (R8). One bullet hits one target.
- **Cap:** soft cap ~20 on screen (cooldown makes this natural; no hard enforcement needed).

### 6.3 Asteroid / debris (R5, R8, R9)
Two sizes, spawned at the top with random x and downward drift.
| Size | Radius | Hits to destroy | Speed (down) | H-drift | Score | Damage to player |
|---|---|---|---|---|---|---|
| Small | 12 px | 1 | 2.5–4.0 px/f | ±0.5 px/f | **10** | **20** |
| Large | 26 px | 2 | 1.5–2.8 px/f | ±0.4 px/f | **20** | **30** |
- **Spawn x:** uniform within `[radius, 600-radius]`. **Spawn y:** `-radius` (just off top).
- **Mix:** 70% small, 30% large at spawn.
- **Collision shape:** circle of the listed radius.
- **Hit feedback (R17):** large asteroid that survives a hit flashes white for ~5 frames; on destroy,
  emit a small shape-burst (see 6.7).
- **Despawn:** when `y - radius > 800` (off bottom) — no score, no penalty (player dodged it).
- **Damage:** on contact with the player (and player not in i-frames), apply listed damage, then the
  asteroid is **destroyed** (consumed by the hit) and triggers i-frames.

### 6.4 Enemy fighter — "the shooter" (R6, R8, R9)
The required enemy that shoots back. One type is enough.
- **Shape:** downward-pointing triangle / chevron, ~**26 px** wide × **24 px** tall (magenta).
  Collision: circle radius **13**.
- **HP:** **2** player-bullet hits to destroy. **Score on kill: 50.**
- **Spawn:** at top, `y=-24`, random x in `[40, 560]`.
- **Movement (entry → strafe):**
  - Phase A (entry): descend at `2 px/f` until `y ≥ 120`.
  - Phase B (strafe): hold a y-band; move horizontally at `±2 px/f`, reversing direction at the
    screen edges (`x` kept within `[20, 580]`). Continue a slow descent of `0.3 px/f`.
  - **Despawn** if it ever reaches `y > 820` (flew off bottom) — no score.
- **Firing (R6):** every **75 frames** (1.25 s) while in Phase B, fire **one** enemy bullet **aimed
  at the player's current position** (compute unit vector to player, scale to bullet speed).
- **Damage on contact (R9):** ramming the player deals **40** damage, destroys the enemy, triggers
  i-frames.
- **Cap:** max **6** enemies alive at once (skip enemy spawn if at cap).

### 6.5 Enemy bullet (R6, R9)
- **Shape:** circle radius **5 px** (orange-red). Collision: circle.
- **Velocity:** fixed aim vector at fire time, magnitude `4.5 px/f` (does not home).
- **Lifetime:** despawn when off any screen edge (`x/y` outside `[-10, 610]×[-10, 810]`).
- **Effect (R9):** on hitting the player (not in i-frames), apply **15** damage, remove the bullet,
  trigger i-frames. Enemy bullets do **not** collide with asteroids or each other.
- **Cap:** soft cap ~40; oldest despawns first if exceeded (cheap safety, rarely hit).

### 6.6 Starfield backdrop (R4)
- Purely cosmetic; no collision. Conveys forward flight, scrolls **independent of input** (R4).
- **Stars:** ~**70** points across 3 parallax layers:
  | Layer | Count | Size | Scroll speed (down) | Color brightness |
  |---|---|---|---|---|
  | Far | 35 | 1 px | 1.0 px/f | dim |
  | Mid | 25 | 2 px | 2.0 px/f | medium |
  | Near | 10 | 3 px | 3.5 px/f | bright |
- **Wrap:** when a star's `y > 800`, respawn it at `y = 0` with a new random x. Runs in all states
  (Start, Play, Game Over) so the screen never feels dead.

### 6.7 Hit/destroy feedback particles (R17, optional-but-cheap)
- On any destroy (asteroid or enemy), spawn **6 tiny squares** (2×2 px) at the death point with
  random velocities in `[-3, 3] px/f` on each axis and a **20-frame** lifetime, fading/shrinking.
- Pure decoration; capped at ~60 particles total; first to expire. Cut entirely if line budget is tight.

---

## 7. Scoring, difficulty & numbers (single source of truth)

### 7.1 Scoring (R11)
- Destroy small asteroid: **+10** · large asteroid: **+20** · enemy fighter: **+50**.
- Score shown top-left at all times during PLAY and on GAME_OVER.
- **High score (R19, optional):** keep the session max in memory; show on GAME_OVER as "BEST: n".
- Survival/time bonus is intentionally **not** used (keeps scoring legible); level-designer may add a
  small per-second tick if desired.

### 7.2 Difficulty ramp (R15) — owned by level-designer, these are defaults
Let `t` = seconds elapsed in the current run (frames / 60).
- **Asteroid spawn interval:** `max(25, 60 − 0.40·t)` frames. (1.0/s → ~2.4/s, floors at ~87 s.)
- **Enemy spawn interval:** `max(70, 150 − 0.90·t)` frames. (every 2.5 s → every ~1.17 s by ~89 s.)
- **Hazard speed bonus:** add `min(2.0, 0.02·t)` px/f to every asteroid's downward speed.
- Net effect: dense, fast field by ~90 s, so most runs end within the **1–3 min** target (R15/AC13).

### 7.3 Master numbers table
| Thing | Value |
|---|---|
| Window | 600 × 800, 60 FPS |
| Player size / collision radius | 28×30 / r=13 |
| Player speed | 5 px/f per axis |
| Player health | 100 HP, 1 life |
| I-frames | 60 frames (1.0 s), blinking |
| Player fire cooldown | 12 frames (~5/s) |
| Player bullet | 4×12, 10 px/f up |
| Asteroid small | r=12, 1 hit, 2.5–4.0 px/f, +10, 20 dmg |
| Asteroid large | r=26, 2 hits, 1.5–2.8 px/f, +20, 30 dmg |
| Asteroid mix | 70% small / 30% large |
| Enemy | r=13, 2 HP, +50, 40 ram dmg, cap 6 |
| Enemy entry speed | 2 px/f to y=120, then strafe ±2, descend 0.3 |
| Enemy fire interval | 75 frames (1.25 s), aimed |
| Enemy bullet | r=5, 4.5 px/f aimed, 15 dmg |
| Starfield | 70 stars / 3 layers, speeds 1.0/2.0/3.5 |
| Asteroid spawn interval | max(25, 60 − 0.40·t) frames |
| Enemy spawn interval | max(70, 150 − 0.90·t) frames |
| Hazard speed bonus | +min(2.0, 0.02·t) px/f |
| Particles | 6 per death, 20 f life, cap ~60 |

---

## 8. Collision rules (summary for the programmer)
Resolve once per frame, in this order, skipping anything destroyed earlier in the frame:
1. **Player bullets × asteroids** → bullet removed; asteroid loses 1 hit; if hits remaining ≤ 0,
   destroy + score + particles.
2. **Player bullets × enemies** → bullet removed; enemy HP −1; if HP ≤ 0, destroy + score + particles.
3. **(player not in i-frames) Player × {asteroid, enemy, enemy-bullet}** → apply that source's damage,
   remove the asteroid/enemy/bullet that hit, start i-frames. (Take at most one damage source per
   frame — first hit wins.)
4. If `health ≤ 0` → transition to GAME_OVER.

Collision math: circle-vs-circle uses squared-distance ≤ (r1+r2)²; player bullet (a rect) vs a
circle may be approximated as circle-vs-circle using half the bullet's height as radius — cheap and
good enough at this scale.

---

## 9. HUD layout (R10, R11)
Drawn during PLAY (and frozen on GAME_OVER):
```
┌────────────────────────────────────────────┐
│ SCORE 01230                    [█████░░░░░] │  ← score top-left; health bar top-right
│                                  HP         │
│                                             │
│                  · starfield ·              │
│                                             │
│                    ▼ enemy                  │
│              ●  asteroids   ●                │
│                                             │
│                    ▲ player                 │
└────────────────────────────────────────────┘
```
- **Score:** top-left, `(12, 10)`, white, zero-padded to 5 digits.
- **Health bar (R10):** top-right, a 120×14 px outlined bar at `(468, 12)`; green fill proportional
  to `health/100`, turns amber < 40, red < 20. (Text "HP n/100" optional next to it.)
- **High score (R19, optional):** small, top-center, "BEST n".
- **Start screen:** centered title "STARSHARD", pitch line, controls, "Press any key to fly".
- **Game Over:** centered "GAME OVER", "SCORE n", "BEST n" (if R19), "R restart · Esc quit".

## 10. Placeholder visuals (Artist will formalize the palette — R/ C2)
All shapes, no assets. Suggested intent (Artist owns exact hex):
- Background: near-black space blue. Stars: white/grey by layer brightness.
- Player: cyan/white triangle. Player bullets: bright cyan.
- Asteroids: grey polygons or circles (large slightly darker/bigger). Debris flash: white.
- Enemy fighter: magenta chevron. Enemy bullets: orange-red.
- Health bar: green→amber→red. Text: white, one built-in font (`pygame.font.SysFont` default).
- Particles: same color as the destroyed object.

## 11. Smoke-test design (R14, AC1, AC2) — build this in from the start
- Flag: `python main.py --smoke-test`. Set `SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy`
  (the code should set these env vars itself when the flag is present, before `pygame.init()`).
- Drive **simulated input** instead of real events: each frame feed a scripted control state, e.g.
  move in a slow left-right sweep and **fire every frame** (cooldown still gates actual shots).
- Force the game into PLAY immediately (skip Start), and **force-spawn** at least a few asteroids and
  one enemy early (e.g. seed 3 asteroids + 1 enemy on frame 1) so collisions/firing exercise.
- Run the main loop for **exactly 120 frames**, then `sys.exit(0)`. No real window, no audio, no
  human, hard frame cap so it can't hang (AC1/AC2, C5/C6). Do **not** call `pygame.display.flip()`
  on a real window dependency — drawing to the dummy surface is fine.
- Use a fixed RNG seed in smoke-test mode for determinism (C6).

## 12. Scope / line-budget guard (C3, ≤ ~500 lines)
Single file `workspace/game/main.py`. Suggested structure to stay lean:
- Constants block (all numbers above) · a few small classes or plain dicts for entities
  (Player, list-of-dicts for bullets/asteroids/enemies/particles/stars) · `update()` / `draw()` per
  state · one `main()` with the loop + smoke-test branch.
- Lists-of-dicts over many classes keeps it short. Keep particles/high-score/pause optional so they
  can be dropped first if the file approaches ~500 lines. Estimated comfortable fit: ~350–450 lines.

## 13. Requirement coverage map
| Req | Where realized |
|---|---|
| R1 single fixed screen | §5 (600×800 fixed) |
| R2 player ship shape | §6.1 |
| R3 keyboard move + clamp | §3, §6.1 |
| R4 auto-scroll starfield | §6.6 |
| R5 scrolling asteroids/debris | §6.3 |
| R6 enemy that shoots back | §6.4, §6.5 |
| R7 player weapon + cooldown | §6.1, §6.2 |
| R8 combat collisions/removal | §6.2–6.4, §8 |
| R9 damage collisions | §6.3–6.5, §8 |
| R10 health/lives + shown | §6.1, §9 |
| R11 score + shown | §7.1, §9 |
| R12 game-over + final score | §4, §9 |
| R13 restart + quit, no relaunch | §3, §4 |
| R14 smoke test | §11 |
| R15 difficulty ramp | §7.2 |
| R16 start screen | §4, §9 |
| R17 hit/destroy feedback | §6.3, §6.7 |
| R18 i-frames | §6.1 |
| R19 high score (optional) | §7.1, §9 |
| R20 combo popups (optional) | not built — out for line budget; level-designer may add |
| R21 power-up (optional) | not built — out for line budget |
| R22 pause (optional) | §3, §4 |

## 14. Open questions / handoffs to downstream roles
- **Artist:** confirm exact palette hex for the colors named in §10; confirm the health-bar
  green/amber/red thresholds read well as shapes.
- **Level-designer:** owns final difficulty numbers (§7.2) — validate the ramp produces 1–3 min runs;
  may tune spawn intervals, the small/large mix, enemy fire interval, and whether a small time bonus
  is added to scoring. Confirm entity caps keep FPS stable.
- **Writer:** provide the Start-screen title/pitch/control copy and the Game Over copy (short).
- No blocking unknowns for the programmer — every MUST has concrete numbers above.
```

---
---

