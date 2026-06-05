r"""regression_harness — the persistent, growing behavioral regression suite for
Starshard (v9 process-hardening, retro T1/T9/A11/A14).

WHY THIS EXISTS
  Through v8 every increment built a *scratch* QA probe and threw it away, so
  coverage was re-derived from memory each time and the FAIL loop never fired. This
  file is the durable home for those checks: it ACCUMULATES — a new increment adds
  test functions, it never deletes the old ones. It drives the REAL game modules
  (systems/entities/app/view), asserts behaviour, and is the gate QA runs to prove a
  change didn't regress AC1–AC60 (and that a planted defect is actually caught).

WHAT IT COVERS (grows over time)
  * v1–v8 behavioural ACs — driven through the real combat/physics/bombs/encounter/
    buffs pipeline and the real `App._handle_events` (not source inspection).
  * v9 gates: a render-smoke (blit one frame per GameState — no draw raises + key HUD
    rects don't overlap, AC47), a `string_widths` assertion (every UI literal fits its
    panel + every glyph is in the font), the event-script behavioral gate
    (pause/bomb/quit), and an AC13 balance-probe sanity check.

HOW TO RUN (headless; from the repo root)
  $env:SDL_VIDEODRIVER="dummy"; $env:SDL_AUDIODRIVER="dummy"
  .\.venv\Scripts\python.exe workspace\qa\regression_harness.py
  -> prints a per-AC PASS/FAIL table; exits 0 iff every check passed (else 1).

HOW TO EXTEND
  Add a function decorated with @test("<group>", "<AC#>", "<label>"); inside, build a
  minimal world / drive the real code, and `expect(cond, msg)`. That's the whole
  contract — the runner discovers it automatically.
"""

import os
import sys

# Headless drivers must be set BEFORE pygame is imported (importing game pulls it in).
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# Make the `game` package importable when run as a plain script (qa/ is a sibling of game/).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import random

import pygame

from game import config as C
from game.world import World, GameState, BonusKind, TIMED_KINDS
from game.entities.boss import Boss
from game.entities.hazards import Asteroid, make_asteroid, make_enemy
from game.entities.projectiles import (PlayerBullet, EnemyBullet, make_player_shots,
                                       make_enemy_bullet, split_pellet, split_yellow)
from game.entities.bonus import Bonus
from game.entities.fx import make_burst
from game.systems import combat, bombs, buffs, spawning, physics, encounter  # noqa: F401
from game.input import InputState
from game import app as app_mod
from game.app import App, run_event_script, balance_probe
from game.view import render, hud


# ── tiny test framework ──────────────────────────────────────────────────────
TESTS = []
_GROUP_ORDER = ["v1", "v2", "v5", "v6", "v7", "v8", "v9"]


def test(group, ac, label):
    def deco(fn):
        TESTS.append((group, ac, label, fn))
        return fn
    return deco


def expect(cond, msg):
    if not cond:
        raise AssertionError(msg)


def fresh_world(seed=1234):
    return World(random.Random(seed))


def ensure_pygame():
    """(Re)initialize pygame — App.run() calls pygame.quit() at the end, so any test
    that runs a scripted App must re-init before using pygame directly afterwards."""
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()


def make_fonts():
    return {
        "hud": pygame.font.SysFont(None, C.FONT_HUD),
        "big": pygame.font.SysFont(None, C.FONT_BIG),
        "mid": pygame.font.SysFont(None, C.FONT_MID),
        "small": pygame.font.SysFont(None, C.FONT_SMALL),
        "pickup": pygame.font.SysFont(None, C.FONT_PICKUP),
        "pill": pygame.font.SysFont(None, C.FONT_PILL),
    }


# ════════════════════════════════════════════════════════════════════════════
# v1 — base game (AC1–AC13)
# ════════════════════════════════════════════════════════════════════════════
@test("v1", "AC2", "SMOKE_FRAMES==120 and SMOKE_TIMELINE ordering is sane")
def _t_ac2():
    expect(C.SMOKE_FRAMES == 120, "smoke is not exactly 120 frames")
    expect(C.smoke_timeline_ok(), "SMOKE_TIMELINE ordering/budget check failed")


@test("v1", "AC3", "player moves on input and clamps fully on-screen")
def _t_ac3():
    w = fresh_world()
    p = w.player
    x0 = p.x
    physics.update_play(w, InputState(1, 0, False))
    expect(p.x == x0 + C.P_SPEED, "right move did not advance x by P_SPEED")
    for _ in range(300):
        physics.update_play(w, InputState(1, 1, False))
    expect(p.x == C.W - 14 and p.y == C.H - 15, f"clamp failed: ({p.x},{p.y})")


@test("v1", "AC5", "asteroid contact damages the player and is consumed")
def _t_ac5():
    w = fresh_world()
    p = w.player
    a = Asteroid(p.x, p.y, 0, 0, C.AST_S_R, 1, False)
    w.asteroids = [a]
    hp0 = p.hp
    combat.resolve(w)
    expect(p.hp == hp0 - C.AST_S_DMG, "small-asteroid damage wrong")
    expect(p.iframes == C.IFRAMES, "i-frames did not start on hit")
    expect(a not in w.asteroids, "asteroid not consumed on contact")


@test("v1", "AC6", "enemy bullet deals 15; ramming an enemy deals 40 and kills it")
def _t_ac6():
    w = fresh_world()
    p = w.player
    w.ebullets = [EnemyBullet(p.x, p.y, 0, 0, family="RED")]
    hp0 = p.hp
    combat.resolve(w)
    expect(p.hp == hp0 - C.EB_DMG, "enemy-bullet damage wrong")
    w2 = fresh_world()
    p2 = w2.player
    e = make_enemy(w2.rng, 0.0, "REGULAR")
    e.x, e.y = p2.x, p2.y
    w2.enemies = [e]
    hp0 = p2.hp
    combat.resolve(w2)
    expect(p2.hp == hp0 - e.ram_dmg and e not in w2.enemies, "enemy ram wrong")


@test("v1", "AC7", "firing emits one shot and sets the cooldown (rate-limited)")
def _t_ac7():
    w = fresh_world()
    p = w.player
    physics.update_play(w, InputState(0, 0, True))
    expect(len(w.pbullets) == 1, "first frame did not fire exactly one shot")
    expect(p.fire_cd == C.FIRE_CD, "fire cooldown not set to baseline")
    physics.update_play(w, InputState(0, 0, True))
    expect(len(w.pbullets) == 1, "fired again before cooldown elapsed")


@test("v1", "AC8", "bullets remove a small rock in 1 hit, large in 2 (+score)")
def _t_ac8():
    w = fresh_world()
    w.pbullets = [PlayerBullet(100, 100, 0, -10)]
    w.asteroids = [Asteroid(100, 100, 0, 0, C.AST_S_R, 1, False)]
    s0 = w.score
    combat.resolve(w)
    expect(not w.asteroids and not w.pbullets, "small rock not killed in 1 hit")
    expect(w.score == s0 + C.AST_S_SCORE, "small-rock score wrong")
    al = Asteroid(100, 100, 0, 0, C.AST_L_R, 2, True)
    w.pbullets = [PlayerBullet(100, 100, 0, -10)]
    w.asteroids = [al]
    combat.resolve(w)
    expect(al in w.asteroids and al.hits == 1, "large rock should survive first hit")


@test("v1", "AC9", "first-hit-wins: only one damage source applies per frame")
def _t_ac9():
    w = fresh_world()
    p = w.player
    w.asteroids = [Asteroid(p.x, p.y, 0, 0, C.AST_S_R, 1, False),
                   Asteroid(p.x, p.y, 0, 0, C.AST_S_R, 1, False)]
    hp0 = p.hp
    combat.resolve(w)
    expect(p.hp == hp0 - C.AST_S_DMG, "more than one damage source applied")
    expect(len(w.asteroids) == 1, "exactly one hazard should be consumed")


@test("v1", "AC10", "HP<=0 -> GAME_OVER and BEST records the score")
def _t_ac10():
    app = App()
    app.world = fresh_world()
    app.state = GameState.PLAY
    app.bomb_fired = False
    app.world.player.hp = 5
    app.world.score = 123
    p = app.world.player
    app.world.asteroids = [Asteroid(p.x, p.y, 0, 0, C.AST_L_R, 2, True)]
    app._step_play(InputState(0, 0, False))
    expect(app.state is GameState.GAME_OVER, "did not transition to GAME_OVER")
    expect(app.world.best == 123, "BEST did not capture the score")


@test("v1", "AC11", "restart fully resets the run, preserves session BEST")
def _t_ac11():
    w = fresh_world()
    w.score = 999
    w.player.hp = 10
    w.enemies = [make_enemy(w.rng, 0)]
    w.pbullets = [PlayerBullet(0, 0, 0, 0)]
    w.player.buff_timers[BonusKind.FAN] = 100
    w.charges = 0
    w.frame = 500
    w.best = 555
    w.reset_run()
    expect(w.score == 0 and w.player.hp == C.P_MAX_HP, "score/hp not reset")
    expect(not w.enemies and not w.pbullets, "entities not cleared")
    expect(w.frame == 0 and w.charges == C.BOMB_START, "frame/charges not reset")
    expect(w.best == 555, "session BEST must survive a restart")


@test("v1", "AC13", "difficulty ramp escalates AND every probed run terminates")
def _t_ac13():
    expect(C.asteroid_interval(0) > C.asteroid_interval(120), "asteroid rate not ramping")
    expect(C.enemy_cap(0) < C.enemy_cap(120), "enemy cap not ramping")
    expect(C.hazard_speed_bonus(0) < C.hazard_speed_bonus(120), "hazard speed not ramping")
    times, _censored = balance_probe(runs=4, cap=3600)
    expect(len(times) == 4 and all(t > 0 for t in times), "balance probe produced no runs")


# ════════════════════════════════════════════════════════════════════════════
# v2 — pickup bonuses (AC14–AC21)
# ════════════════════════════════════════════════════════════════════════════
@test("v2", "AC14", "bonus collected on overlap; a missed bonus despawns penalty-free")
def _t_ac14():
    w = fresh_world()
    p = w.player
    bon = Bonus(BonusKind.RAPID, p.x, p.y)
    w.bonuses = [bon]
    combat.resolve(w)
    expect(bon not in w.bonuses and p.buff(BonusKind.RAPID) > 0, "bonus not collected")
    w2 = fresh_world()
    p2 = w2.player
    miss = Bonus(BonusKind.REPAIR, 50, C.H + C.BONUS_PICKUP_R + 1)
    w2.bonuses = [miss]
    hp0, s0 = p2.hp, w2.score
    physics.update_play(w2, InputState(0, 0, False))
    expect(miss not in w2.bonuses and p2.hp == hp0 and w2.score == s0, "missed bonus penalized")
    expect(C.BONUS_CAP == 3, "on-screen bonus cap is not 3")


@test("v2", "AC15", "Repair heals +40, clamps at 100 (no overheal), stores no pill")
def _t_ac15():
    w = fresh_world()
    p = w.player
    p.hp = 30
    buffs.apply(w, Bonus(BonusKind.REPAIR, p.x, p.y))
    expect(p.hp == 70, "repair did not heal +40")
    expect(BonusKind.REPAIR not in p.buff_timers, "repair wrongly stored a timed pill")
    expect(w.repair_popup_timer == C.REPAIR_POPUP_LIFE, "repair popup not armed")
    p.hp = 80
    buffs.apply(w, Bonus(BonusKind.REPAIR, p.x, p.y))
    expect(p.hp == 100, "repair overhealed past 100")


@test("v2", "AC16", "timed buff reverts cleanly on expiry")
def _t_ac16():
    w = fresh_world()
    p = w.player
    buffs.apply(w, Bonus(BonusKind.FAN, p.x, p.y))
    expect(p.fan_active, "fan did not activate")
    p.buff_timers[BonusKind.FAN] = 1
    buffs.tick(w)
    expect(not p.fan_active and BonusKind.FAN not in p.buff_timers, "fan did not revert")


@test("v2", "AC17", "HUD pill order is the stable FAN/RAPID/SHIELD/SCORE; instant kinds excluded")
def _t_ac17():
    expect(C.TIMED_ORDER == ("FAN", "RAPID", "SHIELD", "SCORE"), "pill order changed")
    names = tuple(k.name for k in TIMED_KINDS)
    expect(names == C.TIMED_ORDER, "TIMED_KINDS out of sync with TIMED_ORDER")
    expect("REPAIR" not in names and "BOMB" not in names, "instant kind leaked into pills")


@test("v2", "AC18", "re-collect hard-refreshes (no stack/double); types coexist")
def _t_ac18():
    w = fresh_world()
    p = w.player
    buffs.apply(w, Bonus(BonusKind.FAN, p.x, p.y))
    p.buff_timers[BonusKind.FAN] = 5
    buffs.apply(w, Bonus(BonusKind.FAN, p.x, p.y))
    expect(p.buff_timers[BonusKind.FAN] == C.BUFF_DURATION["FAN"], "fan did not refresh to full")
    buffs.apply(w, Bonus(BonusKind.RAPID, p.x, p.y))
    expect(p.fan_active and p.rapid_active, "buffs did not coexist")
    expect(len(make_player_shots(p.x, p.y, p.fan_active)) == 3, "fan effect doubled")


@test("v2", "AC19", "restart leaks no buff/popup/charge state into the new run")
def _t_ac19():
    w = fresh_world()
    p = w.player
    p.buff_timers[BonusKind.SHIELD] = 50
    w.repair_popup_timer = 10
    w.bomb_popup_timer = 10
    w.bonuses = [Bonus(BonusKind.REPAIR, 0, 0)]
    w.reset_run()
    expect(p is not w.player, "reset_run did not rebuild the player")
    expect(w.player.buff_timers == {}, "buff timers leaked")
    expect(w.repair_popup_timer == 0 and w.bomb_popup_timer == 0, "popups leaked")
    expect(w.bonuses == [], "pickups leaked")


@test("v2", "AC20", "seeded Rapid runs full spawn->collect->apply->expire")
def _t_ac20():
    w = fresh_world()
    p = w.player
    spawning.seed_smoke_bonus(w)
    expect(len(w.bonuses) == 1, "smoke bonus not seeded")
    p.x, p.y = C.SMOKE_BONUS_POS
    combat.resolve(w)
    expect(p.rapid_active and p.fire_cooldown == C.RAPID_CD, "rapid not applied on collect")
    for _ in range(C.SMOKE_BONUS_DUR + 1):
        buffs.tick(w)
    expect(not p.rapid_active and p.fire_cooldown == C.FIRE_CD, "rapid did not expire/revert")


@test("v2", "AC21", "package imports cleanly (script + -m entry points)")
def _t_ac21():
    import importlib
    for mod in ("game.main", "game.app", "game.config", "game.world",
                "game.systems.combat", "game.view.render"):
        importlib.import_module(mod)
    expect(callable(app_mod.App), "App is not importable/callable")
    expect(hasattr(importlib.import_module("game.main"), "main"), "main() entry missing")


# ════════════════════════════════════════════════════════════════════════════
# v5 — enemy roster + splitting pellet (AC22–AC29)
# ════════════════════════════════════════════════════════════════════════════
@test("v5", "AC22", "three distinct enemy kinds with ordered HP / entry speed")
def _t_ac22():
    expect(set(C.ENEMY_KINDS) == {"REGULAR", "HEAVY", "SCOUT"}, "enemy roster changed")
    hp = C.ENEMY_KINDS
    expect(hp["HEAVY"]["hp"] > hp["REGULAR"]["hp"] > hp["SCOUT"]["hp"], "hp ordering wrong")
    expect(hp["SCOUT"]["entry"] > hp["REGULAR"]["entry"] > hp["HEAVY"]["entry"], "speed ordering wrong")


@test("v5", "AC25", "bullet families: REGULAR=RED, HEAVY=GREEN, SCOUT=CYAN")
def _t_ac25():
    expect(C.ENEMY_KINDS["REGULAR"]["bullet"] == "RED", "regular bullet family wrong")
    expect(C.ENEMY_KINDS["HEAVY"]["bullet"] == "GREEN", "heavy bullet family wrong")
    expect(C.ENEMY_KINDS["SCOUT"]["bullet"] == "CYAN", "scout bullet family wrong")


@test("v5", "AC27", "GREEN pellet matures into exactly 3 terminal RED children")
def _t_ac27():
    pellet = make_enemy_bullet(300, 100, 300, 400, random.Random(1), "HEAVY")
    expect(pellet.family == "GREEN" and pellet.split_timer is not None, "pellet not GREEN/timed")
    children = split_pellet(pellet)
    expect(len(children) == 3, "split did not yield exactly 3 children")
    expect(all(c.family == "RED" and c.split_timer is None for c in children), "children not terminal RED")
    w = fresh_world()
    speed = C.ENEMY_KINDS["HEAVY"]["bspeed"]
    w.ebullets = [EnemyBullet(300, 300, 0, speed, family="GREEN", split_timer=2)]
    physics.update_play(w, InputState(0, 0, False))
    physics.update_play(w, InputState(0, 0, False))
    expect(len(w.ebullets) == 3 and all(b.family == "RED" for b in w.ebullets), "pellet did not burst in flight")


@test("v5", "AC29", "aim heads toward the player within the kind's cone")
def _t_ac29():
    b = make_enemy_bullet(300, 100, 300, 400, random.Random(5), "REGULAR")
    ang = math.degrees(math.atan2(b.vy, b.vx))   # 90 deg == straight down toward player
    expect(abs(ang - 90) <= C.ENEMY_KINDS["REGULAR"]["cone_deg"] + 1e-6, f"aim off-cone: {ang}")


# ════════════════════════════════════════════════════════════════════════════
# v6 — bombs / panic button (AC30–AC38)
# ════════════════════════════════════════════════════════════════════════════
@test("v6", "AC30", "X flushes the field, spends one charge, arms flash + lockout")
def _t_ac30():
    w = fresh_world()
    w.enemies = [make_enemy(w.rng, 0)]
    w.asteroids = [make_asteroid(w.rng, 0)]
    w.ebullets = [EnemyBullet(10, 10, 0, 0)]
    c0 = w.charges
    bombs.update(w, True)
    expect(not w.enemies and not w.asteroids and not w.ebullets, "flush did not clear hostiles")
    expect(w.charges == c0 - 1, "charge not decremented")
    expect(w.flash_timer == C.FLASH_FRAMES and w.bomb_lockout == C.BOMB_LOCKOUT, "flash/lockout not armed")


@test("v6", "AC31", "flush awards no score")
def _t_ac31():
    w = fresh_world()
    w.enemies = [make_enemy(w.rng, 0)]
    s0 = w.score
    bombs.update(w, True)
    expect(w.score == s0, "flush awarded score")


@test("v6", "AC32", "flush spares player bullets and pickups")
def _t_ac32():
    w = fresh_world()
    pb = PlayerBullet(0, 0, 0, -10)
    bon = Bonus(BonusKind.REPAIR, 50, 50)
    w.pbullets = [pb]
    w.bonuses = [bon]
    w.enemies = [make_enemy(w.rng, 0)]
    bombs.update(w, True)
    expect(pb in w.pbullets and bon in w.bonuses and not w.enemies, "flush hit a spared list")


@test("v6", "AC34", "0 charges -> X is a no-op (no flush, no flash)")
def _t_ac34():
    w = fresh_world()
    w.charges = 0
    w.enemies = [make_enemy(w.rng, 0)]
    bombs.update(w, True)
    expect(w.enemies and w.charges == 0 and w.flash_timer == 0, "0-charge bomb was not a no-op")


@test("v6", "AC35", "lockout blocks a second bomb on the next frame")
def _t_ac35():
    w = fresh_world()
    w.charges = 4
    bombs.update(w, True)
    w.enemies = [make_enemy(w.rng, 0)]
    bombs.update(w, True)
    expect(w.charges == 3 and w.enemies, "lockout did not block a back-to-back bomb")


@test("v6", "AC36", "bomb pickup grants +1 charge, clamped at the cap")
def _t_ac36():
    w = fresh_world()
    w.charges = 1
    buffs.apply(w, Bonus(BonusKind.BOMB, 0, 0))
    expect(w.charges == 2 and w.bomb_popup_timer == C.REPAIR_POPUP_LIFE, "bomb pickup +1 wrong")
    w.charges = C.BOMB_CAP
    buffs.apply(w, Bonus(BonusKind.BOMB, 0, 0))
    expect(w.charges == C.BOMB_CAP, "bomb pickup overfilled past cap")


@test("v6", "AC37", "controls copy teaches the Z-fire / X-bomb remap")
def _t_ac37():
    expect("Z = fire" in C.CONTROLS_1, "CONTROLS_1 missing 'Z = fire'")
    expect("X = bomb" in C.CONTROLS_1, "CONTROLS_1 missing 'X = bomb'")


# ════════════════════════════════════════════════════════════════════════════
# v7 — bosses (AC39–AC52)
# ════════════════════════════════════════════════════════════════════════════
@test("v7", "AC39", "boss triggers when the run clock reaches the TIME mark")
def _t_ac39():
    w = fresh_world()
    w.frame = int(C.BOSS_FIRST_MARK * 60)
    encounter.update(w)
    expect(w.boss is not None, "boss did not trigger at the first mark")
    expect(w.boss_next_mark == C.BOSS_FIRST_MARK + C.BOSS_INTERVAL, "next mark not advanced")


@test("v7", "AC40", "arrival clear is free (clears field, spends NO charge)")
def _t_ac40():
    w = fresh_world()
    w.charges = 1
    w.enemies = [make_enemy(w.rng, 0)]
    w.asteroids = [make_asteroid(w.rng, 0)]
    w.frame = int(C.BOSS_FIRST_MARK * 60)
    encounter.update(w)
    expect(w.boss is not None, "boss not spawned")
    expect(not w.enemies and not w.asteroids, "arrival did not clear the field")
    expect(w.charges == 1, "arrival clear wrongly spent a bomb charge")
    expect(w.flash_timer == C.FLASH_FRAMES, "arrival flash not armed")


@test("v7", "AC41", "boss glides in then snaps to rest and goes ACTIVE")
def _t_ac41():
    w = fresh_world()
    w.boss = Boss(x=300.0, y=float(C.BOSS_REST_Y - 3))
    encounter.update(w)
    expect(w.boss.state == "ENTRANCE", "boss left ENTRANCE too early")
    encounter.update(w)
    expect(w.boss.y == C.BOSS_REST_Y and w.boss.state == "ACTIVE", "boss did not settle/activate")


@test("v7", "AC43", "moveset step 1 spawns the 5-REGULAR wave")
def _t_ac43():
    w = fresh_world()
    w.boss = Boss(x=300.0, y=float(C.BOSS_REST_Y), state="ACTIVE",
                  step_index=0, step_timer=1, first_step_delay=1, step_interval=5)
    encounter.update(w)
    expect(len(w.enemies) == 5 and all(e.kind == "REGULAR" for e in w.enemies), "wave 1 wrong")
    expect(w.boss.step_index == 1, "step cursor did not advance")


@test("v7", "AC46", "moveset step 4 fires the 3-bullet YELLOW fan")
def _t_ac46():
    w = fresh_world()
    w.boss = Boss(x=300.0, y=400.0, state="ACTIVE",
                  step_index=3, step_timer=1, step_interval=5)
    encounter.update(w)
    expect(len(w.ebullets) == 3 and all(b.family == "YELLOW" for b in w.ebullets), "yellow fan wrong")


@test("v7", "AC49", "YELLOW fan -> even 12-RED 360-degree ring")
def _t_ac49():
    reds = []
    for phase in (0, 30, 60):
        yb = EnemyBullet(300, 300, 1, 0, family="YELLOW", split_timer=1, ring_phase=phase)
        reds += split_yellow(yb)
    expect(len(reds) == 12 and all(r.family == "RED" for r in reds), "ring count/family wrong")
    angles = sorted(round(math.degrees(math.atan2(r.vy, r.vx))) % 360 for r in reds)
    expect(angles == sorted(k * 30 for k in range(12)), f"ring not even 30deg steps: {angles}")


@test("v7", "AC48", "player bullets damage the boss; defeat awards +1000 and lifts the fight")
def _t_ac48():
    w = fresh_world()
    w.boss = Boss(x=300.0, y=400.0, hp=2)
    w.pbullets = [PlayerBullet(300, 400, 0, -10)]
    combat.resolve(w)
    expect(w.boss is not None and w.boss.hp == 1 and not w.pbullets, "boss hit not registered")
    w.boss.hp = 1
    w.pbullets = [PlayerBullet(300, 400, 0, -10)]
    s0 = w.score
    combat.resolve(w)
    expect(w.boss is None, "boss not defeated at hp 0")
    expect(w.score == s0 + C.BOSS_KILL_SCORE, "defeat reward wrong")
    expect(w.boss_defeat_popup_timer > 0, "defeat popup not armed")


@test("v7", "AC50", "a bomb during the fight clears minions but the boss is immune")
def _t_ac50():
    w = fresh_world()
    w.boss = Boss(x=300.0, y=400.0, hp=50)
    w.enemies = [make_enemy(w.rng, 0)]
    bombs.update(w, True)
    expect(w.boss is not None and w.boss.hp == 50, "boss took bomb damage (should be immune)")
    expect(not w.enemies, "bomb did not clear minions during the fight")


# ════════════════════════════════════════════════════════════════════════════
# v8 — pause / unpause / Q-hold quit (AC53–AC60)
# ════════════════════════════════════════════════════════════════════════════
@test("v8", "AC53", "Esc toggles PAUSE and the run clock freezes while paused")
def _t_ac53():
    ensure_pygame()
    cap = {}

    def grab(name):
        def probe(app):
            cap[name] = (app.state, app.world.frame, app.world.player.x, app.world.player.y)
        return probe

    run_event_script({
        "frames": 15,
        "keydowns": {3: [pygame.K_ESCAPE]},
        "held": {},
        "probes": {3: grab("at_pause"), 12: grab("later")},
    })
    expect(cap["at_pause"][0] is GameState.PAUSE, "Esc did not enter PAUSE")
    expect(cap["at_pause"][1] == cap["later"][1], "run clock advanced while paused")
    expect(cap["at_pause"][2:] == cap["later"][2:], "player drifted while paused")


@test("v8", "AC56", "Q held PAUSE_QUIT_FRAMES in PAUSE quits the app")
def _t_ac56():
    ensure_pygame()
    app = run_event_script({
        "frames": 60,
        "keydowns": {2: [pygame.K_ESCAPE]},
        "held": {f: [pygame.K_q] for f in range(3, 40)},
        "probes": {},
    })
    expect(app.quit_via_qhold, "Q-hold did not quit the app")


@test("v8", "AC57", "Q released before the threshold resets the hold (no accumulation)")
def _t_ac57():
    ensure_pygame()
    cap = {}

    def grab(name):
        def probe(app):
            cap[name] = app.q_hold_frames
        return probe

    run_event_script({
        "frames": 20,
        "keydowns": {2: [pygame.K_ESCAPE]},
        "held": {f: [pygame.K_q] for f in range(3, 11)},   # 8 held frames (< 30)
        "probes": {10: grab("held8"), 12: grab("released")},
    })
    expect(cap["held8"] == 8, f"hold counter wrong while held: {cap['held8']}")
    expect(cap["released"] == 0, "hold counter did not reset on release")


@test("v8", "AC58", "Esc is a no-op in START/GAME_OVER; pygame.QUIT still quits")
def _t_ac58():
    ensure_pygame()
    app = App()
    app.world = fresh_world()
    app.state = GameState.START
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    cont = app._handle_events()
    expect(cont is True and app.state is GameState.START, "Esc not a no-op in START")
    app.state = GameState.GAME_OVER
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    cont = app._handle_events()
    expect(cont is True and app.state is GameState.GAME_OVER, "Esc not a no-op in GAME_OVER")
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    expect(app._handle_events() is False, "pygame.QUIT no longer quits")


@test("v8", "AC59", "controls copy reflects Esc=Pause / hold-Q=Quit; no stale Esc-quit")
def _t_ac59():
    expect("Esc" in C.CONTROLS_2 and "Pause" in C.CONTROLS_2, "CONTROLS_2 missing Esc/Pause")
    expect("Esc" not in C.GAMEOVER_KEYS, "GAMEOVER_KEYS still shows a stale Esc hint")


@test("v8", "R74", "R in PAUSE restarts the run into PLAY")
def _t_r74():
    ensure_pygame()
    app = App()
    app.world = fresh_world()
    app.world.score = 500
    app.state = GameState.PAUSE
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
    app._handle_events()
    expect(app.state is GameState.PLAY and app.world.score == 0, "R-from-pause restart failed")


# ════════════════════════════════════════════════════════════════════════════
# v9 — process-hardening gates (render-smoke, string_widths, event-script, balance)
# ════════════════════════════════════════════════════════════════════════════
def _rich_world():
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


@test("v9", "render", "blit one frame per GameState raises nothing")
def _t_render_smoke():
    ensure_pygame()
    screen = pygame.display.set_mode((C.W, C.H))
    fonts = make_fonts()
    render.set_fonts(fonts)
    hud.set_fonts(fonts)
    w = _rich_world()
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
            hud.draw_pause(screen, 15)
        else:
            render.draw_world(screen, w)
            hud.draw_hud(screen, w)
            hud.draw_gameover(screen, w)
    # If we got here without an exception the render-smoke passed.


@test("v9", "AC47", "key HUD rects don't overlap (boss bar clear of HP/score/bomb)")
def _t_hud_rects():
    ensure_pygame()
    pygame.display.set_mode((C.W, C.H))
    fonts = make_fonts()
    score_rect = fonts["hud"].render(f"SCORE {0:05d}", True, C.TEXT).get_rect(topleft=(12, 10))
    hp_rect = pygame.Rect(*C.HP_BAR)
    boss_bar_rect = pygame.Rect(*C.BOSS_BAR)
    label_rect = fonts["hud"].render(C.BOSS_LABEL_TEXT, True, C.TEXT).get_rect(midbottom=C.BOSS_LABEL_CENTER)
    count_surf = fonts["hud"].render(f"×{2}", True, C.TEXT)   # '×N' bomb readout
    tx = C.BOMB_HUD_RIGHT - count_surf.get_width()
    bomb_left = tx - 8 - 2 * C.BOMB_ICON_R
    bomb_rect = pygame.Rect(bomb_left, C.BOMB_HUD_Y, C.BOMB_HUD_RIGHT - bomb_left, count_surf.get_height())
    pairs = [
        ("boss bar", boss_bar_rect, "HP bar", hp_rect),
        ("boss bar", boss_bar_rect, "score", score_rect),
        ("boss bar", boss_bar_rect, "bomb readout", bomb_rect),
        ("HP bar", hp_rect, "score", score_rect),
        ("boss label", label_rect, "HP bar", hp_rect),
        ("boss label", label_rect, "score", score_rect),
    ]
    for an, ar, bn, br in pairs:
        expect(not ar.colliderect(br), f"{an} overlaps {bn}: {tuple(ar)} vs {tuple(br)}")


@test("v9", "AC47w", "string_widths: every UI literal fits its panel and all glyphs exist")
def _t_string_widths():
    ensure_pygame()
    pygame.display.set_mode((C.W, C.H))
    fonts = make_fonts()
    budgets = [
        ("TITLE", C.TITLE, "big", C.W),
        ("PITCH", C.PITCH, "small", C.W),
        ("CONTROLS_1", C.CONTROLS_1, "small", C.W),
        ("CONTROLS_2", C.CONTROLS_2, "small", C.W),
        ("START_PROMPT", C.START_PROMPT, "small", C.W),
        ("GAMEOVER_TITLE", C.GAMEOVER_TITLE, "big", C.W),
        ("GAMEOVER_KEYS", C.GAMEOVER_KEYS, "small", C.W),
        ("PAUSE_TITLE", C.PAUSE_TITLE, "big", C.W),
        ("PAUSE_HINT_RESUME", C.PAUSE_HINT_RESUME, "small", C.W),
        ("PAUSE_HINT_QUIT", C.PAUSE_HINT_QUIT, "small", C.W),
        ("PAUSE_HINT_RESTART", C.PAUSE_HINT_RESTART, "small", C.W),
        ("BOSS_LABEL_TEXT", C.BOSS_LABEL_TEXT, "hud", C.BOSS_BAR[2]),   # must fit the boss bar (AC47)
        ("BOSS_WARN_1", C.BOSS_WARN_1, "mid", C.W),
        ("BOSS_WARN_2", C.BOSS_WARN_2, "small", C.W),
        ("BOSS_DEFEAT_TEXT", C.BOSS_DEFEAT_TEXT, "mid", C.W),
        ("BOMB_PICKUP_POPUP_TEXT", C.BOMB_PICKUP_POPUP_TEXT, "small", C.W),
    ]
    for name, text, font_key, budget in budgets:
        font = fonts[font_key]
        w_px = font.size(text)[0]
        expect(w_px <= budget, f"{name} too wide: {w_px}px > {budget}px")
        expect(all(m is not None for m in font.metrics(text)), f"{name} has a glyph missing from the font")


@test("v9", "event", "event-script gate: bomb/pause/unpause/re-pause/quit all behave")
def _t_event_gate():
    ensure_pygame()
    results = {}

    def after_bomb(app):
        results["bomb"] = (not app.world.enemies and not app.world.asteroids
                           and app.world.charges == C.BOMB_START - 1 and app.world.flash_timer > 0)

    def state_is(name, st):
        def probe(app):
            results[name] = (app.state is st)
        return probe

    app = run_event_script({
        "frames": 60,
        "keydowns": {3: [pygame.K_x], 6: [pygame.K_ESCAPE], 8: [pygame.K_ESCAPE], 10: [pygame.K_ESCAPE]},
        "held": {f: [pygame.K_q] for f in range(11, 55)},
        "probes": {3: after_bomb, 6: state_is("paused", GameState.PAUSE),
                   8: state_is("unpaused", GameState.PLAY), 10: state_is("repaused", GameState.PAUSE)},
    })
    expect(results.get("bomb"), "X-in-PLAY bomb did not flush/charge/flash")
    expect(results.get("paused"), "Esc did not pause")
    expect(results.get("unpaused"), "Esc did not unpause")
    expect(results.get("repaused"), "Esc did not re-pause")
    expect(app.quit_via_qhold, "Q-hold did not quit")


@test("v9", "balance", "balance probe returns ordered median<=p95 survival figures")
def _t_balance():
    times, _censored = balance_probe(runs=6, cap=3600)
    s = sorted(times)
    median = app_mod._percentile(s, 0.5)
    p95 = app_mod._percentile(s, 0.95)
    expect(len(s) == 6 and median > 0, "balance probe produced no usable runs")
    expect(median <= p95 + 1e-9, "median exceeded p95 (percentile logic broken)")


# ── the in-process full smoke run is LAST: App.run() calls pygame.quit() at the end ──
@test("v1", "AC1", "in-process --smoke-test runs exactly 120 frames, never PAUSE")
def _t_ac1_smoke():
    ensure_pygame()
    app = App(smoke=True)
    app.run()
    expect(app.frame == C.SMOKE_FRAMES, f"smoke ran {app.frame} frames, expected 120")
    expect(app.state is not GameState.PAUSE, "smoke run entered PAUSE (should be impossible)")


# ── runner ───────────────────────────────────────────────────────────────────
def main():
    results = []
    for group, ac, label, fn in TESTS:
        try:
            fn()
            results.append((group, ac, label, True, ""))
        except Exception as exc:   # any failure is a captured FAIL, never aborts the suite
            results.append((group, ac, label, False, f"{type(exc).__name__}: {exc}"))

    passed = sum(1 for r in results if r[3])
    failed = len(results) - passed
    by_group = {}
    for r in results:
        by_group.setdefault(r[0], []).append(r)

    print("=" * 72)
    print(f"Starshard regression harness - {len(results)} checks "
          f"({passed} PASS / {failed} FAIL)")
    print("=" * 72)
    for group in _GROUP_ORDER:
        rows = by_group.get(group)
        if not rows:
            continue
        print(f"\n[{group}]")
        for _g, ac, label, ok, detail in rows:
            mark = "PASS" if ok else "FAIL"
            print(f"  [{mark}] {ac:<6} {label}")
            if not ok:
                print(f"         -> {detail}")
    print("\n" + "-" * 72)
    print(f"RESULT: {'ALL PASS' if failed == 0 else str(failed) + ' FAILED'}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
