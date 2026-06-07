"""Unit lane — smoke constants (AC2) + seeded Rapid lifecycle via systems (AC20).

AC20 uses only spawning+combat+buffs (no App) → unit per the §2.4 borderline ruling.
"""

from game import config as C
from game.systems import buffs, combat, spawning


def test_ac2_smoke_constants():
    """AC2: SMOKE_FRAMES==120 and SMOKE_TIMELINE ordering is sane."""
    assert C.SMOKE_FRAMES == 120, "smoke is not exactly 120 frames"
    assert C.smoke_timeline_ok(), "SMOKE_TIMELINE ordering/budget check failed"


def test_ac20_seeded_rapid_lifecycle(fresh_world):
    """AC20: seeded Rapid runs full spawn->collect->apply->expire."""
    w = fresh_world()
    p = w.player
    spawning.seed_smoke_bonus(w)
    assert len(w.bonuses) == 1, "smoke bonus not seeded"
    p.x, p.y = C.SMOKE_BONUS_POS
    combat.resolve(w)
    assert p.rapid_active and p.fire_cooldown == C.RAPID_CD, "rapid not applied on collect"
    for _ in range(C.SMOKE_BONUS_DUR + 1):
        buffs.tick(w)
    assert not p.rapid_active and p.fire_cooldown == C.FIRE_CD, "rapid did not expire/revert"
