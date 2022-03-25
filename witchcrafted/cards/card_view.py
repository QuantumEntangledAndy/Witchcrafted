"""Card view and edit gui."""

from tkinter import ttk
from tkinter import filedialog as fd
from PIL import ImageTk, Image

from witchcrafted.utils import AppFrame


class CardView(AppFrame):
    """The cards frame."""

    def __init__(self, container):
        """Init the frame."""
        super().__init__(container)
        self.card_data = None
        self.image = None

        self.reset()

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        ttk.Button(self, text="Import", command=(lambda: self.import_image())).grid(
            column=0, row=0
        )
        ttk.Button(self, text="Export", command=(lambda: self.export_image())).grid(
            column=1, row=0
        )
        ttk.Button(
            self, text="Close", command=(lambda: self.parent.view_select())
        ).grid(column=2, row=0, sticky="e")

        self.image_label = ttk.Label(self)
        self.image_label.grid(column=0, row=1, columnspan=3)

    def export_image(self):
        """Export the image."""
        card_id = self.card_data["Card ID"]
        file_name = fd.asksaveasfilename(
            initialdir=self.settings.out_dir,
            initialfile=f"{card_id}.bmp",
            filetypes=(("Bitmap", "*.bmp"), ("PNG", "*.png")),
            defaultextension=".bmp",
        )
        if file_name is not None and self.image is not None:
            self.image.save(file_name)

    def import_image(self):
        """Export the image."""
        card_id = self.card_data["Card ID"]
        file_name = fd.askopenfilename(
            initialdir=self.settings.out_dir,
            initialfile=f"{card_id}.bmp",
            filetypes=(("Bitmap", "*.bmp"), ("PNG", "*.png")),
            defaultextension=".bmp",
        )
        if file_name is not None and self.image is not None:
            imported_image = Image.open(file_name)
            (imported_width, imported_height) = imported_image.size
            (orig_width, orig_height) = self.image.size
            imported_image.resize((orig_width, orig_height), Image.BICUBIC)
            self.image = imported_image
            self.reset()

    def reset(self):
        """Reset the card view."""
        if self.card_data is not None:
            if self.image is not None:
                thumbnail = self.image
                self.thumbnail = ImageTk.PhotoImage(thumbnail)
                self.image_label.configure(image=self.thumbnail)
