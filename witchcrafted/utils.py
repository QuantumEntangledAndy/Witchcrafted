"""Useful utility functions."""

from tkinter import ttk
from enum import Enum
from itertools import zip_longest
from random import randint, choice


def grouper(iterable, n, *, incomplete="fill", fillvalue=None):
    """Collect data into non-overlapping fixed-length chunks or blocks."""
    # grouper('ABCDEFG', 3, fillvalue='x') --> ABC DEF Gxx
    # grouper('ABCDEFG', 3, incomplete='strict') --> ABC DEF ValueError
    # grouper('ABCDEFG', 3, incomplete='ignore') --> ABC DEF
    args = [iter(iterable)] * n
    if incomplete == "fill":
        return zip_longest(*args, fillvalue=fillvalue)
    if incomplete == "strict":
        return zip(*args, strict=True)
    if incomplete == "ignore":
        return zip(*args)
    else:
        raise ValueError("Expected fill, strict, or ignore")


def multiline_strip(text):
    """Strip extra chars from every line."""
    return "\n".join(map(lambda x: x.strip(), text.strip().split("\n")))


def random_color():
    """Generate a random color string."""
    hex_string = "0123456789abcdef"
    return "#" + "".join([choice(hex_string) for x in range(6)])


def clamp(num, min_value, max_value):
    """Clamp a value."""
    return max(min(num, max_value), min_value)


class MainFrames(Enum):
    """Enum of the primary app frames."""

    SETUP = 1
    CARDS = 2


class AppFrame(ttk.Frame):
    """A frame that setsup various app related properties."""

    def __init__(self, container, *args, **kwargs):
        """Init the frame."""
        super().__init__(container, *args, **kwargs)
        self.settings = container.settings
        self.app = container.app
        self.parent = container

        # for col in range(0, 20):
        #     self.columnconfigure(col, weight=1)
        #     self.rowconfigure(col, weight=1)

        if self.settings.debug:
            s = ttk.Style()
            style_name = f"Frame{randint(0, 65535)}.TFrame"
            s.configure(style_name, background=random_color())
            self.configure(style=style_name)

        self.update()

    def switch_to(self, main_frame):
        """Switch the app to another primary frame."""
        self.app.main_frame = main_frame
        self.app.switch_frame()

    def reset(self):
        """Reset the frame."""
        # Should be overloaded
