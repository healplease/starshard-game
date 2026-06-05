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
    hp: int = C.P_MAX_HP
    iframes: int = 0           # post-hit invulnerability (R18)
    fire_cd: int = 0           # frames until the next shot is allowed
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
    def rapid_active(self):
        from ..world import BonusKind
        return self.buff(BonusKind.RAPID) > 0

    @property
    def score_mult_active(self):
        from ..world import BonusKind
        return self.buff(BonusKind.SCORE) > 0

    @property
    def fire_cooldown(self):
        """Current cooldown to apply after firing — halved while Rapid is up."""
        return C.RAPID_CD if self.rapid_active else C.FIRE_CD
