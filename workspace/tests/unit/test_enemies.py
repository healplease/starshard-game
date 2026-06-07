"""Unit lane — enemy roster + splitting pellet aim (AC22, AC25, AC27, AC29)."""

import math
import random

from game import config as C
from game.entities.projectiles import EnemyBullet, make_enemy_bullet, split_pellet
from game.input import InputState
from game.systems import physics


def test_ac22_enemy_roster():
    """AC22: three distinct enemy kinds with ordered HP / entry speed."""
    assert set(C.ENEMY_KINDS) == {"REGULAR", "HEAVY", "SCOUT"}, "enemy roster changed"
    hp = C.ENEMY_KINDS
    assert hp["HEAVY"]["hp"] > hp["REGULAR"]["hp"] > hp["SCOUT"]["hp"], "hp ordering wrong"
    assert hp["SCOUT"]["entry"] > hp["REGULAR"]["entry"] > hp["HEAVY"]["entry"], (
        "speed ordering wrong"
    )


def test_ac25_bullet_families():
    """AC25: bullet families: REGULAR=RED, HEAVY=GREEN, SCOUT=CYAN."""
    assert C.ENEMY_KINDS["REGULAR"]["bullet"] == "RED", "regular bullet family wrong"
    assert C.ENEMY_KINDS["HEAVY"]["bullet"] == "GREEN", "heavy bullet family wrong"
    assert C.ENEMY_KINDS["SCOUT"]["bullet"] == "CYAN", "scout bullet family wrong"


def test_ac27_green_pellet_splits(fresh_world):
    """AC27: GREEN pellet matures into exactly 3 terminal RED children."""
    pellet = make_enemy_bullet(300, 100, 300, 400, random.Random(1), "HEAVY")
    assert pellet.family == "GREEN" and pellet.split_timer is not None, "pellet not GREEN/timed"
    children = split_pellet(pellet)
    assert len(children) == 3, "split did not yield exactly 3 children"
    assert all(c.family == "RED" and c.split_timer is None for c in children), (
        "children not terminal RED"
    )
    w = fresh_world()
    speed = C.ENEMY_KINDS["HEAVY"]["bspeed"]
    w.ebullets = [EnemyBullet(300, 300, 0, speed, family="GREEN", split_timer=2)]
    physics.update_play(w, InputState(0, 0, False))
    physics.update_play(w, InputState(0, 0, False))
    assert len(w.ebullets) == 3 and all(b.family == "RED" for b in w.ebullets), (
        "pellet did not burst in flight"
    )


def test_ac29_aim_within_cone():
    """AC29: aim heads toward the player within the kind's cone."""
    b = make_enemy_bullet(300, 100, 300, 400, random.Random(5), "REGULAR")
    ang = math.degrees(math.atan2(b.vy, b.vx))  # 90 deg == straight down toward player
    assert abs(ang - 90) <= C.ENEMY_KINDS["REGULAR"]["cone_deg"] + 1e-6, f"aim off-cone: {ang}"
