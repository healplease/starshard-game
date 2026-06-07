"""E2E-lane fixtures (test_plan.md §2.4).

The e2e checks build `App`, drive the event loop, run `balance_probe`, or blit. Because
`App.run()` calls `pygame.quit()` at the end, the session-scoped `pygame_init` in the
root conftest isn't enough once a prior test has torn pygame down — every e2e test must
(re)initialize pygame at setup. This mirrors the old harness's `ensure_pygame()` call at
the top of each App-driven check.
"""

import pygame
import pytest


@pytest.fixture(autouse=True)
def ensure_pygame():
    """Re-init pygame + its font subsystem before each e2e test (App.run quits pygame)."""
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    yield
