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
    flash: int = 0  # white survived-hit flash countdown (R17)

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
    dir: int  # strafe direction (-1 / +1)
    id: int = 0  # v20: unique within-run ship ID (R128); set in make_enemy via world
    kind: str = "REGULAR"  # v5 roster key (REGULAR/HEAVY/SCOUT/LASER) — branched on for
    hp: int = C.EN_HP  #   stats/move/fire/render (R36/AC29); hp set per kind in factory
    phase: str = "A"  # "A" = entry descent, "B" = strafe + fire (LASER: B = beam cycle)
    fire_timer: float = 0.0
    flash: int = 0  # 1-frame white flash on taking a bullet (R17)
    # v20 LASER beam cycle (kind=="LASER" only; level_spec §V20L.1): the 3-state attack
    # loop. cooldown after entry, then WINDUP→DAMAGING→COOLDOWN repeating. Driven in
    # systems/lasers; the enemy is frozen (no reposition) while it owns a live beam.
    beam_phase: str = "COOLDOWN"  # "COOLDOWN" | "WINDUP" | "DAMAGING" (LASER only)
    beam_timer: int = 0  # frames left in the current beam phase
    repo_target_x: float = 0.0  # COOLDOWN reposition goal x (uniform in band, re-rolled per cd)

    @property
    def spec(self):
        """This kind's locked stat row (GDD §V5.2 / config.ENEMY_KINDS)."""
        return C.ENEMY_KINDS[self.kind]

    @property
    def r(self):
        return self.spec["r"]  # collision radius (18 / 13 / 10)

    @property
    def score(self):
        return self.spec["score"]  # score on kill (80 / 50 / 60)

    @property
    def ram_dmg(self):
        return self.spec["ram"]  # contact damage to the player (50 / 40 / 30)


def make_asteroid(rng, t):
    """Spawn one asteroid at the top with size/speed rolled against the ramp."""
    large = rng.random() < C.large_chance(t)
    r = C.AST_L_R if large else C.AST_S_R
    lo, hi = C.AST_L_SPD if large else C.AST_S_SPD
    drift = C.AST_L_DRIFT if large else C.AST_S_DRIFT
    return Asteroid(
        x=rng.uniform(r, C.W - r),
        y=float(-r),
        vx=rng.uniform(-drift, drift),
        vy=rng.uniform(lo, hi) + C.hazard_speed_bonus(t),  # ramp speed bonus
        r=r,
        hits=2 if large else 1,
        large=large,
    )


def make_enemy(rng, t, kind="REGULAR", ship_id=0):
    """Spawn one enemy of `kind` at the top, ready to descend then strafe (GDD §6.4,
    §V5.2). Position/mechanism are kind-independent (level_spec §V5.1); only the
    stats differ. The first fire cooldown is the ramp base scaled by this kind's
    fire_mult (HEAVY fires least often, SCOUT throttled, REGULAR == v1).
    v20: `ship_id` (from world.next_ship_id) is this enemy's unique within-run ID (R128);
    a LASER additionally starts in COOLDOWN so it WINDS UP only after its entry descent."""
    spec = C.ENEMY_KINDS[kind]
    e = Enemy(
        x=rng.uniform(40, 560),
        y=-24.0,
        dir=rng.choice((-1, 1)),
        id=ship_id,
        kind=kind,
        hp=spec["hp"],
        fire_timer=round(C.enemy_fire_interval(t) * spec["fire_mult"]),
    )
    if kind == "LASER":
        # Enters in COOLDOWN with a short pre-fire timer so it begins WINDUP shortly after
        # it settles into Phase B (it does not fire mid-entry). repo_target_x = its spawn x.
        e.beam_phase = "COOLDOWN"
        e.beam_timer = C.BEAM_COOLDOWN_F
        e.repo_target_x = e.x
    return e
