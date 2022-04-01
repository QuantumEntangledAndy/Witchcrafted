"""Card edit view."""

from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
import io
import asyncio

from witchcrafted.utils import Async
from witchcrafted.cards.card_data import CardData


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

    def import_image(self):
        """Import an image."""
