"""E2E lane — pause / unpause / Q-hold-quit gestures (AC53, AC56, AC57, AC58, AC61,
AC62, AC63, AC66, AC67, R76).

Drives the REAL `App` loop (`run_event_script`) and `App._handle_events` with scripted
Esc/Q keydowns + held keys — the gesture machinery, not pure logic.
"""

import random

import pygame

from game import config as C
from game.app import App, run_event_script
from game.entities.hazards import Asteroid
from game.input import InputState
from game.world import GameState, World


def _run_from_state(state, script):
    """Run the REAL App loop but begin in `state` (override the headless PLAY force in
    `_new_world`) so START / GAME_OVER hold-to-quit is exercised through the live loop."""
    app = App(event_script=script)

    def patched():  # replaces _new_world: start in `state`, no smoke seed
        app.world = World(random.Random(C.SMOKE_SEED))
        app.state = state

    app._new_world = patched
    app.run()
    return app


def test_ac53_esc_pauses_and_freezes_clock():
    """AC53: Esc toggles PAUSE and the run clock freezes while paused."""
    cap = {}

    def grab(name):
        def probe(app):
            cap[name] = (app.state, app.world.frame, app.world.player.x, app.world.player.y)

        return probe

    run_event_script({
        "frames": 15,
        "keydowns": {3: [pygame.K_ESCAPE]},
        "held": {},
        "probes": {3: grab("at_pause"), 12: grab("later")},
    })
    assert cap["at_pause"][0] is GameState.PAUSE, "Esc did not enter PAUSE"
    assert cap["at_pause"][1] == cap["later"][1], "run clock advanced while paused"
    assert cap["at_pause"][2:] == cap["later"][2:], "player drifted while paused"


def test_ac56_qhold_quits_from_pause():
    """AC56: Q held PAUSE_QUIT_FRAMES in PAUSE quits the app."""
    app = run_event_script({
        "frames": 60,
        "keydowns": {2: [pygame.K_ESCAPE]},
        "held": {f: [pygame.K_q] for f in range(3, 40)},
        "probes": {},
    })
    assert app.quit_via_qhold, "Q-hold did not quit the app"


def test_ac57_qhold_resets_on_release():
    """AC57: Q released before the threshold resets the hold (no accumulation)."""
    cap = {}

    def grab(name):
        def probe(app):
            cap[name] = app.q_hold_frames

        return probe

    run_event_script({
        "frames": 20,
        "keydowns": {2: [pygame.K_ESCAPE]},
        "held": {f: [pygame.K_q] for f in range(3, 11)},  # 8 held frames (< 30)
        "probes": {10: grab("held8"), 12: grab("released")},
    })
    assert cap["held8"] == 8, f"hold counter wrong while held: {cap['held8']}"
    assert cap["released"] == 0, "hold counter did not reset on release"


def test_ac58_esc_noop_in_start_gameover(fresh_world):
    """AC58: Esc is a no-op in START/GAME_OVER; pygame.QUIT still quits."""
    app = App()
    app.world = fresh_world()
    app.state = GameState.START
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    cont = app._handle_events()
    assert cont is True and app.state is GameState.START, "Esc not a no-op in START"
    app.state = GameState.GAME_OVER
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    cont = app._handle_events()
    assert cont is True and app.state is GameState.GAME_OVER, "Esc not a no-op in GAME_OVER"
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    assert app._handle_events() is False, "pygame.QUIT no longer quits"


def test_ac66_hold_counter_resets_on_transition(fresh_world):
    """AC66: the hold counter resets to 0 on every state transition (q AND r, §V12.4)."""

    def fresh_app(state):
        app = App()
        app.world = fresh_world()
        app.state = state
        app.q_hold_frames = 25  # a near-complete hold carried into the transition
        app.r_hold_frames = 25  # v12: BOTH counters must zero on every transition
        return app

    def both_zero(app):
        return app.q_hold_frames == 0 and app.r_hold_frames == 0

    # #1 START -> PLAY (a non-Q key starts and resets)
    app = fresh_app(GameState.START)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    app._handle_events()
    assert app.state is GameState.PLAY and both_zero(app), "#1 START->PLAY did not reset both"

    # #2 PLAY -> PAUSE (Esc)
    app = fresh_app(GameState.PLAY)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    app._handle_events()
    assert app.state is GameState.PAUSE and both_zero(app), "#2 PLAY->PAUSE did not reset both"

    # #3 PAUSE -> PLAY (Esc resume)
    app = fresh_app(GameState.PAUSE)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    app._handle_events()
    assert app.state is GameState.PLAY and both_zero(app), "#3 PAUSE->PLAY did not reset both"

    # #4 PLAY -> GAME_OVER (die with Q AND R incidentally held — the #1 risk)
    app = fresh_app(GameState.PLAY)
    app.world.player.hp = 1
    p = app.world.player
    app.world.asteroids = [Asteroid(p.x, p.y, 0, 0, C.AST_L_R, 2, True)]
    app._step_play(InputState(0, 0, False))
    assert app.state is GameState.GAME_OVER, "#4 did not reach GAME_OVER"
    assert both_zero(app), "#4 PLAY->GAME_OVER did not zero both counters"

    # #5 GAME_OVER -> PLAY (v12: R-HOLD restart, KEYDOWN branch removed)
    app = fresh_app(GameState.GAME_OVER)
    app.r_hold_frames = C.RESTART_HOLD_FRAMES - 1  # one held frame from firing
    app.event_script = {"held": {app.frame: [pygame.K_r]}}
    app._restart_hold_step()
    assert app.state is GameState.PLAY and both_zero(app), "#5 GAME_OVER->PLAY did not reset both"

    # #6 PAUSE -> PLAY (v12: R-HOLD restart)
    app = fresh_app(GameState.PAUSE)
    app.r_hold_frames = C.RESTART_HOLD_FRAMES - 1
    app.event_script = {"held": {app.frame: [pygame.K_r]}}
    app._restart_hold_step()
    assert app.state is GameState.PLAY and both_zero(app), "#6 PAUSE->PLAY did not reset both"


def test_r76_start_q_carveout(fresh_world):
    """R76: START — Q is carved out of 'any key starts'; other keys still start."""
    app = App()
    app.world = fresh_world()
    app.state = GameState.START
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q))
    app._handle_events()
    assert app.state is GameState.START, "a Q tap wrongly started the run (R76 unreachable)"
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
    app._handle_events()
    assert app.state is GameState.PLAY, "a non-Q key did not start the run"


def test_ac61_qhold_quits_from_start():
    """AC61: holding Q PAUSE_QUIT_FRAMES on START quits the app."""
    app = _run_from_state(GameState.START, {
        "frames": 50,
        "held": {f: [pygame.K_q] for f in range(0, 45)},  # 45 continuous held frames > 30
        "probes": {},
    })
    assert app.quit_via_qhold, "Q held on START did not quit"


def test_ac62_qhold_quits_from_gameover():
    """AC62: holding Q PAUSE_QUIT_FRAMES on GAME_OVER quits the app."""
    app = _run_from_state(GameState.GAME_OVER, {
        "frames": 50,
        "held": {f: [pygame.K_q] for f in range(0, 45)},
        "probes": {},
    })
    assert app.quit_via_qhold, "Q held on GAME_OVER did not quit"


def test_ac63_release_resets_no_accumulation():
    """AC63: release before threshold resets; re-press starts from 0 (no accumulation)."""
    cap = {}

    def grab(name):
        def probe(app):
            cap[name] = app.q_hold_frames

        return probe

    app = _run_from_state(GameState.START, {
        "frames": 30,
        "held": {
            **{f: [pygame.K_q] for f in range(0, 10)},  # 10 held (<30)
            **{f: [pygame.K_q] for f in range(14, 18)},  # then re-press for 4
        },
        "probes": {9: grab("held10"), 12: grab("released"), 17: grab("repress4")},
    })
    assert not app.quit_via_qhold, "a sub-threshold hold wrongly quit"
    assert cap["held10"] == 10, f"counter wrong while held: {cap['held10']}"
    assert cap["released"] == 0, "counter did not reset on release"
    assert cap["repress4"] == 4, f"re-press accumulated instead of starting from 0: {cap['repress4']}"


def test_ac67_qhold_excluded_in_play():
    """AC67: Q held in PLAY does NOT arm the gesture or quit (real loop)."""
    cap = {}

    def grab(app):
        cap["state"] = app.state
        cap["q"] = app.q_hold_frames

    # Headless start forces PLAY; hold Q for 40 frames without ever pausing.
    app = run_event_script({
        "frames": 45,
        "keydowns": {},
        "held": {f: [pygame.K_q] for f in range(0, 40)},
        "probes": {38: grab},
    })
    assert not app.quit_via_qhold, "Q held in PLAY quit the run (R81 violated)"
    assert cap["state"] is GameState.PLAY, "state left PLAY under a held Q"
    assert cap["q"] == 0, "the hold counter advanced during PLAY (gesture armed mid-run)"
