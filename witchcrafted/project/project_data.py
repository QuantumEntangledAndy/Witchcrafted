"""Handles project files."""

from io import BytesIO
from zipfile import ZipFile
from yaml import dump, safe_load
import re
from PIL import Image
import time
from packaging.version import parse as version_parse

from kivy.app import App

from witchcrafted.cards.card_data import CardData
from witchcrafted.utils import sanatize_text, make_logger, set_up_logger

logger = make_logger(__file__)
set_up_logger(logger)

PROJECT_VERSION = "1.0.0"


class ProjectData:
    """Project data."""

    @property
    def description(self):
        """Get the description."""
        return self._description

    @description.setter
    def description(self, value):
        """Set the description."""
        self._description = value

    @property
    def name(self):
        """Get the name."""
        return self._name

    @name.setter
    def name(self, value):
        """Set the name."""
        self._name = value

    def __init__(self):
        """Create a new project with a name."""
        self._name = None
        self._description = None
        self.edits = {}

    def __repr__(self, *args, **kwargs):
        """Debug print."""
        return (
            "<"
            + f"{type(self).__name__}"
            + f", name: {self.name}"
            + f", description: {self.description}"
            + f", edits: {repr(self.edits)}"
            + ">"
        )

    def add_card_image(self, card_id, image):
        """Add a card image to the project."""
        self.edits[card_id]["image"] = image

    async def store(self):
        """Store working edited data into the project data."""
        for card_id in CardData.edited_cards():
            self.edits[card_id] = {}
            card_data = CardData(card_id)
            if card_data.edited("image"):
                image = await card_data.get_image()
                if image:
                    self.add_card_image(card_id, image)

    async def apply(self):
        """Apply project data into working editing data."""
        for (card_id, edit) in self.edits.items():
            card_data = CardData(card_id)
            image = edit.get("image", None)
            if image:
                await card_data.set_image(image)

    async def save(self, file_name):
        """Save the project."""
        zip_bytes = BytesIO()
        await self.store()

        meta = {
            "name": self.name,
            "description": self.description,
            "version": PROJECT_VERSION,
        }

        with ZipFile(zip_bytes, mode="w", allowZip64=True) as zip_ob:
            zip_ob.writestr("meta.yml", dump(meta, default_flow_style=False))

            for (card_id, edit) in self.edits.items():
                image = edit.get("image", None)
                if image:
                    with zip_ob.open(f"cards/{card_id}/image.png", mode="w") as fo:
                        image.save(fo, "PNG")

        with open(file_name, "wb") as outfile:
            outfile.write(zip_bytes.getbuffer())

    @classmethod
    async def load(cls, file_name):
        """Load a project (dosen't apply the edits)."""
        output = cls()
        with ZipFile(file_name, mode="r", allowZip64=True) as zip_ob:
            namelist = zip_ob.namelist()
            version = None
            if "meta.yml" in namelist:
                with zip_ob.open("meta.yml", mode="r") as fo:
                    meta = safe_load(fo)
                    version = meta.get("version", None)
                    output.name = meta.get("name", "")
                    output.description = meta.get("description", "")
            if not version:
                logger.warn("Project version missing")
                return
            file_version = version_parse(version)
            max_version = version_parse(PROJECT_VERSION)
            if file_version > max_version:
                logger.warn("Project version unsupported")
                return None
            card_images = [
                int(re.match(r"^cards/([0-9]+)/image.png$", c).group(1))
                for c in namelist
                if re.match(r"^cards/[0-9]+/image.png$", c)
            ]
            for card_id in card_images:
                with zip_ob.open(f"cards/{card_id}/image.png", mode="r") as fo:
                    if card_id not in output.edits:
                        output.edits[card_id] = {}
                    image = Image.open(fo)
                    image.load()
                    output.edits[card_id]["image"] = image
        app = App.get_running_app()
        app.root.card_view.reset_panels()
        return output

    async def commit(self):
        """Commit changes to disk."""
        for card_id in CardData.edited_card():
            card_data = CardData(card_id)
            stamp = time.strftime("%Y-%m-%d_%H%M", time.localtime())
            name = self.name if self.name else "Navnlos"
            await card_data.commit(sanatize_text(f"{name}_{stamp}"))
