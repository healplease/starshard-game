r"""app — the Game/App: the state machine, the run loop, and the smoke harness.

This is the orchestration layer (GDD §V2.9): it owns the loop, drives the systems
pipeline in §V2.7 order, calls the view, and hosts the `--smoke-test` branch. It
mutates the World only via systems; it never draws directly (view does that).
"""

import random

import pygame

from . import config as C
from .world import World, GameState
from .input import read_input, smoke_input
from .systems import spawning, physics, combat, buffs, scoring, bombs, encounter
from .view import render, hud


class App:
    def __init__(self, smoke=False):
        self.smoke = smoke
        self.state = GameState.START
        self.frame = 0          # global loop counter (smoke cap + start-screen blink)
        self.bomb_fired = False  # X key-down edge this frame (v6, GDD §V6.4)

    # ── setup ────────────────────────────────────────────────────────────────
    def _init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((C.W, C.H))
        pygame.display.set_caption("Starshard")
        self.clock = pygame.time.Clock()
        fonts = {
            "hud": pygame.font.SysFont(None, C.FONT_HUD),
            "big": pygame.font.SysFont(None, C.FONT_BIG),
            "mid": pygame.font.SysFont(None, C.FONT_MID),
            "small": pygame.font.SysFont(None, C.FONT_SMALL),
            "pickup": pygame.font.SysFont(None, C.FONT_PICKUP),
            "pill": pygame.font.SysFont(None, C.FONT_PILL),
        }
        render.set_fonts(fonts)
        hud.set_fonts(fonts)

    def _new_world(self):
        rng = random.Random(C.SMOKE_SEED) if self.smoke else random.Random()
        self.world = World(rng)
        if self.smoke:
            # Force PLAY immediately + seed hazards for collision coverage (GDD §11).
            self.state = GameState.PLAY
            spawning.seed_smoke(self.world)

    # ── the systems pipeline for one PLAY frame (§V2.7 order) ──────────────────
    def _step_play(self, inp):
        w = self.world
        physics.update_play(w, inp)     # move + fire + despawn
        encounter.update(w)             # v7: boss trigger + entrance/oscillation/moveset (§V7.3)
        bombs.update(w, self.bomb_fired)  # v6: flush+flash BEFORE the damage step (§V6.3)
        combat.resolve(w)               # collisions, collect, damage + boss hits/defeat (steps 1–4)
        spawning.update(w)              # ramped asteroid/enemy spawns + bonus drip (frozen while boss)
        buffs.tick(w)                   # tick timers, expiry→revert (step 5)
        w.frame += 1
        scoring.survival_tick(w)        # +1/s survival bonus (×mult)
        if w.player.hp <= 0:            # step 6 → GAME_OVER
            w.best = max(w.best, w.score)
            self.state = GameState.GAME_OVER

    # ── event handling (discrete transitions: quit / start / restart) ──────────
    def _handle_events(self):
        self.bomb_fired = False                      # reset the per-frame X edge (v6)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.state is GameState.START:
                    self.state = GameState.PLAY
                elif self.state is GameState.GAME_OVER and event.key == pygame.K_r:
                    self.world.reset_run()           # R13/R31 — no leak into the new run
                    self.state = GameState.PLAY
                elif self.state is GameState.PLAY and event.key == pygame.K_x:
                    self.bomb_fired = True            # X key-down edge → bomb (§V6.4)
        return True

    # ── render one frame for the current state ─────────────────────────────────
    def _draw(self):
        self.screen.fill(C.BG)
        render.draw_starfield(self.screen, self.world)
        if self.state is GameState.START:
            hud.draw_start(self.screen, self.frame)
        elif self.state is GameState.PLAY:
            render.draw_world(self.screen, self.world)
            hud.draw_hud(self.screen, self.world)
            hud.draw_flash(self.screen, self.world)   # v6 flash: above HUD, PLAY-only (§V6.6)
        else:  # GAME_OVER — frozen field + dim + text
            render.draw_world(self.screen, self.world)
            hud.draw_hud(self.screen, self.world)
            hud.draw_gameover(self.screen, self.world)
        pygame.display.flip()

    # ── main loop ──────────────────────────────────────────────────────────────
    def run(self):
        self._init_pygame()
        self._new_world()
        running = True
        while running:
            if self.smoke:
                # Seed the guaranteed-lifecycle Rapid pickup a couple of frames in
                # so spawn→collect→apply→expire all run before the 120-f cap (§V2.5).
                if self.frame == C.SMOKE_SEED_FRAME:
                    spawning.seed_smoke_bonus(self.world)
                # Seed a GREEN pellet that bursts ~frame 16 → 3 RED children update
                # to f120: exercises the full split lifecycle headlessly (§V5.6/AC27).
                if self.frame == C.SMOKE_SPLIT_FRAME:
                    spawning.seed_smoke_split(self.world)
                # Scripted X key-down ~f20 (after the ~f16 split) → one flush clears
                # the seeded enemy + asteroids + the 3 red split children, charge 2→1,
                # flash f20→~f38 (GDD §V6.10 / AC30/AC32/AC33).
                self.bomb_fired = (self.frame == C.SMOKE_BOMB_FRAME)
                # v7 boss seed (GDD §V7.15), strictly AFTER the v5 (f16) + v6 (f20)
                # seeds: a token target @f38 so the FREE arrival clear @f40 has
                # something to remove (charge stays at 1 → AC40), then the boss @f40
                # runs a compressed entrance + moveset (step 1 + yellow→12-red split)
                # inside the 120-f budget (AC41/AC42/AC49/AC50/AC51).
                if self.frame == C.SMOKE_BOSS_PRESEED_FRAME:
                    spawning.seed_smoke_boss_target(self.world)
                if self.frame == C.SMOKE_BOSS_FRAME:
                    encounter.seed_smoke_boss(self.world)
                inp = smoke_input(self.frame)
                # Drain the event queue so the OS/dummy driver stays happy.
                pygame.event.pump()
            else:
                running = self._handle_events()
                inp = read_input()

            physics.update_starfield(self.world)     # cosmetic, runs in every state
            if self.state is GameState.PLAY:
                self._step_play(inp)

            self._draw()
            self.clock.tick(C.FPS)

            self.frame += 1
            if self.smoke and self.frame >= C.SMOKE_FRAMES:
                running = False

        pygame.quit()
