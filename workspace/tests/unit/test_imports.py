"""Unit lane — package import surface (AC21). Ported from harness."""

import importlib

from game import app as app_mod


def test_ac21_package_imports_cleanly():
    """AC21: package imports cleanly (script + -m entry points)."""
    for mod in (
        "game.main",
        "game.app",
        "game.config",
        "game.world",
        "game.systems.combat",
        "game.view.render",
    ):
        importlib.import_module(mod)
    assert callable(app_mod.App), "App is not importable/callable"
    assert hasattr(importlib.import_module("game.main"), "main"), "main() entry missing"
