"""Unit lane — World.reset_run (AC11). Ported from harness."""

from game import config as C
from game.entities.hazards import make_enemy
from game.entities.projectiles import PlayerBullet
from game.world import BonusKind


def test_ac11_reset_run(fresh_world):
    """AC11: restart fully resets the run, preserves session BEST."""
    w = fresh_world()
    w.score = 999
    w.player.hp = 10
    w.enemies = [make_enemy(w.rng, 0)]
    w.pbullets = [PlayerBullet(0, 0, 0, 0)]
    w.player.buff_timers[BonusKind.FAN] = 100
    w.charges = 0
    w.frame = 500
    w.best = 555
    w.reset_run()
    assert w.score == 0 and w.player.hp == C.P_MAX_HP, "score/hp not reset"
    assert not w.enemies and not w.pbullets, "entities not cleared"
    assert w.frame == 0 and w.charges == C.BOMB_START, "frame/charges not reset"
    assert w.best == 555, "session BEST must survive a restart"
