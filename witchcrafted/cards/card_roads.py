"""Gui for the row of individual gui cards."""

from witchcrafted.utils import AppFrame, clamp, Async
from witchcrafted.cards.card_board import CardBoard
from witchcrafted.cards.card_data import LoadData


class CardRoads(AppFrame):
    """
    All card rows.

    This it the part that shows all the cards.
    """

    PADDING = 1

    @property
    def card_number(self):
        """Get the card that is shown in the top left."""
        return getattr(self, "_card_number", 0.0)

    @card_number.setter
    def card_number(self, card_number):
        """
        Set the card that is shown in the top left.

        Also update the scrolbar and the view.
        """
        self._card_number = card_number
        self.update_scrollbar_limits()
        update_number = getattr(self, "_last_update", 0) + 1
        self._last_update = update_number
        self.next_update = self._frame_number + 10
        self.delayed_update_card_frames()

    @property
    def scrollbar(self):
        """Get the scrollbar."""
        return getattr(self, "_scrollbar", None)

    @scrollbar.setter
    def scrollbar(self, value):
        """Set the scrollbar and update the scrollbar."""
        self._scrollbar = value
        self.update_scrollbar_limits()

    def __init__(self, container):
        """Init the frame."""
        super().__init__(container)
        self.card_list = LoadData.main_cards_ids()

        self.card_frames = {}
        self._frame_number = 0

        # This is a property everything should be ready before setting it
        self.card_number = 0.0

    def set_card_number(self, value):
        """Set the card number."""
        self.card_number = value

    def yview(self, *args):
        """Scroll bar update."""
        if args[0] == "moveto":
            max_cards = len(self.card_list)
            card_number = clamp(float(args[1]), 0.0, 1.0) * max_cards
            self.card_number = card_number
        elif args[0] == "scroll":
            amount = float(args[1])
            kind = args[2]
            if kind == "units":  # Up one row
                max_cards = len(self.card_list)
                card_layout = self.card_layout()
                delta = amount * card_layout[0]
                self.card_number = self.card_number + delta
        else:
            print(args)

    def update_scrollbar_limits(self):
        """Set the scrollbar limits."""
        if self.scrollbar is not None:
            card_number = self.card_number
            max_cards = len(self.card_list)
            lower_limit = card_number / max_cards
            card_layout = self.card_layout()
            upper_limit = min(
                (card_number + card_layout[0] * card_layout[1]) / max_cards, max_cards
            )

            self.scrollbar.set(lower_limit, upper_limit)

    def card_layout(self):
        """Get the number of cards that can be held in the current frame."""
        return (4, 4)

    def delayed_update_card_frames(self):
        """Delay update."""
        Async().async_task(self.update_card_frames())

    async def update_card_frames(self):
        """Update rows of cards."""
        card_number = self.card_number

        first_card_id = int(card_number)
        card_layout = self.card_layout()
        num_visible_cards = card_layout[0] * card_layout[1]
        max_cards = len(self.card_list)

        last_card_id = min(first_card_id + num_visible_cards, max_cards) + 1

        padding = num_visible_cards * 2

        start = int(max((first_card_id - padding), 0))
        end = int(min((last_card_id + padding) + 1, max_cards))
        cards = self.card_list[start:end]

        for idx, card_data in cards.iterrows():
            if idx not in self.card_frames:
                self.card_frames[idx] = CardBoard(self, card_data.to_dict())

        card_frame_width = 1.0 / card_layout[0]
        card_frame_height = 1.0 / card_layout[1]

        del_these = []
        for card_frame_id in self.card_frames:
            if card_frame_id < (first_card_id - padding) or card_frame_id > (
                last_card_id + padding
            ):
                del_these.append(card_frame_id)
            card_frame = self.card_frames[card_frame_id]
            row_first_card = int(card_frame_id / card_layout[0]) * card_layout[0]
            pos_y = (row_first_card - card_number) / card_layout[0] / card_layout[1]
            pos_x = clamp((card_frame_id - row_first_card) / card_layout[0], 0.0, 1.0)
            card_frame.place(
                relx=pos_x,
                rely=pos_y,
                relheight=card_frame_height,
                relwidth=card_frame_width,
                anchor="nw",
            )

        for del_this in del_these:
            self.card_frames[del_this].place_forget()
            self.card_frames[del_this].destroy()
            del self.card_frames[del_this]
