"""Unit lane — save store load/save/corruption + kill counting (AC78, AC79, AC80, AC82, AC83).

Pure save-module + systems logic; every path is pinned to pytest's tmp dir, never the
real user save (conftest also pins STARSHARD_SAVE_PATH as a backstop).
"""

import json
import os

from game import config as C
from game import save
from game.entities.boss import Boss
from game.entities.hazards import Asteroid, make_enemy
from game.entities.projectiles import PlayerBullet
from game.systems import bombs, combat
from game.world import BonusKind


def test_ac78_fresh_install(tmp_save_path):
    """AC78: missing file loads zeros; first save writes the 6 keys."""
    path = tmp_save_path("fresh.json")
    s = save.load(path)  # no file present
    assert all(getattr(s, f) == 0 for f in save.COUNT_FIELDS), "missing file did not load all-zeros"
    assert s.version == save.SCHEMA_VERSION and not os.path.exists(path), (
        "load must not create the file"
    )
    s.runs = 3
    save.save(s, path)  # first flush creates it
    assert os.path.exists(path), "first save did not create the file"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert set(data) == {"version", *save.COUNT_FIELDS}, f"on-disk keys wrong: {sorted(data)}"
    assert data["version"] == 1 and data["runs"] == 3, "first save content wrong"


def test_ac79_round_trip(tmp_save_path):
    """AC79: saved values reload identical in a new load."""
    path = tmp_save_path("roundtrip.json")
    s = save.Store(
        highscore=4200, runs=9, enemies_killed=130, asteroids_destroyed=58, bosses_killed=2
    )
    save.save(s, path)
    r = save.load(path)
    assert all(getattr(r, f) == getattr(s, f) for f in save.COUNT_FIELDS), (
        "reloaded values differ from what was saved"
    )
    assert r.version == 1, "reloaded version wrong"


def test_ac80_corrupt_recovery(tmp_save_path):
    """AC80: corrupt/partial file -> zeros or per-field recovery, never crash."""
    # (a) unparseable garbage → all zeros
    p1 = tmp_save_path("garbage.json")
    with open(p1, "w", encoding="utf-8") as f:
        f.write("}{ not json at all")
    s1 = save.load(p1)
    assert all(getattr(s1, f) == 0 for f in save.COUNT_FIELDS), (
        "garbage file did not fall back to zeros"
    )
    # (b) root is a JSON array (not an object) → all zeros
    p2 = tmp_save_path("array.json")
    with open(p2, "w", encoding="utf-8") as f:
        f.write("[1, 2, 3]")
    assert all(getattr(save.load(p2), f) == 0 for f in save.COUNT_FIELDS), (
        "non-object root not treated as corrupt"
    )
    # (c) partial / mistyped fields → per-field recovery (keep good, default bad to 0)
    p3 = tmp_save_path("partial.json")
    with open(p3, "w", encoding="utf-8") as f:
        f.write('{"version": 1, "runs": 7, "enemies_killed": -4, "asteroids_destroyed": "x"}')
    s3 = save.load(p3)
    assert s3.runs == 7, "valid field not recovered"
    assert s3.enemies_killed == 0 and s3.asteroids_destroyed == 0, (
        "negative/non-int not defaulted to 0"
    )
    assert s3.highscore == 0 and s3.bosses_killed == 0, "missing fields not defaulted to 0"
    # (d) unknown version → distrust the whole shape → all zeros
    p4 = tmp_save_path("ver.json")
    with open(p4, "w", encoding="utf-8") as f:
        f.write('{"version": 99, "runs": 5}')
    assert save.load(p4).runs == 0, "unknown version was trusted instead of zeroed"


def test_ac82_count_accuracy(fresh_world):
    """AC82: asteroid/enemy/boss kills count at the award site only."""
    # asteroid: a large rock takes 2 hits but counts exactly 1 on destroy
    w = fresh_world()
    al = Asteroid(100, 100, 0, 0, C.AST_L_R, 2, True)
    w.asteroids = [al]
    w.pbullets = [PlayerBullet(100, 100, 0, -10)]
    combat.resolve(w)
    assert w.store.asteroids_destroyed == 0 and al.hits == 1, (
        "large rock counted on a non-killing hit"
    )
    w.pbullets = [PlayerBullet(100, 100, 0, -10)]
    combat.resolve(w)
    assert w.store.asteroids_destroyed == 1, "large rock not counted exactly once on destroy"
    # enemy bullet-kill counts; a ram-kill does NOT (no award site)
    w2 = fresh_world()
    e = make_enemy(w2.rng, 0, "REGULAR")
    e.x, e.y, e.hp = 100, 100, 1
    w2.enemies = [e]
    w2.pbullets = [PlayerBullet(100, 100, 0, -10)]
    combat.resolve(w2)
    assert w2.store.enemies_killed == 1, "enemy bullet-kill not counted"
    w3 = fresh_world()
    er = make_enemy(w3.rng, 0, "REGULAR")
    er.x, er.y = w3.player.x, w3.player.y  # ram → collision-consume, no award
    w3.enemies = [er]
    combat.resolve(w3)
    assert er not in w3.enemies and w3.store.enemies_killed == 0, "a ram-kill wrongly counted"
    # bomb clear counts nothing
    w4 = fresh_world()
    w4.enemies = [make_enemy(w4.rng, 0)]
    w4.asteroids = [Asteroid(50, 50, 0, 0, C.AST_S_R, 1, False)]
    bombs.update(w4, True)
    assert w4.store.enemies_killed == 0 and w4.store.asteroids_destroyed == 0, (
        "bomb flush wrongly counted kills"
    )
    # boss defeat counts bosses_killed (+1) and NEVER enemies_killed
    w5 = fresh_world()
    w5.boss = Boss(x=300.0, y=400.0, hp=1)
    w5.pbullets = [PlayerBullet(300, 400, 0, -10)]
    combat.resolve(w5)
    assert w5.boss is None and w5.store.bosses_killed == 1, "boss defeat not counted"
    assert w5.store.enemies_killed == 0, "boss defeat wrongly counted toward enemies_killed"


def test_ac83_highscore(fresh_world):
    """AC83: highscore = max over flushes, reflects Score×2, never decreases."""
    s = save.Store(highscore=500)
    s.record_highscore(300)  # lower score must not lower the high
    assert s.highscore == 500, "highscore decreased on a lower score"
    s.record_highscore(900)
    assert s.highscore == 900, "highscore did not rise to a new best"
    # Score×2 is baked into world.score before the flush reads it → a doubled score persists.
    w = fresh_world()
    w.player.buff_timers[BonusKind.SCORE] = 100  # Score×2 active
    a = Asteroid(100, 100, 0, 0, C.AST_S_R, 1, False)
    w.asteroids = [a]
    w.pbullets = [PlayerBullet(100, 100, 0, -10)]
    combat.resolve(w)
    assert w.score == C.AST_S_SCORE * C.SCORE_MULT, "Score×2 not applied to the run score"
    w.store.record_highscore(w.score)
    assert w.store.highscore == C.AST_S_SCORE * C.SCORE_MULT, (
        "flush did not capture the doubled score"
    )
