"""
Masterduel modding tool.

Usage:
    masterduel [options]

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import tkinter as tk
from docopt import docopt
import ctypes
from witchcrafted.settings import Settings
from witchcrafted.setup import SetupFrame
from witchcrafted.cards import CardsFrame
from witchcrafted.utils import MainFrames

from pathlib import Path

try:  # Windows 8.1 and later
    ctypes.windll.shcore.SetProcesspiAwareness(2)
except Exception:
    pass
try:  # Before Windows 8.1
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:  # Windows 8 or before
    pass


class App(tk.Tk):
    """Main GUI app."""

    def __init__(self, opts):
        """Init the app."""
        super().__init__()
        self.settings = Settings(Path("./settings.yaml"))
        self.app = self

        if self.settings.debug:
            style = tk.ttk.Style()
            style.theme_use("classic")

        self.app_init()

        self.frame_init()

    def app_init(self):
        """Initialise the settings of the app."""
        (screen_width, screen_height) = self.get_display_size()

        # configure the root window
        self.title("Witchcrafted")
        self.geometry(f"{screen_width}x{screen_height}")

    def frame_init(self):
        """Create the various primary app frames."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.main_frames = {MainFrames.SETUP: SetupFrame(self)}
        self.main_frames = {MainFrames.CARDS: CardsFrame(self)}

        for frame in self.main_frames.values():
            frame.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")

        if not self.settings.setup:
            self.main_frame = MainFrames.SETUP
        else:
            self.main_frame = MainFrames.CARDS

        self.switch_frame()

    def switch_frame(self):
        """Switch to the current frame."""
        self.main_frames[self.main_frame].reset()
        self.main_frames[self.main_frame].tkraise()

    def get_display_size(self):
        """Get the current display size."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        return screen_width, screen_height


def main(opts):
    """Run the program."""
    app = App(opts)
    app.mainloop()


if __name__ == "__main__":
    opts = docopt(__doc__)
    main(opts)
