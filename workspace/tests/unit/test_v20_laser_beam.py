"""Unit lane — v20 LASER enemy + sweeping beam + projectile ownership + death
attribution (R120–R132 / AC109–AC120). Pure logic: builds World/entities and drives
combat / lasers / physics directly — no App, no event loop, no blit.
"""

import math

from game import config as C
from game.entities.hazards import Asteroid, make_enemy
from game.entities.projectiles import EnemyBullet, PlayerBullet, make_player_shots
from game.input import InputState
from game.systems import combat, lasers, physics


# ── helpers ──────────────────────────────────────────────────────────────────
def _laser(world, x=300.0, y=150.0):
    """A LASER already in Phase B at (x, y), ready to fire."""
    e = make_enemy(world.rng, world.t, "LASER", ship_id=world.next_ship_id())
    e.x, e.y = x, y
    e.phase = "B"
    e.repo_target_x = x
    world.enemies.append(e)
    return e


def _arm_damaging(world, e):
    """Arm a beam on `e` and advance it through its full WINDUP so it is DAMAGING."""
    lasers.arm_beam(world, e)
    for _ in range(C.BEAM_WINDUP_F):
        lasers.update_beams(world)
    return world.beams[0]


# ── R128: ship IDs + projectile source (additive) ────────────────────────────
def test_ac116_ship_ids_unique(fresh_world):
    w = fresh_world()
    ids = {w.player.id}
    for _ in range(5):
        e = make_enemy(w.rng, 0.0, "REGULAR", ship_id=w.next_ship_id())
        assert e.id not in ids, "ship ID not unique within a run"
        ids.add(e.id)
    assert w.player.id != 0, "player has no ID"


def test_ac116_player_shot_carries_source(fresh_world):
    w = fresh_world()
    p = w.player
    shots = make_player_shots(p.x, p.y, C.PB_SPEED, source=p.id)
    assert all(b.source == p.id for b in shots), "player bullet missing source"


def test_ac116_enemy_bullet_carries_source(fresh_world):
    w = fresh_world()
    e = make_enemy(w.rng, 0.0, "REGULAR", ship_id=w.next_ship_id())
    e.x, e.y, e.phase, e.fire_timer = 300.0, 120.0, "B", 0
    w.enemies = [e]
    physics.update_play(w, InputState(0, 0, False))
    assert w.ebullets, "enemy did not fire"
    assert all(b.source == e.id for b in w.ebullets), "enemy bullet missing source"


def test_source_field_is_additive(fresh_world):
    """A bullet with no source still has the default 0 and moves normally (no regression)."""
    w = fresh_world()
    b = EnemyBullet(100.0, 100.0, 0.0, 4.0, family="RED")
    assert b.source == 0
    pb = PlayerBullet(100.0, 100.0, 0.0, -10.0)
    assert pb.source == 0


# ── R122/R123: windup harmless, damaging lethal ──────────────────────────────
def test_ac111_windup_harmless(fresh_world):
    w = fresh_world()
    e = _laser(w, x=w.player.x, y=200.0)
    lasers.arm_beam(w, e)
    beam = w.beams[0]
    assert beam.phase == "WINDUP" and beam.width == 0.0 and not beam.lethal
    # Put the player exactly on the beam line; combat must deal NO damage in windup.
    hp0 = w.player.hp
    combat.resolve(w)
    assert w.player.hp == hp0, "windup line dealt damage (must be harmless)"


def test_ac111_damaging_lethal(fresh_world):
    w = fresh_world()
    e = _laser(w, x=w.player.x, y=200.0)
    beam = _arm_damaging(w, e)
    assert beam.lethal and beam.width >= C.BEAM_START_W
    hp0 = w.player.hp
    combat.resolve(w)
    assert w.player.hp == hp0 - C.BEAM_DMG, "damaging beam did not deal BEAM_DMG"
    assert w.player.iframes == C.IFRAMES, "beam hit did not start i-frames"


# ── R124: widening, draw == collision width ──────────────────────────────────
def test_ac112_beam_widens_linearly(fresh_world):
    w = fresh_world()
    e = _laser(w)
    beam = _arm_damaging(w, e)
    w0 = beam.width  # just armed
    for _ in range(C.BEAM_DAMAGE_F // 2):
        lasers.update_beams(w)
    w_mid = w.beams[0].width
    assert C.BEAM_START_W <= w0 < w_mid <= C.BEAM_FINAL_W, "beam did not widen 2→6 over the phase"


def test_draw_equals_collision_band_is_the_radius(fresh_world):
    """The hit band IS the passed radius (= P_HITBOX_R + the live half-width): a point at
    perpendicular distance D from the line is missed at r<D and hit at r>D — so widening
    the beam (bigger w → bigger r) is exactly what reaches a point an early thin beam misses."""
    w = fresh_world()
    e = _laser(w, x=300.0, y=200.0)
    beam = _arm_damaging(w, e)
    tx, ty = lasers.beam_endpoint(beam)
    dx, dy = tx - beam.ox, ty - beam.oy
    n = math.hypot(dx, dy)
    nx, ny = -dy / n, dx / n  # unit perpendicular to the beam line
    mx, my = beam.ox + dx * 0.5, beam.oy + dy * 0.5  # a point ON the segment
    dist = 4.0
    px, py = mx + nx * dist, my + ny * dist  # exactly `dist` off the line
    assert not lasers.seg_circle_hit(beam.ox, beam.oy, tx, ty, px, py, dist - 0.5), (
        "point hit at r < its perpendicular distance"
    )
    assert lasers.seg_circle_hit(beam.ox, beam.oy, tx, ty, px, py, dist + 0.5), (
        "point missed at r > its perpendicular distance"
    )


# ── R125: sweep ~0.1× P_SPEED, capped arc ────────────────────────────────────
def test_ac113_beam_sweeps_slowly_capped(fresh_world):
    w = fresh_world()
    e = _laser(w)
    beam = _arm_damaging(w, e)
    a0 = beam.angle
    lasers.update_beams(w)
    per_frame_deg = abs(math.degrees(beam.angle - a0))
    assert abs(per_frame_deg - C.BEAM_SWEEP_DPS) < 1e-6, "sweep rate != BEAM_SWEEP_DPS"
    # The lateral approach at the player's range is ~0.1× P_SPEED (≈0.5 px/f) — out-walkable.
    # Across the whole DAMAGING phase the total swept arc never exceeds BEAM_SWEEP_MAX_DEG.
    for _ in range(C.BEAM_DAMAGE_F - 1):
        if not w.beams:
            break
        lasers.update_beams(w)
        assert abs(math.degrees(beam.angle - beam.start_angle)) <= C.BEAM_SWEEP_MAX_DEG + 1e-6, (
            "swept arc exceeded BEAM_SWEEP_MAX_DEG"
        )


# ── R126: persists to timeout, survives contact ──────────────────────────────
def test_ac114_beam_survives_contact_and_persists_to_timeout(fresh_world):
    w = fresh_world()
    e = _laser(w, x=w.player.x, y=200.0)
    beam = _arm_damaging(w, e)
    # Player stands in the beam; resolve a contact — the beam must NOT be consumed.
    combat.resolve(w)
    assert beam in w.beams, "beam consumed on contact (must persist, R126)"
    # It is removed only when the DAMAGING phase times out.
    for _ in range(C.BEAM_DAMAGE_F):
        lasers.update_beams(w)
    assert not w.beams, "beam not removed on timeout"


def test_one_tick_per_phase_via_iframes(fresh_world):
    """A player who STAYS in the beam takes at most ~1 tick/phase (IFRAMES==BEAM_DAMAGE_F)."""
    w = fresh_world()
    e = _laser(w, x=w.player.x, y=200.0)
    _arm_damaging(w, e)
    hp0 = w.player.hp
    for _ in range(C.BEAM_DAMAGE_F):
        combat.resolve(w)
        if w.player.iframes > 0:
            w.player.iframes -= 1  # let i-frames age as the loop would
        lasers.update_beams(w)
    assert hp0 - w.player.hp <= C.BEAM_DMG, "beam out-damaged the i-frame cap (>1 tick/phase)"


# ── R121/R129: owner-freeze via own beam's source ────────────────────────────
def test_ac110_owner_frozen_while_own_beam_live(fresh_world):
    w = fresh_world()
    e = _laser(w, x=200.0, y=200.0)
    e.repo_target_x = 560.0  # would drift right in cooldown
    lasers.arm_beam(w, e)  # beam now live & owned by e
    x_before = e.x
    lasers.update_laser(w, e)  # immobile while it owns a live beam
    assert e.x == x_before, "LASER moved while its own beam was live (must be frozen)"


def test_ac110_multi_laser_independent_freeze(fresh_world):
    w = fresh_world()
    a = _laser(w, x=150.0, y=200.0)
    b = _laser(w, x=450.0, y=200.0)
    a.repo_target_x = b.repo_target_x = 300.0
    lasers.arm_beam(w, a)  # only A fires
    xa, xb = a.x, b.x
    lasers.update_laser(w, a)  # A frozen
    lasers.update_laser(w, b)  # B (no beam) repositions
    assert a.x == xa, "A not frozen by its own beam"
    assert b.x != xb, "B should reposition (it owns no beam) — multi-laser freeze leaked"


def test_laser_repositions_in_cooldown_then_rearms(fresh_world):
    w = fresh_world()
    e = _laser(w, x=100.0, y=120.0)
    e.repo_target_x = 400.0
    e.beam_timer = 3
    for _ in range(3):
        lasers.update_laser(w, e)  # drifts toward 400 during cooldown, then arms on timeout
    assert e.x > 100.0, "LASER did not reposition during cooldown"
    assert any(bm.source == e.id for bm in w.beams), "LASER did not arm a beam after cooldown"


# ── R130/R131: death attribution + Killed by <name> ──────────────────────────
def test_ac117_attribution_enemy_body(fresh_world):
    w = fresh_world()
    p = w.player
    p.hp = 1
    e = make_enemy(w.rng, 0.0, "HEAVY", ship_id=w.next_ship_id())
    e.x, e.y = p.x, p.y
    w.enemies = [e]
    combat.resolve(w)
    assert w.player.hp <= 0 and w.killed_by == "HEAVY", "enemy-body kill not attributed"


def test_ac117_attribution_projectile_via_source(fresh_world):
    w = fresh_world()
    p = w.player
    p.hp = 1
    e = make_enemy(w.rng, 0.0, "SCOUT", ship_id=w.next_ship_id())
    e.x, e.y = -999, -999  # off-field but alive, so source resolves
    w.enemies = [e]
    w.ebullets = [EnemyBullet(p.x, p.y, 0, 0, family="CYAN", source=e.id)]
    combat.resolve(w)
    assert w.player.hp <= 0 and w.killed_by == "SCOUT", "projectile kill not attributed via source"


def test_ac117_attribution_beam_to_laser(fresh_world):
    w = fresh_world()
    p = w.player
    p.hp = 1
    e = _laser(w, x=p.x, y=200.0)
    _arm_damaging(w, e)
    combat.resolve(w)
    assert w.player.hp <= 0 and w.killed_by == "LASER", "beam kill not attributed to LASER"


def test_ac117_attribution_asteroid(fresh_world):
    w = fresh_world()
    p = w.player
    p.hp = 1
    w.asteroids = [Asteroid(p.x, p.y, 0, 0, C.AST_S_R, 1, False)]
    combat.resolve(w)
    assert w.player.hp <= 0 and w.killed_by == "ASTEROID", "asteroid kill not attributed"


def test_ac118_killed_by_fallback_for_unknown_source(fresh_world):
    """A projectile whose source resolves to no live ship → the SOMETHING fallback."""
    w = fresh_world()
    p = w.player
    p.hp = 1
    w.ebullets = [EnemyBullet(p.x, p.y, 0, 0, family="RED", source=99999)]
    combat.resolve(w)
    assert w.player.hp <= 0 and w.killed_by == C.KILLED_BY_FALLBACK, "unknown source not fallback"


def test_ac118_every_source_has_a_name():
    """Every blessed lethal source maps to a display name; an unknown handle falls back."""
    for k in ("ASTEROID", "REGULAR", "HEAVY", "SCOUT", "MOTHERSHIP", "NOVA", "LASER"):
        assert C.KILLED_BY_NAMES[k] == k, f"{k} display name not its blessed name"
    assert C.KILLED_BY_NAMES.get("???", C.KILLED_BY_FALLBACK) == "SOMETHING"


# ── R120/R132: roster + smoke seed ───────────────────────────────────────────
def test_ac109_laser_in_roster_killable_scores():
    assert "LASER" in C.ENEMY_KINDS
    assert C.ENEMY_KINDS["LASER"]["hp"] == C.LASER_HP == 3
    assert C.ENEMY_KINDS["LASER"]["score"] == C.LASER_SCORE == 100
    assert C.ENEMY_KINDS["LASER"]["r"] == C.LASER_R == 14


def test_laser_killed_by_player_fire_scores(fresh_world):
    w = fresh_world()
    e = _laser(w, x=200.0, y=200.0)
    s0 = w.score
    for _ in range(C.LASER_HP):
        w.pbullets = [PlayerBullet(e.x, e.y, 0, -10, source=w.player.id)]
        combat.resolve(w)
    assert e not in w.enemies, "LASER not killed by LASER_HP bullets"
    assert w.score == s0 + C.LASER_SCORE, "LASER score not awarded"
    assert w.store.enemies_killed >= 1, "LASER kill not counted"


def test_spawn_ladder_includes_laser_after_gate(fresh_world):
    """After LASER_GATE the Storm/Squeeze ladder can return LASER; before it, never."""
    w = fresh_world()
    # before the gate (t=55s) — never LASER
    kinds_pre = {C.choose_enemy_kind(55.0, w.rng) for _ in range(400)}
    assert "LASER" not in kinds_pre, "LASER spawned before its gate"
    # after the gate (Storm t=120s) — LASER appears
    kinds_post = {C.choose_enemy_kind(120.0, w.rng) for _ in range(400)}
    assert "LASER" in kinds_post, "LASER never spawns after its gate"


def test_smoke_seed_runs_full_cycle(fresh_world):
    """The smoke laser seed arms a beam that reaches DAMAGING within the 120-f budget."""
    from game.systems import spawning

    w = fresh_world()
    spawning.seed_smoke_laser(w)
    assert w.beams and w.beams[0].phase == "WINDUP", "smoke laser did not arm a WINDUP beam"
    for _ in range(C.BEAM_WINDUP_F):
        lasers.update_beams(w)
    assert w.beams and w.beams[0].phase == "DAMAGING", "smoke beam did not reach DAMAGING in budget"
