r"""boss — the boss entity model (GDD §V7.4/§V7.7 + v16 §V16.x, R59/R60/R66/R99–R104).

A `Boss` is its OWN entity (not an `Enemy` in the v5 roster): it carries its own
big HP pool, the flat defeat reward (awarded by systems/encounter on death), a
two-state lifecycle (ENTRANCE → ACTIVE; ARRIVAL and DEFEAT are 1-frame manager
transitions), and the moveset cursor. The movement/firing/collision *verbs* live
in systems/encounter.py + systems/combat.py — this is state only, mirroring the
Enemy/Player split.

v16: a Boss is one of N pool types (`type` keys `config.BOSS_SPECS`). The per-boss
values the unchanged v7 loop reads (`hp`/`r`/`ram_dmg`/`kill_score`/cadence) live on
the INSTANCE, populated from the spec by `make_boss` — so combat/encounter/hud read
the active boss, never a hard-coded constant. The defaults stay the Mothership's v7
values so a bare `Boss(...)` is still a Mothership (back-compat for existing tests).
`split_dist` + the step cadence stay per-instance so the smoke seed can compress any
boss (short entrance + fast moveset) without touching the play-time constants (§V7.15).
"""

from dataclasses import dataclass

from .. import config as C


@dataclass
class Boss:
    x: float
    y: float
    id: int = 0  # v20: unique within-run ship ID (R128); set in make_boss via world
    type: str = "MOTHERSHIP"  # which BOSS_SPECS entry this boss is (v16 §V16.2)
    hp: int = C.BOSS_HP
    hp_max: int = C.BOSS_HP  # bar fills hp / hp_max (per-boss, art_spec §V16.4)
    r: float = C.BOSS_R  # collision radius (per-boss)
    ram_dmg: int = C.BOSS_RAM_DMG  # body-contact damage (per-boss)
    kill_score: int = C.BOSS_KILL_SCORE  # flat defeat reward (per-boss)
    state: str = "ENTRANCE"  # ENTRANCE (descending) → ACTIVE (settled: oscillate + fire)
    osc_dir: int = 1  # oscillation ping-pong direction (-1 / +1)
    step_index: int = 0  # 0..3 → which moveset step fires NEXT (cycles 1→2→3→4)
    step_timer: int = 0  # frames until the next moveset step fires
    flash: int = 0  # 1-frame white hit-feedback tick (cuttable juice)
    ring_phase: int = 0  # v16 NOVA: precessing ring start-angle accumulator (deg)
    # Per-instance levers so the smoke boss can be compressed (GDD §V7.15):
    split_dist: float = C.YELLOW_SPLIT_DIST  # frozen yellow-fan "midway" distance (Mothership)
    first_step_delay: int = C.BOSS_FIRST_STEP_DELAY  # f after settle before step 1
    step_interval: int = C.BOSS_STEP_INTERVAL  # f between subsequent steps


def make_boss(
    boss_type, pos, *, ship_id=0, first_step_delay=None, step_interval=None, split_dist=None
):
    """Build a Boss of `boss_type` from its `config.BOSS_SPECS` entry (v16 §V16.2): the
    per-boss stats come from the spec; the entrance/rest/oscillation framing is shared
    (the v7 globals, read by encounter). The three keyword overrides let the smoke seed
    compress the fight in-budget without touching the play-time constants (§V7.15).
    v20: `ship_id` (from world.next_ship_id) is the boss's unique within-run ID (R128)."""
    spec = C.BOSS_SPECS[boss_type]
    return Boss(
        x=float(pos[0]),
        y=float(pos[1]),
        id=ship_id,
        type=boss_type,
        hp=spec["hp"],
        hp_max=spec["hp"],
        r=spec["r"],
        ram_dmg=spec["ram_dmg"],
        kill_score=spec["kill_score"],
        first_step_delay=spec["first_step_delay"] if first_step_delay is None else first_step_delay,
        step_interval=spec["step_interval"] if step_interval is None else step_interval,
        split_dist=spec["split_dist"] if split_dist is None else split_dist,
    )
