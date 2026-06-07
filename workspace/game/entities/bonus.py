r"""bonus — the diamond pickup model + the buff registry (GDD §V2.4 / art_spec §V2.1).

A `Bonus` is a falling collectible carrying its `kind` (a BonusKind) and an
optional `duration_override` used only by the smoke seed to shorten a buff so its
full lifecycle (apply→expire) fits inside 120 frames (level_spec §V2.5). The
letter/color/name lookups read config tables keyed by the kind's name.
"""

from dataclasses import dataclass
from typing import Optional

from .. import config as C


@dataclass
class Bonus:
    kind: "BonusKind"  # forward ref (enum lives in world.py)
    x: float
    y: float
    duration_override: Optional[int] = None  # smoke-only short duration

    @property
    def letter(self):
        return C.BONUS_LETTERS[self.kind.name]

    @property
    def color(self):
        return C.BONUS_COLORS[self.kind.name]


def buff_duration(kind, override=None):
    """Frames a timed buff should run for: an explicit override (smoke) wins,
    else the config default. Returns None for instant kinds (e.g. Repair)."""
    if override is not None:
        return override
    return C.BUFF_DURATION.get(kind.name)
