"""Frame for the init setup."""
import tkinter as tk
from tkinter import ttk
from witchcrafted.utils import multiline_strip, AppFrame, MainFrames


class InfoFrame(AppFrame):
    """The info frame."""

    def __init__(self, container):
        """Init the frame."""
        super().__init__(container)

        row = 0
        # Desc
        ttk.Label(
            self,
            text=multiline_strip(
                """Welcome!

                  First we need to know where various directories are:
                  1. Game Data Directory: The game folder which contains the 0000 folder try looking in steam apps
                  2. The Mods Direcotry: The folder where you save all your possible mods too
                  3. The Output Directory: The place where the modified files are saved to
            """  # noqa
            ),
        ).grid(column=0, row=row, columnspan=2, sticky=tk.W + tk.E)


class FoldersFrame(AppFrame):
    """The folders frame."""

    def __init__(self, container):
        """Init the frame."""
        super().__init__(container)

        row = 0
        # Game dir
        ttk.Label(self, text="Game Data Directory:").grid(
            column=0, row=row, sticky=tk.W
        )
        self.data = ttk.Entry(self, width=30)
        self.data.focus()
        self.data.grid(column=1, row=row, sticky=tk.W)
        row += 1
        # Mod dir
        ttk.Label(self, text="Mods Directory:").grid(column=0, row=row, sticky=tk.W)
        self.mods = ttk.Entry(self, width=30)
        self.mods.grid(column=1, row=row, sticky=tk.W)
        row += 1
        # Output dir
        ttk.Label(self, text="Output Directory:").grid(column=0, row=row, sticky=tk.W)
        self.output = ttk.Entry(self, width=30)
        self.output.grid(column=1, row=row, sticky=tk.W)
        row += 1

    def reset(self):
        """Reset the frame before showing."""
        self.data.focus()

        self.data.delete(0, "end")
        self.data.insert(0, self.settings.source_dir)

        self.mods.delete(0, "end")
        self.mods.insert(0, self.settings.mods_dir)

        self.output.delete(0, "end")
        self.output.insert(0, self.settings.out_dir)


class ButtonsFrame(AppFrame):
    """The Ok buttons."""

    def __init__(self, container):
        """Init the frame."""
        super().__init__(container)

        ttk.Button(self, text="Ok", command=self.ok_pressed).grid(
            column=0, row=0, sticky=tk.E
        )

    def ok_pressed(self):
        """Act on pressing ok."""
        self.settings.setup = True
        self.switch_to(MainFrames.CARDS)


class SetupFrame(AppFrame):
    """The initial setup frame."""

    def __init__(self, container):
        """Init the frame."""
        super().__init__(container)

        InfoFrame(self).grid(column=0, row=0, sticky=tk.W)

        self.folders = FoldersFrame(self)
        self.folders.grid(column=0, row=1, sticky=tk.W)
        ButtonsFrame(self).grid(column=0, row=2, sticky=tk.W)

    def reset(self):
        """Reset the frame before showing."""
        self.folders.reset()
