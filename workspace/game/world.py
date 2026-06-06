r"""world — the plain-data state container plus the game's enums.

`World` holds every mutable piece of game state (the player, entity lists, score,
ramp timers, the RNG). It carries **no pygame and no rendering** — systems mutate
it, view reads it. The cosmetic starfield lives here too (it scrolls in every
state), but `reset_run()` deliberately preserves it (and `best` + `rng`) so a
restart only wipes the *run*, never the session (R31 / level_spec §2).
"""

from enum import Enum

from . import config as C
from .entities.player import Player
from .entities.fx import make_starfield
from .save import Store


class GameState(Enum):
    START = "START"
    PLAY = "PLAY"
    PAUSE = "PAUSE"
    STATS = "STATS"          # v14: lifetime-stats ledger, reached from START via Tab (GDD §V14.2)
    GAME_OVER = "GAME_OVER"


class BonusKind(Enum):
    """All six bonus kinds. The four *timed* kinds appear in HUD pill order
    (Fan, Rapid, Shield, Score, GDD §V2.6); Repair and BOMB are instant (no pill).
    BOMB (v6, GDD §V6.6) grants +1 bomb charge instead of a buff."""
    REPAIR = "REPAIR"
    FAN = "FAN"
    RAPID = "RAPID"
    SHIELD = "SHIELD"
    SCORE = "SCORE"
    BOMB = "BOMB"


# Timed kinds in their stable HUD order, derived from config.TIMED_ORDER.
TIMED_KINDS = tuple(BonusKind[name] for name in C.TIMED_ORDER)


class World:
    """The blackboard for one process: a persistent starfield/best/rng plus the
    run-specific state that `reset_run()` rebuilds on every fresh run (R13)."""

    def __init__(self, rng):
        self.rng = rng
        self.best = 0
        # v14 lifetime-stats store (R94): process-lifetime, NOT run state — `reset_run`
        # deliberately never touches it, so the five counters carry across every run in
        # the session. The App swaps in the disk-loaded store after construction; a bare
        # World (tests) gets a zeroed one so the combat/encounter counters always have a home.
        self.store = Store()
        self.stars = make_starfield(rng)   # cosmetic; persists across runs
        self.reset_run()

    def reset_run(self):
        """Wipe everything run-specific to the level_spec §2 starting state.
        Keeps rng, stars, and best (no leak between runs — R31 / AC19)."""
        self.player = Player(x=float(C.P_START[0]), y=float(C.P_START[1]))
        self.asteroids = []
        self.enemies = []
        self.pbullets = []
        self.ebullets = []
        self.bonuses = []
        self.particles = []
        self.score = 0
        self.frame = 0                 # run frame counter (t = frame / 60)
        self.sec_score_at = 0          # last whole second credited (survival bonus)
        self.repair_popup_timer = 0    # transient "+40" popup (R29 / art_spec §V2.4)
        # v6 bomb state (GDD §V6.2) — restart resets to BOMB_START, no leak (AC36).
        self.charges = C.BOMB_START    # bomb charges, clamped [0, BOMB_CAP]
        self.flash_timer = 0           # full-screen activation flash countdown (§V6.5)
        self.bomb_lockout = 0          # frames X is ignored after a bomb (§V6.4)
        self.bomb_popup_timer = 0      # transient "+1 BOMB" popup (art_spec §V6.4)
        # v7 boss state (GDD §V7.x) — restart clears any in-progress fight, no leak.
        self.boss = None               # the active Boss entity, or None (None ⇒ freeze lifted)
        self.boss_next_mark = C.BOSS_FIRST_MARK   # next TIME mark (s) to fire a boss (75, 165, …)
        self.boss_defeat_popup_timer = 0          # transient "MOTHERSHIP DOWN" + "+points" popup
        self.boss_defeat_points = 0               # the actual award shown (1000, or 2000 ×Score×2)
        # Spawn countdowns. The first drip is drawn now so a bonus lands ~10–14 s
        # in (level_spec §V2.1). Asteroid/enemy timers start at their t=0 interval.
        self.ast_timer = C.asteroid_interval(0)
        self.enemy_timer = C.enemy_interval(0)
        self.bonus_drip_timer = rng_drip(self.rng)

    @property
    def t(self):
        """Seconds elapsed in the current run."""
        return self.frame / 60.0


def rng_drip(rng):
    """A fresh drip-cadence draw in [DRIP_MIN, DRIP_MAX] (level_spec §V2.1)."""
    return rng.randint(C.DRIP_MIN, C.DRIP_MAX)
