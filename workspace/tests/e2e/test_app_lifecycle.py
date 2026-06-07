"""E2E lane — App lifecycle + balance probe (AC1, AC10, AC13, AC85, v9 balance).

These build an `App` / run the in-process smoke loop / call `balance_probe`, so they live
in the e2e lane even where the assertion is about world/save logic (§2.4 borderline calls).
"""

import os

from game import app as app_mod
from game import config as C
from game import save
from game.app import App, balance_probe
from game.entities.hazards import Asteroid
from game.input import InputState
from game.world import GameState


def test_ac1_smoke_run():
    """AC1: in-process --smoke-test runs exactly 120 frames, never PAUSE."""
    app = App(smoke=True)
    app.run()
    assert app.frame == C.SMOKE_FRAMES, f"smoke ran {app.frame} frames, expected 120"
    assert app.state is not GameState.PAUSE, "smoke run entered PAUSE (should be impossible)"


def test_ac101_smoke_overdrive_lifecycle():
    """AC100/AC101 (v18): the repointed smoke seed (Overdrive, was Rapid) runs a full
    lifecycle through the REAL App smoke loop — applied (cd 12->6 + speed 10->12) then
    expired back to baseline, both observed before frame 120. Instruments the live
    pipeline by spying on `_draw` so it asserts behaviour, not code shape."""
    assert C.SMOKE_BONUS_KIND == "OVERDRIVE", "smoke seed must be repointed off RAPID (R113)"
    app = App(smoke=True)
    trace = []
    orig_draw = app._draw

    def spy():
        p = app.world.player
        trace.append((p.overdrive_active, p.fire_cooldown, p.bullet_speed))
        orig_draw()

    app._draw = spy
    app.run()
    applied = [t for t in trace if t[0] and t[1] == C.OVERDRIVE_CD and t[2] == C.OVERDRIVE_SPEED]
    reverted = [t for t in trace if not t[0] and t[1] == C.FIRE_CD and t[2] == C.PB_SPEED]
    assert applied, "Overdrive never applied (cd 6 + speed 12) during the smoke run"
    assert reverted, "Overdrive never reverted to baseline (cd 12 + speed 10) before frame 120"


def test_ac10_hp_zero_game_over(fresh_world):
    """AC10: HP<=0 -> GAME_OVER and BEST records the score."""
    app = App()
    app.world = fresh_world()
    app.state = GameState.PLAY
    app.bomb_fired = False
    app.world.player.hp = 5
    app.world.score = 123
    p = app.world.player
    app.world.asteroids = [Asteroid(p.x, p.y, 0, 0, C.AST_L_R, 2, True)]
    app._step_play(InputState(0, 0, False))
    assert app.state is GameState.GAME_OVER, "did not transition to GAME_OVER"
    assert app.world.best == 123, "BEST did not capture the score"


def test_ac13_ramp_and_termination():
    """AC13: difficulty ramp escalates AND every probed run terminates."""
    assert C.asteroid_interval(0) > C.asteroid_interval(120), "asteroid rate not ramping"
    assert C.enemy_cap(0) < C.enemy_cap(120), "enemy cap not ramping"
    assert C.hazard_speed_bonus(0) < C.hazard_speed_bonus(120), "hazard speed not ramping"
    times, _censored = balance_probe(runs=4, cap=3600)
    assert len(times) == 4 and all(t > 0 for t in times), "balance probe produced no runs"


def test_balance_probe_percentiles():
    """v9 balance: balance probe returns ordered median<=p95 survival figures."""
    times, _censored = balance_probe(runs=6, cap=3600)
    s = sorted(times)
    median = app_mod._percentile(s, 0.5)
    p95 = app_mod._percentile(s, 0.95)
    assert len(s) == 6 and median > 0, "balance probe produced no usable runs"
    assert median <= p95 + 1e-9, "median exceeded p95 (percentile logic broken)"


def test_ac85_headless_safe_save_path():
    """AC85: a smoke App resolves a temp save path, not the real one."""
    app = App(smoke=True)
    assert app.save_path != save.default_save_path(), "smoke App targets the real user save path"
    # resolve_path with no env/override falls back to a temp file for headless runs.
    saved = os.environ.pop(save.SAVE_PATH_ENV, None)
    try:
        hp = save.resolve_path(headless=True)
        assert hp != save.default_save_path() and hp.endswith(".json"), (
            "headless fallback is not a temp file"
        )
    finally:
        if saved is not None:
            os.environ[save.SAVE_PATH_ENV] = saved
