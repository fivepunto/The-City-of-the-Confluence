"""pytest configuration for the pure-Python engine suite.

The game's rules engine (game/core/) and data registry (game/data/) import with
zero Ren'Py dependency, so they run headlessly. This puts game/ on sys.path so
`import data` and `from core import ...` resolve the same way they do in the
Ren'Py boot (game/script.rpy).
"""
import os
import sys

_GAME = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game")
if _GAME not in sys.path:
    sys.path.insert(0, _GAME)
