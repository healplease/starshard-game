"""E2E lane — render-smoke per GameState (v9 render, AC68 render, AC77, v11 pulse, AC84).

Blits one frame per state / arc combination and reads alpha off rendered surfaces, so
these are e2e (they exercise the view layer, not pure logic).
"""

import pygame

from game import config as C
from game.entities.boss import Boss
from game.entities.bonus import Bonus
from game.entities.fx import make_burst
from game.entities.hazards import make_asteroid, make_enemy
from game.entities.projectiles import EnemyBullet
from game.view import hud, render
from game.world import BonusKind, GameState


def _rich_world(fresh_world):
    """A world populated so one frame exercises every draw path."""
    w = fresh_world()
    p = w.player
    p.buff_timers[BonusKind.FAN] = 400
    p.buff_timers[BonusKind.RAPID] = 200
    p.buff_timers[BonusKind.SHIELD] = 150
    p.buff_timers[BonusKind.SCORE] = 300
    w.enemies = [make_enemy(w.rng, 30, k) for k in ("REGULAR", "HEAVY", "SCOUT")]
    for e in w.enemies:
        e.phase, e.y = "B", 200
    w.asteroids = [make_asteroid(w.rng, 30) for _ in range(3)]
    w.ebullets = [
        EnemyBullet(100, 100, 0, 3, family="RED"),
        EnemyBullet(150, 150, 0, 3, family="GREEN", split_timer=20),
        EnemyBullet(200, 200, 2, 3, family="CYAN"),
        EnemyBullet(250, 250, 1, 3, family="YELLOW", split_timer=20, ring_phase=0),
    ]
    w.bonuses = [Bonus(BonusKind.REPAIR, 80, 300), Bonus(BonusKind.BOMB, 120, 350)]
    w.particles = make_burst(w.rng, 300, 300, C.ENEMY)
    w.charges = 3
    w.flash_timer = 10
    w.repair_popup_timer = 20
    w.bomb_popup_timer = 20
    w.boss = Boss(x=300.0, y=400.0, state="ENTRANCE", hp=80)
    w.boss_defeat_popup_timer = 20
    w.boss_defeat_points = 2000
    return w


def test_render_smoke_all_states(screen, fonts, fresh_world):
    """v9 render: blit one frame per GameState raises nothing."""
    render.set_fonts(fonts)
    hud.set_fonts(fonts)
    w = _rich_world(fresh_world)
    for state in (GameState.START, GameState.PLAY, GameState.PAUSE, GameState.GAME_OVER):
        screen.fill(C.BG)
        render.draw_starfield(screen, w)
        if state is GameState.START:
            hud.draw_start(screen, 0)
        elif state is GameState.PLAY:
            render.draw_world(screen, w)
            hud.draw_hud(screen, w)
            hud.draw_flash(screen, w)
        elif state is GameState.PAUSE:
            render.draw_world(screen, w)
            hud.draw_hud(screen, w)
            hud.draw_pause(screen, 15, 15)  # v12: both Q + R arcs
        else:
            render.draw_world(screen, w)
            hud.draw_hud(screen, w)
            hud.draw_gameover(screen, w)
    # Reaching here without an exception is the pass.


def test_ac68_render_start_gameover_arc(screen, fonts, fresh_world):
    """AC68 render-smoke: START + GAME_OVER draw with AND without the arc."""
    render.set_fonts(fonts)
    hud.set_fonts(fonts)
    w = _rich_world(fresh_world)
    for q in (0, 15, 30):  # without arc (0) and with arc (held)
        screen.fill(C.BG)
        render.draw_starfield(screen, w)
        hud.draw_start(screen, 0)
        hud.draw_start_quit_arc(screen, q)
        screen.fill(C.BG)
        render.draw_starfield(screen, w)
        hud.draw_gameover(screen, w)
        hud.draw_gameover_quit_arc(screen, q)
    # Reaching here without an exception is the pass.


def test_ac77_render_pause_gameover_dual_arc(screen, fonts, fresh_world):
    """AC77 render-smoke: PAUSE + GAME_OVER draw with BOTH Q and R arcs (no/each/both held)."""
    render.set_fonts(fonts)
    hud.set_fonts(fonts)
    w = _rich_world(fresh_world)
    # Every required combination: neither held, Q only, R only, both held.
    for q, r in ((0, 0), (15, 0), (0, 15), (30, 30)):
        screen.fill(C.BG)
        render.draw_world(screen, w)
        hud.draw_hud(screen, w)
        hud.draw_pause(screen, q, r)  # PAUSE: both tracks always on
        screen.fill(C.BG)
        render.draw_world(screen, w)
        hud.draw_gameover(screen, w)
        hud.draw_gameover_quit_arc(screen, q)  # GAME_OVER: only while held
        hud.draw_gameover_restart_arc(screen, r)
    # Reaching here without an exception is the pass.


def test_pulse_invuln_alpha(screen, fonts, fresh_world):
    """v11 pulse: invuln ship pulses 128<->255 on a 30-f cosine; solid when not invuln."""
    render.set_fonts(fonts)
    p = fresh_world().player  # P_START, no shield ring drawn

    def alpha_at(blink):  # blink_timer == iframes when no shield
        p.iframes = blink
        screen.fill(C.BG)
        render._draw_player(screen, p)
        return render._PLAYER_SURF.get_at(render._PLAYER_LOCAL)[3]  # ship-centre alpha

    assert alpha_at(C.INVULN_PULSE_PERIOD) == C.INVULN_ALPHA_CEIL, (
        "phase 0 (full cycle) is not at the 255 ceiling"
    )
    assert alpha_at(C.INVULN_PULSE_PERIOD // 2) == C.INVULN_ALPHA_FLOOR, (
        "phase 0.5 (half cycle) is not at the 128 floor"
    )
    seen = set()
    for b in range(1, C.INVULN_PULSE_PERIOD + 1):
        a = alpha_at(b)
        assert C.INVULN_ALPHA_FLOOR <= a <= C.INVULN_ALPHA_CEIL, (
            f"alpha {a} left [128,255] at blink {b} (ship invisible or over-bright)"
        )
        seen.add(a)
    assert len(seen) > 3, f"alpha took only {len(seen)} values over a cycle — not a smooth pulse"
    # Not invulnerable → solid ship straight to screen; centre dot is opaque PLAYER_EDGE.
    p.iframes = 0
    assert not p.invulnerable, "player still invulnerable with iframes 0 / no shield"
    screen.fill(C.BG)
    render._draw_player(screen, p)
    assert tuple(screen.get_at((int(p.x), int(p.y)))[:3]) == C.PLAYER_EDGE, (
        "solid ship centre not drawn at full colour when not invulnerable"
    )


def test_ac84_stats_render_smoke(screen, fonts, fresh_world):
    """AC84: STATS render-smoke — draw_stats raises nothing and rows don't overlap."""
    from game import save

    render.set_fonts(fonts)
    hud.set_fonts(fonts)
    store = save.Store(
        highscore=98765, runs=321, enemies_killed=1234, asteroids_destroyed=987, bosses_killed=12
    )
    screen.fill(C.BG)
    render.draw_starfield(screen, fresh_world())
    hud.draw_stats(screen, store)  # (a) no draw raises
    # (b) the populated text rects are mutually non-overlapping (art §V14a.8 gate).
    rects = []
    title = fonts["big"].render(C.STATS_TITLE, True, C.PLAYER)
    rects.append(title.get_rect(midtop=(C.W // 2, C.STATS_TITLE_Y)))
    rows = [
        (C.STATS_LBL_HIGHSCORE, store.highscore),
        (C.STATS_LBL_RUNS, store.runs),
        (C.STATS_LBL_ENEMIES, store.enemies_killed),
        (C.STATS_LBL_ASTEROIDS, store.asteroids_destroyed),
        (C.STATS_LBL_BOSSES, store.bosses_killed),
    ]
    for (label, value), cy in zip(rows, C.STATS_ROW_CY):
        rects.append(fonts["mid"].render(label, True, C.TEXT).get_rect(midleft=(C.STATS_BAND_L, cy)))
        rects.append(
            fonts["mid"].render(str(value), True, C.TEXT).get_rect(midright=(C.STATS_BAND_R, cy))
        )
    rects.append(
        fonts["small"].render(C.STATS_HINT, True, C.TEXT_DIM).get_rect(midtop=(C.W // 2, C.STATS_HINT_Y))
    )
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            assert not rects[i].colliderect(rects[j]), (
                f"STATS rect {i} {tuple(rects[i])} overlaps rect {j} {tuple(rects[j])}"
            )
