r"""input — keyboard → a uniform InputState, plus the scripted smoke provider.

Continuous controls (move + fire) flow through `InputState`; discrete, edge-
triggered transitions (start / restart / quit) are KEYDOWN events handled in
app.py's event loop. Both the real and the smoke path emit the same InputState
shape so the rest of the game is identical headless or live (GDD §V2.9 / §11).
"""

from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class InputState:
    dx: int  # -1 / 0 / +1   (left/right, additive of arrows + WASD)
    dy: int  # -1 / 0 / +1   (up/down)
    fire: bool
    focus: bool = False  # v19: hold-SHIFT Focus this frame → ×0.5 move step (R114)


def read_input():
    """Sample the real keyboard (arrows or WASD; Z to fire) — R3/R7/R52.
    v6 remap: fire is **Z** (the taught key, GDD §V6.9); Space is kept as a
    *silent, unadvertised* secondary fire alias (permitted by R52). The bomb (X)
    is edge-triggered and handled as a KEYDOWN event in app.py, not here."""
    k = pygame.key.get_pressed()
    left = k[pygame.K_LEFT] or k[pygame.K_a]
    right = k[pygame.K_RIGHT] or k[pygame.K_d]
    up = k[pygame.K_UP] or k[pygame.K_w]
    down = k[pygame.K_DOWN] or k[pygame.K_s]
    return InputState(
        dx=int(right) - int(left),
        dy=int(down) - int(up),
        fire=bool(k[pygame.K_z] or k[pygame.K_SPACE]),
        focus=bool(k[pygame.K_LSHIFT] or k[pygame.K_RSHIFT]),  # v19: either SHIFT → Focus (R114)
    )


def smoke_input(frame):
    """Scripted headless input (GDD §11): a slow left-right sweep, firing every
    frame (the cooldown still gates real shots). Keeps the smoke run deterministic
    and exercises movement + firing + collisions without a human.
    v19 (R119): hold Focus (SHIFT) across a mid-run window so the headless path
    exercises the ×0.5 move step AND the SHIFT-held red hitbox indicator (R114/R117)."""
    going_left = (frame // 30) % 2 == 0
    focus = 60 <= frame < 90  # a focused movement window (still sweeping → step is halved)
    return InputState(dx=-1 if going_left else 1, dy=0, fire=True, focus=focus)
