"""Unit lane — timed buffs / repair / restart cleanup (AC15–AC19). Ported from harness."""

from game import config as C
from game.entities.bonus import Bonus
from game.entities.projectiles import make_player_shots
from game.systems import buffs
from game.world import TIMED_KINDS, BonusKind


def test_ac15_repair_no_overheal(fresh_world):
    """AC15: Repair heals +40, clamps at 100 (no overheal), stores no pill."""
    w = fresh_world()
    p = w.player
    p.hp = 30
    buffs.apply(w, Bonus(BonusKind.REPAIR, p.x, p.y))
    assert p.hp == 70, "repair did not heal +40"
    assert BonusKind.REPAIR not in p.buff_timers, "repair wrongly stored a timed pill"
    assert w.repair_popup_timer == C.REPAIR_POPUP_LIFE, "repair popup not armed"
    p.hp = 80
    buffs.apply(w, Bonus(BonusKind.REPAIR, p.x, p.y))
    assert p.hp == 100, "repair overhealed past 100"


def test_ac16_timed_buff_reverts(fresh_world):
    """AC16: timed buff reverts cleanly on expiry."""
    w = fresh_world()
    p = w.player
    buffs.apply(w, Bonus(BonusKind.FAN, p.x, p.y))
    assert p.fan_active, "fan did not activate"
    p.buff_timers[BonusKind.FAN] = 1
    buffs.tick(w)
    assert not p.fan_active and BonusKind.FAN not in p.buff_timers, "fan did not revert"


def test_ac17_pill_order():
    """AC17: pill order is stable FAN/OVERDRIVE/RAILGUN/SHIELD/SCORE (v18); instant kinds out."""
    assert C.TIMED_ORDER == ("FAN", "OVERDRIVE", "RAILGUN", "SHIELD", "SCORE"), "pill order changed"
    names = tuple(k.name for k in TIMED_KINDS)
    assert names == C.TIMED_ORDER, "TIMED_KINDS out of sync with TIMED_ORDER"
    assert "REPAIR" not in names and "BOMB" not in names, "instant kind leaked into pills"


def test_ac18_recollect_refreshes(fresh_world):
    """AC18: re-collect hard-refreshes (no stack/double); types coexist."""
    w = fresh_world()
    p = w.player
    buffs.apply(w, Bonus(BonusKind.FAN, p.x, p.y))
    p.buff_timers[BonusKind.FAN] = 5
    buffs.apply(w, Bonus(BonusKind.FAN, p.x, p.y))
    assert p.buff_timers[BonusKind.FAN] == C.BUFF_DURATION["FAN"], "fan did not refresh to full"
    buffs.apply(w, Bonus(BonusKind.OVERDRIVE, p.x, p.y))
    assert p.fan_active and p.overdrive_active, "buffs did not coexist"
    assert len(make_player_shots(p.x, p.y, p.bullet_speed, fan=True, sides=True)) == 3, (
        "fan effect doubled"
    )


def test_ac19_restart_no_leak(fresh_world):
    """AC19: restart leaks no buff/popup/charge state into the new run."""
    w = fresh_world()
    p = w.player
    p.buff_timers[BonusKind.SHIELD] = 50
    w.repair_popup_timer = 10
    w.bomb_popup_timer = 10
    w.bonuses = [Bonus(BonusKind.REPAIR, 0, 0)]
    w.reset_run()
    assert p is not w.player, "reset_run did not rebuild the player"
    assert w.player.buff_timers == {}, "buff timers leaked"
    assert w.repair_popup_timer == 0 and w.bomb_popup_timer == 0, "popups leaked"
    assert w.bonuses == [], "pickups leaked"
