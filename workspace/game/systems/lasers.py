r"""lasers — the v20 LASER enemy's 3-state sweeping beam (GDD §V20.2/§V20.3,
level_spec §V20L.1, art_spec §V20a).

The LASER is a stationary area-denial zoner. After its shared entry descent
(physics Phase A → B) it runs a fire→cooldown loop:

  COOLDOWN (90 f, MOBILE) — no beam of its own is live, so the enemy repositions:
    drift toward a fresh uniform firing x @ LASER_REPO_SPEED while descending slowly
    @ LASER_REPO_DESCENT. When the timer elapses it ARMS a beam — capturing the
    player's CURRENT direction once (the FROZEN fire-time aim) — and enters WINDUP.
  WINDUP (30 f, IMMOBILE) — a thin harmless telegraph line; 0 damage (R123).
  DAMAGING (60 f, IMMOBILE) — lethal, widening 2→6 px, ROTATING about the emitter
    eye toward+past the frozen aim @ BEAM_SWEEP_DPS (capped BEAM_SWEEP_MAX_DEG);
    persists the full phase, removed ONLY on timeout (R126) — never on contact.

The freeze is OWNERSHIP-driven (R129): the enemy is frozen iff a live beam exists
whose `source` == its own ship ID, so multiple LASER enemies coexist (each frozen by
its own beam) and each unfreezes the instant its own beam times out. The beam entity
owns the windup/damaging timers + the rotation; the enemy just owns the cooldown gap.
"""

import math

from .. import config as C
from ..entities.projectiles import Beam


def _beam_origin(e):
    """The emitter eye = the beam origin + the rotation pivot (art_spec §V20a.4)."""
    return e.x, e.y + C.LASER_EYE_DY


def _owns_live_beam(world, e):
    """R129: is a beam whose `source` == this LASER's ID currently live?"""
    return any(b.source == e.id for b in world.beams)


def update_laser(world, e):
    """One Phase-B frame for a LASER enemy. Immobile while it owns a live beam
    (WINDUP/DAMAGING); repositions + counts down to the next arm during COOLDOWN."""
    if _owns_live_beam(world, e):
        # Frozen for the WHOLE attack (R121): no reposition, no descent. The beam's own
        # timers (update_beams) drive the windup→damaging→removal; the enemy just waits.
        e.beam_phase = (
            "DAMAGING" if any(b.lethal for b in world.beams if b.source == e.id) else "WINDUP"
        )
        return

    # COOLDOWN — mobile: drift toward the fresh firing x, descend slowly.
    e.beam_phase = "COOLDOWN"
    if e.x < e.repo_target_x:
        e.x = min(e.repo_target_x, e.x + C.LASER_REPO_SPEED)
    elif e.x > e.repo_target_x:
        e.x = max(e.repo_target_x, e.x - C.LASER_REPO_SPEED)
    e.x = max(C.LASER_REPO_X_LO, min(C.LASER_REPO_X_HI, e.x))
    e.y += C.LASER_REPO_DESCENT

    e.beam_timer -= 1
    if e.beam_timer <= 0:
        arm_beam(world, e)


def arm_beam(world, e):
    """Capture the FROZEN fire-time aim (player direction NOW) once and spawn a WINDUP
    beam owned by this LASER (GDD §V20.3.2(1)(2)). After this the player is never read
    again by this beam — it sweeps the captured spot, not the live player."""
    ox, oy = _beam_origin(e)
    p = world.player
    aim = math.atan2(p.y - oy, p.x - ox)  # toward the fire-time player position
    world.beams.append(
        Beam(
            ox=ox,
            oy=oy,
            angle=aim,
            target_angle=aim,
            start_angle=aim,
            phase="WINDUP",
            timer=C.BEAM_WINDUP_F,
            source=e.id,
        )
    )
    # The enemy is now frozen-by-ownership; on this beam's removal it re-enters COOLDOWN.
    e.beam_phase = "WINDUP"


def _reenter_cooldown(world, e):
    """A LASER whose beam just timed out picks a fresh firing x and starts its cooldown
    (so the next beam comes from a different lane, GDD §V20.3.4)."""
    e.repo_target_x = world.rng.uniform(C.LASER_REPO_X_LO, C.LASER_REPO_X_HI)
    e.beam_timer = C.BEAM_COOLDOWN_F
    e.beam_phase = "COOLDOWN"


def update_beams(world):
    """Advance every live beam one frame: rotate the sweep, count the phase timer,
    promote WINDUP→DAMAGING, and remove a beam ONLY when its DAMAGING phase times out
    (R126 — never on contact; contact is resolved in combat and does not touch beams)."""
    survivors = []
    expired_sources = set()
    for b in world.beams:
        if b.phase == "DAMAGING":
            # Rotate toward the frozen target, capped to the total swept arc. Here
            # target == start (aim-at-fire-time), so the cap drives a bounded drift
            # THROUGH and a touch PAST the captured spot (§V20.3.2(2)). The new angle is
            # CLAMPED to the cap so the total swept arc never exceeds BEAM_SWEEP_MAX_DEG.
            cap = math.radians(C.BEAM_SWEEP_MAX_DEG)
            swept = b.angle - b.start_angle
            if swept < cap:
                b.angle = min(b.start_angle + cap, b.angle + math.radians(C.BEAM_SWEEP_DPS))
        b.timer -= 1
        if b.timer <= 0:
            if b.phase == "WINDUP":
                b.phase = "DAMAGING"
                b.timer = C.BEAM_DAMAGE_F
                survivors.append(b)
            else:  # DAMAGING timed out → remove (R126)
                expired_sources.add(b.source)
        else:
            survivors.append(b)
    world.beams = survivors
    # Any LASER whose beam just timed out re-enters its mobile cooldown gap.
    if expired_sources:
        for e in world.enemies:
            if e.kind == "LASER" and e.id in expired_sources and not _owns_live_beam(world, e):
                _reenter_cooldown(world, e)


def beam_endpoint(b):
    """The far end of the beam: from the origin along the live angle to the first screen-
    edge crossing, then + BEAM_OVERSHOOT (art_spec §V20a.4) → the endless-to-edge look.
    Returns (tx, ty) for both draw and the collision segment far point (the off-screen
    tail can't touch the player, so collision uses this same segment)."""
    ox, oy = b.ox, b.oy
    dx, dy = math.cos(b.angle), math.sin(b.angle)
    # Distance to each screen edge along the ray; take the nearest positive crossing.
    best = None
    if dx > 1e-9:
        best = _min_pos(best, (C.W - ox) / dx)
    elif dx < -1e-9:
        best = _min_pos(best, (0 - ox) / dx)
    if dy > 1e-9:
        best = _min_pos(best, (C.H - oy) / dy)
    elif dy < -1e-9:
        best = _min_pos(best, (0 - oy) / dy)
    dist = (best if best is not None else 0.0) + C.BEAM_OVERSHOOT
    return ox + dx * dist, oy + dy * dist


def _min_pos(cur, val):
    """Helper: smallest strictly-positive crossing distance."""
    if val <= 0:
        return cur
    return val if cur is None else min(cur, val)


def seg_circle_hit(ox, oy, tx, ty, px, py, r):
    """True iff the point (px,py) is within `r` of the segment (ox,oy)-(tx,ty). Used for
    the beam draw==collision test: r = P_HITBOX_R + beam half-width (art_spec §V20a.3.2,
    GDD §V20.3.3 line/segment-vs-circle, NOT circle-vs-circle)."""
    dx, dy = tx - ox, ty - oy
    seg_len2 = dx * dx + dy * dy
    if seg_len2 <= 1e-9:
        return (px - ox) ** 2 + (py - oy) ** 2 <= r * r
    t = ((px - ox) * dx + (py - oy) * dy) / seg_len2
    t = max(0.0, min(1.0, t))  # clamp to the segment
    cx, cy = ox + t * dx, oy + t * dy
    return (px - cx) ** 2 + (py - cy) ** 2 <= r * r
