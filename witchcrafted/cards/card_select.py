"""Gui that holds are cards for selection."""

from tkinter import ttk

from witchcrafted.utils import AppFrame
from witchcrafted.cards.card_roads import CardRoads


class CardsSelect(AppFrame):
    """The cards frame."""

    def __init__(self, container):
        """
        Init the frame.

        This shows the card selection area and it's scrollbar.
        """
        super().__init__(container)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.card_area = CardRoads(self)
        self.card_area.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.card_area.yview
        )
        self.scrollbar.grid(column=1, row=0, padx=0, pady=0, sticky="ns")
        self.card_area.scrollbar = self.scrollbar
