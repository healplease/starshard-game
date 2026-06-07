"""Unit lane — v18 bonus rebalance (R106–R112 / AC94–AC100).

Pure logic only (no App/render): Fan's 2:1 side cadence, the re-sliced RNG ladder,
Rapid's removal, the Overdrive/Railgun fire-cd + bullet-speed effects, and the
strongest-wins cross-stat stacking with clean revert (GDD §V18.4).
"""

from game import config as C
from game.entities.bonus import Bonus
from game.entities.projectiles import make_player_shots
from game.input import InputState
from game.systems import buffs, physics
from game.world import BonusKind


# ── R106 / AC94 — Fan side beams fire at exactly half the center cadence (2:1) ──
def test_r106_fan_side_beams_half_cadence(fresh_world):
    w = fresh_world()
    p = w.player
    buffs.apply(w, Bonus(BonusKind.FAN, p.x, p.y))
    center_shots = side_volleys = 0
    for _ in range(600):  # ~50 volleys at the baseline 12-f cadence
        w.pbullets.clear()
        physics.update_play(w, InputState(0, 0, True))
        if w.pbullets:  # a volley fired this frame
            center_shots += 1
            if any(b.vx != 0 for b in w.pbullets):  # side beams have non-zero vx (±12°)
                side_volleys += 1
            # a side volley is the full 3-beam fan; a skip frame is center-only
            assert len(w.pbullets) in (1, 3), "fan volley not 1 (skip) or 3 (full) beams"
    assert center_shots > 0, "fan never fired"
    # sides fire every other volley, starting on the first → exactly 2:1 center:side
    assert side_volleys == (center_shots + 1) // 2, "fan side cadence is not 2:1"


def test_r106_fresh_fan_starts_with_a_side_volley(fresh_world):
    """A fresh Fan pickup begins its 2:1 cadence on shot 1 (full fan), parity reset."""
    w = fresh_world()
    p = w.player
    p.fan_fire_count = 7  # leftover parity from a prior (expired) Fan
    buffs.apply(w, Bonus(BonusKind.FAN, p.x, p.y))
    assert p.fan_fire_count == 0, "fresh Fan did not reset its side-cadence parity"
    shots = make_player_shots(p.x, p.y, p.bullet_speed, fan=True, sides=True)
    assert len(shots) == 3, "first fan volley should be the full 3-beam fan"


# ── R107 / AC95 — Fan is rarer than its old weight 20; ladder still sound ──────
def test_r107_fan_rarer_than_before():
    width = {}
    lo = 0
    for hi, name in C.BONUS_WEIGHTS:
        width[name] = hi - lo + 1
        lo = hi + 1
    assert width["FAN"] == 12, "Fan weight should be 12 (was 20)"
    assert width["FAN"] < 20, "Fan must be strictly rarer than its old weight (R107)"


# ── R108 / AC96 — Rapid is gone everywhere ────────────────────────────────────
def test_r108_rapid_fully_retired():
    assert not hasattr(BonusKind, "RAPID"), "RAPID BonusKind still exists"
    assert "RAPID" not in dict(C.BONUS_WEIGHTS).values(), "RAPID still in the RNG ladder"
    for reg in (C.BONUS_LETTERS, C.BONUS_COLORS, C.BONUS_NAMES, C.BUFF_DURATION):
        assert "RAPID" not in reg, "RAPID lingers in a bonus registry"
    assert "RAPID" not in C.TIMED_ORDER, "RAPID still in the HUD pill order"
    assert C.SMOKE_BONUS_KIND != "RAPID", "smoke seed still points at RAPID"
    assert not hasattr(C, "RAPID_CD"), "RAPID_CD constant still defined"


# ── R111 / AC99 — combined new weight == 20, ladder sums 100, non-overlapping ──
def test_r111_ladder_sums_100_non_overlapping():
    width = {}
    lo = 0
    for hi, name in C.BONUS_WEIGHTS:
        assert hi >= lo, "ladder thresholds overlap / go backwards"
        width[name] = hi - lo + 1
        lo = hi + 1
    assert C.BONUS_WEIGHTS[-1][0] == 99, "ladder must be exhaustive over 0–99"
    assert sum(width.values()) == 100, "ladder does not sum to 100"
    assert width["OVERDRIVE"] + width["RAILGUN"] == 20, "new kinds' combined weight != old Rapid 20"
    assert len(width) == 7, "roster should be exactly 7 kinds"


# ── R109a / R110 / AC97 — Overdrive: cd halved + speed up a bit; reverts ───────
def test_r109a_overdrive_effects_and_revert(fresh_world):
    w = fresh_world()
    p = w.player
    assert p.fire_cooldown == C.FIRE_CD and p.bullet_speed == C.PB_SPEED, "baseline wrong"
    buffs.apply(w, Bonus(BonusKind.OVERDRIVE, p.x, p.y))
    assert p.fire_cooldown == 6 and p.bullet_speed == 12, "overdrive effects wrong"
    assert C.OVERDRIVE_SPEED > C.PB_SPEED, "overdrive speed must be a small bump up"
    p.buff_timers[BonusKind.OVERDRIVE] = 1
    buffs.tick(w)
    assert p.fire_cooldown == C.FIRE_CD and p.bullet_speed == C.PB_SPEED, "overdrive did not revert"


# ── R109b / R110 / AC98 — Railgun: speed up a lot + cd up a bit (smaller cut) ──
def test_r109b_railgun_effects_and_revert(fresh_world):
    w = fresh_world()
    p = w.player
    buffs.apply(w, Bonus(BonusKind.RAILGUN, p.x, p.y))
    assert p.bullet_speed == 16 and p.fire_cooldown == 9, "railgun effects wrong"
    # cooldown cut is smaller than Overdrive's halving, and bounded > 6 < 12
    assert 6 < C.RAILGUN_CD < C.FIRE_CD, "railgun cd must sit strictly between 6 and 12"
    assert (C.FIRE_CD - C.RAILGUN_CD) < (C.FIRE_CD - C.OVERDRIVE_CD), "railgun cut not smaller"
    assert C.RAILGUN_SPEED > C.OVERDRIVE_SPEED, "railgun speed-up must exceed overdrive's"
    p.buff_timers[BonusKind.RAILGUN] = 1
    buffs.tick(w)
    assert p.fire_cooldown == C.FIRE_CD and p.bullet_speed == C.PB_SPEED, "railgun did not revert"


# ── R112 / AC100 — strongest-wins per stat; bounded; clean revert on each expiry ─
def test_r112_strongest_wins_both_active(fresh_world):
    w = fresh_world()
    p = w.player
    buffs.apply(w, Bonus(BonusKind.OVERDRIVE, p.x, p.y))
    buffs.apply(w, Bonus(BonusKind.RAILGUN, p.x, p.y))
    # min cd (Overdrive wins 6) / max speed (Railgun wins 16) — NOT composed
    assert p.fire_cooldown == 6, "fire cd should resolve to the strongest (min) = 6"
    assert p.bullet_speed == 16, "bullet speed should resolve to the strongest (max) = 16"
    assert p.fire_cooldown >= C.OVERDRIVE_CD > 0, "cd must stay bounded above zero"


def test_r112_one_expires_other_remains(fresh_world):
    w = fresh_world()
    p = w.player
    buffs.apply(w, Bonus(BonusKind.OVERDRIVE, p.x, p.y))
    buffs.apply(w, Bonus(BonusKind.RAILGUN, p.x, p.y))
    p.buff_timers[BonusKind.OVERDRIVE] = 1
    buffs.tick(w)  # Overdrive expires; Railgun remains
    assert not p.overdrive_active and p.railgun_active, "wrong buff expired"
    # cd falls back to Railgun's 9 (Overdrive gone), speed stays Railgun's 16
    assert p.fire_cooldown == 9 and p.bullet_speed == 16, (
        "stat did not cleanly drop the contributor"
    )
    p.buff_timers[BonusKind.RAILGUN] = 1
    buffs.tick(w)
    assert p.fire_cooldown == C.FIRE_CD and p.bullet_speed == C.PB_SPEED, "did not fall to baseline"


def test_r112_restart_clears_buff_stats(fresh_world):
    w = fresh_world()
    p = w.player
    buffs.apply(w, Bonus(BonusKind.OVERDRIVE, p.x, p.y))
    buffs.apply(w, Bonus(BonusKind.RAILGUN, p.x, p.y))
    p.fan_fire_count = 5
    w.reset_run()
    np = w.player
    assert np.buff_timers == {}, "buff timers leaked across restart"
    assert np.fire_cooldown == C.FIRE_CD and np.bullet_speed == C.PB_SPEED, (
        "stats leaked across restart"
    )
    assert np.fan_fire_count == 0, "fan cadence parity leaked across restart"


# ── R110 — buffed bullet speed scales the emitted bullet velocity ─────────────
def test_r110_bullet_speed_scales_velocity():
    fast = make_player_shots(300, 700, C.RAILGUN_SPEED)
    base = make_player_shots(300, 700, C.PB_SPEED)
    assert abs(fast[0].vy) == C.RAILGUN_SPEED and abs(base[0].vy) == C.PB_SPEED, "speed not applied"
    # 16 px/f < smallest target diameter (2*AST_S_R=24) → no tunneling (level_spec §V18.1)
    assert C.RAILGUN_SPEED < 2 * C.AST_S_R, "railgun bullet could tunnel the smallest target"
