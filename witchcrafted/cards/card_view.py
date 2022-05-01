"""
The infinite scrolling card view.

Cards are selectable for edit.
"""

import asyncio

from kivy.uix.recycleview import RecycleView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty, NumericProperty

from witchcrafted.cards.card_data import LoadData, CardData


class CardView(GridLayout):
    """The containing card view."""

    card_scroll = ObjectProperty(None)
    filter_box = ObjectProperty(None)

    def reset_panels(self):
        """Reset the panels by resetting their card IDs."""
        self.card_scroll.refresh_from_data()

    def filter_cards(self, text):
        """Filter cards by name."""
        self.card_scroll.filter_cards(text)


class CardScroll(RecycleView):
    """The scrolling cardview."""

    card_grid = ObjectProperty(None)

    num_of_columns = NumericProperty(4)
    num_of_rows = NumericProperty(4)

    def __init__(self, **kwargs):
        """Create data and build."""
        super().__init__(**kwargs)
        self.df = LoadData.main_cards_data()
        self.fill_data(10)

    def filter_cards(self, text):
        """Filter cards by name."""
        df = LoadData.main_cards_data()
        df = df[df["English Name"].str.contains(text)]
        self.df = df
        self.data.clear()
        self.fill_data(10)
        self.reset_panels()

    def scroll_data(self):
        """Fill the grid with more cards."""
        try:
            top = (self.card_grid.top - self.y) / self.card_grid.height
            if self.scroll_y * self.card_grid.height < self.height / 2:
                print("== Before ==")
                print(f"top: {top}")
                print(f"scroll_y: {self.scroll_y}")
                print(f"height: {self.height}")
                print(f"card_grid.height: {self.card_grid.height}")
                self.fill_data(4)
                y = top + self.height
                self.scroll_y = y / self.card_grid.height
                print("== After ==")
                print(f"top: {top}")
                print(f"scroll_y: {self.scroll_y}")
                print(f"height: {self.height}")
                print(f"card_grid.height: {self.card_grid.height}")
        except ZeroDivisionError:
            pass

    def reset_panels(self):
        """Reset the panels by resetting their card IDs."""
        self.refresh_from_data()

    def fill_data(self, num_of_rows):
        """Fill so many rows of data."""
        df = self.df[
            len(self.data) : len(self.data) + num_of_rows * self.num_of_columns  # noqa
        ]

        def map_data(card_row):
            card_data = card_row[1].to_dict()
            return {
                "card_id": card_data["Card ID"],
                "card_image": None,
                "card_name": None,
            }

        data = list(
            map(
                map_data,
                df.iterrows(),
            )
        )
        #  Async().async_fire(self.pre_load(data))
        self.data.extend(data)

    async def pre_load(self, data):
        """Start preloading any data."""
        for datum in data:
            card_id = datum["card_id"]
            if card_id:
                card_data = CardData(card_id)
                await card_data.get_core_image()
                await asyncio.sleep(0.2)
