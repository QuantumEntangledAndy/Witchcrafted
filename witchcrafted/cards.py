"""Infinite scrolling list of cards."""

from tkinter import ttk
from witchcrafted.utils import AppFrame, clamp
import pandas as pd
from threading import Thread
import UnityPy
from pathlib import Path
from PIL import ImageTk, Image


class AsyncLoadPicture(Thread):
    """Async load picture from the game files."""

    def __init__(self, root_path, card_data):
        """Init with the card data."""
        super().__init__()
        self.image = None
        self.card_data = card_data
        self.root_path = Path(root_path)

    def run(self):
        """Run this code on the thread."""
        top_level_folder = self.card_data["Folder Name"]
        tcg_file_name = self.card_data["File, TCG"]
        tcg_file_prefix = tcg_file_name[0:2]
        file_path_tcg = self.root_path.joinpath(
            top_level_folder, tcg_file_prefix, tcg_file_name
        )
        ocg_file_name = self.card_data["File, OCG"]
        ocg_file_prefix = ocg_file_name[0:2]
        file_path_ocg = self.root_path.joinpath(
            top_level_folder, ocg_file_prefix, ocg_file_name
        )

        if file_path_tcg.exists():
            file_path = file_path_tcg
        elif file_path_ocg.exists():
            file_path = file_path_ocg
        else:
            return
        env = UnityPy.load(f"{file_path}")
        for obj in env.objects:
            if obj.type.name in ["Texture2D"]:
                data = obj.read()
                path = obj.container
                if path is None:
                    path = data.name
                resouce_name = Path(path).stem
                card_id = str(self.card_data["Card ID"])
                if resouce_name == card_id:
                    self.image = data.image


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
        thread = AsyncLoadPicture(self.settings.source_dir, self.card_data)
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
                ttk.Label(self, image=self.thumbnail).place(
                    relx=0.5, rely=0.5, anchor="center"
                )


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
        df = pd.read_csv("assets/card_list.csv")
        self.card_list = df[(df["Folder Name"] == "0000")]
        self.card_list.reset_index(inplace=True)
        self.card_frames = {}
        self._frame_number = 0
        self.cycle()

        # This is a property everything should be ready before setting it
        self.card_number = 0.0
        self.update_scrollbar_limits()

    def cycle(self):
        """Update the cycle number used for delayed-postponable updates."""
        self._frame_number += 1
        self.after(10, self.cycle)

    def set_card_number(self, value):
        """Set the card number."""
        self.card_number = value

    def yview(self, *args):
        """Scroll bar update."""
        print(args)
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
        if self._frame_number >= self.next_update:
            self.update_card_frames()
        else:
            self.after(50, self.delayed_update_card_frames)

    def update_card_frames(self):
        """Update rows of cards."""
        card_number = self.card_number
        print(f"Update to {card_number}")

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


class CardsFrame(AppFrame):
    """The cards frame."""

    def __init__(self, container):
        """Init the frame."""
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
