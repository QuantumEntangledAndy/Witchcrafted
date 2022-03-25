"""Masterduel modding tool."""
__version__ = "0.1.0"

from . import main, cards, settings, setup, utils

__all__ = [main, cards, settings, setup, utils]


def app():
    """Poetry app script's entry point."""
    main.main({})
