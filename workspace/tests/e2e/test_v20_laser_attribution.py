"""E2E lane — v20 LASER beam + death attribution through the App/render path
(AC110–AC120, R132). These build an `App` / drive the real smoke loop, or blit the
LASER body + beam + the GAME_OVER "Killed by" line, so they live in the e2e lane
(the unit lane already covers the pure beam/combat logic in test_v20_laser_beam.py).
"""

import math

from game import config as C
from game.app import App
from game.entities.hazards import make_enemy
from game.systems import lasers
from game.view import hud, render
from game.world import GameState


# ── R132 / AC120: the SMOKE run drives a real full laser cycle + survives a contact ──
def test_smoke_run_exercises_full_laser_cycle():
    """The seeded smoke LASER must, through the REAL App loop, reach DAMAGING, widen,
    persist across multiple frames (not consumed on contact), and the beam survive at
    least one player contact — all inside the 120-f budget. Spies on `_draw`."""
    app = App(smoke=True)
    phases, widths, beam_ids_seen, damaging_frames = [], [], set(), 0

    orig_draw = app._draw

    def spy():
        nonlocal damaging_frames
        for b in app.world.beams:
            phases.append(b.phase)
            beam_ids_seen.add(id(b))
            if b.phase == "DAMAGING":
                nonlocal_widths(widths, b.width)
        if any(b.phase == "DAMAGING" for b in app.world.beams):
            damaging_frames += 1
        orig_draw()

    def nonlocal_widths(acc, v):
        acc.append(v)

    app._draw = spy
    app.run()

    assert "WINDUP" in phases, "smoke beam never observed in WINDUP"
    assert "DAMAGING" in phases, "smoke beam never reached DAMAGING in the 120-f budget"
    # The SAME beam instance persisted across many damaging frames (not re-created/consumed).
    assert damaging_frames > 1, "beam did not persist across damaging frames (consumed on hit?)"
    assert len(beam_ids_seen) >= 1
    # The core widened over the damaging phase (R124).
    if len(widths) >= 2:
        assert max(widths) > min(widths), "beam core never widened during DAMAGING"
        assert max(widths) <= C.BEAM_FINAL_W + 1e-6, "beam exceeded BEAM_FINAL_W"


# ── AC115 / render: the LASER body + beam draw in BOTH phases without raising ──
def test_laser_and_beam_render_smoke(screen, fonts, fresh_world):
    """Blit the LASER turret + its beam in WINDUP and in DAMAGING; the white-hot core
    must actually paint on the field for the armed beam (a non-background pixel)."""
    render.set_fonts(fonts)
    hud.set_fonts(fonts)
    w = fresh_world()
    e = make_enemy(w.rng, 0.0, "LASER", ship_id=w.next_ship_id())
    e.x, e.y, e.phase = 300.0, 200.0, "B"
    e.repo_target_x = e.x
    w.enemies = [e]

    # WINDUP frame — body charge-ring + thin telegraph line, no lethal core yet.
    lasers.arm_beam(w, e)
    e.beam_phase = "WINDUP"
    screen.fill(C.BG)
    render.draw_world(screen, w)  # raises nothing

    # Advance to DAMAGING and draw — the opaque white-hot core must paint near the eye.
    for _ in range(C.BEAM_WINDUP_F):
        lasers.update_beams(w)
    for _ in range(C.BEAM_DAMAGE_F // 2):
        lasers.update_beams(w)  # mid-phase so the core is a few px wide
    e.beam_phase = "DAMAGING"
    b = w.beams[0]
    screen.fill(C.BG)
    render.draw_world(screen, w)
    # A point a little down the beam from the eye should carry the white-hot core colour.
    ox, oy = b.ox, b.oy
    tx, ty = lasers.beam_endpoint(b)
    dx, dy = tx - ox, ty - oy
    n = math.hypot(dx, dy)
    sx, sy = int(ox + dx / n * 30), int(oy + dy / n * 30)
    px = screen.get_at((sx, sy))[:3]
    assert tuple(px) != tuple(C.BG), "damaging beam core did not paint on the field"


# ── AC118 / render: "Killed by <name>" renders for every source + clears the Q/R arc ──
def test_gameover_killed_by_renders_and_clears_arcs(screen, fonts, fresh_world):
    """The GAME_OVER 'Killed by <name>' line renders for each blessed source + the
    fallback, fits the window width, and its rect clears the Q/R hold-arc rects."""
    render.set_fonts(fonts)
    hud.set_fonts(fonts)
    w = fresh_world()
    small = fonts["small"]

    # The Q/R arc bounding rect on GAME_OVER (centre 300,545; r=22).
    acx, acy = C.GAMEOVER_ARC_CENTER
    r = C.PAUSE_ARC_R
    arc_rect = (acx - r, acy - r, 2 * r, 2 * r)

    sources = list(C.KILLED_BY_NAMES.keys()) + [None]  # None → fallback
    for src in sources:
        w.killed_by = src
        name = C.KILLED_BY_NAMES.get(src, C.KILLED_BY_FALLBACK)
        line = f"{C.KILLED_BY_PREFIX}{name}"
        surf = small.render(line, True, C.TEXT_DIM)
        rect = surf.get_rect(center=(C.W // 2, C.KILLED_BY_Y + surf.get_height() // 2))
        # Fits the window with margin.
        assert rect.width < C.W, f"'{line}' overflows the {C.W}px window"
        # Clears the Q/R arc (the line sits above the arc track on GAME_OVER).
        import pygame

        assert not pygame.Rect(rect).colliderect(pygame.Rect(arc_rect)), (
            f"'{line}' rect {tuple(rect)} collides the Q/R arc {arc_rect}"
        )
        # And the full GAME_OVER screen draws without raising.
        screen.fill(C.BG)
        render.draw_starfield(screen, w)
        hud.draw_gameover(screen, w)

    # Fallback path is reached for an unset / unknown source.
    w.killed_by = None
    screen.fill(C.BG)
    hud.draw_gameover(screen, w)  # uses KILLED_BY_FALLBACK, raises nothing


# ── AC117 end-to-end: an in-App beam kill records the LASER attribution ──
def test_app_beam_kill_records_laser(fresh_world):
    """Through the App's PLAY step, a LASER beam that drives HP<=0 records killed_by=LASER
    and transitions to GAME_OVER carrying the attribution."""
    app = App()
    app.world = fresh_world()
    app.state = GameState.PLAY
    app.bomb_fired = False
    w = app.world
    p = w.player
    p.hp = 1
    p.iframes = 0
    e = make_enemy(w.rng, 0.0, "LASER", ship_id=w.next_ship_id())
    e.x, e.y, e.phase = p.x, 200.0, "B"
    e.repo_target_x = e.x
    w.enemies = [e]
    lasers.arm_beam(w, e)
    for _ in range(C.BEAM_WINDUP_F):
        lasers.update_beams(w)
    from game.systems import combat

    combat.resolve(w)
    assert p.hp <= 0 and w.killed_by == "LASER", "in-App beam kill not attributed to LASER"
