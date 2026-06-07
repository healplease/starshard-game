r"""combat — the per-frame collision pipeline (GDD §8, superseded by §V2.7 for v2).

Resolved in order, each step skipping anything already destroyed this frame:
  1. player bullets × asteroids        → score(×mult) + particles on destroy
  2. player bullets × enemies          → score + particles + enemy-drop roll
  3. player × bonus pickups (collect)  → apply buff + collect burst (always allowed)
  4. player × {asteroid, enemy, ebullet} damage — ONLY while vulnerable; skipped
     entirely while Shield (or post-hit i-frames) is active (R27). First hit wins.
Buff-timer ticking (step 5) and the health<=0 check (step 6) are driven by the
app loop (buffs.tick + the return value).
"""

from .. import config as C
from ..entities.fx import make_burst
from . import buffs, encounter, scoring, spawning


def _hit(x1, y1, r1, x2, y2, r2):
    """Circle-vs-circle via squared distance (GDD §8). Player bullet (a rect) is
    approximated as a circle of half its height — cheap and fine at this scale."""
    rr = r1 + r2
    return (x1 - x2) ** 2 + (y1 - y2) ** 2 <= rr * rr


def resolve(world):
    p = world.player
    dead_pb, dead_ast, dead_en, dead_eb, dead_bonus = set(), set(), set(), set(), set()

    # 1) Player bullets × asteroids
    for b in world.pbullets:
        if id(b) in dead_pb:
            continue
        for a in world.asteroids:
            if id(a) in dead_ast:
                continue
            if _hit(b.x, b.y, C.PB_H / 2, a.x, a.y, a.r):
                dead_pb.add(id(b))
                a.hits -= 1
                if a.hits <= 0:
                    dead_ast.add(id(a))
                    scoring.award(world, a.score)
                    world.store.asteroids_destroyed += (
                        1  # v14 R93: count at the destroy/award site (1 per rock)
                    )
                    world.particles += make_burst(world.rng, a.x, a.y, a.color)
                elif a.large:
                    a.flash = 5  # survived hit → white flash (R17)
                break

    # 2) Player bullets × enemies (+ enemy-drop on a bullet-kill, §V2.5)
    for b in world.pbullets:
        if id(b) in dead_pb:
            continue
        for e in world.enemies:
            if id(e) in dead_en:
                continue
            if _hit(b.x, b.y, C.PB_H / 2, e.x, e.y, e.r):
                dead_pb.add(id(b))
                e.hp -= 1
                e.flash = 1
                if e.hp <= 0:
                    dead_en.add(id(e))
                    scoring.award(world, e.score)  # minion SCORE on, normal v5 (§V7.3)
                    world.store.enemies_killed += (
                        1  # v14 R93: count at the destroy/award site (incl. boss minions)
                    )
                    world.particles += make_burst(world.rng, e.x, e.y, C.ENEMY)
                    # Minion pickup-DROPS are SUPPRESSED during a boss fight (§V7.3):
                    # no farming charges/buffs off boss-spawned adds (boss-active → skip).
                    if world.boss is None:
                        spawning.roll_enemy_drop(world, e.x, e.y)
                break

    # 2b) Player bullets × boss (folded into §V2.7 step 2, R60/§V7.13) — −1 HP per
    #     hit; the boss is its OWN entity (not a v5 Enemy: no kind score, just its
    #     own HP + the +1000 defeat reward). On HP ≤ 0 → DEFEAT (award + lift freeze).
    boss = world.boss
    if boss is not None:
        for b in world.pbullets:
            if id(b) in dead_pb:
                continue
            if _hit(b.x, b.y, C.PB_H / 2, boss.x, boss.y, C.BOSS_R):
                dead_pb.add(id(b))
                boss.hp -= 1
                boss.flash = 1
                if boss.hp <= 0:
                    encounter.on_defeat(world)  # +1000 (×mult), drop boss → freeze lifts
                    break

    # 3) Player × bonus pickups — collect (independent of invulnerability, §V2.7)
    for bonus in world.bonuses:
        if id(bonus) in dead_bonus:
            continue
        if _hit(p.x, p.y, C.P_R, bonus.x, bonus.y, C.BONUS_PICKUP_R):
            dead_bonus.add(id(bonus))
            buffs.apply(world, bonus)
            world.particles += make_burst(world.rng, bonus.x, bonus.y, bonus.color)

    # 4) Player damage — only while vulnerable (Shield/​i-frames skip this), first hit wins
    if not p.invulnerable:
        dmg = 0
        # Boss body ram (R61/§V7.13) — the scariest thing to touch (60 > HEAVY 50);
        # the boss is NOT consumed (it persists), unlike a hazard hit.
        if world.boss is not None and _hit(p.x, p.y, C.P_R, world.boss.x, world.boss.y, C.BOSS_R):
            dmg = C.BOSS_RAM_DMG
        for a in world.asteroids:
            if dmg:
                break
            if id(a) not in dead_ast and _hit(p.x, p.y, C.P_R, a.x, a.y, a.r):
                dmg, _ = a.dmg, dead_ast.add(id(a))
                break
        if dmg == 0:
            for e in world.enemies:
                if id(e) not in dead_en and _hit(p.x, p.y, C.P_R, e.x, e.y, e.r):
                    dmg, _ = e.ram_dmg, dead_en.add(id(e))
                    break
        if dmg == 0:
            for b in world.ebullets:
                if id(b) not in dead_eb and _hit(p.x, p.y, C.P_R, b.x, b.y, C.EB_R):
                    dmg, _ = C.EB_DMG, dead_eb.add(id(b))
                    break
        if dmg:
            p.hp -= dmg
            p.iframes = C.IFRAMES

    # Sweep out everything destroyed this frame
    world.pbullets = [b for b in world.pbullets if id(b) not in dead_pb]
    world.asteroids = [a for a in world.asteroids if id(a) not in dead_ast]
    world.enemies = [e for e in world.enemies if id(e) not in dead_en]
    world.ebullets = [b for b in world.ebullets if id(b) not in dead_eb]
    world.bonuses = [b for b in world.bonuses if id(b) not in dead_bonus]
