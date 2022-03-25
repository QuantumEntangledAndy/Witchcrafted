"""
Card data.

This is loaded from database or from the game files.
"""

from threading import Thread
import UnityPy
from pathlib import Path


class AsyncLoadData(Thread):
    """Async load picture etc from the game files."""

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
