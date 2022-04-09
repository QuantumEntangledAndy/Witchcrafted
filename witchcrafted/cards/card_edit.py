"""Card edit view."""

from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from kivy.app import App
from PIL import Image as PilImage

import io
import asyncio

from witchcrafted.utils import Async
from witchcrafted.cards.card_data import CardData
from witchcrafted.dialogs import LoadDialog, SaveDialog


class CardEdit(GridLayout):
    """Card edit view."""

    card_id = ObjectProperty(None, allownone=True)
    card_image = ObjectProperty(None, allownone=True)
    card_name = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        """Init the view."""
        super().__init__(**kwargs)
        self._card_lock = asyncio.Lock()

    def on_card_id(self, instance, new_card_id):
        """Act on change of selected_card_id."""
        Async().async_task(self.async_update_card(new_card_id))

    async def async_update_card(self, new_card_id):
        """Async update data from card_id."""
        async with self._card_lock:
            card_data = CardData(new_card_id)
            self.card_name = await card_data.get_name()
            image = await card_data.get_image()
            if image is not None:
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                buf.seek(0)
                self.card_image = CoreImage(buf, ext="png")

    def export_image(self):
        """Export the image."""
        Async().async_task(self.export_image_async())

    async def export_image_async(self):
        """Export the image async."""
        app = App.get_running_app()
        start_path = app.config.get("paths", "output")
        file_path = await SaveDialog.show(
            extensions=[".jpg", ".jpeg", ".png"],
            start_path=start_path,
            start_file=f"{self.card_id}.png",
        )
        if file_path:
            async with self._card_lock:
                card_data = CardData(self.card_id)
                image = await card_data.get_image()
                image.save(file_path)

    def import_image(self):
        """Import an image."""
        Async().async_task(self.import_image_async())

    async def import_image_async(self):
        """Import an image async."""
        app = App.get_running_app()
        start_path = app.config.get("paths", "output")
        file_paths = await LoadDialog.show(
            extensions=[".jpg", ".jpeg", ".png", ".bmp"], start_path=start_path
        )
        if file_paths:
            file_path = file_paths[0]
            async with self._card_lock:
                image = PilImage.open(file_path)
                card_data = CardData(self.card_id)
                await card_data.set_image(image)
            await self.async_update_card(self.card_id)
            app.root.card_view.reset_panels()
