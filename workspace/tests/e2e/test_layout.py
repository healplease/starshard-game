"""E2E lane — rendered-layout geometry (AC47 HUD rects, AC68 arc rects, AC71 R/Q arcs).

Validates rendered layout (rect/arc overlap) against a real display surface, so these
are e2e per §2.4 (string-width math alone would be unit).
"""

import pygame
from game import config as C


def _start_text_rects(fonts):
    """The START text rects (centred at x=W//2), matching hud.draw_start blit sites."""
    lines = [
        (C.TITLE, "big", 250),
        (C.PITCH, "small", 320),
        (C.CONTROLS_1, "small", 470),
        (C.CONTROLS_2, "small", 500),
        (C.START_STATS_HINT, "small", 530),  # v14 Tab-stats hint
        (C.START_PROMPT, "small", 560),
        (C.START_QUIT_HINT, "small", 600),
    ]
    rects = []
    for text, fk, y in lines:
        surf = fonts[fk].render(text, True, C.TEXT)
        rects.append(surf.get_rect(topleft=(C.W // 2 - surf.get_width() // 2, y)))
    return rects


def _gameover_text_rects(fonts):
    """The GAME_OVER text rects (centred at x=W//2), matching hud.draw_gameover sites."""
    lines = [
        (C.GAMEOVER_TITLE, "big", 300),
        (f"SCORE {0:05d}", "mid", 380),
        (f"BEST {0:05d}", "mid", 420),
        (C.GAMEOVER_KEYS, "small", 480),
    ]
    rects = []
    for text, fk, y in lines:
        surf = fonts[fk].render(text, True, C.TEXT)
        rects.append(surf.get_rect(topleft=(C.W // 2 - surf.get_width() // 2, y)))
    return rects


def _pause_text_rects(fonts):
    """The PAUSE text rects, matching hud.draw_pause blit sites (all midtop at x=W//2)."""
    cx = C.W // 2
    lines = [
        (C.PAUSE_TITLE, "big", C.PAUSE_HEADING_Y),
        (C.PAUSE_HINT_RESUME, "small", C.PAUSE_HINT_Y1),
        (C.PAUSE_HINT_QUIT, "small", C.PAUSE_HINT_Y2),
        (C.PAUSE_HINT_RESTART, "small", C.PAUSE_HINT_Y3),
    ]
    rects = []
    for text, fk, y in lines:
        surf = fonts[fk].render(text, True, C.TEXT)
        rects.append(surf.get_rect(midtop=(cx, y)))
    return rects


def test_ac47_hud_rects_no_overlap(screen, fonts):
    """AC47: key HUD rects don't overlap (boss bar clear of HP/score/bomb)."""
    score_rect = fonts["hud"].render(f"SCORE {0:05d}", True, C.TEXT).get_rect(topleft=(12, 10))
    hp_rect = pygame.Rect(*C.HP_BAR)
    boss_bar_rect = pygame.Rect(*C.BOSS_BAR)
    label_rect = (
        fonts["hud"].render(C.BOSS_LABEL_TEXT, True, C.TEXT).get_rect(midbottom=C.BOSS_LABEL_CENTER)
    )
    count_surf = fonts["hud"].render(f"×{2}", True, C.TEXT)  # '×N' bomb readout
    tx = C.BOMB_HUD_RIGHT - count_surf.get_width()
    bomb_left = tx - 8 - 2 * C.BOMB_ICON_R
    bomb_rect = pygame.Rect(
        bomb_left, C.BOMB_HUD_Y, C.BOMB_HUD_RIGHT - bomb_left, count_surf.get_height()
    )
    pairs = [
        ("boss bar", boss_bar_rect, "HP bar", hp_rect),
        ("boss bar", boss_bar_rect, "score", score_rect),
        ("boss bar", boss_bar_rect, "bomb readout", bomb_rect),
        ("HP bar", hp_rect, "score", score_rect),
        ("boss label", label_rect, "HP bar", hp_rect),
        ("boss label", label_rect, "score", score_rect),
    ]
    for an, ar, bn, br in pairs:
        assert not ar.colliderect(br), f"{an} overlaps {bn}: {tuple(ar)} vs {tuple(br)}"


def test_ac68_arc_rects_clear_text(screen, fonts):
    """AC68: arc rect overlaps NO text rect on START or GAME_OVER, stays on-screen."""
    r = C.PAUSE_ARC_R
    start_arc = pygame.Rect(C.START_ARC_CENTER[0] - r, C.START_ARC_CENTER[1] - r, 2 * r, 2 * r)
    go_arc = pygame.Rect(C.GAMEOVER_ARC_CENTER[0] - r, C.GAMEOVER_ARC_CENTER[1] - r, 2 * r, 2 * r)
    for tr in _start_text_rects(fonts):
        assert not start_arc.colliderect(tr), (
            f"START arc {tuple(start_arc)} overlaps text {tuple(tr)}"
        )
    for tr in _gameover_text_rects(fonts):
        assert not go_arc.colliderect(tr), (
            f"GAME_OVER arc {tuple(go_arc)} overlaps text {tuple(tr)}"
        )
    assert start_arc.bottom <= C.H and go_arc.bottom <= C.H, "arc rect runs off the bottom edge"


def test_ac71_r_arc_colocated_and_clear(screen, fonts):
    """AC71: R arc is co-located with the Q arc (v13) and clears all text (PAUSE / GAME_OVER)."""
    r = C.PAUSE_ARC_R

    def arc_rect(center):
        return pygame.Rect(center[0] - r, center[1] - r, 2 * r, 2 * r)

    # PAUSE: Q arc at (300,483) computed by draw_pause as (W//2, PAUSE_PANEL_Y+56).
    pause_q = arc_rect((C.W // 2, C.PAUSE_PANEL_Y + 56))
    pause_r = arc_rect(C.PAUSE_RESTART_ARC_CENTER)
    go_q = arc_rect(C.GAMEOVER_ARC_CENTER)
    go_r = arc_rect(C.GAMEOVER_RESTART_ARC_CENTER)

    # (a) v13 §V13.2 LOCKED: the R arc is CO-LOCATED on its screen's Q-arc centre
    # (overlap on dual-hold is intended; the violet R fill is drawn on top of amber Q).
    assert tuple(pause_r) == tuple(pause_q), (
        f"PAUSE R arc {tuple(pause_r)} not co-located with Q arc {tuple(pause_q)}"
    )
    assert tuple(go_r) == tuple(go_q), (
        f"GAME_OVER R arc {tuple(go_r)} not co-located with Q arc {tuple(go_q)}"
    )
    # (b) the R arc must clear every text rect on its screen
    for tr in _pause_text_rects(fonts):
        assert not pause_r.colliderect(tr), (
            f"PAUSE R arc {tuple(pause_r)} overlaps text {tuple(tr)}"
        )
    for tr in _gameover_text_rects(fonts):
        assert not go_r.colliderect(tr), f"GAME_OVER R arc {tuple(go_r)} overlaps text {tuple(tr)}"
    # (c) both R rects stay inside the window
    assert pause_r.bottom <= C.H and go_r.bottom <= C.H and pause_r.left >= 0 and go_r.left >= 0, (
        "R arc rect runs off a screen edge"
    )
