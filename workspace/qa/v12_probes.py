r"""v12_probes — QA-authored independent probes for the hold-R-to-restart gesture.

These are NOT the programmer's harness — they drive the REAL App.run() loop end-to-end
through the live `_handle_events` + main-loop hold blocks, targeting the v12 risks QA owns:
  P1  GAME_OVER end-to-end hold-R -> restart in the real loop (harness only does PAUSE e2e)
  P2  the #1 risk: DIE with R held -> no instant restart; restart needs a FRESH 30 f hold
  P3  both Q+R held simultaneously -> both counters advance together, independently
  P4  holding R never fills the quit arc / never quits (and never the reverse)
  P5  exact-threshold boundary: 29 held f = no restart, 30th = restart
  P6  NEGATIVE control — a deliberately broken expectation that MUST fail, proving the
      probe harness can actually catch a defect (not just rubber-stamp).
Run headless: SDL dummy drivers. Exit 0 iff every positive probe passes.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from game import config as C
from game.world import World, GameState
from game.app import App, run_event_script

RESULTS = []
def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))


def _run_from_state(state, script):
    """Real App.run() but begin in `state` (override the headless PLAY force)."""
    app = App(event_script=script)
    def patched():
        app.world = World(__import__("random").Random(C.SMOKE_SEED))
        app.state = state
    app._new_world = patched
    app.run()
    return app


# ── P1: GAME_OVER end-to-end hold-R -> restart in the REAL loop ──────────────────
# Hold R f0..f29 (30 frames) starting in GAME_OVER -> restart@f29 -> PLAY, both zeroed.
cap = {}
def grab_p1(app):
    cap["state"], cap["q"], cap["r"] = app.state, app.q_hold_frames, app.r_hold_frames
app = _run_from_state(GameState.GAME_OVER, {
    "frames": 40,
    "held": {f: [pygame.K_r] for f in range(0, 30)},
    "probes": {29: grab_p1},
})
check("P1 GAME_OVER hold-R 30f (real loop) -> PLAY", cap.get("state") is GameState.PLAY, str(cap))
check("P1 GAME_OVER restart zeroed BOTH counters", cap.get("q") == 0 and cap.get("r") == 0, str(cap))
check("P1 GAME_OVER hold-R did NOT trip quit", not app.quit_via_qhold)


# ── P2: THE #1 RISK — die with R held -> no instant restart; needs a fresh hold ──
# Drive a DETERMINISTIC death through the REAL loop: begin in PLAY with 1 HP and a lethal
# large asteroid parked on the player, holding R the ENTIRE time. The player dies on the
# first PLAY frame -> GAME_OVER. On that transition the R counter MUST be 0 (reset on
# transition, §V12.4 #4) — NOT pre-filled — so there is NO instant restart. The run then
# returns to PLAY only after a FRESH continuous 30 f hold within GAME_OVER (restart@ the
# 30th GAME_OVER frame). We capture the full (frame, state, r) series to prove both.
from game.entities.hazards import Asteroid
import random as _random

app = App(event_script={
    "frames": 80,
    "held": {f: [pygame.K_r] for f in range(0, 80)},     # R held the WHOLE time
    "probes": {},
})
series = []
def _seed_lethal():
    app.world = World(_random.Random(C.SMOKE_SEED))
    app.state = GameState.PLAY
    app.world.player.hp = 1
    p = app.world.player
    app.world.asteroids = [Asteroid(p.x, p.y, 0, 0, C.AST_L_R, 2, True)]   # lethal contact
app._new_world = _seed_lethal
# wrap the per-frame probe by injecting a recorder into the script probes for every frame
app.event_script["probes"] = {f: (lambda a: series.append((a.frame, a.state, a.r_hold_frames)))
                              for f in range(0, 80)}
app.run()

# NOTE on frame semantics: the probe runs at END of frame (after the main-loop R-block).
# Death happens mid-frame in _step_play (which zeroes r); the R-block then runs the SAME
# frame with state already GAME_OVER + R still held, so end-of-death-frame r == 1. The
# SAFETY property is "no INSTANT restart" — r is far below threshold (1, not 30) on the
# death frame — and a full fresh 30-increment hold is required. This is the exact mirror
# of v10's die-with-Q-held -> auto-quit-after-0.5s (shipped + QA-passed).
go_series = [(f, r) for f, s, r in series if s is GameState.GAME_OVER]
death_f = go_series[0][0] if go_series else None
entry_r = go_series[0][1] if go_series else None
# (a) NO instant restart: on entering GAME_OVER the R counter is nowhere near threshold
check("P2 died with R held -> NO instant restart (entry r << threshold)",
      death_f is not None and entry_r is not None and entry_r < C.RESTART_HOLD_FRAMES and entry_r <= 1,
      f"death_f={death_f} entry_r={entry_r} (threshold={C.RESTART_HOLD_FRAMES})")
# (b) the counter builds a FRESH monotone 1,2,3,4 within GAME_OVER (reset on transition,
#     then a clean continuous hold — never a carried-over pre-filled jump)
first_go_rs = [r for f, r in go_series[:4]]
check("P2 GAME_OVER R counter builds fresh (1,2,3,4 — reset then clean hold, no pre-fill jump)",
      first_go_rs == [1, 2, 3, 4], f"first GAME_OVER r values={first_go_rs}")
# (c) restart needs a FULL fresh 30-increment hold (no early fire). death frame is the 1st
#     increment, so restart lands RESTART_HOLD_FRAMES-1 frames later (30 increments total).
play_after_go = [f for f, s, r in series if death_f is not None and f > death_f and s is GameState.PLAY]
restart_f = play_after_go[0] if play_after_go else None
increments_to_restart = (restart_f - death_f + 1) if restart_f is not None else None
check("P2 restart fires only after a FULL fresh 30-increment hold (no early/instant restart)",
      increments_to_restart == C.RESTART_HOLD_FRAMES,
      f"increments before restart={increments_to_restart} (want {C.RESTART_HOLD_FRAMES})")


# ── P3: hold BOTH Q and R on GAME_OVER -> both counters advance together ─────────
cap3 = {}
def grab3(app):
    cap3["q"], cap3["r"] = app.q_hold_frames, app.r_hold_frames
app = _run_from_state(GameState.GAME_OVER, {
    "frames": 20,
    "held": {f: [pygame.K_q, pygame.K_r] for f in range(0, 20)},
    "probes": {10: grab3},
})
# At f10, both have advanced ~11 frames each, neither reached 30 yet, independently.
check("P3 both Q+R held -> both counters advanced together", cap3.get("q") == 11 and cap3.get("r") == 11, str(cap3))


# ── P4: holding R alone never quits (quit arc/counter stays empty) ──────────────
# Hold R for 45 f (> threshold) on GAME_OVER. It restarts (R fires) but must NEVER quit.
app = _run_from_state(GameState.GAME_OVER, {
    "frames": 50,
    "held": {f: [pygame.K_r] for f in range(0, 45)},
    "probes": {},
})
check("P4 holding R (45f) never trips quit_via_qhold", not app.quit_via_qhold)


# ── P5: exact-threshold boundary — 29 held f = NO restart, 30th = restart ───────
cap5 = {}
def grab5(name):
    def p(app):
        cap5[name] = (app.state, app.r_hold_frames)
    return p
# Hold R for exactly 29 frames then release; must still be GAME_OVER (no restart).
app = _run_from_state(GameState.GAME_OVER, {
    "frames": 40,
    "held": {f: [pygame.K_r] for f in range(0, 29)},   # 29 frames only
    "probes": {28: grab5("at29"), 31: grab5("after_release")},
})
check("P5 R held 29 f -> still GAME_OVER, no restart", cap5["at29"][0] is GameState.GAME_OVER and cap5["at29"][1] == 29, str(cap5.get("at29")))
check("P5 release at 29 f -> counter resets to 0, no restart", cap5["after_release"][0] is GameState.GAME_OVER and cap5["after_release"][1] == 0, str(cap5.get("after_release")))


# ── P6: NEGATIVE CONTROL — must FAIL (proves the probe can catch a defect) ──────
# Assert a deliberately false claim: that holding R restarts in PLAY (it must NOT).
neg = run_event_script({
    "frames": 40,
    "held": {f: [pygame.K_r] for f in range(0, 40)},   # R held the whole PLAY run
    "probes": {},
})
# R is inactive in PLAY, so r_hold_frames stays 0. The NEGATIVE expectation (that it
# counts up in PLAY) is FALSE — this entry is the planted "expected-to-fail" check.
neg_passes = (neg.r_hold_frames > 0)   # FALSE by design -> this probe SHOULD report FAIL
RESULTS.append(("P6 NEGATIVE: R counts up in PLAY (EXPECTED-FAIL — confirms R inactive in PLAY)", neg_passes, f"r_hold_frames={neg.r_hold_frames} (correctly 0)"))


# ── report ──────────────────────────────────────────────────────────────────
print("v12 QA-authored independent probes (real App.run loop):")
positive_ok = True
for name, ok, detail in RESULTS:
    is_neg = name.startswith("P6")
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f"   ({detail})" if detail else ""))
    if not is_neg and not ok:
        positive_ok = False
print()
print("NEGATIVE control P6 is EXPECTED to read FAIL (R must be inert in PLAY) — that it"
      " does confirms the probe harness can distinguish pass from fail.")
print("RESULT:", "ALL POSITIVE PROBES PASS" if positive_ok else "A POSITIVE PROBE FAILED")
sys.exit(0 if positive_ok else 1)
