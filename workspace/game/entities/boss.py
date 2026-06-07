r"""boss — the Mothership entity model (GDD §V7.4/§V7.7, R59/R60/R66).

A `Boss` is its OWN entity (not an `Enemy` in the v5 roster): it carries its own
big HP pool, the +1000 defeat reward (awarded by systems/encounter on death), a
two-state lifecycle (ENTRANCE → ACTIVE; ARRIVAL and DEFEAT are 1-frame manager
transitions), and the moveset cursor. The movement/firing/collision *verbs* live
in systems/encounter.py + systems/combat.py — this is state only, mirroring the
Enemy/Player split. `split_dist` and the step cadence are stored per-instance so
the smoke seed can spawn a compressed boss (short entrance + fast moveset) without
touching the play-time constants (GDD §V7.15).
"""

from dataclasses import dataclass

from .. import config as C


@dataclass
class Boss:
    x: float
    y: float
    hp: int = C.BOSS_HP
    state: str = "ENTRANCE"  # ENTRANCE (descending) → ACTIVE (settled: oscillate + fire)
    osc_dir: int = 1  # oscillation ping-pong direction (-1 / +1)
    step_index: int = 0  # 0..3 → which moveset step fires NEXT (cycles 1→2→3→4)
    step_timer: int = 0  # frames until the next moveset step fires
    flash: int = 0  # 1-frame white hit-feedback tick (cuttable juice)
    # Per-instance levers so the smoke boss can be compressed (GDD §V7.15):
    split_dist: float = C.YELLOW_SPLIT_DIST  # frozen yellow-fan "midway" distance
    first_step_delay: int = C.BOSS_FIRST_STEP_DELAY  # f after settle before step 1
    step_interval: int = C.BOSS_STEP_INTERVAL  # f between subsequent steps
