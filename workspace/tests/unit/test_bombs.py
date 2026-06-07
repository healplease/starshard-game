"""Unit lane — bombs / panic button (AC30, AC31, AC32, AC34, AC35, AC36)."""

from game import config as C
from game.entities.bonus import Bonus
from game.entities.hazards import make_asteroid, make_enemy
from game.entities.projectiles import EnemyBullet, PlayerBullet
from game.systems import bombs, buffs
from game.world import BonusKind


def test_ac30_bomb_flushes(fresh_world):
    """AC30: X flushes the field, spends one charge, arms flash + lockout."""
    w = fresh_world()
    w.enemies = [make_enemy(w.rng, 0)]
    w.asteroids = [make_asteroid(w.rng, 0)]
    w.ebullets = [EnemyBullet(10, 10, 0, 0)]
    c0 = w.charges
    bombs.update(w, True)
    assert not w.enemies and not w.asteroids and not w.ebullets, "flush did not clear hostiles"
    assert w.charges == c0 - 1, "charge not decremented"
    assert w.flash_timer == C.FLASH_FRAMES and w.bomb_lockout == C.BOMB_LOCKOUT, (
        "flash/lockout not armed"
    )


def test_ac31_flush_no_score(fresh_world):
    """AC31: flush awards no score."""
    w = fresh_world()
    w.enemies = [make_enemy(w.rng, 0)]
    s0 = w.score
    bombs.update(w, True)
    assert w.score == s0, "flush awarded score"


def test_ac32_flush_spares_bullets_and_pickups(fresh_world):
    """AC32: flush spares player bullets and pickups."""
    w = fresh_world()
    pb = PlayerBullet(0, 0, 0, -10)
    bon = Bonus(BonusKind.REPAIR, 50, 50)
    w.pbullets = [pb]
    w.bonuses = [bon]
    w.enemies = [make_enemy(w.rng, 0)]
    bombs.update(w, True)
    assert pb in w.pbullets and bon in w.bonuses and not w.enemies, "flush hit a spared list"


def test_ac34_zero_charge_noop(fresh_world):
    """AC34: 0 charges -> X is a no-op (no flush, no flash)."""
    w = fresh_world()
    w.charges = 0
    w.enemies = [make_enemy(w.rng, 0)]
    bombs.update(w, True)
    assert w.enemies and w.charges == 0 and w.flash_timer == 0, "0-charge bomb was not a no-op"


def test_ac35_lockout_blocks_second(fresh_world):
    """AC35: lockout blocks a second bomb on the next frame."""
    w = fresh_world()
    w.charges = 4
    bombs.update(w, True)
    w.enemies = [make_enemy(w.rng, 0)]
    bombs.update(w, True)
    assert w.charges == 3 and w.enemies, "lockout did not block a back-to-back bomb"


def test_ac36_bomb_pickup_charge(fresh_world):
    """AC36: bomb pickup grants +1 charge, clamped at the cap."""
    w = fresh_world()
    w.charges = 1
    buffs.apply(w, Bonus(BonusKind.BOMB, 0, 0))
    assert w.charges == 2 and w.bomb_popup_timer == C.REPAIR_POPUP_LIFE, "bomb pickup +1 wrong"
    w.charges = C.BOMB_CAP
    buffs.apply(w, Bonus(BonusKind.BOMB, 0, 0))
    assert w.charges == C.BOMB_CAP, "bomb pickup overfilled past cap"
