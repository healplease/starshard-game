r"""render — draw the scene per state (art_spec §7 render order, §V2.6 for v2).

Read-only: every function reads World/config and draws; nothing here mutates game
state. Layer order (back→front): starfield → asteroids+enemy bullets → bonus
diamonds → player bullets → enemies → player(+shield ring) → particles. The HUD
and state overlays are drawn on top by view/hud.py.
"""

import math

import pygame

from .. import config as C
from ..systems import lasers


def draw_starfield(screen, world):
    for s in world.stars:
        pygame.draw.rect(screen, s.color, (s.x, int(s.y), s.size, s.size))


def draw_world(screen, world):
    """Draw the live field (used in PLAY and frozen under the GAME_OVER dim)."""
    # Asteroids — large first so small ones layer on top (art_spec §7)
    for a in sorted(world.asteroids, key=lambda a: -a.r):
        color = C.FLASH if a.flash > 0 else a.color
        pygame.draw.circle(screen, color, (int(a.x), int(a.y)), a.r)
    # v20 LASER beams FIRST in the enemy-bullet layer (art_spec §V20a.5), so the small
    # bullets below sit on top of the wide beam and stay visible.
    for beam in world.beams:
        _draw_beam(screen, beam)
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
    if e.kind == "LASER":
        _draw_laser(screen, e)
        return
    pts = _enemy_pts(e.kind, e.x, e.y)
    pygame.draw.polygon(screen, C.FLASH if e.flash > 0 else C.ENEMY, pts)
    pygame.draw.polygon(screen, C.ENEMY_EDGE, pts, _ENEMY_EDGE_W[e.kind])


def _draw_laser(screen, e):
    """The LASER turret-eye (art_spec §V20a.2.1): a gunmetal octagon housing + a searing-
    orange emitter eye with a white-hot pupil; a charge ring is drawn only during WINDUP."""
    cx, cy = e.x, e.y
    house = [
        (cx - 17, cy - 5),
        (cx - 10, cy - 12),
        (cx + 10, cy - 12),
        (cx + 17, cy - 5),
        (cx + 17, cy + 12),
        (cx - 17, cy + 12),
    ]
    pygame.draw.polygon(screen, C.FLASH if e.flash > 0 else C.LASER_BODY, house)
    pygame.draw.polygon(screen, C.STAR_FAR, house, 2)  # cold grey-blue outline
    ex, ey = int(cx), int(cy + C.LASER_EYE_DY)
    pygame.draw.circle(screen, C.LASER_EYE, (ex, ey), C.LASER_EYE_R)
    pygame.draw.circle(screen, C.BEAM_CORE, (ex, ey), C.LASER_PUPIL_R)
    if e.beam_phase == "WINDUP":  # "powering up" ring — pairs with the windup line
        pygame.draw.circle(screen, C.LASER_EYE, (ex, ey), C.LASER_CHARGE_RING_R, 2)


def _draw_beam(screen, beam):
    """The LASER beam (art_spec §V20a.3): WINDUP = a thin faint orange telegraph line
    (no collision); DAMAGING = a white-hot core (width == collision width `w`) sheathed
    in a render-only orange glow. The glow is paint, NOT reach (draw==collision invariant
    holds on the CORE width). Far end = the endless-to-edge point (lasers.beam_endpoint)."""
    tx, ty = lasers.beam_endpoint(beam)
    o = (int(beam.ox), int(beam.oy))
    far = (int(tx), int(ty))
    if beam.phase == "WINDUP":
        surf = pygame.Surface((C.W, C.H), pygame.SRCALPHA)
        pygame.draw.line(surf, (*C.LASER_EYE, C.WINDUP_ALPHA), o, far, 2)
        screen.blit(surf, (0, 0))
        return
    w = max(1, int(round(beam.width)))  # the SINGLE width — draw == collision (R124)
    glow = pygame.Surface((C.W, C.H), pygame.SRCALPHA)  # render-only orange halo
    pygame.draw.line(glow, (*C.LASER_EYE, C.BEAM_GLOW_ALPHA), o, far, w + 2 * C.BEAM_GLOW_W)
    screen.blit(glow, (0, 0))
    pygame.draw.line(screen, C.BEAM_CORE, o, far, w)  # white-hot lethal core


def _draw_enemy_bullet(screen, b):
    """v19 (art_spec §V19a.3): draw == collision for EVERY family — each draws its body
    at the single shared EB_R (no more render-only inflation). Identity is carried by hue
    (+ a hot core / motion tail), not by a fatter radius."""
    x, y = int(b.x), int(b.y)
    if b.family == "GREEN":  # heavy pellet — purple hue (v17) + a hot core (identity, not size)
        pygame.draw.circle(screen, C.EB_COLOR_PURPLE, (x, y), C.EB_R)
        pygame.draw.circle(screen, C.FLASH, (x, y), 2)
    elif b.family == "CYAN":  # scout — head dot at EB_R + a render-only motion streak
        inv = 1.0 / max(1e-6, math.hypot(b.vx, b.vy))
        tail = (int(b.x - b.vx * inv * C.CYAN_TAIL_LEN), int(b.y - b.vy * inv * C.CYAN_TAIL_LEN))
        pygame.draw.line(screen, C.EB_COLOR_CYAN, (x, y), tail, 3)
        pygame.draw.circle(screen, C.EB_COLOR_CYAN, (x, y), C.EB_R)
    elif b.family == "YELLOW":  # boss fan telegraph — "charged" round + white core
        pygame.draw.circle(screen, C.EB_COLOR_YELLOW, (x, y), C.EB_R)
        pygame.draw.circle(screen, C.FLASH, (x, y), 2)  # white core = "about to burst"
    elif b.family == "NOVA":  # v16 NOVA — azure plasma round + hot white core
        pygame.draw.circle(screen, C.NOVA_BULLET, (x, y), C.EB_R)
        pygame.draw.circle(screen, C.FLASH, (x, y), 2)  # hot white core
    else:  # RED — regular + every split child (plain dot)
        pygame.draw.circle(screen, C.EB_COLOR_RED, (x, y), C.EB_R)


def _draw_boss(screen, boss):
    """Dispatch to the active boss's silhouette by type (v16 §V16.2 — the body is part
    of each boss's visual key, not a hard-coded shape). Only one boss is ever active."""
    _BOSS_DRAW[boss.type](screen, boss)


def _draw_mothership(screen, boss):
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


def _draw_nova(screen, boss):
    """The NOVA silhouette (art_spec §V16.2.1): a radiant electric-blue pulsar — 12
    blue spikes behind a solid disc (the disc r=62 ⊇ the r=60 collision circle), an
    inner energy ring, and a white-hot heart where the bullets originate. Radially
    symmetric blue star — distinct from the Mothership carrier in shape AND hue."""
    cx, cy = boss.x, boss.y
    # 1) radiant spikes FIRST (behind the disc; the disc overlaps their roots)
    for k in range(C.NOVA_SPIKES):
        a = math.radians(k * (360.0 / C.NOVA_SPIKES))
        aL = a - math.radians(C.NOVA_SPIKE_HALF_DEG)
        aR = a + math.radians(C.NOVA_SPIKE_HALF_DEG)
        tip = (cx + C.NOVA_SPIKE_R * math.cos(a), cy + C.NOVA_SPIKE_R * math.sin(a))
        bL = (cx + C.NOVA_DISC_R * math.cos(aL), cy + C.NOVA_DISC_R * math.sin(aL))
        bR = (cx + C.NOVA_DISC_R * math.cos(aR), cy + C.NOVA_DISC_R * math.sin(aR))
        pygame.draw.polygon(screen, C.NOVA_RAY, [tip, bL, bR])
    # 2) solid star disc — guarantees coverage of the r=60 collision circle
    pygame.draw.circle(screen, C.NOVA_BODY, (int(cx), int(cy)), C.NOVA_DISC_R)
    # 3) inner energy ring (flavor)
    pygame.draw.circle(screen, C.NOVA_RAY, (int(cx), int(cy)), C.NOVA_RING_R, 3)
    # 4) white-hot pulsar core (where bullets spawn) + bright rim; flash on a hit.
    rim = C.FLASH if boss.flash > 0 else C.STAR_NEAR
    pygame.draw.circle(screen, C.STAR_NEAR, (int(cx), int(cy)), C.NOVA_HOT_R)
    pygame.draw.circle(screen, rim, (int(cx), int(cy)), C.NOVA_HOT_R, 2)


# Body silhouette per boss type — the visual key picked from the active boss (§V16.2).
_BOSS_DRAW = {"MOTHERSHIP": _draw_mothership, "NOVA": _draw_nova}


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


# ── v19 §V19a.2: SHIFT red hitbox indicator (PLAY + SHIFT-held, after particles) ──
# A red readout of the player's TRUE damage hitbox (R115): a filled disc at P_HITBOX_R
# (HITBOX_RED @ HITBOX_ALPHA) plus a 1-px fully-opaque rim so the exact collision edge
# stays crisp over the cyan ship. Render-only — it reads the same radius/center the
# collision uses, changes no state. Straight alpha baked INTO the draw color on a small
# SRCALPHA surface (NOT set_alpha — the v11 §V11.5 gotcha); the surface is built once.
_HITBOX_SURF = None


def draw_hitbox_indicator(screen, world):
    """Draw the red hitbox circle iff Focus (SHIFT) is held; the app gates this to PLAY.
    Centered on the ship origin, radius = the live collision constant P_HITBOX_R (so a
    retune follows automatically). No-op when SHIFT is up (world.focus False)."""
    if not world.focus:
        return
    global _HITBOX_SURF
    r = C.P_HITBOX_R
    d = 2 * r + 2  # +2 px margin so the 1-px rim is never clipped
    if _HITBOX_SURF is None:
        _HITBOX_SURF = pygame.Surface((d, d), pygame.SRCALPHA)
    surf = _HITBOX_SURF
    surf.fill((0, 0, 0, 0))  # clear the prior frame
    c = (d // 2, d // 2)
    pygame.draw.circle(surf, (*C.HITBOX_RED, C.HITBOX_ALPHA), c, r)  # 50% fill
    pygame.draw.circle(surf, (*C.HITBOX_RED, 255), c, r, 1)  # opaque 1-px rim on the radius
    p = world.player
    screen.blit(surf, (int(p.x) - c[0], int(p.y) - c[1]))


# ── v17 §V17.2: low-HP red edge vignette (PLAY only, below the HUD, hp < 25) ───
# Baked ONCE at PEAK alpha (cheap concentric-circle fill — no per-pixel loop): alpha
# ≈ 0 inside r=300, ramping to VIGNETTE_MAX_ALPHA at the corners (r=500). The bake has
# per-pixel alpha, so set_alpha() is unreliable (v11 §V11.5 gotcha) — the per-frame
# pulse scales it with BLEND_RGBA_MULT instead.
_VIGNETTE = None
_VCX, _VCY = C.W // 2, C.H // 2  # screen center (300, 400)


def _build_vignette():
    surf = pygame.Surface((C.W, C.H), pygame.SRCALPHA)  # per-pixel alpha
    span = C.VIGNETTE_OUTER_R - C.VIGNETTE_INNER_R
    for d in range(
        C.VIGNETTE_OUTER_R, C.VIGNETTE_INNER_R, -1
    ):  # large→small; inner overwrites center
        f = (d - C.VIGNETTE_INNER_R) / span
        a = int(C.VIGNETTE_MAX_ALPHA * (f**C.VIGNETTE_FALLOFF_K))
        pygame.draw.circle(surf, (*C.VIGNETTE_TINT, a), (_VCX, _VCY), d)
    return surf


def draw_low_hp_vignette(screen, world):
    """Subtle red edge glow that breathes while hp < trigger (art_spec §V17.2).
    Center stays clear; only the corners reach peak alpha; a slow ~1 s cosine pulse
    between MIN and MAX alpha. Distinct from the v6 bomb flash (full-screen near-white
    one-shot, above the HUD)."""
    if world.player.hp >= C.VIGNETTE_HP_TRIGGER:
        return
    global _VIGNETTE
    if _VIGNETTE is None:
        _VIGNETTE = _build_vignette()
    phase = (world.frame % C.VIGNETTE_PULSE_PERIOD) / C.VIGNETTE_PULSE_PERIOD
    pulse = 0.5 - 0.5 * math.cos(2 * math.pi * phase)  # smooth 0→1→0
    edge_a = C.VIGNETTE_MIN_ALPHA + (C.VIGNETTE_MAX_ALPHA - C.VIGNETTE_MIN_ALPHA) * pulse
    mul = int(round(255 * edge_a / C.VIGNETTE_MAX_ALPHA))  # scale baked PEAK down to current
    frame_v = _VIGNETTE.copy()  # the baked peak is read-only; scale a per-frame copy
    frame_v.fill((255, 255, 255, mul), special_flags=pygame.BLEND_RGBA_MULT)  # scale alpha only
    screen.blit(frame_v, (0, 0))


# Fonts are injected once by the app (kept here so render stays a pure consumer).
_FONTS = {}


def set_fonts(fonts):
    _FONTS.update(fonts)
