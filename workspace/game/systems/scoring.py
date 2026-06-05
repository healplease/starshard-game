r"""scoring — award points (with the v2 Score×2 multiplier) + the survival tick.

Every score gain flows through `award`, so the Score×2 buff (R34 / GDD §V2.7) is
applied uniformly at every site (asteroid, enemy, survival). Session high score is
held on the World and refreshed by the app on GAME_OVER.
"""

from .. import config as C


def award(world, base):
    """Add `base` points, doubled while Score×2 is active (GDD §V2.7)."""
    mult = C.SCORE_MULT if world.player.score_mult_active else 1
    world.score += base * mult


def survival_tick(world):
    """+1 point per full second survived (level_spec §7), via `award` so the
    Score×2 multiplier covers the time bonus too (GDD §V2.7)."""
    sec = world.frame // 60
    if sec > world.sec_score_at:
        award(world, sec - world.sec_score_at)
        world.sec_score_at = sec
