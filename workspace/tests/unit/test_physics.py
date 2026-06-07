"""Unit lane — movement/clamp physics (AC3). Ported from regression_harness."""

from game import config as C
from game.input import InputState
from game.systems import physics


def test_ac3_move_and_clamp(fresh_world):
    """AC3: player moves on input and clamps fully on-screen."""
    w = fresh_world()
    p = w.player
    x0 = p.x
    physics.update_play(w, InputState(1, 0, False))
    assert p.x == x0 + C.P_SPEED, "right move did not advance x by P_SPEED"
    for _ in range(300):
        physics.update_play(w, InputState(1, 1, False))
    assert p.x == C.W - 14 and p.y == C.H - 15, f"clamp failed: ({p.x},{p.y})"
