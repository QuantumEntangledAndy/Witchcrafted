"""An individual card panel."""

from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.behaviors.button import ButtonBehavior
import io
import asyncio

from witchcrafted.cards.card_data import CardData
from witchcrafted.utils import Async


class CardPanel(ButtonBehavior, GridLayout):
    """A card panel in the scrolling card view."""

    image = ObjectProperty(None, allownone=True)
    card_id = ObjectProperty(None, allownone=True)
    card_image = ObjectProperty(None, allownone=True)
    card_name = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        """Init the view."""
        super().__init__(**kwargs)
        self._card_lock = asyncio.Lock()

    def on_card_id(self, instance, new_card_id):
        """Act on card id changing."""
        self.card_id = new_card_id
        self.update_card()

    def update_card(self):
        """Update the card."""
        Async().async_task(self.async_update_card())

    async def async_update_card(self):
        """Async update data from card_id."""
        new_card_id = self.card_id
        async with self._card_lock:
            card_data = CardData(new_card_id)
            self.card_name = await card_data.get_name()
            image = await card_data.get_image()
            if image is not None:
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                buf.seek(0)
                self.card_image = CoreImage(buf, ext="png")
