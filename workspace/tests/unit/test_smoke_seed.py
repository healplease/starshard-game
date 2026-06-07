"""Unit lane — smoke constants (AC2) + seeded Overdrive lifecycle via systems (AC20/AC100).

AC20 uses only spawning+combat+buffs (no App) → unit per the §2.4 borderline ruling.
v18: the smoke seed is Overdrive (was Rapid, R108/R113) — cd 12→6 + speed 10→12.
"""

from game import config as C
from game.systems import buffs, combat, spawning


def test_ac2_smoke_constants():
    """AC2: SMOKE_FRAMES==120 and SMOKE_TIMELINE ordering is sane."""
    assert C.SMOKE_FRAMES == 120, "smoke is not exactly 120 frames"
    assert C.smoke_timeline_ok(), "SMOKE_TIMELINE ordering/budget check failed"


def test_ac20_seeded_overdrive_lifecycle(fresh_world):
    """AC20/AC100: seeded Overdrive runs full spawn->collect->apply->expire (cd + speed revert)."""
    w = fresh_world()
    p = w.player
    spawning.seed_smoke_bonus(w)
    assert len(w.bonuses) == 1, "smoke bonus not seeded"
    p.x, p.y = C.SMOKE_BONUS_POS
    combat.resolve(w)
    assert p.overdrive_active, "overdrive not applied on collect"
    assert p.fire_cooldown == C.OVERDRIVE_CD and p.bullet_speed == C.OVERDRIVE_SPEED, (
        "overdrive cd/speed not applied on collect"
    )
    for _ in range(C.SMOKE_BONUS_DUR + 1):
        buffs.tick(w)
    assert not p.overdrive_active, "overdrive did not expire"
    assert p.fire_cooldown == C.FIRE_CD and p.bullet_speed == C.PB_SPEED, (
        "overdrive did not revert to baseline cd/speed"
    )
