r"""save — the v14 lifetime-stats persistence store (R92–R98).

A single JSON object at the file root persists five lifetime values + a `version`
across process runs. It lives in a per-user, per-game subfolder. The store is held
in memory for the whole process (R94) and written only at a flush (R95, atomic
write-temp-then-rename so a crash mid-write never corrupts the file). Loading never
crashes — a missing / unparseable / partial file falls back to zeros, with per-field
recovery for a partly-valid file (R96). No pygame, no game imports — pure I/O.

Path (R92): default = a per-user OS dir (Windows %APPDATA%\Starshard\, macOS
~/Library/Application Support/Starshard/, else $XDG_DATA_HOME or ~/.local/share/
Starshard/). Overridable (R98) via the STARSHARD_SAVE_PATH env var or an explicit
arg, so headless smoke/regression runs target a throwaway temp file and never touch
the player's real stats.
"""

import json
import os
import sys
import tempfile

SCHEMA_VERSION = 1                          # v14 = version 1 (R92)
KNOWN_VERSIONS = (1,)                        # versions whose shape we trust (R96)
# The five snake_case count fields — frozen keys, code reads/writes exactly these (R92).
COUNT_FIELDS = ("highscore", "runs", "enemies_killed", "asteroids_destroyed", "bosses_killed")

SAVE_PATH_ENV = "STARSHARD_SAVE_PATH"       # R98 override (smoke/regression → temp)
APP_DIR_NAME = "Starshard"                  # per-game subfolder
SAVE_FILENAME = "stats.json"


class Store:
    """The process-lifetime store (R94): five lifetime ints + the schema version.
    Counters accumulate in memory during play; `record_highscore` + `save` run only
    at a flush. Fields match COUNT_FIELDS / the R92 schema exactly."""

    def __init__(self, highscore=0, runs=0, enemies_killed=0,
                 asteroids_destroyed=0, bosses_killed=0):
        self.version = SCHEMA_VERSION
        self.highscore = highscore
        self.runs = runs
        self.enemies_killed = enemies_killed
        self.asteroids_destroyed = asteroids_destroyed
        self.bosses_killed = bosses_killed

    def record_highscore(self, score):
        """R93/§highscore: highscore is the best single-run score ever seen — refreshed
        at every flush to max(stored, current run score). Never decreases."""
        self.highscore = max(self.highscore, score)

    def to_dict(self):
        """The full on-disk object: `version` + the five frozen count keys (R92)."""
        d = {"version": SCHEMA_VERSION}
        for field in COUNT_FIELDS:
            d[field] = getattr(self, field)
        return d


# ── path resolution (R92 default + R98 override) ─────────────────────────────────
def default_save_path():
    """The per-user, per-game save file path for this OS (R92)."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:                                   # Linux / other POSIX — XDG base dir
        base = os.environ.get("XDG_DATA_HOME") or os.path.join(
            os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, APP_DIR_NAME, SAVE_FILENAME)


def resolve_path(override=None, headless=False):
    """Pick the save path (R98): an explicit arg wins, then the STARSHARD_SAVE_PATH
    env var, then a throwaway temp file for headless runs, then the real per-user path.
    Headless never touches the player's real stats even with no env set (AC85)."""
    if override:
        return override
    env = os.environ.get(SAVE_PATH_ENV)
    if env:
        return env
    if headless:
        return os.path.join(tempfile.gettempdir(), "starshard_headless_stats.json")
    return default_save_path()


# ── load (R96: never crash; zeros / per-field recovery) ─────────────────────────
def _valid_count(v):
    """A usable count field: an int (JSON bool is NOT an int here), and ≥ 0 (R96)."""
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def load(path=None):
    """Load the store from `path`, never raising (R96). Missing/unreadable/unparseable
    file, a non-object root, or an unknown `version` → all-zeros. A partly-valid object
    recovers each count field independently (missing / non-int / negative → that field 0)."""
    path = path or resolve_path()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):           # missing / unreadable / unparseable JSON
        return Store()
    if not isinstance(data, dict):          # root is not a JSON object → corrupt
        return Store()
    version = data.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version not in KNOWN_VERSIONS:
        return Store()                      # unknown shape → don't trust it (R96)
    store = Store()
    for field in COUNT_FIELDS:              # per-field defensive recovery
        v = data.get(field)
        if _valid_count(v):
            setattr(store, field, v)        # else keep the 0 default
    return store


# ── save (R95: atomic write-temp-then-rename) ───────────────────────────────────
def save(store, path=None):
    """Atomically persist the full store (all five values + version). Writes a temp
    file in the target dir then os.replace()s it over the real file — atomic on Windows
    and POSIX, so a crash mid-write leaves the old file intact (R95)."""
    path = path or resolve_path()
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(store.to_dict(), f)
    os.replace(tmp, path)                   # atomic swap into place
