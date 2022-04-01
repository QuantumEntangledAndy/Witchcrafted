"""Masterduel modding tool."""
__version__ = "0.1.0"

from . import main, cards, utils, main_panel

__all__ = [main, cards, utils, main_panel]


def app():
    """Poetry app script's entry point."""
    main.main({})
