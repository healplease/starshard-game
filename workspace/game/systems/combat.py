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
from . import buffs, encounter, lasers, scoring, spawning


def _hit(x1, y1, r1, x2, y2, r2):
    """Circle-vs-circle via squared distance (GDD §8). Player bullet (a rect) is
    approximated as a circle of half its height — cheap and fine at this scale."""
    rr = r1 + r2
    return (x1 - x2) ** 2 + (y1 - y2) ** 2 <= rr * rr


def _name_for_kind(kind):
    """v20 (R131): map a lethal-source handle (enemy/boss kind) to a display name,
    falling back to KILLED_BY_FALLBACK for any unknown/unresolvable source — never blank."""
    return C.KILLED_BY_NAMES.get(kind, C.KILLED_BY_FALLBACK)


def _name_for_source(world, source_id):
    """v20 (R130): resolve a projectile/beam `source` (a firing ship's ID) to that ship's
    display name AT THE DAMAGE INSTANT (the ship may be culled before GAME_OVER reads it).
    Search the live ships for the ID → its kind/boss name; miss → the SOMETHING fallback."""
    for e in world.enemies:
        if e.id == source_id:
            return _name_for_kind(e.kind)
    if world.boss is not None and world.boss.id == source_id:
        return _name_for_kind(world.boss.type)
    return C.KILLED_BY_FALLBACK


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
            if _hit(b.x, b.y, C.PB_H / 2, boss.x, boss.y, boss.r):
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

    # 4) Player damage — only while vulnerable (Shield/​i-frames skip this), first hit wins.
    #    v19 R115: every player-DAMAGE test uses the always-on small circle P_HITBOX_R
    #    (≈50% of the drawn P_R), NOT the draw/pickup radius — boss-ram, asteroid, enemy,
    #    and ebullet all shrink together; pickup collection (step 3) stays generous at P_R.
    if not p.invulnerable:
        dmg = 0
        src_name = None  # v20 (R130): the lethal source's display-name handle, captured here
        # Boss body ram (R61/§V7.13) — the scariest thing to touch (60 > HEAVY 50);
        # the boss is NOT consumed (it persists), unlike a hazard hit.
        if world.boss is not None and _hit(
            p.x, p.y, C.P_HITBOX_R, world.boss.x, world.boss.y, world.boss.r
        ):
            dmg = world.boss.ram_dmg
            src_name = _name_for_kind(world.boss.type)  # body → that boss's name
        for a in world.asteroids:
            if dmg:
                break
            if id(a) not in dead_ast and _hit(p.x, p.y, C.P_HITBOX_R, a.x, a.y, a.r):
                dmg, _ = a.dmg, dead_ast.add(id(a))
                src_name = "ASTEROID"  # body → ASTEROID (covers asteroid + debris)
                break
        if dmg == 0:
            for e in world.enemies:
                if id(e) not in dead_en and _hit(p.x, p.y, C.P_HITBOX_R, e.x, e.y, e.r):
                    dmg, _ = e.ram_dmg, dead_en.add(id(e))
                    src_name = _name_for_kind(e.kind)  # body → that enemy's kind name
                    break
        if dmg == 0:
            for b in world.ebullets:
                if id(b) not in dead_eb and _hit(p.x, p.y, C.P_HITBOX_R, b.x, b.y, C.EB_R):
                    dmg, _ = b.dmg, dead_eb.add(id(b))  # per-bullet dmg (NOVA 25 > EB_DMG 15)
                    src_name = _name_for_source(world, b.source)  # projectile → owner's name
                    break
        # v20 beam × player (R123/R126): a DAMAGING beam is lethal on contact via the
        # segment/circle test at the live core HALF-width + P_HITBOX_R (draw==collision),
        # but is NEVER consumed (it persists to timeout — not added to any dead-set).
        if dmg == 0:
            for beam in world.beams:
                if not beam.lethal:
                    continue  # WINDUP is harmless (R123/AC111)
                tx, ty = lasers.beam_endpoint(beam)
                if lasers.seg_circle_hit(
                    beam.ox, beam.oy, tx, ty, p.x, p.y, C.P_HITBOX_R + beam.width / 2
                ):
                    dmg = C.BEAM_DMG
                    src_name = _name_for_source(world, beam.source)  # beam → owner (→ LASER)
                    break
        if dmg:
            p.hp -= dmg
            p.iframes = C.IFRAMES
            if p.hp <= 0:  # v20: the hit that drove HP<=0 → record its source name (R130)
                world.killed_by = src_name or C.KILLED_BY_FALLBACK

    # Sweep out everything destroyed this frame
    world.pbullets = [b for b in world.pbullets if id(b) not in dead_pb]
    world.asteroids = [a for a in world.asteroids if id(a) not in dead_ast]
    world.enemies = [e for e in world.enemies if id(e) not in dead_en]
    world.ebullets = [b for b in world.ebullets if id(b) not in dead_eb]
    world.bonuses = [b for b in world.bonuses if id(b) not in dead_bonus]
