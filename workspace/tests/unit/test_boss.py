"""Unit lane — boss trigger / moveset / combat (AC39, AC40, AC41, AC43, AC46, AC48, AC49, AC50)."""

import math

from game import config as C
from game.entities.boss import Boss
from game.entities.hazards import make_asteroid, make_enemy
from game.entities.projectiles import EnemyBullet, PlayerBullet, split_yellow
from game.systems import bombs, combat, encounter


def test_ac39_boss_triggers(fresh_world):
    """AC39: boss triggers when the run clock reaches the TIME mark."""
    w = fresh_world()
    w.frame = int(C.BOSS_FIRST_MARK * 60)
    encounter.update(w)
    assert w.boss is not None, "boss did not trigger at the first mark"
    assert w.boss_next_mark == C.BOSS_FIRST_MARK + C.BOSS_INTERVAL, "next mark not advanced"


def test_ac40_arrival_clear_free(fresh_world):
    """AC40: arrival clear is free (clears field, spends NO charge)."""
    w = fresh_world()
    w.charges = 1
    w.enemies = [make_enemy(w.rng, 0)]
    w.asteroids = [make_asteroid(w.rng, 0)]
    w.frame = int(C.BOSS_FIRST_MARK * 60)
    encounter.update(w)
    assert w.boss is not None, "boss not spawned"
    assert not w.enemies and not w.asteroids, "arrival did not clear the field"
    assert w.charges == 1, "arrival clear wrongly spent a bomb charge"
    assert w.flash_timer == C.FLASH_FRAMES, "arrival flash not armed"


def test_ac41_boss_glides_then_activates(fresh_world):
    """AC41: boss glides in then snaps to rest and goes ACTIVE."""
    w = fresh_world()
    w.boss = Boss(x=300.0, y=float(C.BOSS_REST_Y - 3))
    encounter.update(w)
    assert w.boss.state == "ENTRANCE", "boss left ENTRANCE too early"
    encounter.update(w)
    assert w.boss.y == C.BOSS_REST_Y and w.boss.state == "ACTIVE", "boss did not settle/activate"


def test_ac43_moveset_step1_wave(fresh_world):
    """AC43: moveset step 1 spawns the 5-REGULAR wave."""
    w = fresh_world()
    w.boss = Boss(
        x=300.0,
        y=float(C.BOSS_REST_Y),
        state="ACTIVE",
        step_index=0,
        step_timer=1,
        first_step_delay=1,
        step_interval=5,
    )
    encounter.update(w)
    assert len(w.enemies) == 5 and all(e.kind == "REGULAR" for e in w.enemies), "wave 1 wrong"
    assert w.boss.step_index == 1, "step cursor did not advance"


def test_ac46_moveset_step4_yellow_fan(fresh_world):
    """AC46: moveset step 4 fires the 3-bullet YELLOW fan."""
    w = fresh_world()
    w.boss = Boss(x=300.0, y=400.0, state="ACTIVE", step_index=3, step_timer=1, step_interval=5)
    encounter.update(w)
    assert len(w.ebullets) == 3 and all(b.family == "YELLOW" for b in w.ebullets), (
        "yellow fan wrong"
    )


def test_ac48_boss_damage_and_defeat(fresh_world):
    """AC48: player bullets damage the boss; defeat awards +1000 and lifts the fight."""
    w = fresh_world()
    w.boss = Boss(x=300.0, y=400.0, hp=2)
    w.pbullets = [PlayerBullet(300, 400, 0, -10)]
    combat.resolve(w)
    assert w.boss is not None and w.boss.hp == 1 and not w.pbullets, "boss hit not registered"
    w.boss.hp = 1
    w.pbullets = [PlayerBullet(300, 400, 0, -10)]
    s0 = w.score
    combat.resolve(w)
    assert w.boss is None, "boss not defeated at hp 0"
    assert w.score == s0 + C.BOSS_KILL_SCORE, "defeat reward wrong"
    assert w.boss_defeat_popup_timer > 0, "defeat popup not armed"


def test_ac49_yellow_ring():
    """AC49: YELLOW fan -> even 12-RED 360-degree ring."""
    reds = []
    for phase in (0, 30, 60):
        yb = EnemyBullet(300, 300, 1, 0, family="YELLOW", split_timer=1, ring_phase=phase)
        reds += split_yellow(yb)
    assert len(reds) == 12 and all(r.family == "RED" for r in reds), "ring count/family wrong"
    angles = sorted(round(math.degrees(math.atan2(r.vy, r.vx))) % 360 for r in reds)
    assert angles == sorted(k * 30 for k in range(12)), f"ring not even 30deg steps: {angles}"


def test_ac50_bomb_spares_boss(fresh_world):
    """AC50: a bomb during the fight clears minions but the boss is immune."""
    w = fresh_world()
    w.boss = Boss(x=300.0, y=400.0, hp=50)
    w.enemies = [make_enemy(w.rng, 0)]
    bombs.update(w, True)
    assert w.boss is not None and w.boss.hp == 50, "boss took bomb damage (should be immune)"
    assert not w.enemies, "bomb did not clear minions during the fight"
