"""Handles project files."""

from io import BytesIO
from zipfile import ZipFile
from yaml import dump, safe_load
import re
import PIL

from witchcrafted.cards.card_data import CardData

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

    def add_card_image(self, card_id, image):
        """Add a card image to the project."""
        self.edits[card_id]["image"] = image

    async def store(self):
        """Store working edited data into the project data."""
        for card_id in CardData.edited_card():
            card_data = CardData(card_id)
            image = await card_data.get_image()
            if image:
                self.add_card_image(card_id, image)

    async def apply(self):
        """Apply project data into working editing data."""
        for (card_id, edit) in self.edits.iter():
            card_data = CardData(card_id)
            image = edit.get("image", None)
            if image:
                await card_data.set_image(image)

    def save(self, file_name):
        """Save the project."""
        zip_bytes = BytesIO()

        meta = {
            "name": self.name,
            "description": self.description,
            "__VERSION__": PROJECT_VERSION,
        }

        with ZipFile(zip_bytes, mode="w", allowZip64=True) as zip_ob:
            with zip_ob.open("meta.yml", mode="w") as fo:
                dump(meta, fo)

            for (card_id, edit) in self.edits.iter():
                image = self.edits.get("image", None)
                if image:
                    with zip_ob.open(f"cards/{card_id}/image.png", mode="w") as fo:
                        image.save(fo, "PNG")

        with open(file_name, "wb") as outfile:
            outfile.write(zip_bytes.getbuffer())

    @classmethod
    def load(cls, file_name):
        """Load a project (dosen't apply the edits)."""
        output = cls()
        with ZipFile(file_name, mode="r", allowZip64=True) as zip_ob:
            namelist = zip_ob.namelist()
            if "meta.yml" in namelist:
                with zip_ob.open("meta.yml", mode="r") as fo:
                    meta = safe_load(fo)
                    output.name = meta["name"]
                    output.description = meta["description"]
            card_images = [
                int(re.match(r"^cards/([0-9])/image.png$", c).group(1))
                for c in namelist
                if re.match(r"^cards/[0-9]/image.png$", c)
            ]
            for card_id in card_images:
                with zip_ob.open(f"cards/{card_id}/image.png", mode="r") as fo:
                    output.edits[card_id]["image"] = PIL.open(fo, "PNG")
