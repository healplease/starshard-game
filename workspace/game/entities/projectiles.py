r"""projectiles — player & enemy bullet models + factories (GDD §6.2, §6.5, §V5.3/§V5.4).

Player bullets carry a velocity vector so the v2 spread-fan (GDD §V2.2) is a
data-only change: `make_player_shots` emits one straight beam normally, or three
angled beams while Fan is active — every beam is an ordinary 1-hit player bullet.

Enemy bullets are now a single uniform type with a render `family` (RED/GREEN/
CYAN) and an optional `split_timer` (GDD §V5.4): the HEAVY's GREEN pellet freezes
a midway split distance at fire time and bursts into 3 RED children fanned about
its frozen heading; every other family leaves `split_timer = None` and is an
ordinary aimed bullet. Collision stays a flat r=5 for all families (combat).
"""

import math
from dataclasses import dataclass
from typing import Optional

from .. import config as C


@dataclass
class PlayerBullet:
    x: float
    y: float
    vx: float
    vy: float


@dataclass
class EnemyBullet:
    x: float
    y: float
    vx: float
    vy: float
    family: str = "RED"               # render hue/shape: RED / GREEN / CYAN / YELLOW (§V5.2/§V7.12)
    split_timer: Optional[int] = None  # frames until a GREEN/YELLOW bullet bursts; None = never splits
    ring_phase: Optional[int] = None   # v7 YELLOW only: this fan bullet's ring quarter (0/30/60°)

    @property
    def color(self):
        return C.EB_COLORS[self.family]


def make_player_shots(px, py, fan_active):
    """Shots fired this frame: 3-beam fan if Fan is active, else 1 forward beam.
    Nose origin = (px, py-15), matching the ship triangle's tip (art_spec §2.1)."""
    velocities = C.FAN_VELOCITIES if fan_active else C.SINGLE_VELOCITY
    return [PlayerBullet(px, py - 15, vx, vy) for vx, vy in velocities]


def make_enemy_bullet(ex, ey, px, py, rng, kind="REGULAR"):
    """One enemy bullet for `kind`, fired through the shared aim routine (§V5.3):
    a heading toward the player's CURRENT position, perturbed per-shot by a uniform
    angle in [-cone, +cone]. cone=0 reduces identically to v1 dead-on aim (AC29).
    A GREEN (HEAVY) pellet additionally freezes its midway split distance NOW from
    the fire-time pellet→player distance D (GDD §V5.4) — nothing about the player is
    read again after this call.
    """
    spec = C.ENEMY_KINDS[kind]
    speed = spec["bspeed"]
    base = math.atan2(py - ey, px - ex)
    cone = math.radians(spec["cone_deg"])
    theta = base + rng.uniform(-cone, cone)
    vx, vy = math.cos(theta) * speed, math.sin(theta) * speed
    family = spec["bullet"]
    split_timer = None
    if family == "GREEN":
        d = math.hypot(px - ex, py - ey)
        s = max(C.SPLIT_FRACTION * d, C.SPLIT_MIN_DIST)   # frozen split distance (§V5.4)
        split_timer = round(s / speed)                    # distance ÷ speed → frozen timer
    return EnemyBullet(ex, ey, vx, vy, family=family, split_timer=split_timer)


def split_pellet(pellet):
    """Replace a matured GREEN pellet with EXACTLY 3 RED children fanned about its
    own frozen heading at (-18°, 0°, +18°) — center included (GDD §V5.4.3). Each
    child is an ordinary RED enemy bullet (terminal: split_timer stays None)."""
    base = math.atan2(pellet.vy, pellet.vx)               # the pellet's frozen heading
    children = []
    for off_deg in (-C.FAN_HALF_ANGLE, 0, C.FAN_HALF_ANGLE):
        theta = base + math.radians(off_deg)
        vx, vy = math.cos(theta) * C.CHILD_SPEED, math.sin(theta) * C.CHILD_SPEED
        children.append(EnemyBullet(pellet.x, pellet.y, vx, vy, family="RED"))
    return children


def split_yellow(bullet):
    """Replace a matured YELLOW boss-fan bullet with EXACTLY 4 RED children — this
    bullet's quarter of the even 12-red 360° ring (GDD §V7.12). Headings are the
    ABSOLUTE set (ring_phase + k·90°), k=0..3; with the three fan bullets carrying
    ring_phase 0 / 30 / 60 the union is the even {0,30,…,330}° ring. Children are
    ordinary RED enemy bullets (terminal: never re-split, like the v5 red children)."""
    children = []
    for k in range(4):
        theta = math.radians(bullet.ring_phase + k * 90)
        vx, vy = math.cos(theta) * C.RED_CHILD_SPEED, math.sin(theta) * C.RED_CHILD_SPEED
        children.append(EnemyBullet(bullet.x, bullet.y, vx, vy, family="RED"))
    return children
