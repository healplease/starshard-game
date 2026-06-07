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
    source: int = 0  # v20 (R128): the firing ship's ID (the player); additive, no motion change


@dataclass
class EnemyBullet:
    x: float
    y: float
    vx: float
    vy: float
    family: str = (
        "RED"  # render hue/shape: RED / GREEN / CYAN / YELLOW / NOVA (§V5.2/§V7.12/§V16.3)
    )
    split_timer: Optional[int] = (
        None  # frames until a GREEN/YELLOW bullet bursts; None = never splits
    )
    ring_phase: Optional[int] = None  # v7 YELLOW only: this fan bullet's ring quarter (0/30/60°)
    dmg: int = C.EB_DMG  # per-hit player damage; default v1/v5/v7 EB_DMG, NOVA overrides (§V16.3)
    source: int = 0  # v20 (R128): the firing ship's ID (enemy/boss); additive, no motion change

    @property
    def color(self):
        return C.EB_COLORS[self.family]


@dataclass
class Beam:
    """v20 (GDD §V20.3): the LASER's weapon — a persistent timed line SEGMENT (not a
    point bullet). Anchored at the firing ship's emitter eye (`ox, oy` = origin = pivot),
    it sweeps by ROTATING about that origin: `angle` (radians) is the live aim heading,
    advancing toward `target_angle` (the frozen fire-time aim) at BEAM_SWEEP_DPS, capped
    to BEAM_SWEEP_MAX_DEG total. Two phases: WINDUP (harmless, thin telegraph) then
    DAMAGING (lethal, widening 2→6 px, removed ONLY on timeout — never on contact, R126).
    `source` = the owning LASER's ship ID (drives the owner-freeze + death attribution)."""

    ox: float  # origin / pivot = the emitter eye (cx, cy+LASER_EYE_DY)
    oy: float
    angle: float  # live aim heading (radians); rotates toward target_angle
    target_angle: float  # frozen fire-time aim (radians) — the captured player direction
    start_angle: float  # the angle at arm-time (to cap the total swept arc)
    phase: str  # "WINDUP" | "DAMAGING"
    timer: int  # frames left in the current phase
    source: int  # owning LASER ship ID (R128/R129)

    @property
    def width(self):
        """Live core width in px — the SINGLE number driving BOTH draw and collision
        (art_spec §V20a.3.2 invariant). 0 in WINDUP (harmless); LINEAR 2→6 over DAMAGING."""
        if self.phase != "DAMAGING":
            return 0.0
        td = 1.0 - self.timer / C.BEAM_DAMAGE_F  # progress 0→1 through the damaging phase
        return C.BEAM_START_W + (C.BEAM_FINAL_W - C.BEAM_START_W) * td

    @property
    def lethal(self):
        return self.phase == "DAMAGING"


def make_player_shots(px, py, speed, fan=False, sides=True, source=0):
    """Shots fired this frame, every beam scaled to the resolved bullet `speed`
    (v18 — bullet speed is a buffable stat, GDD §V18.4). Nose origin = (px, py-15),
    matching the ship triangle's tip (art_spec §2.1). v20: every shot carries
    `source` = the player's ship ID (R128, player shots included for consistency).
      - No Fan: one forward (center) beam.
      - Fan, `sides=True`: the full 3-beam fan (center + both ±12° sides).
      - Fan, `sides=False`: center beam only — the skipped half of the 2:1
        center:side cadence (R106/§V18.3); the side beams fire every other shot.
    """
    if fan and sides:
        dirs = C.FAN_DIRS  # center + both side beams
    else:
        dirs = (C.CENTER_DIR,)  # lone center beam (no Fan, or Fan's side-skip frame)
    return [PlayerBullet(px, py - 15, dx * speed, dy * speed, source=source) for dx, dy in dirs]


def make_enemy_bullet(ex, ey, px, py, rng, kind="REGULAR", source=0):
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
        s = max(C.SPLIT_FRACTION * d, C.SPLIT_MIN_DIST)  # frozen split distance (§V5.4)
        split_timer = round(s / speed)  # distance ÷ speed → frozen timer
    return EnemyBullet(ex, ey, vx, vy, family=family, split_timer=split_timer, source=source)


def split_pellet(pellet):
    """Replace a matured GREEN pellet with EXACTLY 3 RED children fanned about its
    own frozen heading at (-18°, 0°, +18°) — center included (GDD §V5.4.3). Each
    child is an ordinary RED enemy bullet (terminal: split_timer stays None)."""
    base = math.atan2(pellet.vy, pellet.vx)  # the pellet's frozen heading
    children = []
    for off_deg in (-C.FAN_HALF_ANGLE, 0, C.FAN_HALF_ANGLE):
        theta = base + math.radians(off_deg)
        vx, vy = math.cos(theta) * C.CHILD_SPEED, math.sin(theta) * C.CHILD_SPEED
        children.append(EnemyBullet(pellet.x, pellet.y, vx, vy, family="RED", source=pellet.source))
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
        children.append(EnemyBullet(bullet.x, bullet.y, vx, vy, family="RED", source=bullet.source))
    return children
