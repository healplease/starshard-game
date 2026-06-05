# Requirements — "Starshard"

Owner: business-analyst · Date: 2026-06-05 · Status: complete
Source: `workspace/shared/brief.md` (theme), `CLAUDE.md` (scope guardrails)

---

## 1. Product vision (one line)
Pilot a lone scout ship down an endless scrolling starfield — dodge drifting asteroids and debris,
blast enemy fighters, and rack up the highest score you can before your ship is destroyed.

## 2. Target player
- Casual arcade player; anyone who has played a classic top-down shmup (Galaga / 1942 lineage).
- Wants a pick-up-and-play loop with zero tutorial: arrows to move, space to shoot.
- No prior knowledge required; success is "beat my last score".

## 3. Session length
- **One run: ~1–3 minutes** (escalating difficulty makes most runs end inside 3 minutes).
- Restart is instant (one key) so the play→die→retry loop stays tight.

---

## 4. Functional requirements (MoSCoW, testable)

Each requirement is numbered for traceability and written so QA can check it (many via `--smoke-test`,
some by observation). "Shapes only / keyboard only" is assumed for all of them per `CLAUDE.md`.

### MUST have (v1 — the game is not shippable without these)
- **R1 — Single screen, fixed window.** The game runs in one fixed-size window (single screen, 2D,
  top-down). No scrolling camera; the *world* scrolls past the player.
- **R2 — Player ship.** A player-controlled ship is drawn as a shape (e.g. a triangle) near the
  bottom-center at start.
- **R3 — Keyboard movement.** Arrow keys (and/or WASD) move the ship left/right and up/down. The
  ship is **clamped to the screen** — it cannot leave the visible play area.
- **R4 — Auto-scrolling backdrop.** A starfield (points/small shapes) scrolls continuously downward
  to convey forward flight. Scrolling is automatic and independent of player input.
- **R5 — Scrolling hazards (asteroids/debris).** Obstacles spawn at the top and move downward at
  varying speeds/sizes, drawn as shapes (e.g. circles/polygons). Colliding with one damages the player.
- **R6 — Enemy that shoots back.** At least one enemy type spawns from the top, moves into the play
  area, and **fires projectiles toward the player**. Enemy bullets damage the player on contact.
- **R7 — Player weapon.** Pressing the fire key (Space) shoots projectiles upward. A fire-rate
  cooldown prevents one bullet per frame (no continuous laser stream).
- **R8 — Combat collisions.** Player bullets destroy enemies and asteroids on hit (asteroids may take
  1+ hits). Destroyed objects are removed from play.
- **R9 — Damage collisions.** Asteroid/debris contact, enemy contact, and enemy-bullet contact each
  reduce player health/lives.
- **R10 — Health/lives.** The player has a finite health pool and/or a small number of lives. When it
  reaches zero the run ends. Current health/lives is shown on screen as shapes or text.
- **R11 — Score.** Score increases for destroying enemies and asteroids (and/or for survival time).
  Current score is displayed on screen at all times during play.
- **R12 — Game-over state.** When health/lives hit zero, play stops and a Game Over screen shows the
  final score.
- **R13 — Restart.** From Game Over, a single key restarts a fresh run (score, health, entities reset)
  without relaunching the process. A key to quit is also available.
- **R14 — Headless smoke test.** `workspace/game/main.py --smoke-test` initializes pygame, runs the
  main loop for exactly **120 frames** with **simulated input**, then **exits 0**, honoring
  `SDL_VIDEODRIVER=dummy` / `SDL_AUDIODRIVER=dummy`. No window or audio device required.

### SHOULD have (strongly desired, cut only under pressure)
- **R15 — Difficulty ramp.** Spawn rate and/or hazard speed increase over time so runs escalate and
  naturally end within the target session length.
- **R16 — Start screen.** A simple title/instructions screen before the first run (press a key to
  begin), so controls are discoverable.
- **R17 — Hit/destroy feedback.** Visible feedback on hits (e.g. brief flash, color change, or a
  simple particle burst made of shapes) — no external assets.
- **R18 — Brief invulnerability.** After taking damage, a short i-frames window (visualized, e.g.
  blinking) prevents instant multi-hit death.

### COULD have (nice, only if cheap and within line budget)
- **R19 — High score** persisted for the session (in memory) and shown on Game Over.
- **R20 — Score popups / combo** for consecutive kills.
- **R21 — Power-up** (e.g. a shape that grants temporary faster fire or a shield) on a timer/drop.
- **R22 — Pause** toggle.

### WON'T have (this version) — see Non-goals
See section 5.

---

## 5. Non-goals (explicitly out of scope for v1)
- ❌ External image, sprite, or audio files of any kind (shapes + on-screen text only).
- ❌ Sound or music.
- ❌ Multiple levels, stages, or a boss campaign (single endless arena only).
- ❌ Scrolling/zooming camera, parallax beyond a simple starfield, or 3D.
- ❌ Mouse, gamepad, or touch input (keyboard only).
- ❌ Networking, multiplayer, leaderboards, or on-disk save files.
- ❌ Settings/options menus, multiple ships, or weapon-selection systems.
- ❌ Narrative cutscenes or dialogue (the Writer provides only short UI/flavor copy).
- ❌ Anything pushing `main.py` materially over ~500 lines.

---

## 6. Constraints (from CLAUDE.md — every downstream role must respect)
- **C1 — Single screen, keyboard-only, 2D.**
- **C2 — Placeholder art only:** colored shapes + on-screen text; no external image/sound files.
- **C3 — Code budget:** `workspace/game/main.py` stays under **~500 lines**.
- **C4 — Tech:** Python 3.14 + `pygame-ce`, run via `.\.venv\Scripts\python.exe`.
- **C5 — Headless verifiable:** must support `--smoke-test` (120 frames, simulated input, exit 0)
  with `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy`.
- **C6 — Deterministic-enough smoke test:** smoke-test must not require a human, a display, or audio,
  and must not hang (hard frame cap).

### Risks / watch-items
- Difficulty tuning (R15) is easy to get wrong → flag to level-designer to specify concrete numbers.
- Collision count could grow expensive → keep entity caps modest to protect the line budget and FPS.
- I-frames (R18) vs. instant death — without it, a single asteroid cluster can feel unfair.

---

## 7. Acceptance criteria (what QA will check later)

QA should be able to confirm each of these. **[Smoke]** = checkable headlessly via `--smoke-test`;
**[Play]** = checkable by playing/observing.

- **AC1 [Smoke]** `python main.py --smoke-test` exits with code **0** after exactly **120 frames**,
  with dummy video/audio drivers, no window, no hang.
- **AC2 [Smoke]** The smoke test drives **simulated input** (movement + fire) and the loop survives
  spawning, movement, firing, and collisions without raising an exception.
- **AC3 [Play]** On launch the player ship appears and responds to arrow keys; the ship cannot move
  off-screen (R2, R3).
- **AC4 [Play]** The starfield/backdrop scrolls automatically without player input (R4).
- **AC5 [Play]** Asteroids/debris spawn at the top and travel downward; touching one reduces the
  player's health/lives (R5, R9).
- **AC6 [Play]** At least one enemy type appears and fires projectiles that can damage the player
  (R6); enemy bullets reduce health on contact (R9).
- **AC7 [Play]** Pressing fire shoots player projectiles upward at a limited rate; they destroy
  asteroids and enemies on hit, which are then removed (R7, R8).
- **AC8 [Play]** Score is visible and increases when enemies/asteroids are destroyed (R11).
- **AC9 [Play]** Health/lives are visible and decrease on damage (R10).
- **AC10 [Play]** When health/lives reach zero, a Game Over screen shows the final score (R12).
- **AC11 [Play]** A single key restarts a fresh run (everything reset) without relaunching; a quit key
  exits cleanly (R13).
- **AC12 [Code]** `main.py` is a single file under ~500 lines using only shapes/text — no external
  asset files referenced (C2, C3).
- **AC13 [Play]** A run typically ends within ~1–3 minutes due to the difficulty ramp (R15/Session).

> Note: SHOULD/COULD requirements (R15–R22) are acceptance-checked only if implemented; their absence
> does not fail v1 as long as all MUST items (R1–R14) pass.

---
---

