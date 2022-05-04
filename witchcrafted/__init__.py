"""Masterduel modding tool."""
__version__ = "0.1.0"

from . import main, cards, utils, main_panel, dialogs, project, imagehash

__all__ = [main, cards, utils, main_panel, dialogs, project, imagehash]


def app():
    """Poetry app script's entry point."""
    main.main({})
