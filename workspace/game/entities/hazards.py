r"""hazards — Asteroid (small/large) and Enemy fighter models + factories
(GDD §6.3, §6.4 / level_spec §3–§4). Size-derived stats (score/damage/color)
are read from config via the `large` flag so the model stays minimal.
"""

from dataclasses import dataclass

from .. import config as C


@dataclass
class Asteroid:
    x: float
    y: float
    vx: float
    vy: float
    r: int
    hits: int
    large: bool
    flash: int = 0          # white survived-hit flash countdown (R17)

    @property
    def score(self):
        return C.AST_L_SCORE if self.large else C.AST_S_SCORE

    @property
    def dmg(self):
        return C.AST_L_DMG if self.large else C.AST_S_DMG

    @property
    def color(self):
        return C.ASTEROID_L if self.large else C.ASTEROID_S


@dataclass
class Enemy:
    x: float
    y: float
    dir: int                # strafe direction (-1 / +1)
    kind: str = "REGULAR"   # v5 roster key (REGULAR / HEAVY / SCOUT) — branched on for
    hp: int = C.EN_HP       #   stats/move/fire/render (R36/AC29); hp set per kind in factory
    phase: str = "A"        # "A" = entry descent, "B" = strafe + fire
    fire_timer: float = 0.0
    flash: int = 0          # 1-frame white flash on taking a bullet (R17)

    @property
    def spec(self):
        """This kind's locked stat row (GDD §V5.2 / config.ENEMY_KINDS)."""
        return C.ENEMY_KINDS[self.kind]

    @property
    def r(self):
        return self.spec["r"]          # collision radius (18 / 13 / 10)

    @property
    def score(self):
        return self.spec["score"]      # score on kill (80 / 50 / 60)

    @property
    def ram_dmg(self):
        return self.spec["ram"]        # contact damage to the player (50 / 40 / 30)


def make_asteroid(rng, t):
    """Spawn one asteroid at the top with size/speed rolled against the ramp."""
    large = rng.random() < C.large_chance(t)
    r = C.AST_L_R if large else C.AST_S_R
    lo, hi = C.AST_L_SPD if large else C.AST_S_SPD
    drift = C.AST_L_DRIFT if large else C.AST_S_DRIFT
    return Asteroid(
        x=rng.uniform(r, C.W - r), y=float(-r),
        vx=rng.uniform(-drift, drift),
        vy=rng.uniform(lo, hi) + C.hazard_speed_bonus(t),   # ramp speed bonus
        r=r, hits=2 if large else 1, large=large,
    )


def make_enemy(rng, t, kind="REGULAR"):
    """Spawn one enemy of `kind` at the top, ready to descend then strafe (GDD §6.4,
    §V5.2). Position/mechanism are kind-independent (level_spec §V5.1); only the
    stats differ. The first fire cooldown is the ramp base scaled by this kind's
    fire_mult (HEAVY fires least often, SCOUT throttled, REGULAR == v1)."""
    spec = C.ENEMY_KINDS[kind]
    return Enemy(
        x=rng.uniform(40, 560), y=-24.0,
        dir=rng.choice((-1, 1)),
        kind=kind, hp=spec["hp"],
        fire_timer=round(C.enemy_fire_interval(t) * spec["fire_mult"]),
    )
