"""E2E lane — STATS nav + run/flush accounting (AC82r runs, AC81 flush, nav).

Drives the real `App._handle_events` / `_restart_hold_step` / `_step_play` and asserts
the run-count and save-flush side effects, so these are e2e (App + save side effects).
"""

import os

import pygame
from game import config as C
from game import save
from game.app import App
from game.entities.hazards import Asteroid
from game.input import InputState
from game.world import GameState


def test_ac82r_runs_counts_per_run_begun(fresh_world):
    """AC82r: runs counts once per run begun (initial start + each restart), not on resume."""
    app = App()
    app.world = fresh_world()
    app.store = save.Store()
    app.world.store = app.store
    app.state = GameState.START
    # initial START → PLAY (a non-Q/non-Tab key) counts one run
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
    app._handle_events()
    assert app.state is GameState.PLAY and app.store.runs == 1, "initial run begin not counted"
    # Esc→PAUSE then Esc→PLAY (resume) must NOT count a new run
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    app._handle_events()
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    app._handle_events()
    assert app.state is GameState.PLAY and app.store.runs == 1, "Esc-resume wrongly counted a run"
    # a hold-R restart counts a new run
    app.state = GameState.PAUSE
    app.r_hold_frames = C.RESTART_HOLD_FRAMES - 1
    app.event_script = {"held": {app.frame: [pygame.K_r]}}
    app._restart_hold_step()
    assert app.state is GameState.PLAY and app.store.runs == 2, "hold-R restart did not count a run"


def test_ac81_flush_only_on_gameover_and_quit(fresh_world, tmp_save_path):
    """AC81: flush only on GAME_OVER + hold-Q quit — not on restart."""
    path = tmp_save_path("flush.json")
    # A hold-R restart must NOT write the file.
    app = App(save_path=path)
    app.world = fresh_world()
    app.store = save.load(path)
    app.world.store = app.store
    app.state = GameState.PAUSE
    app.r_hold_frames = C.RESTART_HOLD_FRAMES - 1
    app.event_script = {"held": {app.frame: [pygame.K_r]}}
    app._restart_hold_step()
    assert app.state is GameState.PLAY and not os.path.exists(path), (
        "restart wrongly flushed the file"
    )
    # GAME_OVER flushes (writes the file).
    app.world.player.hp = 1
    p = app.world.player
    app.world.asteroids = [Asteroid(p.x, p.y, 0, 0, C.AST_L_R, 2, True)]
    app._step_play(InputState(0, 0, False))
    assert app.state is GameState.GAME_OVER and os.path.exists(path), (
        "GAME_OVER did not flush the file"
    )


def test_nav_stats_tab_esc(fresh_world):
    """nav: Tab opens STATS from START; Tab/Esc return; other keys inert in STATS."""
    app = App()
    app.world = fresh_world()
    app.store = save.Store()
    app.world.store = app.store
    app.state = GameState.START
    # Tab on START → STATS (and does NOT start a run)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB))
    app._handle_events()
    assert app.state is GameState.STATS and app.store.runs == 0, (
        "Tab did not open STATS (or wrongly began a run)"
    )
    # a non-Tab/Esc key in STATS is inert (no start, no quit)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
    app._handle_events()
    assert app.state is GameState.STATS, "a stray key left STATS"
    # Tab toggles back to START
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB))
    app._handle_events()
    assert app.state is GameState.START, "Tab did not toggle STATS→START"
    # Esc also backs out STATS→START
    app.state = GameState.STATS
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    app._handle_events()
    assert app.state is GameState.START, "Esc did not back STATS→START"
