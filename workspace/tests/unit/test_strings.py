"""Unit lane — UI copy + string-width fit (AC37, AC47w, AC59, AC65).

String-widths (AC47w) is unit per §2.4: it uses `font.size()` width math only — no blit.
"""

from game import config as C


def test_ac37_controls_copy():
    """AC37: controls copy teaches the Z-fire / X-bomb remap."""
    assert "Z = fire" in C.CONTROLS_1, "CONTROLS_1 missing 'Z = fire'"
    assert "X = bomb" in C.CONTROLS_1, "CONTROLS_1 missing 'X = bomb'"


def test_ac59_pause_quit_copy():
    """AC59: controls copy reflects Esc=Pause / hold-Q=Quit; no stale Esc-quit."""
    assert "Esc" in C.CONTROLS_2 and "Pause" in C.CONTROLS_2, "CONTROLS_2 missing Esc/Pause"
    assert "Esc" not in C.GAMEOVER_KEYS, "GAMEOVER_KEYS still shows a stale Esc hint"


def test_ac65_quit_hint_copy():
    """AC65: START shows the quit hint; GAMEOVER_KEYS adds it with no stale 'Esc'."""
    assert C.START_QUIT_HINT == "Hold Q  Quit", "START quit-hint string changed unexpectedly"
    assert "Q" in C.START_QUIT_HINT and "Quit" in C.START_QUIT_HINT, (
        "START hint does not teach Q-quit"
    )
    assert "Quit" in C.GAMEOVER_KEYS and "Q" in C.GAMEOVER_KEYS, (
        "GAMEOVER_KEYS missing the quit hint"
    )
    assert "Restart" in C.GAMEOVER_KEYS, "GAMEOVER_KEYS lost its Restart hint"
    assert "Esc" not in C.GAMEOVER_KEYS, "GAMEOVER_KEYS reintroduced a stale Esc hint"
    assert "Esc" not in C.START_QUIT_HINT, "START quit-hint wrongly mentions Esc"


def test_ac47w_string_widths(fonts):
    """AC47w: every UI literal fits its panel and all glyphs exist in the font."""
    budgets = [
        ("TITLE", C.TITLE, "big", C.W),
        ("PITCH", C.PITCH, "small", C.W),
        ("CONTROLS_1", C.CONTROLS_1, "small", C.W),
        ("CONTROLS_2", C.CONTROLS_2, "small", C.W),
        ("START_PROMPT", C.START_PROMPT, "small", C.W),
        ("START_QUIT_HINT", C.START_QUIT_HINT, "small", C.W),
        ("GAMEOVER_TITLE", C.GAMEOVER_TITLE, "big", C.W),
        ("GAMEOVER_KEYS", C.GAMEOVER_KEYS, "small", C.W),
        ("PAUSE_TITLE", C.PAUSE_TITLE, "big", C.W),
        ("PAUSE_HINT_RESUME", C.PAUSE_HINT_RESUME, "small", C.W),
        ("PAUSE_HINT_QUIT", C.PAUSE_HINT_QUIT, "small", C.W),
        ("PAUSE_HINT_RESTART", C.PAUSE_HINT_RESTART, "small", C.W),
        (
            "BOSS_LABEL_TEXT",
            C.BOSS_LABEL_TEXT,
            "hud",
            C.BOSS_BAR[2],
        ),  # must fit the boss bar (AC47)
        ("BOSS_WARN_1", C.BOSS_WARN_1, "mid", C.W),
        ("BOSS_WARN_2", C.BOSS_WARN_2, "small", C.W),
        ("BOSS_DEFEAT_TEXT", C.BOSS_DEFEAT_TEXT, "mid", C.W),
        ("BOMB_PICKUP_POPUP_TEXT", C.BOMB_PICKUP_POPUP_TEXT, "small", C.W),
        ("STATS_TITLE", C.STATS_TITLE, "big", C.STATS_BAND_R - C.STATS_BAND_L),
        ("STATS_LBL_HIGHSCORE", C.STATS_LBL_HIGHSCORE, "mid", 260),
        ("STATS_LBL_RUNS", C.STATS_LBL_RUNS, "mid", 260),
        ("STATS_LBL_ENEMIES", C.STATS_LBL_ENEMIES, "mid", 260),
        ("STATS_LBL_ASTEROIDS", C.STATS_LBL_ASTEROIDS, "mid", 260),
        ("STATS_LBL_BOSSES", C.STATS_LBL_BOSSES, "mid", 260),
        ("STATS_HINT", C.STATS_HINT, "small", C.W),
        ("START_STATS_HINT", C.START_STATS_HINT, "small", C.W),
    ]
    for name, text, font_key, budget in budgets:
        font = fonts[font_key]
        w_px = font.size(text)[0]
        assert w_px <= budget, f"{name} too wide: {w_px}px > {budget}px"
        assert all(m is not None for m in font.metrics(text)), (
            f"{name} has a glyph missing from the font"
        )
