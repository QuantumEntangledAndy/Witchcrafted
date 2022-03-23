"""
Scrollable frame.

source: https://blog.teclado.com/tkinter-scrollable-frames/
"""

import tkinter as tk
from tkinter import ttk
from witchcrafted.utils import AppFrame


class ScrollableFrame(AppFrame):
    """A scrollable frame."""

    def __init__(self, container, *args, **kwargs):
        """Init the frame."""
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        canvas.app = self.app
        canvas.settings = self.settings

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = AppFrame(canvas)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
