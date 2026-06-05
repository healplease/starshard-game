r"""main — the thin entry point (GDD §V2.9, R32/R33).

Parses `--smoke-test`, sets the dummy SDL drivers *before* pygame is imported,
makes the `game` package importable whether launched as a script or with `-m`,
then builds and runs the App.

  Run:   .\.venv\Scripts\python.exe workspace\game\main.py
  Smoke: .\.venv\Scripts\python.exe workspace\game\main.py --smoke-test
         (headless, 120 frames, exits 0 — honors SDL_VIDEODRIVER/AUDIODRIVER=dummy)
"""

import os
import sys


def main():
    smoke = "--smoke-test" in sys.argv
    if smoke:
        # Must be set BEFORE pygame is imported (App import pulls pygame in).
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"

    # Work both as `python workspace/game/main.py` (script: no package context)
    # and as `python -m game.main` (run inside the package).
    if __package__:
        from .app import App
    else:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from game.app import App

    App(smoke=smoke).run()
    sys.exit(0)


if __name__ == "__main__":
    main()
