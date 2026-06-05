r"""app — the Game/App: the state machine, the run loop, and the smoke harness.

This is the orchestration layer (GDD §V2.9): it owns the loop, drives the systems
pipeline in §V2.7 order, calls the view, and hosts the `--smoke-test` branch. It
mutates the World only via systems; it never draws directly (view does that).
"""

import math
import random
import sys

import pygame

from . import config as C
from .world import World, GameState
from .input import read_input, smoke_input, InputState
from .systems import spawning, physics, combat, buffs, scoring, bombs, encounter
from .view import render, hud


class App:
    def __init__(self, smoke=False, event_script=None):
        self.smoke = smoke
        # v9: a headless event-script drives scripted KEYDOWN edges through the REAL
        # `_handle_events` (behavioral test of pause/bomb/quit, retro T1/A13). It is a
        # dict: {"frames": int, "keydowns": {frame: [pygame key, …]},
        #        "held": {frame: [pygame key, …]}, "probes": {frame: fn(app)}}.
        self.event_script = event_script
        self.state = GameState.START
        self.frame = 0          # global loop counter (smoke cap + start-screen blink)
        self.bomb_fired = False  # X key-down edge this frame (v6, GDD §V6.4)
        self.q_hold_frames = 0   # v8: Q-hold timer for quit-from-PAUSE (GDD §V8.3)
        self.quit_via_qhold = False  # v9: set when a Q-hold completes (testable quit seam)

    # ── setup ────────────────────────────────────────────────────────────────
    def _init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((C.W, C.H))
        pygame.display.set_caption("Starshard")
        self.clock = pygame.time.Clock()
        fonts = {
            "hud": pygame.font.SysFont(None, C.FONT_HUD),
            "big": pygame.font.SysFont(None, C.FONT_BIG),
            "mid": pygame.font.SysFont(None, C.FONT_MID),
            "small": pygame.font.SysFont(None, C.FONT_SMALL),
            "pickup": pygame.font.SysFont(None, C.FONT_PICKUP),
            "pill": pygame.font.SysFont(None, C.FONT_PILL),
        }
        render.set_fonts(fonts)
        hud.set_fonts(fonts)

    def _new_world(self):
        headless = self.smoke or self.event_script is not None
        rng = random.Random(C.SMOKE_SEED) if headless else random.Random()
        self.world = World(rng)
        if headless:
            # Force PLAY immediately + seed hazards for collision coverage (GDD §11).
            # The event-script gate starts in PLAY too, with a field present, so a
            # scripted X bomb has something to flush and Esc has PLAY to pause (v9).
            self.state = GameState.PLAY
            spawning.seed_smoke(self.world)

    # ── the systems pipeline for one PLAY frame (§V2.7 order) ──────────────────
    def _step_play(self, inp):
        w = self.world
        physics.update_play(w, inp)     # move + fire + despawn
        encounter.update(w)             # v7: boss trigger + entrance/oscillation/moveset (§V7.3)
        bombs.update(w, self.bomb_fired)  # v6: flush+flash BEFORE the damage step (§V6.3)
        combat.resolve(w)               # collisions, collect, damage + boss hits/defeat (steps 1–4)
        spawning.update(w)              # ramped asteroid/enemy spawns + bonus drip (frozen while boss)
        buffs.tick(w)                   # tick timers, expiry→revert (step 5)
        w.frame += 1
        scoring.survival_tick(w)        # +1/s survival bonus (×mult)
        if w.player.hp <= 0:            # step 6 → GAME_OVER
            w.best = max(w.best, w.score)
            self.state = GameState.GAME_OVER

    # ── event handling (discrete transitions: quit / start / restart) ──────────
    def _handle_events(self):
        self.bomb_fired = False                      # reset the per-frame X edge (v6)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                # v8 R73: Esc toggles PLAY↔PAUSE; silently ignored in START/GAME_OVER
                if event.key == pygame.K_ESCAPE:
                    if self.state is GameState.PLAY:
                        self.state = GameState.PAUSE
                        self.q_hold_frames = 0
                    elif self.state is GameState.PAUSE:
                        self.state = GameState.PLAY
                    # else: START or GAME_OVER — silent no-op
                    continue
                if self.state is GameState.START:
                    self.state = GameState.PLAY
                elif self.state is GameState.GAME_OVER and event.key == pygame.K_r:
                    self.world.reset_run()           # R13/R31 — no leak into the new run
                    self.state = GameState.PLAY
                elif self.state is GameState.PAUSE and event.key == pygame.K_r:
                    self.world.reset_run()           # v8 R74 — restart from PAUSE
                    self.q_hold_frames = 0
                    self.state = GameState.PLAY
                elif self.state is GameState.PLAY and event.key == pygame.K_x:
                    self.bomb_fired = True            # X key-down edge → bomb (§V6.4)
        return True

    # ── render one frame for the current state ─────────────────────────────────
    def _draw(self):
        self.screen.fill(C.BG)
        render.draw_starfield(self.screen, self.world)
        if self.state is GameState.START:
            hud.draw_start(self.screen, self.frame)
        elif self.state is GameState.PLAY:
            render.draw_world(self.screen, self.world)
            hud.draw_hud(self.screen, self.world)
            hud.draw_flash(self.screen, self.world)   # v6 flash: above HUD, PLAY-only (§V6.6)
        elif self.state is GameState.PAUSE:            # v8: frozen world + HUD + pause overlay
            render.draw_world(self.screen, self.world)
            hud.draw_hud(self.screen, self.world)
            hud.draw_pause(self.screen, self.q_hold_frames)
        else:  # GAME_OVER — frozen field + dim + text
            render.draw_world(self.screen, self.world)
            hud.draw_hud(self.screen, self.world)
            hud.draw_gameover(self.screen, self.world)
        pygame.display.flip()

    # ── smoke seeding (driven by the SMOKE_TIMELINE source of truth, v9) ────────
    def _run_smoke_seeds(self):
        """Apply any SMOKE_TIMELINE seeds due on this frame (retro T4/A12). The
        ordering + budget live in `config.SMOKE_TIMELINE`; this only dispatches the
        action. Replaces the old hand-maintained inline schedule so a new seed is a
        one-row edit in config, not a scattered `if frame ==` here."""
        self.bomb_fired = False               # reset the per-frame X edge each smoke frame
        for frame, event, _note in C.SMOKE_TIMELINE:
            if self.frame != frame:
                continue
            if event == "bonus":
                spawning.seed_smoke_bonus(self.world)
            elif event == "split":
                spawning.seed_smoke_split(self.world)
            elif event == "bomb":
                self.bomb_fired = True         # scripted X edge → bomb flush (AC30/32/33)
            elif event == "boss_target":
                spawning.seed_smoke_boss_target(self.world)
            elif event == "boss":
                encounter.seed_smoke_boss(self.world)

    # ── input + held-key seams (so the event-script gate can drive headlessly) ──
    def _scripted_input(self):
        """Continuous input for the event-script gate: neutral (no move/fire) so the
        behavioral assertions are about the scripted KEYDOWN edges, not stray shots."""
        return InputState(dx=0, dy=0, fire=False)

    def _q_held(self):
        """Is the Q key down this frame? Real keyboard normally; the scripted `held`
        set under the event-script gate (real `pygame.key.get_pressed()` can't be
        faked by posted events, so the Q-hold quit needs this seam to be testable)."""
        if self.event_script is not None:
            return pygame.K_q in self.event_script.get("held", {}).get(self.frame, ())
        return bool(pygame.key.get_pressed()[pygame.K_q])

    # ── main loop ──────────────────────────────────────────────────────────────
    def run(self):
        self._init_pygame()
        self._new_world()
        running = True
        while running:
            if self.smoke:
                self._run_smoke_seeds()          # SMOKE_TIMELINE-driven (v9)
                inp = smoke_input(self.frame)
                pygame.event.pump()              # drain the queue so the dummy driver is happy
            elif self.event_script is not None:
                # Inject scripted KEYDOWN edges, then run the REAL `_handle_events`
                # so pause/bomb/quit are exercised through the live code path (v9).
                for key in self.event_script.get("keydowns", {}).get(self.frame, ()):
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
                running = self._handle_events()
                inp = self._scripted_input()
            else:
                running = self._handle_events()
                inp = read_input()

            physics.update_starfield(self.world)     # cosmetic, runs in every state
            if self.state is GameState.PAUSE:          # v8: Q-hold timer (GDD §V8.3)
                if self._q_held():
                    self.q_hold_frames += 1
                    if self.q_hold_frames >= C.PAUSE_QUIT_FRAMES:
                        # v9: end the loop via a flag instead of sys.exit() inline, so
                        # the quit is observable to a harness; `main()` still exit(0)s
                        # and `pygame.quit()` below still runs — same live behavior.
                        self.quit_via_qhold = True
                        running = False
                else:
                    self.q_hold_frames = 0
            elif self.state is GameState.PLAY:
                self._step_play(inp)

            self._draw()
            if not (self.smoke or self.event_script is not None):
                self.clock.tick(C.FPS)           # real-time pacing only when live

            # v9: per-frame probe hook for the event-script gate (capture/assert state).
            if self.event_script is not None:
                probe = self.event_script.get("probes", {}).get(self.frame)
                if probe is not None:
                    probe(self)

            self.frame += 1
            if self.smoke and self.frame >= C.SMOKE_FRAMES:
                running = False
            if self.event_script is not None and self.frame >= self.event_script.get("frames", C.SMOKE_FRAMES):
                running = False

        pygame.quit()


# ── v9 event-script gate (behavioral pause/bomb/quit, retro T1/A13) ───────────
def run_event_script(script):
    """Build + run an App under the event-script gate and return it for inspection.
    The App's loop posts the script's KEYDOWN edges and routes them through the REAL
    `_handle_events`, so pause/bomb/quit are exercised through the live code path
    (not source inspection). Reusable by the regression harness."""
    app = App(event_script=script)
    app.run()
    return app


def _built_in_event_script(results):
    """The default --event-script scenario: bomb (X in PLAY) → pause (Esc) → unpause
    (Esc) → re-pause (Esc) → Q-hold quit. Probes write booleans into `results`."""
    def after_bomb(app):
        results["bomb"] = (not app.world.enemies and not app.world.asteroids
                           and app.world.charges == C.BOMB_START - 1
                           and app.world.flash_timer > 0)

    def paused(app):    results["paused"] = (app.state is GameState.PAUSE)
    def unpaused(app):  results["unpaused"] = (app.state is GameState.PLAY)
    def repaused(app):  results["repaused"] = (app.state is GameState.PAUSE)
    return {
        "frames": 60,
        "keydowns": {3: [pygame.K_x], 6: [pygame.K_ESCAPE],
                     8: [pygame.K_ESCAPE], 10: [pygame.K_ESCAPE]},
        "held": {f: [pygame.K_q] for f in range(11, 55)},   # 30 held PAUSE frames → quit @f40
        "probes": {3: after_bomb, 6: paused, 8: unpaused, 10: repaused},
    }


def run_event_script_gate():
    """Standalone --event-script gate: run the built-in scenario, print a per-check
    report, return True iff every behavioral check passed (CLI maps that to exit 0/1)."""
    results = {}
    app = run_event_script(_built_in_event_script(results))
    results["quit"] = app.quit_via_qhold
    checks = [
        ("bomb: X in PLAY flushes the field, charge 2->1, flash armed", results.get("bomb")),
        ("pause: Esc PLAY->PAUSE",                                      results.get("paused")),
        ("unpause: Esc PAUSE->PLAY",                                    results.get("unpaused")),
        ("re-pause: Esc PLAY->PAUSE",                                   results.get("repaused")),
        ("quit: Q held 30 f in PAUSE exits the app",                   results.get("quit")),
    ]
    print("event-script behavioral gate (scripted KEYDOWN -> real _handle_events):")
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    return all(ok for _, ok in checks)


# ── v9 AC13 balance probe (retro T2/A10) ─────────────────────────────────────
def balance_probe(runs=None, cap=None):
    """Run `runs` deterministic scripted games of the REAL play pipeline under the
    live difficulty ramp until the auto-pilot dies (or `cap` frames). Returns
    (survival_seconds_list, censored_count). The auto-pilot is the fixed smoke sweep
    — deterministic + comparable across versions, a naive non-dodging lower bound.
    No display is needed: the play pipeline (physics/combat/spawning/…) is pure logic."""
    runs = C.BALANCE_PROBE_RUNS if runs is None else runs
    cap = C.BALANCE_PROBE_CAP_FRAMES if cap is None else cap
    times, censored = [], 0
    for i in range(runs):
        app = App()
        app.world = World(random.Random(C.SMOKE_SEED + i))   # distinct deterministic seed/run
        app.state = GameState.PLAY
        app.bomb_fired = False
        f = 0
        while app.state is GameState.PLAY and f < cap:
            app._step_play(smoke_input(f))
            f += 1
        if app.state is GameState.PLAY:                      # never died → censored at the cap
            censored += 1
        times.append(app.world.frame / 60.0)
    return times, censored


def _percentile(sorted_vals, q):
    """Linear-interpolated percentile (q in [0,1]) of a sorted list — no numpy."""
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = q * (len(sorted_vals) - 1)
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return sorted_vals[lo]
    return sorted_vals[lo] * (hi - pos) + sorted_vals[hi] * (pos - lo)


def run_balance_probe(runs=None):
    """Print median / p95 survival seconds across the scripted runs (AC13 instrument)."""
    times, censored = balance_probe(runs)
    s = sorted(times)
    median, p95 = _percentile(s, 0.5), _percentile(s, 0.95)
    cap_s = C.BALANCE_PROBE_CAP_FRAMES / 60.0
    print(f"AC13 balance probe - {len(s)} scripted runs "
          f"(auto-pilot = fixed smoke sweep, naive non-dodging lower bound):")
    print(f"  survival seconds: min={s[0]:.1f}  median={median:.1f}  "
          f"p95={p95:.1f}  max={s[-1]:.1f}")
    if censored:
        print(f"  NOTE: {censored}/{len(s)} run(s) hit the {cap_s:.0f}s cap (censored - "
              f"the naive sweep effectively never dies on that seed).")
    return median, p95
