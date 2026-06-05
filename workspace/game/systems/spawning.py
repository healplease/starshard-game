r"""spawning — difficulty-ramp spawn timers + the v2 bonus economy + smoke seeding.

Owns: asteroid/enemy spawn countdowns (level_spec §3), the bonus timed drip and
the on-screen cap (level_spec §V2.1), the shared kind-weight pick, the enemy-drop
helper called from combat, and the `--smoke-test` seed (level_spec §V2.5).
All numbers come from config; this module only decides *when* and *what* to add.
"""

from .. import config as C
from ..world import BonusKind, rng_drip
from ..entities.hazards import make_asteroid, make_enemy
from ..entities.projectiles import EnemyBullet
from ..entities.bonus import Bonus


def update(world):
    """Advance all spawn countdowns one frame and spawn when they fire.

    v7 spawn-freeze (§V7.2/R58): while a boss is active the v1 asteroid + v5 enemy
    + v2 bonus-drip emits are GATED on `not boss_active` — but the countdowns keep
    free-running (skip-no-bank, identical to the at-cap rule), so resuming on
    boss defeat never dumps a backlog. The only new hostiles during a fight are the
    boss's own minions (from the encounter manager, not here)."""
    t = world.t
    boss_active = world.boss is not None
    # Asteroids — countdown to the ramped interval, respect the §6 cap; frozen while boss-active.
    world.ast_timer -= 1
    if world.ast_timer <= 0:
        if not boss_active and len(world.asteroids) < C.AST_CAP:
            world.asteroids.append(make_asteroid(world.rng, t))
        world.ast_timer = C.asteroid_interval(t)
    # Enemies — spawn attempt; skip (no banking) if at the ramped cap or boss-active.
    # The v1 cap/interval are UNCHANGED; v5 only chooses the KIND at the instant a
    # spawn actually fires (level_spec §V5.1) — variety replaces a REGULAR slot, never adds.
    world.enemy_timer -= 1
    if world.enemy_timer <= 0:
        if not boss_active and len(world.enemies) < C.enemy_cap(t):
            kind = C.choose_enemy_kind(t, world.rng)
            world.enemies.append(make_enemy(world.rng, t, kind))
        world.enemy_timer = C.enemy_interval(t)
    # Bonus timed drip — re-draw the cadence whether or not we spawn (no banking);
    # frozen while boss-active so the fight injects no new economy (§V7.3).
    world.bonus_drip_timer -= 1
    if world.bonus_drip_timer <= 0:
        if not boss_active and len(world.bonuses) < C.BONUS_CAP:
            x = world.rng.uniform(20, 580)
            spawn_bonus(world, x, -float(C.BONUS_HALF_DIAG))
        world.bonus_drip_timer = rng_drip(world.rng)


def spawn_bonus(world, x, y, kind=None, duration=None):
    """Add one bonus pickup (kind rolled by weight unless forced). Caller is
    responsible for the cap check on the drip path; enemy-drop checks below."""
    if kind is None:
        kind = BonusKind[C.pick_bonus_kind(world.rng)]
    world.bonuses.append(Bonus(kind=kind, x=x, y=y, duration_override=duration))


def roll_enemy_drop(world, x, y):
    """On a bullet-kill (combat §V2.7 step 2): 15% chance to drop a bonus at the
    death point, only if under the on-screen cap (ram-kills never call this)."""
    if len(world.bonuses) < C.BONUS_CAP and world.rng.random() < C.ENEMY_DROP_CHANCE:
        spawn_bonus(world, x, y)


def seed_smoke(world):
    """Headless coverage seed (GDD §11 + §V2.5): 3 asteroids + 1 enemy for
    combat/firing, plus one short-duration Rapid pickup parked in the player's
    path so a full spawn→collect→apply→expire bonus lifecycle runs inside 120 f."""
    t = world.t
    for _ in range(3):
        world.asteroids.append(make_asteroid(world.rng, t))
    world.enemies.append(make_enemy(world.rng, t))


def seed_smoke_bonus(world):
    """Place the guaranteed-lifecycle Rapid pickup (level_spec §V2.5). Called a
    couple of frames into the smoke run so it's seeded mid-loop, not at init."""
    bx, by = C.SMOKE_BONUS_POS
    spawn_bonus(world, float(bx), float(by),
                kind=BonusKind[C.SMOKE_BONUS_KIND], duration=C.SMOKE_BONUS_DUR)


def seed_smoke_boss_target(world):
    """Pre-seed a small target (2 asteroids + 1 enemy) a couple of frames before the
    smoke boss arrives (GDD §V7.15) so the FREE arrival flush has something visible
    to remove — making AC40's "field cleared, no charge spent" observable headlessly."""
    t = world.t
    for _ in range(2):
        world.asteroids.append(make_asteroid(world.rng, t))
    world.enemies.append(make_enemy(world.rng, t))


def seed_smoke_split(world):
    """Seed one GREEN pellet already in flight with a forced-short split distance
    (GDD §V5.6), so the full fire→travel→split→children path runs headlessly inside
    120 f: S=SMOKE_SPLIT_DIST(60) → split_timer=round(60/4.5)=13 → bursts ~frame 16,
    then 3 RED children update to frame 120. Bypasses the aim routine (no live
    player read) so the geometry is deterministic regardless of RNG."""
    ux, uy = C.SMOKE_SPLIT_HEADING
    speed = C.ENEMY_KINDS["HEAVY"]["bspeed"]
    bx, by = C.SMOKE_SPLIT_POS
    timer = round(C.SMOKE_SPLIT_DIST / speed)
    world.ebullets.append(EnemyBullet(
        float(bx), float(by), ux * speed, uy * speed,
        family="GREEN", split_timer=timer))
