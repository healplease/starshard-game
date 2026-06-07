r"""buffs — apply-on-collect, tick timers, expiry→revert (GDD §V2.2/§V2.3, R30/R31).

The whole stacking model lives here and is deterministic:
  - Repair is instant: clamp-heal, fire the popup, store nothing (never stacks).
  - A timed buff is a **hard refresh** — set frames_remaining to a full duration
    (reset, not add), so re-collecting can't bank time and effects never double.
  - Different timed types coexist as independent entries in player.buff_timers.
  - On reaching 0 the entry is deleted → the player cleanly reverts to baseline.
Restart cleanup is `World.reset_run()` (player + popup timer rebuilt → no leak).
"""

from .. import config as C
from ..entities.bonus import buff_duration
from ..world import BonusKind


def apply(world, bonus):
    """Apply a just-collected bonus to the player (GDD §V2.2/§V2.3, §V6.6)."""
    p = world.player
    if bonus.kind is BonusKind.REPAIR:
        p.hp = min(C.P_MAX_HP, p.hp + C.REPAIR_HP)  # clamp, no overheal (R24)
        world.repair_popup_timer = C.REPAIR_POPUP_LIFE  # transient "+40" (R29)
    elif bonus.kind is BonusKind.BOMB:
        # Instant +1 bomb charge, clamped to the cap — at full cap it's WASTED
        # (consumed, clamped away), mirroring Repair-at-full (GDD §V6.6, R51).
        world.charges = min(C.BOMB_CAP, world.charges + C.BOMB_PICKUP_CHARGES)
        world.bomb_popup_timer = C.REPAIR_POPUP_LIFE  # transient "+1 BOMB" (art_spec §V6.4)
    else:
        # Hard refresh to one full duration — never accumulate (R30).
        p.buff_timers[bonus.kind] = buff_duration(bonus.kind, bonus.duration_override)


def tick(world):
    """Decrement every active timed buff; delete on expiry (clean revert, R31).
    Also ages the transient repair popup."""
    p = world.player
    for kind in list(p.buff_timers):
        p.buff_timers[kind] -= 1
        if p.buff_timers[kind] <= 0:
            del p.buff_timers[kind]
    if world.repair_popup_timer > 0:
        world.repair_popup_timer -= 1
