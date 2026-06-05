r"""physics — per-frame motion: player control + firing, projectile/hazard/bonus
integration, enemy AI, starfield scroll, and off-screen despawning.

These are the "integrate" verbs (GDD §6, level_spec §3). Player firing lives here
too because it is part of applying input to the player each frame; the bullets it
produces honor the v2 Fan/Rapid buffs via the player's accessors.
"""

from .. import config as C
from ..entities.projectiles import (make_player_shots, make_enemy_bullet,
                                    split_pellet, split_yellow)


def update_starfield(world):
    """Scroll the parallax starfield; runs in EVERY state (GDD §6.6)."""
    for s in world.stars:
        s.y += s.speed
        if s.y > C.H:
            s.y = 0
            s.x = world.rng.randint(0, C.W)


def update_play(world, inp):
    """Advance one PLAY frame of motion (no collisions — combat owns those)."""
    p = world.player
    t = world.t

    # --- Player movement (R3) + clamp the bounding box fully on-screen ---------
    p.x += inp.dx * C.P_SPEED
    p.y += inp.dy * C.P_SPEED
    p.x = max(14, min(C.W - 14, p.x))
    p.y = max(15, min(C.H - 15, p.y))
    if p.iframes > 0:
        p.iframes -= 1
    if p.fire_cd > 0:
        p.fire_cd -= 1
    # --- Player firing (R7) — Fan/Rapid aware (GDD §V2.2) ---
    if inp.fire and p.fire_cd == 0:
        world.pbullets.extend(make_player_shots(p.x, p.y, p.fan_active))
        p.fire_cd = p.fire_cooldown

    # --- Player bullets travel along their velocity; despawn off any edge ---
    for b in world.pbullets:
        b.x += b.vx
        b.y += b.vy
    world.pbullets = [b for b in world.pbullets
                      if -10 <= b.x <= C.W + 10 and b.y > -C.PB_H]

    # --- Asteroids drift down; tick survived-hit flash; despawn off bottom ---
    for a in world.asteroids:
        a.x += a.vx
        a.y += a.vy
        if a.flash > 0:
            a.flash -= 1
    world.asteroids = [a for a in world.asteroids if a.y - a.r <= C.H]

    # --- Enemies: entry → strafe, fire aimed bullets in Phase B (per-kind, §V5.2) ---
    for e in world.enemies:
        spec = e.spec
        if e.flash > 0:
            e.flash -= 1
        if e.phase == "A":
            e.y += spec["entry"]
            if e.y >= 120:
                e.phase = "B"
        else:
            e.x += spec["strafe"] * e.dir
            if e.x <= 20:
                e.x, e.dir = 20, 1
            elif e.x >= 580:
                e.x, e.dir = 580, -1
            e.y += spec["descent"]
            e.fire_timer -= 1
            if e.fire_timer <= 0:
                e.fire_timer = round(C.enemy_fire_interval(t) * spec["fire_mult"])
                world.ebullets.append(
                    make_enemy_bullet(e.x, e.y, p.x, p.y, world.rng, e.kind))
    world.enemies = [e for e in world.enemies if e.y <= 820]

    # --- Enemy bullets: travel along their frozen aim; GREEN pellets count down to
    #     their midway split (GDD §V5.4) → burst into 3 RED children. A pellet that
    #     leaves the screen before maturing produces NO children (handled by the
    #     despawn filter); a pellet that hits the player first is consumed in combat.
    matured = []
    for b in world.ebullets:
        b.x += b.vx
        b.y += b.vy
        if b.split_timer is not None:
            b.split_timer -= 1
            if b.split_timer <= 0 and -10 <= b.x <= C.W + 10 and -10 <= b.y <= C.H + 10:
                matured.append(b)
    if matured:
        burst = set(id(b) for b in matured)
        world.ebullets = [b for b in world.ebullets if id(b) not in burst]
        for pellet in matured:
            # GREEN heavy pellet → 3 RED fan (§V5.4); YELLOW boss fan → 4 RED ring
            # quarter (§V7.12). Both replace the parent with terminal RED children.
            if pellet.family == "YELLOW":
                world.ebullets.extend(split_yellow(pellet))
            else:
                world.ebullets.extend(split_pellet(pellet))
    # Despawn off any edge (children included); this also drops a pellet that left
    # the screen before its timer matured — no split, per R39 edge case.
    world.ebullets = [b for b in world.ebullets
                      if -10 <= b.x <= C.W + 10 and -10 <= b.y <= C.H + 10]
    if len(world.ebullets) > C.EB_CAP:
        world.ebullets = world.ebullets[-C.EB_CAP:]   # drop oldest (safety)

    # --- Bonus pickups: flat 2.0 px/f drift, NOT ramp-accelerated (GDD §V2.4) ---
    for bonus in world.bonuses:
        bonus.y += C.BONUS_SPEED
    # Missed → off the bottom → removed silently, no penalty (R23).
    world.bonuses = [b for b in world.bonuses if b.y - C.BONUS_PICKUP_R <= C.H]

    # --- Particles ---
    for part in world.particles:
        part.x += part.vx
        part.y += part.vy
        part.life -= 1
    world.particles = [pt for pt in world.particles if pt.life > 0]
