"""Primary GUI for the card frame."""

from witchcrafted.utils import AppFrame
from witchcrafted.cards.card_select import CardsSelect
from witchcrafted.cards.card_view import CardView


class CardsFrame(AppFrame):
    """The cards frame."""

    def __init__(self, container):
        """Init the frame."""
        super().__init__(container)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.main_frames = {"CardSelect": CardsSelect(self), "CardView": CardView(self)}
        self.main_frame = "CardSelect"

        for frame in self.main_frames.values():
            frame.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")

        self.switch_frame()

    def reset(self):
        """Set up this frame."""
        self.main_frame = "CardSelect"
        self.switch_frame()

    def switch_frame(self):
        """Switch to the main_frame."""
        self.main_frames[self.main_frame].reset()
        self.main_frames[self.main_frame].tkraise()

    def view_select(self):
        """Switch to the selection screen."""
        self.main_frame = "CardSelect"
        self.switch_frame()

    def view_card(self, card_data, card_image):
        """Switch to the view cards frame."""
        self.main_frames["CardView"].card_data = card_data
        self.main_frames["CardView"].image = card_image
        self.main_frame = "CardView"
        self.switch_frame()
