"""Unit lane — v19 precise controls (R114–R118): Focus ×0.5, the always-on small
circular damage hitbox, ~1.5× draw==collision bullets, and unchanged enemy bodies.

Pure logic: drives `physics.update_play` / `combat.resolve` directly — no App, no
event loop, no blit. The SHIFT-only red indicator (R117) is a render check and lives
in the e2e render-smoke lane.
"""

from game import config as C
from game.entities.boss import Boss
from game.entities.hazards import Asteroid, Enemy
from game.entities.projectiles import EnemyBullet
from game.input import InputState
from game.systems import combat, physics


def _dmg(w):
    """Damage dealt to the player by one combat.resolve (HP delta)."""
    hp0 = w.player.hp
    combat.resolve(w)
    return hp0 - w.player.hp


# ── R114 — hold-SHIFT Focus halves the move step, reverts on release ───────────


def test_r114_focus_halves_move_both_axes(fresh_world):
    """R114: while SHIFT (focus) is held, the per-frame step is ×0.5 on BOTH axes."""
    assert C.FOCUS_SPEED_MULT == 0.5, "Focus multiplier not locked at ×0.5"
    w = fresh_world()
    p = w.player
    x0, y0 = p.x, p.y
    physics.update_play(w, InputState(dx=1, dy=-1, fire=False, focus=True))
    step = C.P_SPEED * C.FOCUS_SPEED_MULT
    assert p.x == x0 + step, "focused x step not halved"
    assert p.y == y0 - step, "focused y step not halved"
    assert w.focus is True, "world.focus not set while SHIFT held"


def test_r114_focus_reverts_on_release(fresh_world):
    """R114: releasing SHIFT restores the full step the SAME frame (held, not toggle)."""
    w = fresh_world()
    p = w.player
    physics.update_play(w, InputState(dx=1, dy=0, fire=False, focus=True))  # focused
    x_after_focus = p.x
    physics.update_play(w, InputState(dx=1, dy=0, fire=False, focus=False))  # released
    assert p.x == x_after_focus + C.P_SPEED, "full speed not restored the frame SHIFT released"
    assert w.focus is False, "world.focus not cleared on release"


def test_r114_focus_does_not_change_firing(fresh_world):
    """R114: Focus is a movement gear only — firing cadence/count is unchanged."""
    w = fresh_world()
    physics.update_play(w, InputState(dx=0, dy=0, fire=True, focus=True))
    assert len(w.pbullets) == 1, "focused fire did not emit exactly one shot"
    assert w.player.fire_cd == C.FIRE_CD, "focused fire changed the cooldown"


# ── R115 — always-on small circular DAMAGE hitbox (P_HITBOX_R), pickup stays P_R ─


def test_r115_hitbox_constant():
    """R115: the damage hitbox is a small circle ≈50% of the drawn ship; P_R unchanged."""
    assert C.P_HITBOX_R == 6, "player damage hitbox radius not locked at 6"
    assert C.P_R == 13, "drawn-ship / pickup radius P_R must stay 13"


def test_r115_graze_inside_old_p_r_no_longer_damages(fresh_world):
    """R115/AC104: a hazard inside the OLD P_R but outside the new small hitbox no
    longer damages — verified for the ebullet, asteroid, and enemy-ram paths (boss in
    its own case)."""
    _graze_case(
        fresh_world,
        "ebullets",
        lambda p, d: EnemyBullet(p.x + d, p.y, 0, 0, family="RED"),
        C.EB_R,
        C.EB_DMG,
    )
    _graze_case(
        fresh_world,
        "asteroids",
        lambda p, d: Asteroid(p.x + d, p.y, 0, 0, C.AST_S_R, 1, False),
        C.AST_S_R,
        C.AST_S_DMG,
    )
    _graze_case(
        fresh_world,
        "enemies",
        lambda p, d: Enemy(p.x + d, p.y, 1, "REGULAR"),
        C.EN_R,
        C.ENEMY_KINDS["REGULAR"]["ram"],
    )


def _graze_case(fresh_world, slot, build, other_r, dmg_amt):
    # graze distance: outside the small hitbox, inside the old draw envelope
    graze_d = C.P_HITBOX_R + other_r + 2  # > P_HITBOX_R+other_r (miss now)
    core_d = C.P_HITBOX_R + other_r - 2  # <= P_HITBOX_R+other_r (hit)
    assert graze_d <= C.P_R + other_r, "control: graze must be inside the OLD P_R envelope"

    w = fresh_world()
    p = w.player
    haz = build(p, graze_d)
    assert combat._hit(p.x, p.y, C.P_R, haz.x, haz.y, other_r), "control: would hit at old P_R"
    setattr(w, slot, [haz])
    assert _dmg(w) == 0, f"{slot}: graze inside old P_R but outside P_HITBOX_R still damaged"

    w2 = fresh_world()
    p2 = w2.player
    setattr(w2, slot, [build(p2, core_d)])
    assert _dmg(w2) == dmg_amt, f"{slot}: hazard inside the small hitbox did not damage"


def test_r115_boss_ram_uses_small_hitbox(fresh_world):
    """R115: the boss BODY ram also tests the small hitbox (not P_R)."""
    other_r = C.BOSS_R
    graze_d = C.P_HITBOX_R + other_r + 2
    core_d = C.P_HITBOX_R + other_r - 2
    assert graze_d <= C.P_R + other_r, "control: graze inside old P_R envelope"
    w = fresh_world()
    p = w.player
    w.boss = Boss(x=p.x + graze_d, y=p.y, state="ACTIVE")
    assert _dmg(w) == 0, "boss graze inside old P_R but outside P_HITBOX_R still rammed"
    w2 = fresh_world()
    p2 = w2.player
    w2.boss = Boss(x=p2.x + core_d, y=p2.y, state="ACTIVE")
    assert _dmg(w2) == C.BOSS_RAM_DMG, "boss inside the small hitbox did not ram"


def test_r115_hitbox_independent_of_focus(fresh_world):
    """R115: the hitbox is the same circle with SHIFT up or down — collision never
    reads Focus (the red indicator only reveals it, it does not resize it)."""
    for focus in (False, True):
        w = fresh_world()
        w.focus = focus
        p = w.player
        w.ebullets = [EnemyBullet(p.x + 4, p.y, 0, 0, family="RED")]  # well inside the small core
        assert _dmg(w) == C.EB_DMG, f"focus={focus}: small hitbox damage differed"


def test_r115_pickup_collection_stays_generous(fresh_world):
    """R115/§V19.7: bonus-pickup collection stays at the generous P_R, NOT the small
    damage hitbox — a pickup grazing the old envelope is still collected."""
    from game.entities.bonus import Bonus
    from game.world import BonusKind

    w = fresh_world()
    p = w.player
    # Distance collectable at P_R but OUTSIDE the small damage hitbox.
    d = C.P_HITBOX_R + C.BONUS_PICKUP_R + 2
    assert d <= C.P_R + C.BONUS_PICKUP_R, "control: pickup within the generous P_R reach"
    bon = Bonus(BonusKind.OVERDRIVE, p.x + d, p.y)
    w.bonuses = [bon]
    combat.resolve(w)
    assert bon not in w.bonuses, "generous pickup not collected at P_R reach"
    assert p.buff(BonusKind.OVERDRIVE) > 0, "pickup buff not applied"


# ── R116 — every bullet family ~50% larger, draw == collision ──────────────────


def test_r116_bullets_larger_draw_eq_collision():
    """R116: every family ~1.5×; draw==collision; the render-only inflation constants
    (draw≠collision) are retired."""
    assert C.EB_R == 8, "shared enemy/boss bullet radius not ~1.5× (8)"
    assert (C.PB_W, C.PB_H) == (6, 18), "player bullet rect not 6×18"
    assert C.PB_H / 2 == 9, "player bullet collision radius not 9 (draw-coupled)"
    assert C.CYAN_TAIL_LEN == 18, "scout motion tail not scaled to 18"
    for retired in ("PELLET_DRAW_R", "NOVA_BULLET_DRAW_R", "CYAN_HEAD_R"):
        assert not hasattr(C, retired), f"stale render-only draw constant {retired} still present"


# ── R118 — enemy / asteroid / boss BODY radii unchanged ────────────────────────


def test_r118_enemy_body_radii_unchanged():
    """R118: only the player hitbox + bullet sizes changed — enemy/asteroid/boss bodies
    are untouched."""
    assert C.EN_R == 13, "base enemy radius changed"
    assert (C.AST_S_R, C.AST_L_R) == (12, 26), "asteroid radii changed"
    assert C.BOSS_R == 70 and C.NOVA_R == 60, "boss body radii changed"
    assert C.ENEMY_KINDS["REGULAR"]["r"] == 13
    assert C.ENEMY_KINDS["HEAVY"]["r"] == 18
    assert C.ENEMY_KINDS["SCOUT"]["r"] == 10
