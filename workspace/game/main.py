r"""main — the thin entry point (GDD §V2.9, R32/R33).

Parses the headless flags, sets the dummy SDL drivers *before* pygame is imported,
makes the `game` package importable whether launched as a script or with `-m`,
then builds and runs the App (or a v9 headless gate).

  Run:     .\.venv\Scripts\python.exe workspace\game\main.py
  Smoke:   .\.venv\Scripts\python.exe workspace\game\main.py --smoke-test
           (headless, 120 frames, exits 0 — honors SDL_VIDEODRIVER/AUDIODRIVER=dummy)
  Events:  .\.venv\Scripts\python.exe workspace\game\main.py --event-script
           (headless behavioral gate: scripted KEYDOWN → real _handle_events; exit 0/1)
  Balance: .\.venv\Scripts\python.exe workspace\game\main.py --balance-probe [K]
           (AC13 instrument: K scripted runs → median / p95 survival seconds; exit 0)
"""

import os
import sys
import tempfile


def _import_app():
    """Import App + the v9 gate helpers, working both as a script and under `-m`."""
    if __package__:
        from . import app as app_mod
    else:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from game import app as app_mod
    return app_mod


def main():
    argv = sys.argv[1:]
    smoke = "--smoke-test" in argv
    event_script = "--event-script" in argv
    balance = "--balance-probe" in argv

    # Every headless mode runs without a real window/audio device. Must be set
    # BEFORE pygame is imported (importing App pulls pygame in).
    if smoke or event_script or balance:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        # v14 R98/AC85: every headless mode targets a throwaway save file so it never
        # mutates the player's real lifetime stats (the balance probe builds a non-headless
        # App, so the env override — not App's headless flag — is what guarantees this).
        os.environ.setdefault(
            "STARSHARD_SAVE_PATH",
            os.path.join(tempfile.gettempdir(), "starshard_headless_stats.json"),
        )

    app_mod = _import_app()

    if balance:
        # Optional positional run-count after the flag (e.g. `--balance-probe 30`).
        runs = None
        i = argv.index("--balance-probe")
        if i + 1 < len(argv) and argv[i + 1].isdigit():
            runs = int(argv[i + 1])
        app_mod.run_balance_probe(runs)
        sys.exit(0)

    if event_script:
        ok = app_mod.run_event_script_gate()
        sys.exit(0 if ok else 1)

    app_mod.App(smoke=smoke).run()
    sys.exit(0)


if __name__ == "__main__":
    main()
