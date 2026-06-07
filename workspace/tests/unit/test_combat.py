"""Unit lane — combat/collision pipeline (AC5, AC6, AC7, AC8, AC9, AC14).

Ported from regression_harness. Pure logic: builds World/entities and drives
`combat.resolve` / `physics.update_play` directly — no App, no event loop, no blit.
"""

from game import config as C
from game.entities.bonus import Bonus
from game.entities.hazards import Asteroid, make_enemy
from game.entities.projectiles import EnemyBullet, PlayerBullet
from game.input import InputState
from game.systems import combat, physics
from game.world import BonusKind


def test_ac5_asteroid_contact(fresh_world):
    """AC5: asteroid contact damages the player and is consumed."""
    w = fresh_world()
    p = w.player
    a = Asteroid(p.x, p.y, 0, 0, C.AST_S_R, 1, False)
    w.asteroids = [a]
    hp0 = p.hp
    combat.resolve(w)
    assert p.hp == hp0 - C.AST_S_DMG, "small-asteroid damage wrong"
    assert p.iframes == C.IFRAMES, "i-frames did not start on hit"
    assert a not in w.asteroids, "asteroid not consumed on contact"


def test_ac6_enemy_bullet_and_ram(fresh_world):
    """AC6: enemy bullet deals 15; ramming an enemy deals 40 and kills it."""
    w = fresh_world()
    p = w.player
    w.ebullets = [EnemyBullet(p.x, p.y, 0, 0, family="RED")]
    hp0 = p.hp
    combat.resolve(w)
    assert p.hp == hp0 - C.EB_DMG, "enemy-bullet damage wrong"
    w2 = fresh_world()
    p2 = w2.player
    e = make_enemy(w2.rng, 0.0, "REGULAR")
    e.x, e.y = p2.x, p2.y
    w2.enemies = [e]
    hp0 = p2.hp
    combat.resolve(w2)
    assert p2.hp == hp0 - e.ram_dmg and e not in w2.enemies, "enemy ram wrong"


def test_ac7_fire_cooldown(fresh_world):
    """AC7: firing emits one shot and sets the cooldown (rate-limited)."""
    w = fresh_world()
    p = w.player
    physics.update_play(w, InputState(0, 0, True))
    assert len(w.pbullets) == 1, "first frame did not fire exactly one shot"
    assert p.fire_cd == C.FIRE_CD, "fire cooldown not set to baseline"
    physics.update_play(w, InputState(0, 0, True))
    assert len(w.pbullets) == 1, "fired again before cooldown elapsed"


def test_ac8_bullet_kills_rocks(fresh_world):
    """AC8: bullets remove a small rock in 1 hit, large in 2 (+score)."""
    w = fresh_world()
    w.pbullets = [PlayerBullet(100, 100, 0, -10)]
    w.asteroids = [Asteroid(100, 100, 0, 0, C.AST_S_R, 1, False)]
    s0 = w.score
    combat.resolve(w)
    assert not w.asteroids and not w.pbullets, "small rock not killed in 1 hit"
    assert w.score == s0 + C.AST_S_SCORE, "small-rock score wrong"
    al = Asteroid(100, 100, 0, 0, C.AST_L_R, 2, True)
    w.pbullets = [PlayerBullet(100, 100, 0, -10)]
    w.asteroids = [al]
    combat.resolve(w)
    assert al in w.asteroids and al.hits == 1, "large rock should survive first hit"


def test_ac9_first_hit_wins(fresh_world):
    """AC9: first-hit-wins: only one damage source applies per frame."""
    w = fresh_world()
    p = w.player
    w.asteroids = [
        Asteroid(p.x, p.y, 0, 0, C.AST_S_R, 1, False),
        Asteroid(p.x, p.y, 0, 0, C.AST_S_R, 1, False),
    ]
    hp0 = p.hp
    combat.resolve(w)
    assert p.hp == hp0 - C.AST_S_DMG, "more than one damage source applied"
    assert len(w.asteroids) == 1, "exactly one hazard should be consumed"


def test_ac14_bonus_collect_and_miss(fresh_world):
    """AC14: bonus collected on overlap; a missed bonus despawns penalty-free."""
    w = fresh_world()
    p = w.player
    bon = Bonus(BonusKind.OVERDRIVE, p.x, p.y)
    w.bonuses = [bon]
    combat.resolve(w)
    assert bon not in w.bonuses and p.buff(BonusKind.OVERDRIVE) > 0, "bonus not collected"
    w2 = fresh_world()
    p2 = w2.player
    miss = Bonus(BonusKind.REPAIR, 50, C.H + C.BONUS_PICKUP_R + 1)
    w2.bonuses = [miss]
    hp0, s0 = p2.hp, w2.score
    physics.update_play(w2, InputState(0, 0, False))
    assert miss not in w2.bonuses and p2.hp == hp0 and w2.score == s0, "missed bonus penalized"
    assert C.BONUS_CAP == 3, "on-screen bonus cap is not 3"
