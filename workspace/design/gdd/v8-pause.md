# v8 increment — Pause / Unpause + Q-hold to Quit

Owner: lead-game-designer · Date: 2026-06-05 · Status: complete
Inputs: `workspace/requirements/requirements/v8.md` (R69–R75, AC53–AC60, **§32 Open-values
table**), `workspace/shared/brief.md` v8 increment, `workspace/shared/handoffs.md` (entry 55),
GDD `v7-bosses.md` (the freeze machinery is extended here, not replaced), and `workspace/game/app.py`
(the live `_step_play()` / `_handle_events()` structure the Programmer modifies).
Implements: **R69–R75 (MUST)** — locks every §32 Designer lever with a concrete value (t_quit
frames, restart-from-PAUSE key, starfield/particle behaviour during PAUSE) and locks the design
intent for the levers the Artist/Writer own (arc style+position+color direction; overlay
structure/background; heading color treatment) so no §32 entry remains TBD. Enumerates the exact
freeze-list subsystems at the module level so the Programmer has an unambiguous implementation
target. Confirms the Esc-toggle state machine and the no-op behaviour in START / GAME_OVER.

> This section **appends** to v1+v2+v5+v6+v7; it does not replace them. All prior numbers
> (R1–R68, AC1–AC52) still hold. The cross-increment *why* is in `../history.md`.

---

## V8.1 Feature in one line

Pressing Esc in PLAY snaps the game into a **first-class PAUSE state** that freezes every
game-logic system (the §V2.7 pipeline does not run); a centred overlay shows control hints and a
real-time Q-hold progress arc; a second Esc resumes from the exact frozen state; holding Q for
**30 frames (0.5 s)** quits the application, with instant arc-reset on early release; R restarts
the run; Esc in START or GAME_OVER is silently ignored.

---

## V8.2 ★ THE STATE MACHINE — Esc toggle + no-op guard (R69 / R73) — LOCKED

### V8.2.1 PAUSE as a first-class GameState

PAUSE is a **new, fourth top-level `GameState`** (joining `START`, `PLAY`, `GAME_OVER`). It is
not a flag on PLAY, not a sub-state of the encounter manager, and not a boolean in `World`. The
existing guard in `app.py`'s main loop —

```python
if self.state is GameState.PLAY:
    self._step_play(inp)
```

— is sufficient to freeze all game logic: PAUSE simply never enters this branch. No other code
path runs the §V2.7 pipeline outside of `_step_play()`, so **the freeze is structurally
guaranteed by architecture**, not by individual system checks.

### V8.2.2 Esc-toggle transition table (LOCKED)

| Current state | Input | Resulting state | Side-effect |
|---|---|---|---|
| START | K_ESCAPE KEYDOWN | START | **silently ignored** — no transition |
| PLAY | K_ESCAPE KEYDOWN | **PAUSE** | pause overlay + arc appear; all systems freeze |
| PAUSE | K_ESCAPE KEYDOWN | **PLAY** | overlay removed; all systems resume; no drift |
| GAME_OVER | K_ESCAPE KEYDOWN | GAME_OVER | **silently ignored** — no transition |

**BA ruling (R73): the existing `if event.key == pygame.K_ESCAPE: return False` line in
`App._handle_events()` is REMOVED by the Programmer.** The `pygame.QUIT` event (window close
button) is unchanged and continues to exit the application.

### V8.2.3 No-op confirmation (R73)

Esc in START and GAME_OVER is silently ignored — no log, no sound, no visual feedback. The
`_handle_events()` event loop simply has no branch that matches (K_ESCAPE, START) or
(K_ESCAPE, GAME_OVER) after the removal above. This is the complete contract — no special-case
guard function required.

---

## V8.3 ★ t_quit — HOLD THRESHOLD (R72) — LOCKED

| Lever (§32) | Value | Programmer constant |
|---|---|---|
| **Hold duration to quit** | **30 frames = 0.5 s @ 60 FPS** | `PAUSE_QUIT_FRAMES = 30` |

**Rationale:** 0.5 s is the BA's suggested target (§32); 30 frames maps cleanly to the existing
60-FPS clock. It is long enough to be deliberate (a player idly resting a thumb on Q will not
accidentally quit) but short enough to be responsive (not tedious). The arc fills at a rate of
one frame per degree × (360/30) = 12°/frame — a visually smooth sweep at 60 FPS.

**Q-hold timer mechanics (programmer-ready):**
- `q_hold_frames` is an `int` counter on `App` (initialised to 0, reset on `reset_run()` / any
  state transition out of PAUSE).
- Each PAUSE frame: `pressed = pygame.key.get_pressed()[pygame.K_q]`. If `pressed`:
  `q_hold_frames += 1`; if `q_hold_frames >= PAUSE_QUIT_FRAMES`: call `pygame.quit()` then
  `sys.exit(0)`. If not `pressed`: `q_hold_frames = 0` (instant reset — no accumulation).
- Arc fill ratio passed to the renderer: `fill = q_hold_frames / PAUSE_QUIT_FRAMES` (0.0 → 1.0).
- Q-hold logic runs **only when `state is GameState.PAUSE`** — it is not evaluated in any other
  state (R72 / §33 non-goal).
- `pygame.key.get_pressed()` is called in the main loop's PAUSE branch (not inside
  `_handle_events()`, which is event-driven). This ensures the counter advances every held frame.

---

## V8.4 ★ Q-HOLD ARC — LOCKED

| Dimension | Locked value | Artist note |
|---|---|---|
| **Shape** | Circular arc, clockwise from 12 o'clock (−90° base), sweeping 0°→360° as fill 0.0→1.0 | Confirm pygame.draw.arc call: start_angle offset = `−π/2`, sweep = `fill × 2π` |
| **Radius** | **22 px** | Compact — fits inside the overlay panel; visually distinct from the boss HP bar (rectangular) and buff pills (14×14 boxes) |
| **Stroke weight** | **3 px** | Use `pygame.draw.arc(…, width=3)` |
| **Fill color** | **`HP_AMBER` = `(240, 190, 50)`** — reuse existing palette entry | Warm amber reads "caution / countdown"; distinct from ENEMY magenta, PLAYER cyan, BOSS_WEAPON_YELLOW, and BONUS_BOMB violet; no new palette entry needed |
| **Track (unfilled) color** | **`HP_BACK` = `(40, 44, 58)`** — reuse existing dim track | Matches buff-pill timer-bar track; dark, unobtrusive |
| **Position** | **Horizontally centered at `x = W//2 = 300`**, `y_center = pause_panel_y + 56`* | Sits below the last hint text line inside the overlay panel; does not overlap boss HP bar (center-top), buff pills (left), player HP bar (left-top), or bomb readout (right-top) |

\* `pause_panel_y` is the vertical center of the overlay text block (see §V8.6). The exact pixel
value depends on the font sizes the Artist picks — the formula `panel_center_y + 56` is the
constraint; the Artist resolves the literal pixel from their font choices.

**Collision clearance (§34 risk "Overlay/arc HUD collision"):** the Q-hold arc is inside the
pause overlay panel at screen center; the boss HP bar sits at center-top (above it); the player
HP bar, buff pills, and bomb readout are on the left and right edges. The arc at radius 22 at
screen center does not reach any of these elements.

---

## V8.5 ★ FREEZE LIST — exact subsystems enumerated (R70) — LOCKED

**Mechanism:** PAUSE never calls `_step_play()`. Every system listed in the §V2.7 pipeline that
runs inside `_step_play()` is therefore frozen with zero additional guard code. The list below
names the module function and what it freezes, so the Programmer can verify completeness.

| # | Module / function | What it gates | R70 clause |
|---|---|---|---|
| 1 | `physics.update_play(w, inp)` | **Player position, all entity positions and velocities** (player, asteroids, enemies, Mothership + minions, player bullets, enemy bullets, all split pellets, fan bullets, split children) | R70 bullet 1 |
| 2 | `encounter.update(w)` | **All boss encounter timers**: boss entrance descent step, oscillation phase accumulator, moveset cadence counter, boss trigger / breakpoint-mark evaluation | R70 bullets 3, 5 |
| 3 | `bombs.update(w, bomb_fired)` | **Bomb dispatch + flash timer tick** — no flush fires, no new flash frame issued | R70 bullet 6 (player cannot act) |
| 4 | `combat.resolve(w)` | **All damage resolution**: player-bullet × asteroid/enemy/boss, entity × player collisions, pickup collection events, boss HP deduction | R70 bullet 8 |
| 5 | `spawning.update(w)` | **All spawners**: v1 asteroid/debris spawner, v5 enemy spawner, v2 bonus-pickup drip spawner; v7 boss-minion moveset spawn steps (gated inside `encounter.update` — also frozen) | R70 bullet 2 |
| 6 | `buffs.tick(w)` | **All buff duration timers**: FAN, RAPID, SHIELD, SCORE×2 timers do not decrement; no buff expires mid-pause | R70 bullet 4 |
| 7 | `w.frame += 1` | **Run clock `t = w.frame / 60.0`** does not advance; the boss breakpoint marks (`t = 75, 165, …`) do not approach; AC13 timing is preserved | R70 bullet 3 |
| 8 | `scoring.survival_tick(w)` | **Survival score tick** does not fire; `w.sec_score_at` is not updated | R70 bullet 7 |

**Cosmetic systems that continue during PAUSE (Designer decision, §32 delegated):**

| System | Function | Decision | Rationale |
|---|---|---|---|
| Starfield scroll | `physics.update_starfield(w)` | **CONTINUES** — called every state in the existing main loop (`app.py` line outside the PLAY guard); Programmer makes **no change** | Signals app is alive; purely cosmetic — star positions cannot affect any game-state variable; natural architecture (already every-state) |
| Cosmetic particles | Updated inside `physics.update_play()` | **FREEZE** — `update_play()` is inside `_step_play()` and is not called during PAUSE; Programmer makes **no change** | Zero-work decision; existing particles hold position on-screen, creating a natural "world suspended mid-explosion" aesthetic; no game-state effect either way |

**Implementation completeness check:** all 8 items in R70 are covered by entries 1–8 above. The
starfield/particle ruling satisfies the one delegated item in R70 (the "optionally delegated"
bullet 8 note). No R70 clause is unaddressed.

---

## V8.6 ★ PAUSE OVERLAY — LOCKED (design) / Artist spec (exact visuals)

### V8.6.1 Structure (Designer — LOCKED)

The pause overlay is a **two-layer composite** rendered over the frozen game world:

1. **Full-screen dim layer:** A `pygame.Surface((W, H))` filled with `OVERLAY` (`BG = (10, 12, 22)`)
   at **alpha 110** — lighter than the GAME_OVER dim (alpha 160) so the frozen game world remains
   more visible, reinforcing that this is a *temporary* state, not a terminal one. The game world
   with all frozen entities is visible beneath it.

2. **Centered text + arc panel:** A vertically stacked block, horizontally centered at `x = W//2`.
   The block contains (top-to-bottom):
   - **PAUSED heading** — large font; color `PLAYER` cyan `(80, 220, 255)` — immediately
     distinguishable from GAME_OVER's red heading, and from ENEMY magenta.
   - **Resume hint line** — small/mid font; `TEXT_DIM` color; exact string → Writer (§32).
   - **Q-hold quit hint line** — small/mid font; `TEXT_DIM` color; exact string → Writer (§32).
   - **Restart hint line** — small/mid font; `TEXT_DIM` color; exact string → Writer (§32).
   - **Q-hold arc** (§V8.4) — 48px below the last hint line (i.e., arc center at
     `bottom_hint_y + 48`); `HP_AMBER` fill, `HP_BACK` track, r=22, stroke=3.

   No explicit background panel box is drawn — the full-screen dim already separates the overlay
   from the game world. This matches the GAME_OVER treatment (`draw_gameover` in `hud.py`) and
   avoids a design-language inconsistency.

### V8.6.2 Distinguishability from GAME_OVER (§34 risk)

| Property | PAUSE overlay | GAME_OVER overlay |
|---|---|---|
| Dim alpha | 110 (lighter) | 160 (heavier) |
| Heading text | Writer's PAUSED string | `GAMEOVER_TITLE = "GAME OVER"` |
| Heading color | **PLAYER cyan** `(80, 220, 255)` | **HP_RED** `(230, 60, 60)` |
| Score display | No score line | Score + Best |
| Action hint | Esc resume · R restart · Q hold | R restart only |
| Arc | Q-hold progress arc | None |

These differences are orthogonal — even a colorblind player sees different structure (arc vs.
score lines, shorter vs. taller content block).

### V8.6.3 Removal (R71)

The overlay is removed immediately when the state leaves PAUSE — on the second Esc (→ PLAY) or
on an R-restart (→ PLAY). Because `_draw()` dispatches on `self.state`, the overlay is simply
never rendered outside PAUSE — no explicit "hide" step needed.

---

## V8.7 ★ RESTART-FROM-PAUSE KEY BINDING (R74) — LOCKED

| Lever (§32) | Value | Key constant |
|---|---|---|
| **Restart-from-PAUSE key** | **R** | `pygame.K_r` |

**Rationale:** R is already the GAME_OVER restart key (R13 / `app.py` event handler). Using the
same key maintains a consistent mental model: R always means "restart the run, regardless of
where you are." No new binding to learn.

**Behaviour (R74):** on `K_r KEYDOWN` while `state is GameState.PAUSE`:
1. `self.world.reset_run()` — identical to the GAME_OVER path (R13 / R31).
2. `self.q_hold_frames = 0` — reset the Q-hold timer so it doesn't carry into the new run.
3. `self.state = GameState.PLAY` — transitions directly to PLAY (not through START, not back
   through PAUSE).

The overlay is removed (§V8.6.3) and the arc disappears with it. No confirmation step (§33
non-goal — restart from PAUSE is a one-step conscious action per R74 ruling).

---

## V8.8 ★ STARFIELD AND PARTICLES DURING PAUSE — LOCKED

| Element | Decision | Mechanism |
|---|---|---|
| **Starfield** | **Continues scrolling during PAUSE** | `physics.update_starfield(w)` is already called in the main loop outside the `if PLAY:` guard; Programmer makes **no change** |
| **Cosmetic particles** | **Frozen during PAUSE** | Particle updates are inside `physics.update_play()` → inside `_step_play()` → not called in PAUSE; Programmer makes **no change** |

Both decisions are the zero-work architecture choices — they arise naturally from the existing code
structure. The starfield continuing gives the pause screen a living background without any
game-state consequence. Frozen particles create a "world caught mid-explosion" aesthetic that
reinforces the pause effect.

---

## V8.9 Config constants (Programmer: add to `config.py`)

| Constant | Value | Section |
|---|---|---|
| `PAUSE_QUIT_FRAMES` | `30` | Q-hold threshold (§V8.3) |

**Reused — do NOT redefine:**
- `HP_AMBER = (240, 190, 50)` — Q-hold arc fill color (§V8.4)
- `HP_BACK = (40, 44, 58)` — Q-hold arc track color (§V8.4)
- `PLAYER = (80, 220, 255)` — PAUSED heading color (§V8.6)
- `TEXT_DIM = (140, 148, 170)` — hint line color (§V8.6)
- `OVERLAY = (10, 12, 22)` — pause dim fill color (§V8.6)

**Strings — do NOT define here; Writer owns (§32):**
- PAUSED heading text (key for `config.py`: `PAUSE_TITLE` or equivalent)
- Resume hint line (`PAUSE_HINT_RESUME`)
- Q-hold quit hint line (`PAUSE_HINT_QUIT`)
- Restart hint line (`PAUSE_HINT_RESTART`)
- Updated `CONTROLS_2` (START screen — currently `"QUIT  Esc"` → must reflect pause + Q-hold)
- Updated `GAMEOVER_KEYS` (GAME_OVER screen — currently `"R  Restart      Esc  Quit"`)

The Programmer should stub placeholder strings (e.g. `PAUSE_TITLE = "PAUSED"`) to unblock
implementation; the Writer replaces them. If the Writer's handoff arrives before the Programmer
touches `config.py`, the Writer writes directly.

---

## V8.10 Programmer implementation guide

All changes confined to the existing module set — no new files required.

### `world.py`
- Add `PAUSE` to the `GameState` enum.

### `app.py` — `_handle_events()`
1. **Remove** `if event.key == pygame.K_ESCAPE: return False` (R73 — BA ruling).
2. **Add** after the `pygame.QUIT` check and before any keydown dispatch:
   - `if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:`
     - `if self.state is GameState.PLAY: self.state = GameState.PAUSE`
     - `elif self.state is GameState.PAUSE: self.state = GameState.PLAY`
     - `# else: silently ignored (START, GAME_OVER)`
3. **Add** inside `KEYDOWN` dispatch:
   - `if self.state is GameState.PAUSE and event.key == pygame.K_r:` →
     `self.world.reset_run(); self.q_hold_frames = 0; self.state = GameState.PLAY`

### `app.py` — main loop
1. **Add** `self.q_hold_frames = 0` to `__init__`.
2. **Add** PAUSE branch in the main loop body (after `update_starfield`, before `_draw`):
   ```python
   if self.state is GameState.PAUSE:
       if pygame.key.get_pressed()[pygame.K_q]:
           self.q_hold_frames += 1
           if self.q_hold_frames >= C.PAUSE_QUIT_FRAMES:
               pygame.quit()
               sys.exit(0)
       else:
           self.q_hold_frames = 0
   elif self.state is GameState.PLAY:
       self._step_play(inp)
   ```
   *(The existing `if self.state is GameState.PLAY: self._step_play(inp)` becomes the `elif`.)*

### `app.py` — `_draw()`
- Add a PAUSE case **before** the GAME_OVER fallback:
  ```python
  elif self.state is GameState.PAUSE:
      render.draw_world(self.screen, self.world)
      hud.draw_hud(self.screen, self.world)
      hud.draw_pause(self.screen, self.q_hold_frames)
  ```
  The world + HUD are drawn first (frozen game is visible beneath the overlay).

### `view/hud.py` — new `draw_pause(screen, q_hold_frames)`
- Draw full-screen dim surface: `Surface((W, H))`, fill `C.OVERLAY`, alpha 110.
- Render PAUSED heading centered at `(W//2, ~340)` in `PLAYER` cyan, large font.
- Render three hint lines centered below, in `TEXT_DIM`, small/mid font (Writer strings).
- Compute `fill = q_hold_frames / C.PAUSE_QUIT_FRAMES`.
- Draw arc track (full circle): `pygame.draw.circle(screen, C.HP_BACK, arc_center, 22, 3)`.
- If `fill > 0`: draw filled arc: `pygame.draw.arc(screen, C.HP_AMBER, arc_rect, start, end, 3)`
  where `start = π/2 − fill×2π` (pygame angle measured CCW from +x; 12 o'clock = π/2) and
  `end = π/2`.

### `config.py`
- Add `PAUSE_QUIT_FRAMES = 30`.
- Add stub strings for Writer: `PAUSE_TITLE`, `PAUSE_HINT_RESUME`, `PAUSE_HINT_QUIT`,
  `PAUSE_HINT_RESTART`.
- **Update** `CONTROLS_2` and `GAMEOVER_KEYS` per the Writer's revised strings (Writer §32).

---

## V8.11 v8 requirement coverage map

| Req | Where realized |
|---|---|
| R69 Esc-toggle PLAY↔PAUSE; no-op in other states | §V8.2 (state table); §V8.2.3 (no-op); Programmer guide §V8.10 |
| R70 Complete game freeze during PAUSE | §V8.5 (freeze list, 8 entries, all R70 bullets covered); §V8.8 (cosmetic exceptions) |
| R71 Pause overlay with control hints | §V8.6 (layout, structure, distinguishability, removal); strings → Writer (§32) |
| R72 Q-hold-to-quit with cancellable arc | §V8.3 (t_quit = 30 f); §V8.4 (arc); §V8.10 (hold-timer mechanic) |
| R73 Esc removed from quit path | §V8.2.2 (transition table); §V8.2.3 (no-op); §V8.10 (remove K_ESCAPE line) |
| R74 Restart from PAUSE (R key) | §V8.7 (LOCKED: K_r); §V8.10 (handler) |
| R75 Smoke gate preserved (no PAUSE in smoke path) | Confirmed: smoke mode calls `pygame.event.pump()` + `smoke_input()`, never generating K_ESCAPE; `_handle_events()` not called; PAUSE state is never entered; 120-frame path unchanged |
| AC53 Esc in PLAY → PAUSE; second Esc → PLAY; no drift | §V8.2 + §V8.5 (freeze-by-architecture) |
| AC54 Boss run clock frozen during PAUSE | §V8.5 entry 7 (`w.frame += 1` gated inside `_step_play`) |
| AC55 Overlay visible in PAUSE; removed on unpause/restart | §V8.6 (structure); §V8.6.3 (removal) |
| AC56 Q held t_quit → arc fills → app exits | §V8.3 (30 f); §V8.4 (arc 0→360°); §V8.10 (exit path) |
| AC57 Q released before t_quit → arc resets; no accumulation | §V8.3 (instant reset on `not pressed`); §V8.10 (else branch) |
| AC58 Esc in START/GAME_OVER → no-op; K_ESCAPE→quit removed; pygame.QUIT intact | §V8.2.3; §V8.10 (remove old line) |
| AC59 CONTROLS_2 / GAMEOVER_KEYS updated | §V8.9 (strings flagged; Writer owns); Programmer stubs |
| AC60 Smoke exits 0 / 120 f; PAUSE never entered | §V8.11 R75 row above |

---

## V8.12 Open questions / handoffs to downstream roles

- **Artist (next):** owns (a) the **exact pixel layout** of the pause overlay text block — vertical
  spacing between heading and hint lines, font size for each tier, precise `y` coordinate for the
  panel center that resolves the `pause_panel_y + 56` arc-position formula (§V8.4, §V8.6);
  (b) **confirm or substitute** the arc color choice (`HP_AMBER`) — must remain distinct from
  boss HP bar, buff pills, player HP bar, bomb readout, and must not clash with the frozen boss
  health visual; (c) confirm the **dim alpha = 110** reads as clearly distinct from GAME_OVER's
  dim (alpha 160) in the full scene. No new palette entries are required — all values reuse
  the existing palette — but the Artist may add one if the amber arc causes a visual conflict.
  The Artist does **not** touch `config.py` string constants — those are Writer's.

- **Writer (next, after Artist):** owns (a) **`PAUSE_TITLE`** — the PAUSED heading string; (b)
  **`PAUSE_HINT_RESUME`**, **`PAUSE_HINT_QUIT`**, **`PAUSE_HINT_RESTART`** — three hint lines;
  (c) the revised **`CONTROLS_2`** (currently `"QUIT  Esc"`) and **`GAMEOVER_KEYS`** (currently
  `"R  Restart      Esc  Quit"`). The Q-hold hint must convey the hold duration and cancellability
  (§32 note). All strings go directly in `config.py`.

- **Programmer (after Artist + Writer):** no blocking unknowns — every §32 Designer lever is a
  concrete value above (§V8.9 consts). Key notes: (a) the Q-hold counter lives on `App`, not
  `World` — it is UI state, not game-simulation state; (b) `pygame.draw.arc` in pygame-ce uses
  angles in **radians**, measured **counter-clockwise from the +x axis** — to draw clockwise from
  12 o'clock, start angle = `π/2 − fill×2π`, end angle = `π/2` (or use `start = π/2`, `end =
  π/2 + fill×2π` with the angles swapped into the `draw.arc` call's convention); (c) reset
  `q_hold_frames` to 0 on **any** transition out of PAUSE (Esc → PLAY, R → PLAY) to prevent a
  stale non-zero value on the next pause entry; (d) the Programmer **confirms** at implementation
  time that the smoke path never enters PAUSE (AC60), consistent with R75.

- **QA (after Programmer):** verifies AC53–AC60 per the test plan. The Q-hold cancel / accumulation
  test (AC57) should cover: press Q, hold for 15 frames, release, verify arc at 0%; press again,
  hold full 30 frames, verify quit. The freeze test (AC53/AC54) should include a ≥ 2-second pause
  interval and check that the boss breakpoint clock did not advance (AC54).

---
---
