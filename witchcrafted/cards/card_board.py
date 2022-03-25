"""The gui of a single card in the select menu."""

from tkinter import ttk
from PIL import ImageTk, Image

from witchcrafted.utils import AppFrame
from witchcrafted.cards.card_data import AsyncLoadData


class CardBoard(AppFrame):
    """A card frame."""

    def __init__(self, container, card_data):
        """Init a card."""
        super().__init__(container)

        self.card_data = card_data
        if self.card_data is not None:
            card_id = self.card_data["Card ID"]
            ttk.Label(self, text=f"{card_id}").place(relx=0.0, rely=0.0, anchor="nw")
            self.load_image()

    def load_image(self):
        """Load an image."""
        thread = AsyncLoadData(self.settings.source_dir, self.card_data)
        thread.start()
        self.monitor(thread)

    def monitor(self, thread):
        """Monitor another thread for finish."""
        width = self.winfo_width()
        height = self.winfo_height()
        if thread.is_alive() or width <= 1 or height <= 1:
            # check the thread every 100ms
            self.after(100, lambda: self.monitor(thread))
            self.update()
        else:
            image = thread.image
            self.image = image
            target_size = min(width, height)

            im_width, im_height = image.size
            if im_width > im_height:
                scale = target_size / im_width
            else:
                scale = target_size / im_height

            new_width = int(im_width * scale)
            new_height = int(im_height * scale)

            thumbnail = image.resize((new_width, new_height), Image.BICUBIC)

            self.thumbnail = ImageTk.PhotoImage(thumbnail)

            if image is not None:
                ttk.Button(
                    self, image=self.thumbnail, command=lambda: self.pick()
                ).place(relx=0.5, rely=0.5, anchor="center")

    def pick(self):
        """Act on picking this card."""
        self.parent.parent.parent.view_card(self.card_data, self.image)
