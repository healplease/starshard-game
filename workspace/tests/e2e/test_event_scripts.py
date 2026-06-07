"""E2E lane — the event-script behavioral gate (v9 event).

Drives the real `App` loop through a scripted bomb / pause / unpause / re-pause / Q-quit
sequence and asserts each beat behaved.
"""

import pygame

from game import config as C
from game.app import run_event_script
from game.world import GameState


def test_event_script_bomb_pause_quit():
    """v9 event: bomb/pause/unpause/re-pause/quit all behave under one script."""
    results = {}

    def after_bomb(app):
        results["bomb"] = (
            not app.world.enemies
            and not app.world.asteroids
            and app.world.charges == C.BOMB_START - 1
            and app.world.flash_timer > 0
        )

    def state_is(name, st):
        def probe(app):
            results[name] = app.state is st

        return probe

    app = run_event_script({
        "frames": 60,
        "keydowns": {3: [pygame.K_x], 6: [pygame.K_ESCAPE], 8: [pygame.K_ESCAPE], 10: [pygame.K_ESCAPE]},
        "held": {f: [pygame.K_q] for f in range(11, 55)},
        "probes": {
            3: after_bomb,
            6: state_is("paused", GameState.PAUSE),
            8: state_is("unpaused", GameState.PLAY),
            10: state_is("repaused", GameState.PAUSE),
        },
    })
    assert results.get("bomb"), "X-in-PLAY bomb did not flush/charge/flash"
    assert results.get("paused"), "Esc did not pause"
    assert results.get("unpaused"), "Esc did not unpause"
    assert results.get("repaused"), "Esc did not re-pause"
    assert app.quit_via_qhold, "Q-hold did not quit"
