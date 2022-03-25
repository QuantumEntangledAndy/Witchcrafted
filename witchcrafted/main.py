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
import concurrent.futures

from witchcrafted.settings import Settings
from witchcrafted.setup import SetupFrame
from witchcrafted.cards import CardsFrame
from witchcrafted.utils import MainFrames

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
        self.async_tasks = []
        self.thread_tasks = []
        self.excecutor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

        if self.settings.debug:
            style = tk.ttk.Style()
            style.theme_use("classic")

        self.app_init()

        self.frame_init()

    def run(self):
        """Run with asyncio."""
        self.loop = asyncio.get_event_loop()
        self.protocol("WM_DELETE_WINDOW", (lambda: self.loop.create_task(self.close())))
        self.tasks = []
        interval = tk._tkinter.getbusywaitinterval() / 1000.0
        self.async_task(self.updater(interval))

        self.loop.run_forever()
        self.loop.close()

    def async_task(self, task):
        """Run an asyncio task."""
        handle = self.loop.create_task(task)
        self.async_tasks.append(handle)
        return handle

    def thread_task(self, task):
        """Run an thread task on the pool."""
        handle = self.excecutor.submit(task)
        self.thread_tasks.append(handle)
        return handle

    async def updater(self, interval):
        """Run a pseudo tkinter mainloop."""
        self.tk.willdispatch()
        while True:
            self.update()
            await asyncio.sleep(interval)

    async def close(self):
        """Close the app and stop all asyncio tasks."""
        # Cancel asyncio
        for task in self.async_tasks:
            task.cancel()
        # Await clean exit
        interval = tk._tkinter.getbusywaitinterval() / 1000.0
        while any(map(lambda x: not x.done(), self.async_tasks)):
            await asyncio.sleep(interval)
        self.loop.stop()

        # Cancel all thread pools
        for task in self.thread_tasks:
            task.cancel()

        self.excecutor.shutdown(wait=True, cancel_futures=True)

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
