r"""render — draw the scene per state (art_spec §7 render order, §V2.6 for v2).

Read-only: every function reads World/config and draws; nothing here mutates game
state. Layer order (back→front): starfield → asteroids+enemy bullets → bonus
diamonds → player bullets → enemies → player(+shield ring) → particles. The HUD
and state overlays are drawn on top by view/hud.py.
"""

import math

import pygame

from .. import config as C


def draw_starfield(screen, world):
    for s in world.stars:
        pygame.draw.rect(screen, s.color, (s.x, int(s.y), s.size, s.size))


def draw_world(screen, world):
    """Draw the live field (used in PLAY and frozen under the GAME_OVER dim)."""
    # Asteroids — large first so small ones layer on top (art_spec §7)
    for a in sorted(world.asteroids, key=lambda a: -a.r):
        color = C.FLASH if a.flash > 0 else a.color
        pygame.draw.circle(screen, color, (int(a.x), int(a.y)), a.r)
    # Enemy bullets — RED dot / GREEN pellet / CYAN streak by family (art_spec §V5.3)
    for b in world.ebullets:
        _draw_enemy_bullet(screen, b)
    # Bonus pickups — diamonds in the hazard layer, before player bullets (§V2.6)
    for bonus in world.bonuses:
        _draw_bonus(screen, bonus)
    # Player bullets
    for b in world.pbullets:
        pygame.draw.rect(screen, C.BULLET_P, (b.x - C.PB_W / 2, b.y - C.PB_H / 2, C.PB_W, C.PB_H))
    # Enemies — distinct body per kind (art_spec §V5.1); magenta fill, told apart
    # by silhouette + size + outline weight (HEAVY > REGULAR > SCOUT).
    for e in world.enemies:
        _draw_enemy(screen, e)
    # Boss — the Mothership draws in the enemy layer; the player ship draws over it
    # next so a ram reads correctly (art_spec §V7.6). Only present during a fight.
    if world.boss is not None:
        _draw_boss(screen, world.boss)
    # Player — smooth alpha pulse while invulnerable (i-frames OR shield, §V11.3);
    # the Shield ring (if any) stays solid (§V11.4).
    _draw_player(screen, world.player)
    # Particles — shrink to 1px late (art_spec §5)
    for p in world.particles:
        sz = 2 if p.life >= 10 else 1
        pygame.draw.rect(screen, p.color, (p.x, p.y, sz, sz))


def _enemy_pts(kind, cx, cy):
    """Per-kind body polygon (art_spec §V5.1.1). +y is down; offsets from center."""
    if kind == "HEAVY":  # armored octagon, 36×32 (chamfer 8)
        return [
            (cx - 18, cy - 8),
            (cx - 10, cy - 16),
            (cx + 10, cy - 16),
            (cx + 18, cy - 8),
            (cx + 18, cy + 8),
            (cx + 10, cy + 16),
            (cx - 10, cy + 16),
            (cx - 18, cy + 8),
        ]
    if kind == "SCOUT":  # small sharp dart, 20×18
        return [(cx, cy + 9), (cx + 10, cy - 9), (cx - 10, cy - 9)]
    # REGULAR — downward chevron, 26×24 (unchanged from v1 §2.1)
    return [(cx, cy + 12), (cx + 13, cy - 12), (cx, cy - 5), (cx - 13, cy - 12)]


# Outline weight reinforces the silhouette: armored 3 / normal 2 / flimsy 1 (§V5.1).
_ENEMY_EDGE_W = {"HEAVY": 3, "REGULAR": 2, "SCOUT": 1}


def _draw_enemy(screen, e):
    pts = _enemy_pts(e.kind, e.x, e.y)
    pygame.draw.polygon(screen, C.FLASH if e.flash > 0 else C.ENEMY, pts)
    pygame.draw.polygon(screen, C.ENEMY_EDGE, pts, _ENEMY_EDGE_W[e.kind])


def _draw_enemy_bullet(screen, b):
    """Three families, one collision radius (EB_R=5); draws are render-only (§V5.3)."""
    x, y = int(b.x), int(b.y)
    if b.family == "GREEN":  # heavy pellet — drawn larger with a hot core
        pygame.draw.circle(screen, C.EB_COLOR_GREEN, (x, y), C.PELLET_DRAW_R)
        pygame.draw.circle(screen, C.FLASH, (x, y), 2)
    elif b.family == "CYAN":  # scout — a fast streak along its heading
        inv = 1.0 / max(1e-6, math.hypot(b.vx, b.vy))
        tail = (int(b.x - b.vx * inv * C.CYAN_TAIL_LEN), int(b.y - b.vy * inv * C.CYAN_TAIL_LEN))
        pygame.draw.line(screen, C.EB_COLOR_CYAN, (x, y), tail, 3)
        pygame.draw.circle(screen, C.EB_COLOR_CYAN, (x, y), C.CYAN_HEAD_R)
    elif b.family == "YELLOW":  # boss fan telegraph — emphasized "charged" round
        pygame.draw.circle(screen, C.EB_COLOR_YELLOW, (x, y), 6)  # collision still EB_R=5
        pygame.draw.circle(screen, C.FLASH, (x, y), 2)  # white core = "about to burst"
    else:  # RED — regular + every split child (plain dot)
        pygame.draw.circle(screen, C.EB_COLOR_RED, (x, y), C.EB_R)


def _draw_boss(screen, boss):
    """The Mothership silhouette (art_spec §V7.2.2): a wide dark blocky hull (8-gon)
    + bridge tower + 3 downward prongs, trimmed in enemy magenta, with a yellow
    reactor core. The painted body ⊇ the r=70 collision circle in every direction."""
    cx, cy = boss.x, boss.y
    hull = [
        (cx - 70, cy - 48),
        (cx + 70, cy - 48),
        (cx + 90, cy - 10),
        (cx + 60, cy + 40),
        (cx + 24, cy + 58),
        (cx - 24, cy + 58),
        (cx - 60, cy + 40),
        (cx - 90, cy - 10),
    ]
    bridge = [(cx - 28, cy - 48), (cx - 20, cy - 74), (cx + 20, cy - 74), (cx + 28, cy - 48)]
    prong_l = [(cx - 50, cy + 50), (cx - 40, cy + 74), (cx - 30, cy + 50)]
    prong_c = [(cx - 12, cy + 58), (cx, cy + 78), (cx + 12, cy + 58)]
    prong_r = [(cx + 30, cy + 50), (cx + 40, cy + 74), (cx + 50, cy + 50)]
    parts = (hull, bridge, prong_l, prong_c, prong_r)
    # Appendages first (so the hull overlaps their roots), then the hull body.
    for poly in (bridge, prong_l, prong_c, prong_r):
        pygame.draw.polygon(screen, C.BOSS_HULL, poly)
    pygame.draw.polygon(screen, C.BOSS_HULL, hull)
    # Panel lines (flavor) + magenta window-lights.
    pygame.draw.line(screen, C.BOSS_PLATE, (cx - 70, cy - 10), (cx + 70, cy - 10), 2)
    pygame.draw.line(screen, C.BOSS_PLATE, (cx, cy - 48), (cx, cy + 58), 2)
    for wx in (-44, -22, 0, 22, 44):
        pygame.draw.circle(screen, C.BOSS_TRIM, (int(cx + wx), int(cy - 28)), 3)
    # Magenta trim outline (the faction read) over hull + appendages; flash on a hit.
    edge = C.FLASH if boss.flash > 0 else C.BOSS_TRIM
    for poly in parts:
        pygame.draw.polygon(screen, edge, poly, 3)
    # Reactor / weapon core (where the yellow fan spawns) — pre-reads attack-4.
    pygame.draw.circle(screen, C.BOSS_CORE, (int(cx), int(cy)), 12)
    pygame.draw.circle(screen, C.FLASH, (int(cx), int(cy)), 12, 2)


def _draw_bonus(screen, bonus):
    cx, cy = bonus.x, bonus.y
    d = C.BONUS_HALF_DIAG
    pts = [(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)]
    pygame.draw.polygon(screen, bonus.color, pts)
    pygame.draw.polygon(screen, C.FLASH, pts, 1)  # 1px white outline
    glyph = _FONTS["pickup"].render(bonus.letter, True, C.BONUS_INK)
    screen.blit(glyph, glyph.get_rect(center=(int(cx), int(cy))))


# Pre-sized once (art_spec §V11.5): the ship's bounding box is 28×30; a 32×34
# surface adds margin for the 2px edge stroke. Built lazily on the first invuln
# draw and reused every frame — never a per-frame alloc (like the v6 flash surface).
_PLAYER_SURF = None
_PLAYER_SURF_SIZE = (32, 34)
_PLAYER_LOCAL = (16, 17)  # local centre on that surface (= the ship's cx, cy)


def _ship_pts(cx, cy):
    """The ship triangle, +y down, offsets from its centre (art_spec §2.1)."""
    return [(cx, cy - 15), (cx - 14, cy + 15), (cx + 14, cy + 15)]


def _draw_player(screen, p):
    cx, cy = p.x, p.y
    if not p.invulnerable:
        # Cheap common path: straight to screen at full opacity, zero surface cost
        # (art_spec §V11.5). Outside invulnerability the ship is always drawn (R18).
        pts = _ship_pts(cx, cy)
        pygame.draw.polygon(screen, C.PLAYER, pts)
        pygame.draw.polygon(screen, C.PLAYER_EDGE, pts, 2)
        pygame.draw.circle(screen, C.PLAYER_EDGE, (int(cx), int(cy)), 3)
        return
    # Invulnerable (i-frames OR shield): smooth cosine alpha pulse between the 128
    # floor and the 255 ceiling over a 30-f cycle, phase driven by blink_timer so it
    # tracks the remaining i-frames/Shield and snaps back to solid the instant invuln
    # ends (the not-invulnerable branch above). Never invisible (floor 128) — §V11.3.
    phase = (p.blink_timer % C.INVULN_PULSE_PERIOD) / C.INVULN_PULSE_PERIOD
    osc = 0.5 + 0.5 * math.cos(2 * math.pi * phase)  # 1.0 bright .. 0.0 dim
    alpha = int(round(C.INVULN_ALPHA_FLOOR + (C.INVULN_ALPHA_CEIL - C.INVULN_ALPHA_FLOOR) * osc))
    global _PLAYER_SURF
    if _PLAYER_SURF is None:
        _PLAYER_SURF = pygame.Surface(_PLAYER_SURF_SIZE, pygame.SRCALPHA)
    surf = _PLAYER_SURF
    surf.fill((0, 0, 0, 0))  # clear the prior frame
    lcx, lcy = _PLAYER_LOCAL
    lpts = _ship_pts(lcx, lcy)
    pygame.draw.polygon(surf, C.PLAYER, lpts)
    pygame.draw.polygon(surf, C.PLAYER_EDGE, lpts, 2)
    pygame.draw.circle(surf, C.PLAYER_EDGE, (lcx, lcy), 3)
    # Scale the surface's alpha CHANNEL by alpha/255 (RGB unchanged). set_alpha is a
    # silent no-op on an SRCALPHA per-pixel surface, so use BLEND_RGBA_MULT (§V11.5).
    surf.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(surf, (int(cx) - lcx, int(cy) - lcy))
    # Shield bubble ring stays SOLID — full alpha, every frame, drawn straight to
    # screen OUTSIDE the alpha surface, so it never pulses or strobes (§V11.4).
    if p.shield_active:
        pygame.draw.circle(screen, C.BONUS_SHIELD, (int(cx), int(cy)), 18, 2)


# Fonts are injected once by the app (kept here so render stays a pure consumer).
_FONTS = {}


def set_fonts(fonts):
    _FONTS.update(fonts)
