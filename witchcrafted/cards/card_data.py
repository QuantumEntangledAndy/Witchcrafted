"""
Card data.

This is loaded from database or from the game files.
"""

import UnityPy
from pathlib import Path
import pandas as pd
import threading
import asyncio
import PIL
import io

from kivy.app import App
from kivy.core.image import Image as CoreImage

from witchcrafted.utils import Async


class LoadData:
    """Load picture etc from the game files."""

    _lock = threading.Lock()

    __df = None
    __df_common = None

    @classmethod
    def cards_data(cls):
        """Get pandas data on all cards."""
        if cls.__df is None:
            with cls._lock:
                if cls.__df is None:
                    cls.__df = pd.read_csv("assets/card_list.csv")
        return cls.__df

    @classmethod
    def main_cards_data(cls):
        """Get pandas data on the cards in the 0000 folder."""
        if cls.__df_common is None:
            df = cls.cards_data()
            card_list = df[(df["Folder Name"] == "0000")]
            card_list.reset_index(inplace=True)
            with cls._lock:
                if cls.__df_common is None:
                    cls.__df_common = card_list
        return cls.__df_common

    @classmethod
    def main_cards_ids(cls):
        """Get card IDs."""
        df = cls.main_cards_data()
        return df[["Card ID"]]

    @classmethod
    def image(cls, card_id):
        """Load an image using pandas data and a card id."""
        df = cls.cards_data()
        app = App.get_running_app()
        root_dir = Path(app.config.get("paths", "source"))

        card_data = df.loc[df["Card ID"] == card_id].iloc[0].to_dict()
        top_level_folder = card_data["Folder Name"]
        tcg_file_name = card_data["File, TCG"]
        ocg_file_name = card_data["File, OCG"]

        tcg_file_prefix = tcg_file_name[0:2]
        file_path_tcg = root_dir.joinpath(
            top_level_folder, tcg_file_prefix, tcg_file_name
        )

        ocg_file_prefix = ocg_file_name[0:2]
        file_path_ocg = root_dir.joinpath(
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
                card_id = str(card_id)
                if resouce_name == card_id:
                    return data.image
        return None


class CardData:
    """Data of an individual card."""

    _lock = threading.Lock()
    _async_lock = asyncio.Lock()
    _card_data_store = {}

    def __init__(self, card_id):
        """Create a dummy card."""
        self.card_id = card_id
        self.update_data()

    @classmethod
    def forget_all(cls):
        """Remove all loaded card data."""
        with cls._lock:
            cls._card_data_store.clear()

    @classmethod
    def edited_card(cls):
        """Get IDs of all edited cards."""
        return [k for (k, v) in cls._card_data_store.items() if v.get("edited", False)]

    def update_data(self):
        """Get or load from global csv data."""
        cls = type(self)
        card_id = self.card_id
        if card_id not in cls._card_data_store:
            with cls._lock:
                if card_id not in cls._card_data_store:
                    df = LoadData.main_cards_data()
                    data = df[(df["Card ID"] == card_id)].iloc[0].to_dict()
                    cls._card_data_store[card_id] = data

        self.data = cls._card_data_store[card_id]
        self.data["edited"] = False

    async def get_name(self):
        """Get the card name."""
        return self.data["English Name"]

    async def get_image(self):
        """Get the image."""
        if "image" not in self.data:
            cls = type(self)
            image = await Async().async_thread(lambda: LoadData.image(self.card_id))
            async with cls._async_lock:
                if "image" not in self.data:
                    self.data["image"] = image
        return self.data["image"]

    async def get_core_image(self):
        """Get the image in CoreImage format."""
        if "core_image" not in self.data:
            image = await self.get_image()
            if image:
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                buf.seek(0)
                card_image = CoreImage(buf, ext="png")

                cls = type(self)
                async with cls._async_lock:
                    if "core_image" not in self.data:
                        self.data["core_image"] = card_image
        return self.data.get("core_image", None)

    async def set_image(self, image):
        """Set the image."""
        if "image" in self.data:
            current_size = image.size
            if current_size != image.size:
                image = image.resize(current_size, PIL.Image.BICUBIC)
        self.data["image"] = image
        self.data["edited"] = True
        self.data.pop("core_image")
