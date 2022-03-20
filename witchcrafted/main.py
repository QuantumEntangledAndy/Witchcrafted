"""
Masterduel modding tool.

Usage:
    masterduel [options]

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from docopt import docopt
import ctypes
from witchcrafted.settings import Settings
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

        (screen_width, screen_height) = self.get_display_size()

        # configure the root window
        self.title("Witchcrafted")
        self.geometry(f"{screen_width}x{screen_height}")

        # label
        self.label = ttk.Label(self, text="Hello, Tkinter!")
        self.label.pack()

        # button
        self.button = ttk.Button(self, text="Click Me")
        self.button["command"] = self.button_clicked
        self.button.pack()

    def button_clicked(self):
        """Show a message."""
        showinfo(title="Information", message="Hello, Tkinter!")

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
