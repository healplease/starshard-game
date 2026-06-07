r"""encounter — the boss encounter manager (GDD §V7.x, R56–R68).

Runs once per PLAY frame, after physics and before the player-bomb/combat steps.
It owns the boss sub-state INSIDE play (no new top-level GameState, §V7.3):

  * TRIGGER  — when the run clock t first reaches the next TIME mark and no boss is
    active (R56/§V7.2): free+silent arrival flush (reuse the factored v6 flush, NO
    charge — R57/§V7.5), then spawn the Mothership off-screen-top. Spawners freeze
    automatically while world.boss is set (see systems/spawning).
  * ENTRANCE — the boss glides straight down at BOSS_ENTRY_SPEED; no attacks until
    it settles at the vertical centre y=BOSS_REST_Y (R59/§V7.7/§V7.8).
  * ACTIVE   — oscillate x in [W/2 ± BOSS_OSC_AMP] (constant-speed ping-pong) and
    run the fixed 4-step moveset (5 REGULAR → 2 HEAVY → 7 SCOUT → yellow fan →
    12-red ring) looping every BOSS_STEP_INTERVAL until defeat (R66–R68).
  * DEFEAT   — driven by combat when boss.hp ≤ 0 (`on_defeat` here): award the big
    flat reward through scoring.award (Score×2 doubles it), drop the boss → the
    spawn freeze lifts and the normal loop resumes immediately (R62/§V7.6).

Per-instance levers (split_dist / step cadence) let the smoke seed force a
compressed boss in-budget (§V7.15) without touching the play-time constants.
"""

import math

from .. import config as C
from ..entities.boss import make_boss
from ..entities.hazards import make_enemy
from ..entities.projectiles import EnemyBullet
from . import bombs, scoring


# ── arrival / trigger ──────────────────────────────────────────────────────────
def _spawn_boss(world, boss_type, pos, **overrides):
    """Free+silent arrival clear (reuse the factored v6 flush — NO charge, NO score,
    R57), THEN spawn the chosen boss so it never appears in the cleared lists. The
    per-boss stats come from `boss_type`'s spec; `overrides` (first_step_delay /
    step_interval / split_dist) let the smoke seed compress the fight (§V7.15)."""
    bombs.trigger_flush(world, arm_flash=True)  # free arrival flush + flash (§V7.5)
    world.boss = make_boss(boss_type, pos, ship_id=world.next_ship_id(), **overrides)


def update(world):
    """One PLAY frame of the encounter manager (called before bombs/combat)."""
    # Age the transient defeat popup regardless of whether a boss is active.
    if world.boss_defeat_popup_timer > 0:
        world.boss_defeat_popup_timer -= 1

    # TRIGGER — natural TIME breakpoint: t reached the next mark and no boss alive.
    if world.boss is None:
        if world.t >= world.boss_next_mark:
            # Selection (v16 §V16.1): pick ONE pool spec uniformly at random (1/N),
            # independent per event — unless a deterministic override is pinned (tests).
            boss_type = world.boss_type_override or C.pick_boss_type(world.rng)
            _spawn_boss(world, boss_type, C.BOSS_SPAWN)  # spec defaults for cadence
            world.boss_next_mark += C.BOSS_INTERVAL  # advance to the next absolute mark
        return

    boss = world.boss
    if boss.flash > 0:
        boss.flash -= 1

    # ENTRANCE — glide straight down, no attacks, until it settles at the centre.
    if boss.state == "ENTRANCE":
        boss.y += C.BOSS_ENTRY_SPEED
        if boss.y >= C.BOSS_REST_Y:
            boss.y = float(C.BOSS_REST_Y)  # snap, no overshoot (§V7.7)
            boss.state = "ACTIVE"
            boss.step_timer = boss.first_step_delay  # one-beat pause before step 1 (§V7.8)
        return

    # ACTIVE — oscillate about x = W/2, then drive the moveset.
    boss.x += C.BOSS_OSC_SPEED * boss.osc_dir
    lo, hi = C.W / 2 - C.BOSS_OSC_AMP, C.W / 2 + C.BOSS_OSC_AMP
    if boss.x <= lo:
        boss.x, boss.osc_dir = lo, 1
    elif boss.x >= hi:
        boss.x, boss.osc_dir = hi, -1

    boss.step_timer -= 1
    if boss.step_timer <= 0:
        _fire_step(world, boss)
        boss.step_index = (boss.step_index + 1) % 4  # 1→2→3→4→1 loop (R66)
        boss.ring_phase = (
            boss.ring_phase + C.NOVA_RING_PHASE_STEP
        ) % 360  # NOVA precession (§V16.5)
        boss.step_timer = boss.step_interval


# ── moveset ────────────────────────────────────────────────────────────────────
def _fire_step(world, boss):
    """Dispatch the current step to the active boss's moveset (v16 §V16.2). The Boss
    entity is shared; only the per-type pattern differs — selection picked the spec."""
    if boss.type == "NOVA":
        _fire_nova_step(world, boss)
    else:
        _fire_mothership_step(world, boss)


def _fire_mothership_step(world, boss):
    """Mothership (v7): steps 1–3 spawn v5 minion waves, step 4 fires the yellow fan
    (R66–R68). boss.step_index 0/1/2 → waves; 3 → fan."""
    if boss.step_index < 3:
        kind, count = C.BOSS_WAVE[boss.step_index + 1]
        _spawn_wave(world, kind, count)
    else:
        _fire_yellow_fan(world, boss)


# ── NOVA moveset (projectile-only, deadlier than the Mothership; R103/R104) ──────
def _nova_bullet(boss, theta, speed, advance=0.0):
    """One NOVA EnemyBullet on heading `theta` at `speed`: family NOVA (azure plasma
    render + EB_COLORS), terminal (no split), and `NOVA_BULLET_DMG` (25 > EB_DMG 15).
    `advance` pre-offsets the spawn along the heading (used by the LANCE stream so its
    4 same-heading bullets are spaced, not stacked — the spatial equivalent of firing
    them on frames f, f+GAP, … from a near-stationary boss). No new collision code."""
    vx, vy = math.cos(theta) * speed, math.sin(theta) * speed
    x = boss.x + math.cos(theta) * advance
    y = boss.y + math.sin(theta) * advance
    return EnemyBullet(x, y, vx, vy, family="NOVA", dmg=C.NOVA_BULLET_DMG, source=boss.id)


def _fire_nova_step(world, boss):
    """NOVA's 4-step projectile cycle (GDD §V16.5): 0 RAKE, 1 BURST, 2 LANCE, 3 ARC.
    Every step is bullets only — NO minion/enemy-spawn path is touched (R103)."""
    base = math.atan2(world.player.y - boss.y, world.player.x - boss.x)  # aim at fire time
    if boss.step_index == 0:  # RAKE — tight aimed 5-fan ±{0,15,30}° (60° wide)
        half = (C.NOVA_SPREAD_COUNT - 1) // 2
        for i in range(-half, half + 1):
            theta = base + math.radians(i * C.NOVA_SPREAD_STEP_DEG)
            world.ebullets.append(_nova_bullet(boss, theta, C.NOVA_BULLET_SPEED))
    elif boss.step_index == 1:  # NOVA BURST — dense 24-bullet precessing 360° ring
        for k in range(C.NOVA_RING_COUNT):
            theta = math.radians(k * C.NOVA_RING_STEP_DEG + boss.ring_phase)
            world.ebullets.append(_nova_bullet(boss, theta, C.NOVA_BULLET_SPEED))
    elif boss.step_index == 2:  # LANCE — aimed rapid stream of 4 fastest bullets
        for k in range(C.NOVA_LANCE_COUNT):
            advance = C.NOVA_LANCE_SPEED * C.NOVA_LANCE_GAP_F * k  # spacing == GAP_F-frame stagger
            world.ebullets.append(_nova_bullet(boss, base, C.NOVA_LANCE_SPEED, advance))
    else:  # ARC WALL — aimed wide 9-bullet 120° wall ±{0,15,30,45,60}°
        half = (C.NOVA_ARC_COUNT - 1) // 2
        for i in range(-half, half + 1):
            theta = base + math.radians(i * C.NOVA_ARC_STEP_DEG)
            world.ebullets.append(_nova_bullet(boss, theta, C.NOVA_BULLET_SPEED))


def _spawn_wave(world, kind, count):
    """Spawn up to `count` v5 minions of `kind`, gated only by the global
    MINION_CAP (no banking; first opening cycle is never capped — §V7.11/AC49).
    Minions are ordinary v5 Enemies (entry→strafe→fire, normal score). They appear
    despite the frozen spawner because they come from the boss, not the spawner."""
    room = C.MINION_CAP - len(world.enemies)
    for _ in range(max(0, min(count, room))):
        world.enemies.append(make_enemy(world.rng, world.t, kind, ship_id=world.next_ship_id()))


def _fire_yellow_fan(world, boss):
    """Step 4 (R68/§V7.12): a 3-bullet YELLOW fan from the boss centre — the centre
    bullet on the boss→player heading at fire time, flanks at ±YELLOW_FAN_SPREAD°.
    Each stores a FROZEN split timer (split_dist ÷ speed) and a ring_phase; when it
    matures (physics) it bursts into 4 RED children — together the even 12-red 360°
    ring. The yellow bullets are damaging enemy bullets in flight (EB_DMG, r=EB_R)."""
    p = world.player
    base = math.atan2(p.y - boss.y, p.x - boss.x)  # heading toward the player NOW
    spread = math.radians(C.YELLOW_FAN_SPREAD)
    timer = round(boss.split_dist / C.YELLOW_SPEED)  # frozen "midway" (no live re-read)
    # (angle offset, ring quarter): centre→{0,90,180,270}, left→{30,…}, right→{60,…}.
    for off, phase in ((0.0, 0), (-spread, 30), (spread, 60)):
        theta = base + off
        world.ebullets.append(
            EnemyBullet(
                boss.x,
                boss.y,
                math.cos(theta) * C.YELLOW_SPEED,
                math.sin(theta) * C.YELLOW_SPEED,
                family="YELLOW",
                split_timer=timer,
                ring_phase=phase,
                source=boss.id,
            )
        )


# ── defeat (called by combat when the last hit drops boss.hp ≤ 0) ───────────────
def on_defeat(world):
    """Award the big flat reward and clear the boss → the spawn freeze lifts and the
    normal loop resumes immediately (R62/§V7.6). The reward flows through
    scoring.award so Score×2 doubles it; the popup tracks the ACTUAL amount."""
    mult = C.SCORE_MULT if world.player.score_mult_active else 1
    kill_score = world.boss.kill_score  # per-boss (Mothership 1000 / NOVA 1500)
    world.boss_defeat_points = kill_score * mult  # honest "+points" (×Score×2 if active)
    # Capture the defeated boss's identity for the popup — boss is cleared below, and the
    # transient popup outlives it, so the HUD reads these (not the now-None boss).
    world.boss_defeat_text = C.BOSS_SPECS[world.boss.type]["defeat"]
    world.boss_defeat_type = world.boss.type
    scoring.award(world, kill_score)  # award() applies the same mult
    world.store.bosses_killed += 1  # v14 R93: only site a boss dies (never enemies_killed)
    world.boss_defeat_popup_timer = C.BOSS_DEFEAT_POPUP_LIFE
    world.boss = None  # surviving minions persist (§V7.9)


# ── smoke seed (GDD §V7.15) ─────────────────────────────────────────────────────
def seed_smoke_boss(world):
    """Force the `SMOKE_BOSS_TYPE` boss @ ~f40 (after the v5 f16 + v6 f20 seeds): the
    free arrival clear (NO charge — residual charge stays at 1 → AC40), then a boss
    spawned NEAR rest with a short entrance + a COMPRESSED moveset so arrival-clear +
    entrance + ≥1 attack step all fire inside the 120-f budget (§V7.15/§V16.7). The
    forced type bypasses the uniform pool draw so coverage is deterministic; the boss
    is NOT defeated (HP 120 stands)."""
    _spawn_boss(
        world,
        C.SMOKE_BOSS_TYPE,
        C.SMOKE_BOSS_SPAWN,
        first_step_delay=C.SMOKE_BOSS_STEP_DELAY,
        step_interval=C.SMOKE_BOSS_STEP_INTERVAL,
        split_dist=C.SMOKE_BOSS_SPLIT_DIST,
    )
