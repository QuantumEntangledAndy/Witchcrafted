"""Useful utility functions."""

from tkinter import ttk
from enum import Enum


def multiline_strip(text):
    """Strip extra chars from every line."""
    return "\n".join(map(lambda x: x.strip(), text.strip().split("\n")))


class MainFrames(Enum):
    """Enum of the primary app frames."""

    SETUP = 1
    LOADING = 2


class AppFrame(ttk.Frame):
    """A frame that setsup various app related properties."""

    def __init__(self, container):
        """Init the frame."""
        super().__init__(container)
        self.settings = container.settings
        self.app = container.app

    def switch_to(self, main_frame):
        """Switch the app to another primary frame."""
        self.app.main_frame = main_frame
        self.app.switch_frame()
