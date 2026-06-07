"""Unit lane — v16 second boss NOVA + extensible boss pool / uniform selection.

Covers: pool/registry shape + one-entry extensibility (R99/AC86), uniform i.i.d.
seedable selection (R100/AC87), NOVA = projectile-only / NO ships (R103/AC91), and
the deadlier-than-Mothership numbers + moveset (R104/AC92). Mothership parity stays
in test_boss.py (untouched, AC39–AC52).
"""

import math
import random

from game import config as C
from game.entities.boss import Boss, make_boss
from game.entities.projectiles import EnemyBullet, PlayerBullet
from game.systems import combat, encounter


# ── pool / registry / selection (R99/R100) ──────────────────────────────────────
def test_pool_shape_and_registry():
    """R99: ordered roster [MOTHERSHIP, NOVA]; every pool entry is a registered spec."""
    assert C.BOSS_POOL == ("MOTHERSHIP", "NOVA"), "pool order/contents wrong"
    assert len(C.BOSS_POOL) == 2, "pool is not exactly two bosses today"
    for t in C.BOSS_POOL:
        assert t in C.BOSS_SPECS, f"{t} missing from BOSS_SPECS"


def test_selection_uniform_and_seedable():
    """R100: uniform 1/N over the pool, repeats allowed, deterministic under a seed."""
    rng = random.Random(0)
    picks = [C.pick_boss_type(rng) for _ in range(4000)]
    assert set(picks) == set(C.BOSS_POOL), "not every boss is ever drawn"
    for t in C.BOSS_POOL:  # ~1/N each (2000 ± slack) → uniform, not weighted
        assert 1700 < picks.count(t) < 2300, f"{t} share not ~1/N: {picks.count(t)}"
    # Seedable: same seed → identical sequence (forceable/reproducible for tests).
    a = [C.pick_boss_type(random.Random(7)) for _ in range(20)]
    b = [C.pick_boss_type(random.Random(7)) for _ in range(20)]
    assert a == b, "selection is not reproducible under a fixed seed"


def test_extensible_one_entry_is_length_driven():
    """AC86: selection reads N from the pool LENGTH — appending one spec makes the new
    boss appear ~1/(N+1) with zero changes to the selection rule itself."""
    extended = C.BOSS_POOL + ("PHANTOM",)
    n = len(extended)
    rng = random.Random(1)
    picks = [extended[rng.randrange(n)] for _ in range(6000)]  # mirrors pick_boss_type
    for t in extended:
        assert 6000 / n * 0.8 < picks.count(t) < 6000 / n * 1.2, f"{t} not ~1/{n}"


def test_override_forces_nova_at_trigger(fresh_world):
    """R105: the pinned override forces a specific boss at the natural breakpoint —
    deterministic in tests, uniform-random in play (override is None by default)."""
    w = fresh_world()
    assert w.boss_type_override is None, "override should default to None (random in play)"
    w.boss_type_override = "NOVA"
    w.frame = int(C.BOSS_FIRST_MARK * 60)
    encounter.update(w)
    assert w.boss is not None and w.boss.type == "NOVA", "override did not force NOVA"
    assert w.boss.hp == C.NOVA_HP and w.boss.r == C.NOVA_R, "NOVA stats not from its spec"


# ── NOVA is deadlier than the Mothership on every axis (R104/AC92) ───────────────
def test_nova_deadlier_numbers():
    """AC92: every lethality axis is strictly worse than the Mothership; headline = dmg."""
    nova, moth = C.BOSS_SPECS["NOVA"], C.BOSS_SPECS["MOTHERSHIP"]
    assert C.NOVA_BULLET_DMG > C.EB_DMG, "bullet dmg not deadlier (25 > 15 is the headline)"
    assert nova["ram_dmg"] > moth["ram_dmg"], "ram dmg not deadlier (80 > 60)"
    assert C.NOVA_BULLET_SPEED > C.EB_SPEED, "bullets not faster (5.5 > 4.5)"
    assert C.NOVA_LANCE_SPEED > C.NOVA_BULLET_SPEED, "lance not the fastest (6.0)"
    assert nova["step_interval"] < moth["step_interval"], "fire-rate not faster (90 < 150 f)"
    assert nova["kill_score"] > moth["kill_score"], "reward not bigger (1500 > 1000)"
    assert nova["hp"] == moth["hp"], "deadlier should be via attacks, not HP-sponge"


# ── NOVA moveset: projectile-only, 4 distinct steps (R103/R104) ──────────────────
def _fire_nova_step(fresh_world, step_index, ring_phase=0):
    """Drive exactly one NOVA moveset step from ACTIVE and return the world."""
    w = fresh_world()
    w.boss = make_boss("NOVA", (300.0, 400.0))
    w.boss.state = "ACTIVE"
    w.boss.step_index = step_index
    w.boss.step_timer = 1
    w.boss.step_interval = 5
    w.boss.ring_phase = ring_phase
    w.player.x, w.player.y = 300.0, 700.0  # straight below → aim heading is +90°
    encounter.update(w)
    return w


def test_nova_step1_rake(fresh_world):
    """Step 1 RAKE: 5 aimed NOVA bullets, deadlier dmg, and NO ships (R103)."""
    w = _fire_nova_step(fresh_world, 0)
    assert len(w.ebullets) == C.NOVA_SPREAD_COUNT, "RAKE bullet count wrong"
    assert all(b.family == "NOVA" and b.dmg == C.NOVA_BULLET_DMG for b in w.ebullets)
    assert all(abs(math.hypot(b.vx, b.vy) - C.NOVA_BULLET_SPEED) < 1e-6 for b in w.ebullets)
    assert not w.enemies, "RAKE spawned ships — NOVA must be projectile-only (R103)"


def test_nova_step2_burst_even_ring(fresh_world):
    """Step 2 BURST: 24-bullet ring at 15° steps offset by the (precessing) ring_phase."""
    w = _fire_nova_step(fresh_world, 1, ring_phase=0)
    assert len(w.ebullets) == C.NOVA_RING_COUNT, "BURST ring count wrong"
    angles = sorted(round(math.degrees(math.atan2(b.vy, b.vx))) % 360 for b in w.ebullets)
    assert angles == sorted(k * C.NOVA_RING_STEP_DEG for k in range(C.NOVA_RING_COUNT)), angles
    assert not w.enemies, "BURST spawned ships (R103)"


def test_nova_ring_precesses(fresh_world):
    """§V16.5: ring_phase advances NOVA_RING_PHASE_STEP every step → ring never repeats."""
    w = _fire_nova_step(fresh_world, 1, ring_phase=0)
    assert w.boss.ring_phase == C.NOVA_RING_PHASE_STEP, "ring_phase did not precess after a step"


def test_nova_step3_lance(fresh_world):
    """Step 3 LANCE: 4 same-heading fastest bullets, spaced (not stacked), aimed."""
    w = _fire_nova_step(fresh_world, 2)
    assert len(w.ebullets) == C.NOVA_LANCE_COUNT, "LANCE bullet count wrong"
    assert all(abs(math.hypot(b.vx, b.vy) - C.NOVA_LANCE_SPEED) < 1e-6 for b in w.ebullets)
    # All 4 share ONE heading (aimed at the player at fire time) and travel downward.
    headings = {(round(b.vx, 6), round(b.vy, 6)) for b in w.ebullets}
    assert len(headings) == 1, "LANCE is not a single aimed stream"
    assert all(b.vy > 0 for b in w.ebullets), "LANCE not aimed downward at the player"
    # …but they are SPACED along that heading (the GAP_F stagger), not stacked at one point.
    assert len({(round(b.x, 3), round(b.y, 3)) for b in w.ebullets}) == C.NOVA_LANCE_COUNT, (
        "LANCE bullets are stacked, not spaced"
    )
    assert not w.enemies, "LANCE spawned ships (R103)"


def test_nova_step4_arc(fresh_world):
    """Step 4 ARC WALL: 9 aimed NOVA bullets over a 120° arc; no ships."""
    w = _fire_nova_step(fresh_world, 3)
    assert len(w.ebullets) == C.NOVA_ARC_COUNT, "ARC bullet count wrong"
    assert all(b.family == "NOVA" for b in w.ebullets)
    assert not w.enemies, "ARC spawned ships (R103)"


def test_nova_full_cycle_spawns_no_ships(fresh_world):
    """R103/AC91: across multiple full 4-step cycles NOVA never spawns a single ship."""
    w = fresh_world()
    w.boss = make_boss("NOVA", (300.0, 400.0))
    w.boss.state = "ACTIVE"
    w.boss.first_step_delay = 1
    w.boss.step_interval = 1
    w.boss.step_timer = 1
    w.player.x, w.player.y = 300.0, 700.0
    for _ in range(10):  # > 2 full cycles
        encounter.update(w)
    assert not w.enemies, "NOVA spawned ships over a full fight — R103 violated"


# ── NOVA damage / reward through the existing paths (no new collision code) ───────
def test_nova_bullet_damage_to_player(fresh_world):
    """NOVA bullets route the normal enemy-bullet × player step but hit for 25, not 15."""
    w = fresh_world()
    p = w.player
    p.iframes = 0
    w.ebullets = [EnemyBullet(p.x, p.y, 0.0, 0.0, family="NOVA", dmg=C.NOVA_BULLET_DMG)]
    hp0 = p.hp
    combat.resolve(w)
    assert p.hp == hp0 - C.NOVA_BULLET_DMG, "NOVA bullet did not deal 25 dmg"


def test_nova_ram_damage(fresh_world):
    """NOVA body ram routes the normal damage step but hits for its per-boss 80."""
    w = fresh_world()
    w.boss = make_boss("NOVA", (300.0, 400.0))
    p = w.player
    p.x, p.y, p.iframes = 300.0, 400.0, 0
    hp0 = p.hp
    combat.resolve(w)
    assert p.hp == hp0 - C.NOVA_RAM_DMG, "NOVA ram did not deal 80 dmg"


def test_nova_defeat_reward(fresh_world):
    """Defeat awards NOVA's bigger flat reward (1500) through scoring.award + arms popup."""
    w = fresh_world()
    w.boss = make_boss("NOVA", (300.0, 400.0))
    w.boss.hp = 1
    w.pbullets = [PlayerBullet(300, 400, 0, -10)]
    s0 = w.score
    combat.resolve(w)
    assert w.boss is None, "NOVA not defeated at hp 0"
    assert w.score == s0 + C.NOVA_KILL_SCORE, "NOVA reward not 1500"
    assert w.boss_defeat_points == C.NOVA_KILL_SCORE, "popup award wrong"
    assert w.boss_defeat_text == C.NOVA_DEFEAT_TEXT and w.boss_defeat_type == "NOVA"


def test_bare_boss_is_mothership_backcompat():
    """A bare Boss(...) keeps the v7 Mothership defaults (existing tests construct these)."""
    b = Boss(x=300.0, y=400.0)
    assert b.type == "MOTHERSHIP"
    assert b.hp == C.BOSS_HP and b.r == C.BOSS_R and b.kill_score == C.BOSS_KILL_SCORE


def test_nova_strings():
    """story §V16.5: NOVA name/label/defeat literals are wired into the spec."""
    s = C.BOSS_SPECS["NOVA"]
    assert s["name"] == "NOVA" and s["label"] == "NOVA"
    assert s["warn2"] == "NOVA INBOUND" and s["defeat"] == "NOVA DOWN"
