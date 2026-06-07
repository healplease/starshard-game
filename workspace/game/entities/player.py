r"""player — the player ship model (GDD §6.1) extended with v2 buff state (§V2.2).

State + tiny accessors only; the movement/firing/collision *verbs* live in
systems/. `buff_timers` maps a BonusKind → frames remaining and holds **only
timed buffs that are currently active** (Repair is instant, never stored).
"""

from dataclasses import dataclass, field

from .. import config as C


@dataclass
class Player:
    x: float
    y: float
    id: int = 0  # v20: unique within-run ship ID (R128); set by World after construction
    hp: int = C.P_MAX_HP
    iframes: int = 0  # post-hit invulnerability (R18)
    fire_cd: int = 0  # frames until the next shot is allowed
    fan_fire_count: int = 0  # v18: counts Fan-active shots → sides fire every other (2:1, §V18.3)
    # BonusKind -> frames remaining (timed buffs only). Default-empty per player.
    buff_timers: dict = field(default_factory=dict)

    def buff(self, kind):
        """Frames remaining on a timed buff (0 if inactive)."""
        return self.buff_timers.get(kind, 0)

    @property
    def invulnerable(self):
        """Invulnerable if EITHER post-hit i-frames OR Shield is active (R27)."""
        from ..world import BonusKind

        return self.iframes > 0 or self.buff(BonusKind.SHIELD) > 0

    @property
    def shield_active(self):
        from ..world import BonusKind

        return self.buff(BonusKind.SHIELD) > 0

    @property
    def blink_timer(self):
        """Drives the invuln blink — longest of i-frames / shield remaining."""
        from ..world import BonusKind

        return max(self.iframes, self.buff(BonusKind.SHIELD))

    @property
    def fan_active(self):
        from ..world import BonusKind

        return self.buff(BonusKind.FAN) > 0

    @property
    def overdrive_active(self):
        from ..world import BonusKind

        return self.buff(BonusKind.OVERDRIVE) > 0

    @property
    def railgun_active(self):
        from ..world import BonusKind

        return self.buff(BonusKind.RAILGUN) > 0

    @property
    def score_mult_active(self):
        from ..world import BonusKind

        return self.buff(BonusKind.SCORE) > 0

    @property
    def fire_cooldown(self):
        """Resolved cooldown after firing — strongest-wins per stat (GDD §V18.4):
        the MIN of baseline and each active buff's target cd (lower = better).
        Overdrive→6, Railgun→9, baseline→12. Bounded ≥ 6 > 0; recomputed each
        shot so an expiring buff just drops a contributor (clean revert)."""
        cds = [C.FIRE_CD]
        if self.overdrive_active:
            cds.append(C.OVERDRIVE_CD)
        if self.railgun_active:
            cds.append(C.RAILGUN_CD)
        return min(cds)

    @property
    def bullet_speed(self):
        """Resolved bullet speed — strongest-wins per stat (GDD §V18.4): the MAX
        of baseline and each active buff's target speed (higher = better).
        Railgun→16, Overdrive→12, baseline→10. Bounded ≤ 16; recomputed each shot
        so an expiring buff falls back cleanly toward PB_SPEED (R110/R31)."""
        speeds = [C.PB_SPEED]
        if self.overdrive_active:
            speeds.append(C.OVERDRIVE_SPEED)
        if self.railgun_active:
            speeds.append(C.RAILGUN_SPEED)
        return max(speeds)
