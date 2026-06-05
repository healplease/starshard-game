r"""fx — cosmetic models: the parallax starfield and death/collect particles
(GDD §6.6, §6.7 / art_spec §3, §5). Pure data + factories; rendering is in view/.
"""

from dataclasses import dataclass

from .. import config as C


@dataclass
class Star:
    x: float
    y: float
    size: int
    speed: float
    color: tuple


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: int
    color: tuple


def make_starfield(rng):
    """70 stars across 3 parallax layers (GDD §6.6 / art_spec §2 table)."""
    layers = (
        (35, 1, 1.0, C.STAR_FAR),
        (25, 2, 2.0, C.STAR_MID),
        (10, 3, 3.5, C.STAR_NEAR),
    )
    stars = []
    for count, size, speed, color in layers:
        for _ in range(count):
            stars.append(Star(rng.randint(0, C.W), rng.randint(0, C.H), size, speed, color))
    return stars


def make_burst(rng, x, y, color):
    """6 tiny debris particles at a death/collect point (GDD §6.7 / art_spec §5)."""
    return [
        Particle(x, y, rng.uniform(-3, 3), rng.uniform(-3, 3), C.PART_LIFE, color)
        for _ in range(6)
    ]
