r"""bombs — the v6 panic button: activation, the screen-flush, the flash + lockout
(GDD §V6.3/§V6.4/§V6.5, R46–R50/R53).

`update(world, fire)` runs once per PLAY frame, **before** combat's §V2.7 player-
damage step, so a panic-bomb on the key-down frame clears the hostile bullets
*before* they can hit (the "I bombed in time" feel, GDD §V6.3). Each frame it ages
the flash / lockout / collect-popup timers, then — on a fresh X edge with charges
left and no active lockout — spends one charge, flushes the three hostile lists
(silent, NO score), and arms the flash + 18-f lockout.

Edge-triggering is the caller's job (app routes a KEYDOWN/scripted edge as `fire`);
the lockout is belt-and-suspenders so two white-outs can't strobe (GDD §V6.4).
"""

from .. import config as C


def _flush(world):
    """Bulk-clear the live hostile lists at this instant (GDD §V6.3 / R48): all
    enemies, all asteroids/debris, and ALL enemy bullets — incl. in-flight GREEN
    pellets and already-split RED children, plus the v7 boss's YELLOW fan + RED
    ring. Silent despawn: awards NO score (BOMB_FLUSH_SCORE=0) — never routed
    through scoring. SPARES player bullets, every pickup (the 6 diamonds), and
    cosmetics (particles/starfield). The v7 boss is its OWN field (world.boss),
    NOT in these lists, so it is IMMUNE to the flush by construction (§V7.14)."""
    world.enemies.clear()
    world.asteroids.clear()
    world.ebullets.clear()


def trigger_flush(world, arm_flash=True):
    """The factored flush core (GDD §V7.5): clear the hostile lists and optionally
    arm the full-screen flash — WITHOUT the charge-decrement / lockout path. The
    v6 player bomb calls this AFTER spending a charge + arming the lockout; the v7
    boss-arrival clear calls it directly (free & silent, no charge — R57)."""
    _flush(world)
    if arm_flash:
        world.flash_timer = C.FLASH_FRAMES  # arm the full-screen flash (§V6.5)


def update(world, fire):
    """Age the bomb timers, then activate on a valid X edge (GDD §V6.3/§V6.4)."""
    # Age the flash / lockout / collect-popup from any prior activation.
    if world.bomb_lockout > 0:
        world.bomb_lockout -= 1
    if world.flash_timer > 0:
        world.flash_timer -= 1
    if world.bomb_popup_timer > 0:
        world.bomb_popup_timer -= 1

    # Activate: needs a fresh edge, a charge, and no active lockout (R46/R47/R53).
    if fire and world.charges > 0 and world.bomb_lockout == 0:
        world.charges -= 1  # −1 (HUD drops by 1 — AC30)
        trigger_flush(world, arm_flash=True)  # clear lists + arm flash (no score)
        world.bomb_lockout = C.BOMB_LOCKOUT  # arm the 18-f lockout (§V6.4)
