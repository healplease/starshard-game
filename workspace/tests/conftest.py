"""Shared pytest fixtures for the Starshard suite (v15 — test_plan.md §2.3).

These replace the old regression_harness helpers (`fresh_world` / `make_fonts` /
`ensure_pygame`). The headless drivers and the save-path override are set at IMPORT
time — before any test module imports `game` (which pulls in pygame) — exactly as the
monolith did at its module top.
"""

import os
import random
import tempfile

# Must be set BEFORE `game`/pygame is imported by any test module.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
# Pin every store flush in the suite to a throwaway temp file so no test ever reads or
# writes the player's real save (R98/AC85).
os.environ.setdefault(
    "STARSHARD_SAVE_PATH",
    os.path.join(tempfile.gettempdir(), "starshard_pytest_stats.json"),
)

import pygame  # noqa: E402  (import after the SDL env is pinned)
import pytest  # noqa: E402
from game import config as C  # noqa: E402
from game.world import World  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _clean_shared_save():
    """Start the session from a clean shared save so no stale file leaks state in."""
    for p in (os.environ["STARSHARD_SAVE_PATH"], os.environ["STARSHARD_SAVE_PATH"] + ".tmp"):
        if os.path.exists(p):
            os.remove(p)
    yield


@pytest.fixture
def fresh_world():
    """Factory mirroring the harness `fresh_world(seed=1234)`."""

    def _make(seed=1234):
        return World(random.Random(seed))

    return _make


@pytest.fixture(scope="session")
def pygame_init():
    """Ensure pygame + its font subsystem are initialized (headless)."""
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    yield


@pytest.fixture
def fonts(pygame_init):
    """The 6-font dict the harness built via `make_fonts()`."""
    return {
        "hud": pygame.font.SysFont(None, C.FONT_HUD),
        "big": pygame.font.SysFont(None, C.FONT_BIG),
        "mid": pygame.font.SysFont(None, C.FONT_MID),
        "small": pygame.font.SysFont(None, C.FONT_SMALL),
        "pickup": pygame.font.SysFont(None, C.FONT_PICKUP),
        "pill": pygame.font.SysFont(None, C.FONT_PILL),
    }


@pytest.fixture
def screen(pygame_init):
    """A real (dummy-driver) display surface for render/layout checks (QA's e2e lane)."""
    return pygame.display.set_mode((C.W, C.H))


@pytest.fixture
def tmp_save_path(tmp_path):
    """Factory for a throwaway save path under pytest's per-test tmp dir."""

    def _make(name="stats.json"):
        return str(tmp_path / name)

    return _make
