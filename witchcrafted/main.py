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
import asyncio

from witchcrafted.settings import Settings
from witchcrafted.setup import SetupFrame
from witchcrafted.cards import CardsFrame
from witchcrafted.utils import MainFrames, Async

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
        self.settings = Settings()
        self.app = self

        self.protocol("WM_DELETE_WINDOW", (lambda: Async().async_fire(self.close())))

        if self.settings.debug:
            style = tk.ttk.Style()
            style.theme_use("classic")

        self.app_init()
        self.frame_init()

    def run(self):
        """Run with asyncio."""
        interval = tk._tkinter.getbusywaitinterval() / 1000.0
        self.async_task(self.updater(interval))

        Async().run()

    def async_task(self, task):
        """Run an asyncio task."""
        handle = Async().async_task(task)
        return handle

    def thread_task(self, task):
        """Run a thread task on the pool."""
        handle = Async().thread_task(task)
        return handle

    async def updater(self, interval):
        """Run a pseudo tkinter mainloop."""
        self.tk.willdispatch()
        while True:
            self.update()
            await asyncio.sleep(interval)

    async def close(self):
        """Close the app and stop all asyncio tasks."""
        await Async().shutdown()

        self.destroy()

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
        self.main_frames = {
            MainFrames.SETUP: SetupFrame(self),
            MainFrames.CARDS: CardsFrame(self),
        }

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
    app.run()


if __name__ == "__main__":
    opts = docopt(__doc__)
    main(opts)
