r"""hud — score, health bar, buff-pill stack, repair popup, and the START /
GAME_OVER / PAUSE text (art_spec §4 + §V2.3/§V2.4/§V8, story §2/§4/§V2/§V8). Read-only.
"""

import math

import pygame

from .. import config as C
from ..world import TIMED_KINDS

_FONTS = {}


def set_fonts(fonts):
    _FONTS.update(fonts)


# ── PLAY HUD ─────────────────────────────────────────────────────────────────
def draw_hud(screen, world):
    p = world.player
    # Score (R11) — top-left, zero-padded to 5 digits
    screen.blit(_FONTS["hud"].render(f"SCORE {world.score:05d}", True, C.TEXT), (12, 10))
    _draw_health_bar(screen, p.hp)
    _draw_buff_pills(screen, p)
    _draw_repair_popup(screen, world)
    _draw_bomb_readout(screen, world)    # v6 — bomb count, top-right under the HP bar
    _draw_bomb_popup(screen, world)      # v6 — transient "+1 BOMB" on collect
    _draw_boss_bar(screen, world)        # v7 — boss health bar + label (active boss only)
    _draw_boss_warn(screen, world)       # v7 — "WARNING / MOTHERSHIP INBOUND" during entrance
    _draw_boss_defeat(screen, world)     # v7 — "MOTHERSHIP DOWN" + "+points" on defeat


def _draw_health_bar(screen, hp):
    rect = pygame.Rect(*C.HP_BAR)
    pygame.draw.rect(screen, C.HP_BACK, rect)
    inner_w = int((rect.width - 4) * max(0, hp) / 100)
    color = C.HP_RED if hp < 20 else C.HP_AMBER if hp < 40 else C.HP_GREEN
    pygame.draw.rect(screen, color, (rect.x + 2, rect.y + 2, inner_w, rect.height - 4))
    pygame.draw.rect(screen, C.HP_BORDER, rect, 2)


def _draw_buff_pills(screen, p):
    """One pill per active timed buff, in stable enum order, packed downward.
    Repair has no pill (it's instant). [14×14 letter box][gap][40×6 timer bar]."""
    slot = 0
    for kind in TIMED_KINDS:
        remaining = p.buff(kind)
        if remaining <= 0:
            continue
        full = C.BUFF_DURATION[kind.name]
        color = C.BONUS_COLORS[kind.name]
        y = C.PILL_TOP + slot * C.PILL_ROW_H
        # letter box
        box = pygame.Rect(C.PILL_X, y, C.PILL_BOX, C.PILL_BOX)
        pygame.draw.rect(screen, color, box)
        pygame.draw.rect(screen, C.HP_BORDER, box, 1)
        glyph = _FONTS["pill"].render(C.BONUS_LETTERS[kind.name], True, C.BONUS_INK)
        screen.blit(glyph, glyph.get_rect(center=box.center))
        # shrinking timer bar (drains left→right), vertically centered on the box
        bar_x = C.PILL_X + C.PILL_BOX + C.PILL_BAR_GAP
        bar_y = y + (C.PILL_BOX - C.PILL_BAR_H) // 2
        pygame.draw.rect(screen, C.PILL_TRACK, (bar_x, bar_y, C.PILL_BAR_W, C.PILL_BAR_H))
        fill_w = int(C.PILL_BAR_W * remaining / full)
        pygame.draw.rect(screen, color, (bar_x, bar_y, fill_w, C.PILL_BAR_H))
        slot += 1


def _draw_repair_popup(screen, world):
    """Transient green "+40" by the HP bar while the popup timer is live (§V2.4)."""
    if world.repair_popup_timer <= 0:
        return
    age = C.REPAIR_POPUP_LIFE - world.repair_popup_timer
    cx, cy = C.REPAIR_POPUP_POS
    surf = _FONTS["hud"].render(C.REPAIR_POPUP_TEXT, True, C.HP_GREEN)
    screen.blit(surf, surf.get_rect(center=(cx, cy - 0.5 * age)))   # gentle upward drift


def _draw_bomb_readout(screen, world):
    """Bomb-charge count: a violet bomb-sphere icon + ×N, right-aligned under the HP
    bar (art_spec §V6.3, GDD §V6.2). Reads the live charge integer so it is correct
    by construction (−1 on a bomb, +1 on a pickup, →2 on restart). The 0 state dims
    the text and hollows the icon → "out of bombs, X does nothing" (R47)."""
    charges = world.charges
    empty = charges == 0
    col = C.TEXT_DIM if empty else C.TEXT
    count_s = _FONTS["hud"].render(f"×{charges}", True, col)
    tx = C.BOMB_HUD_RIGHT - count_s.get_width()
    screen.blit(count_s, (tx, C.BOMB_HUD_Y))
    icx, icy = tx - 8 - C.BOMB_ICON_R, C.BOMB_HUD_Y + 11
    if empty:                                    # hollow violet ring — reads "empty"
        pygame.draw.circle(screen, C.BONUS_BOMB, (icx, icy), C.BOMB_ICON_R, 2)
    else:                                        # filled violet sphere + dark rim + fuse
        pygame.draw.circle(screen, C.BONUS_BOMB, (icx, icy), C.BOMB_ICON_R)
        pygame.draw.circle(screen, C.BONUS_INK, (icx, icy), C.BOMB_ICON_R, 1)
        pygame.draw.line(screen, C.TEXT, (icx + 3, icy - 5), (icx + 6, icy - 9), 2)
        pygame.draw.circle(screen, C.FLASH, (icx + 6, icy - 9), 1)   # spark at the fuse tip


def _draw_bomb_popup(screen, world):
    """Transient violet "+1 BOMB" under the bomb readout on collect (art_spec §V6.4),
    mirroring Repair's "+40" — different row + color, so the two never read alike."""
    if world.bomb_popup_timer <= 0:
        return
    age = C.REPAIR_POPUP_LIFE - world.bomb_popup_timer
    surf = _FONTS["small"].render(C.BOMB_PICKUP_POPUP_TEXT, True, C.BONUS_BOMB)
    screen.blit(surf, surf.get_rect(topright=(C.BOMB_HUD_RIGHT, int(58 - 0.5 * age))))


def _draw_boss_bar(screen, world):
    """Boss health bar + label — wide, center-top, magenta (enemy-faction), drains
    right→left as boss_hp/BOSS_HP_MAX (art_spec §V7.3). Shown only while a boss is
    active; AC47-clear of the HP bar / pills / bomb readout / score (center-top band)."""
    boss = world.boss
    if boss is None:
        return
    rect = pygame.Rect(*C.BOSS_BAR)
    pygame.draw.rect(screen, C.BOSS_BAR_BACK, rect)                 # empty track
    inner_w = int((rect.width - 4) * max(0, boss.hp) / C.BOSS_HP_MAX)
    pygame.draw.rect(screen, C.BOSS_BAR_FILL,
                     (rect.x + 2, rect.y + 2, inner_w, rect.height - 4))
    pygame.draw.rect(screen, C.BOSS_BAR_EDGE, rect, 2)             # frame on top
    label = _FONTS["hud"].render(C.BOSS_LABEL_TEXT, True, C.BOSS_BAR_FILL)
    screen.blit(label, label.get_rect(midbottom=C.BOSS_LABEL_CENTER))


def _draw_boss_warn(screen, world):
    """Transient arrival klaxon (story §V7.3) — two centred lines while the boss is
    still gliding in (ENTRANCE); auto-clears the moment it settles to ACTIVE."""
    boss = world.boss
    if boss is None or boss.state != "ENTRANCE":
        return
    cx, cy = C.BOSS_WARN_CENTER
    line1 = _FONTS["mid"].render(C.BOSS_WARN_1, True, C.ENEMY)
    line2 = _FONTS["small"].render(C.BOSS_WARN_2, True, C.ENEMY)
    screen.blit(line1, line1.get_rect(center=(cx, cy - 18)))
    screen.blit(line2, line2.get_rect(center=(cx, cy + 16)))


def _draw_boss_defeat(screen, world):
    """Transient defeat copy (story §V7.4): "MOTHERSHIP DOWN" + an honest "+points"
    that tracks the ACTUAL award (1000, or 2000 under Score×2) — not a hardcoded literal."""
    if world.boss_defeat_popup_timer <= 0:
        return
    cx, cy = C.BOSS_DEFEAT_CENTER
    age = C.BOSS_DEFEAT_POPUP_LIFE - world.boss_defeat_popup_timer
    line1 = _FONTS["mid"].render(C.BOSS_DEFEAT_TEXT, True, C.ENEMY)
    line2 = _FONTS["hud"].render(f"+{world.boss_defeat_points}", True, C.TEXT)
    screen.blit(line1, line1.get_rect(center=(cx, cy - 18 - 0.4 * age)))
    screen.blit(line2, line2.get_rect(center=(cx, cy + 16 - 0.4 * age)))


# Cached one-time flash overlay surface (art_spec §V6.5: one init-time Surface,
# per-frame set_alpha) — sized once to the window, re-blitted while the flash runs.
_FLASH_SURF = None


def draw_flash(screen, world):
    """Full-screen activation flash: FLASH_TINT overlay at a linearly fading alpha
    (art_spec §V6.5). flash_timer counts down from FLASH_FRAMES, so the elapsed
    frame f = FLASH_FRAMES − flash_timer and alpha = peak·(1 − f/FLASH_FRAMES) =
    peak·flash_timer/FLASH_FRAMES → peak on the activation frame, gone at f=18."""
    if world.flash_timer <= 0:
        return
    global _FLASH_SURF
    if _FLASH_SURF is None:
        _FLASH_SURF = pygame.Surface((C.W, C.H))
        _FLASH_SURF.fill(C.FLASH_COLOR)
    alpha = int(C.FLASH_PEAK_ALPHA * world.flash_timer / C.FLASH_FRAMES)
    _FLASH_SURF.set_alpha(alpha)
    screen.blit(_FLASH_SURF, (0, 0))


# ── Full-screen states ───────────────────────────────────────────────────────
def _center(screen, surf, y):
    screen.blit(surf, (C.W // 2 - surf.get_width() // 2, y))


def draw_start(screen, frame):
    _center(screen, _FONTS["big"].render(C.TITLE, True, C.PLAYER), 250)
    _center(screen, _FONTS["small"].render(C.PITCH, True, C.TEXT), 320)
    _center(screen, _FONTS["small"].render(C.CONTROLS_1, True, C.TEXT_DIM), 470)
    _center(screen, _FONTS["small"].render(C.CONTROLS_2, True, C.TEXT_DIM), 500)
    # v14 (story §V14.2): teach that Tab opens the STATS screen — FONT_SMALL / TEXT_DIM,
    # y530, between CONTROLS_2 (500) and START_PROMPT (560); same treatment as CONTROLS_2.
    _center(screen, _FONTS["small"].render(C.START_STATS_HINT, True, C.TEXT_DIM), 530)
    if (frame // 30) % 2 == 0:                    # blink the prompt
        _center(screen, _FONTS["small"].render(C.START_PROMPT, True, C.TEXT), 560)
    # v10: the Q-hold-to-quit hint — always visible (only the arc below is held-gated),
    # FONT_SMALL / TEXT_DIM, top-y 600; the arc sits 56 px below at START_ARC_CENTER.
    _center(screen, _FONTS["small"].render(C.START_QUIT_HINT, True, C.TEXT_DIM), 600)


def draw_stats(screen, store):
    """v14 STATS screen (art_spec §V14a.5): title + 5-row lifetime ledger + back hint,
    over the scrolling starfield (no dim, no arc). `store` exposes the five R92 ints.
    Labels are dim, values bright; highscore is the headline, set apart by two dividers."""
    cx = C.W // 2  # 300

    # Title (cyan, like START)
    title = _FONTS["big"].render(C.STATS_TITLE, True, C.PLAYER)
    screen.blit(title, title.get_rect(midtop=(cx, C.STATS_TITLE_Y)))

    # Two divider rules (under title, under the highscore headline)
    for y in (C.STATS_DIV_HEADER_Y, C.STATS_DIV_HEADLINE_Y):
        pygame.draw.line(screen, C.STAR_FAR, (C.STATS_BAND_L, y), (C.STATS_BAND_R, y), 1)

    # Ledger rows: (label, value, label_color); field order = art §V14a.1.
    rows = [
        (C.STATS_LBL_HIGHSCORE, store.highscore,           C.TEXT),       # headline (bright label)
        (C.STATS_LBL_RUNS,      store.runs,                C.TEXT_DIM),
        (C.STATS_LBL_ENEMIES,   store.enemies_killed,      C.TEXT_DIM),
        (C.STATS_LBL_ASTEROIDS, store.asteroids_destroyed, C.TEXT_DIM),
        (C.STATS_LBL_BOSSES,    store.bosses_killed,       C.TEXT_DIM),
    ]
    for (label, value, lbl_color), cy in zip(rows, C.STATS_ROW_CY):
        lab = _FONTS["mid"].render(label, True, lbl_color)
        val = _FONTS["mid"].render(str(value), True, C.TEXT)   # natural int, not zero-padded
        screen.blit(lab, lab.get_rect(midleft=(C.STATS_BAND_L, cy)))
        screen.blit(val, val.get_rect(midright=(C.STATS_BAND_R, cy)))

    # Back hint (Tab/Esc — Back)
    hint = _FONTS["small"].render(C.STATS_HINT, True, C.TEXT_DIM)
    screen.blit(hint, hint.get_rect(midtop=(cx, C.STATS_HINT_Y)))


def draw_gameover(screen, world):
    dim = pygame.Surface((C.W, C.H))
    dim.set_alpha(160)
    dim.fill(C.OVERLAY)
    screen.blit(dim, (0, 0))
    _center(screen, _FONTS["big"].render(C.GAMEOVER_TITLE, True, C.HP_RED), 300)
    _center(screen, _FONTS["mid"].render(f"SCORE {world.score:05d}", True, C.TEXT), 380)
    _center(screen, _FONTS["mid"].render(f"BEST {world.best:05d}", True, C.TEXT_DIM), 420)
    _center(screen, _FONTS["small"].render(C.GAMEOVER_KEYS, True, C.TEXT_DIM), 480)


def draw_pause(screen, q_hold_frames, r_hold_frames=0):
    """PAUSE overlay: full-screen dim + centered text block + Q-hold AND R-hold arcs.
    q_hold_frames / r_hold_frames: ints 0..30 — drive each arc's fill ratio independently.
    Both arc tracks are ALWAYS on here (a permanent pause-panel element); each fills only
    while its own key is held. (art_spec §V8.3/§V12.3, GDD §V8.4/§V8.6/§V12.7)
    """
    # ── 1. Full-screen dim (lighter than GAME_OVER's alpha=160) ──────────────
    dim = pygame.Surface((C.W, C.H))
    dim.set_alpha(C.PAUSE_DIM_ALPHA)   # 110 = temporary-state; game world still legible
    dim.fill(C.OVERLAY)
    screen.blit(dim, (0, 0))

    cx = C.W // 2   # 300 — all text and arc are horizontally centred here

    # ── 2. "PAUSED" heading — PLAYER cyan (≠ GAME_OVER's HP_RED) ─────────────
    heading = _FONTS["big"].render(C.PAUSE_TITLE, True, C.PLAYER)
    screen.blit(heading, heading.get_rect(midtop=(cx, C.PAUSE_HEADING_Y)))

    # ── 3. Hint lines — TEXT_DIM, FONT_SMALL ─────────────────────────────────
    for y, text in ((C.PAUSE_HINT_Y1, C.PAUSE_HINT_RESUME),
                    (C.PAUSE_HINT_Y2, C.PAUSE_HINT_QUIT),
                    (C.PAUSE_HINT_Y3, C.PAUSE_HINT_RESTART)):
        surf = _FONTS["small"].render(text, True, C.TEXT_DIM)
        screen.blit(surf, surf.get_rect(midtop=(cx, y)))

    # ── 4. Q-hold + R-hold progress arcs (both tracks always on, §V12.3) ────────
    # v13: R arc now co-located on the Q centre (300,483); draw R AFTER Q so the
    # violet R fill renders on top on dual-hold (§V13.4). Q fill amber, R fill violet.
    draw_hold_arc(screen, (cx, C.PAUSE_PANEL_Y + 56), q_hold_frames, C.PAUSE_QUIT_FRAMES)
    draw_hold_arc(screen, C.PAUSE_RESTART_ARC_CENTER, r_hold_frames,
                  C.RESTART_HOLD_FRAMES, fill_color=C.BONUS_BOMB)


# ── v12: the v8/v10 hold arc generalised — one helper for BOTH gestures ─────────
def draw_hold_arc(screen, center, hold_frames, threshold, fill_color=C.HP_AMBER):
    """The shipped v8 progress arc (HP_BACK track ring + CW fill) at an arbitrary
    centre, driven by any (hold_frames / threshold) ratio (GDD §V12.11, art_spec v8
    §V8.4 / v12 §V12.9 / v13 §V13.3). r=22, stroke=3, CW from 12 o'clock. The track is
    always drawn; the fill is drawn only while hold_frames > 0. fill_color defaults to
    HP_AMBER (the Q-quit arc); the R-restart arc passes BONUS_BOMB violet (v13). No new
    constants."""
    cx, cy = center
    r = C.PAUSE_ARC_R                                  # 22
    rect = pygame.Rect(cx - r, cy - r, 2 * r, 2 * r)   # 44×44 bounding box
    pygame.draw.arc(screen, C.HP_BACK, rect, 0, 2 * math.pi, C.PAUSE_ARC_STROKE)
    fill = hold_frames / threshold                     # 0.0 → 1.0
    if fill > 0:
        # CW from 12 o'clock: pygame.draw.arc draws CCW start→end, so fix end=π/2
        # and sweep the start back by fill×2π.
        end_a   = math.pi / 2
        start_a = end_a - fill * 2 * math.pi
        pygame.draw.arc(screen, fill_color, rect, start_a, end_a, C.PAUSE_ARC_STROKE)


# ── v10: the Q-hold quit arc, reusable at any centre (START + GAME_OVER) ────────
def draw_quit_arc(screen, center, q_hold_frames):
    """The Q-hold quit arc at an arbitrary centre — thin wrapper over draw_hold_arc."""
    draw_hold_arc(screen, center, q_hold_frames, C.PAUSE_QUIT_FRAMES)


def draw_start_quit_arc(screen, q_hold_frames):
    """START: draw the whole widget ONLY while Q is held (art_spec v10 §V10.3)."""
    if q_hold_frames > 0:
        draw_quit_arc(screen, C.START_ARC_CENTER, q_hold_frames)


def draw_gameover_quit_arc(screen, q_hold_frames):
    """GAME_OVER: draw the whole widget ONLY while Q is held (art_spec v10 §V10.3)."""
    if q_hold_frames > 0:
        draw_quit_arc(screen, C.GAMEOVER_ARC_CENTER, q_hold_frames)


# ── v12: the R-hold restart arc on PAUSE + GAME_OVER (art_spec §V12.9) ──────────
def draw_gameover_restart_arc(screen, r_hold_frames):
    """GAME_OVER: draw the whole R widget ONLY while R is held (art_spec v12 §V12.3),
    mirroring draw_gameover_quit_arc. (PAUSE's R arc is drawn inside draw_pause with its
    track always on, matching the Q arc per screen.)"""
    if r_hold_frames > 0:
        draw_hold_arc(screen, C.GAMEOVER_RESTART_ARC_CENTER,
                      r_hold_frames, C.RESTART_HOLD_FRAMES, fill_color=C.BONUS_BOMB)
