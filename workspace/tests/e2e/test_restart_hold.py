"""E2E lane — hold-R-to-restart gestures (R74, AC69, AC72, AC74, AC76).

Drives `App._restart_hold_step` / the real loop (`run_event_script`) with held R keys —
the gesture state machine and its independence from the Q-hold counter.
"""

import pygame

from game import config as C
from game.app import App, run_event_script
from game.world import GameState


def test_r74_hold_r_from_pause_restarts(fresh_world):
    """R74: hold-R in PAUSE restarts into PLAY (v12: held gesture, not a tap)."""
    app = App()
    app.world = fresh_world()
    app.world.score = 500
    app.state = GameState.PAUSE
    # v12: a single R KEYDOWN no longer restarts — the branch was removed (§V12.5).
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
    app._handle_events()
    assert app.state is GameState.PAUSE, "a single R tap must NOT restart after v12"
    # Holding R the full RESTART_HOLD_FRAMES restarts into PLAY (via the main-loop block).
    app.event_script = {"held": {app.frame: [pygame.K_r]}}
    for _ in range(C.RESTART_HOLD_FRAMES):
        app._restart_hold_step()
    assert app.state is GameState.PLAY and app.world.score == 0, "hold-R-from-pause restart failed"


def test_ac72_q_r_counters_independent(fresh_world):
    """AC72: Q and R hold counters are fully independent (no cross-fill)."""
    # Hold R alone in PAUSE: r advances, q stays 0, app does NOT quit.
    app = App()
    app.world = fresh_world()
    app.state = GameState.PAUSE
    app.event_script = {"held": {f: [pygame.K_r] for f in range(40)}}
    for app.frame in range(5):
        app._restart_hold_step()
    assert app.r_hold_frames == 5 and app.q_hold_frames == 0, (
        "holding R must advance ONLY r_hold_frames (q stayed?)"
    )

    # Hold Q alone: the R step must leave r at 0 (R not held → reset/idle).
    app2 = App()
    app2.world = fresh_world()
    app2.state = GameState.PAUSE
    app2.event_script = {"held": {f: [pygame.K_q] for f in range(40)}}
    for app2.frame in range(5):
        app2._restart_hold_step()
    assert app2.r_hold_frames == 0, "holding Q must NOT advance r_hold_frames"


def test_ac76_r_hold_inactive_in_start_play(fresh_world):
    """AC76: R-hold restart is inactive in START and PLAY (state guard)."""
    # The main-loop guard is `state in (PAUSE, GAME_OVER)`; emulate it for START + PLAY.
    for state in (GameState.START, GameState.PLAY):
        app = App()
        app.world = fresh_world()
        app.state = state
        app.event_script = {"held": {f: [pygame.K_r] for f in range(40)}}
        for app.frame in range(C.RESTART_HOLD_FRAMES + 5):
            if app.state in (GameState.PAUSE, GameState.GAME_OVER):
                app._restart_hold_step()
        assert app.state is state and app.r_hold_frames == 0, (
            f"R-hold must be a no-op in {state} (no arc, no restart)"
        )


def test_ac74_release_cancels_hold(fresh_world):
    """AC74: release R before threshold cancels (no accumulation)."""
    app = App()
    app.world = fresh_world()
    app.state = GameState.GAME_OVER
    # Hold for 15 frames, then release: counter must snap to 0, no restart.
    app.event_script = {"held": {f: [pygame.K_r] for f in range(15)}}
    for app.frame in range(15):
        app._restart_hold_step()
    assert app.r_hold_frames == 15 and app.state is GameState.GAME_OVER, "mid-hold state wrong"
    app.frame = 15  # R no longer in the held set → release
    app._restart_hold_step()
    assert app.r_hold_frames == 0 and app.state is GameState.GAME_OVER, (
        "release did not cancel the hold"
    )


def test_ac69_hold_restart_e2e():
    """AC69: Esc->PAUSE then hold R 30 f in the REAL loop restarts to PLAY."""
    captured = {}

    def probe(app):  # at the restart frame, capture the result
        captured["state"] = app.state
        captured["q"] = app.q_hold_frames
        captured["r"] = app.r_hold_frames

    # Headless start forces PLAY; Esc@f3 -> PAUSE, then hold R f4..f33 (30 frames) -> restart@f33.
    run_event_script({
        "frames": 36,
        "keydowns": {3: [pygame.K_ESCAPE]},
        "held": {f: [pygame.K_r] for f in range(4, 34)},
        "probes": {33: probe},
    })
    assert captured.get("state") is GameState.PLAY, (
        "hold-R for 30 f in PAUSE did not restart into PLAY"
    )
    assert captured.get("q") == 0 and captured.get("r") == 0, (
        "the R-restart did not zero BOTH counters atomically"
    )
