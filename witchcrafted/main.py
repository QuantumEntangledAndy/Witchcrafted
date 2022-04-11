"""
Masterduel modding tool.

Usage:
    masterduel [options]

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import kivy
from kivy.app import App as KivyApp
from kivy.properties import ObjectProperty
from kivy.clock import Clock
import re

from docopt import docopt
import ctypes
from colorama import init as colorama_init
from pathlib import Path

from witchcrafted.utils import Async, make_logger, set_up_logger, get_md_paths


kivy.require("2.1.0")

try:  # Windows 8.1 and later
    ctypes.windll.shcore.SetProcesspiAwareness(2)
except Exception:
    pass
try:  # Before Windows 8.1
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:  # Windows 8 or before
    pass


logger = make_logger("witchcrafted")
set_up_logger(logger)


class WitchcraftedApp(KivyApp):
    """Main GUI app."""

    kv_directory = "witchcrafted/view"

    selected_card_id = ObjectProperty(None, allownone=True)

    def __init__(self, opts):
        """Init the app."""
        super().__init__()

    async def async_run(self, *args, **kwargs):
        """Run the loop async."""
        try:
            await super().async_run(*args, **kwargs)
        except KeyboardInterrupt:
            pass
        finally:
            Async().shutdown()

    def build_config(self, config):
        """Prepare the default config."""
        md_paths = get_md_paths()
        if md_paths:
            md_path = md_paths[0]
            local_dir = md_path.joinpath("LocalData")
            profile_dir = None
            for profile in local_dir.iterdir():
                if profile.name != "00000000" and re.match(
                    r"^[0-9a-f]+$", profile.name
                ):
                    profile_dir = profile
            if not profile_dir:
                profile_dir = Path("./masterduel/source")
            masterduel_data = md_path.joinpath("masterduel_Data")
            streaming_assets = masterduel_data.joinpath("StreamingAssets")
            config.setdefaults(
                "paths",
                {
                    "source": f"{profile_dir}",
                    "datasource": f"{masterduel_data}",
                    "assetsource": f"{streaming_assets}",
                    "output": "./masterduel/output",
                },
            )
        else:
            config.setdefaults(
                "paths",
                {
                    "source": "./masterduel/source",
                    "datasource": "./masterduel/source",
                    "assetsource": "./masterduel/source",
                    "output": "./masterduel/output",
                },
            )
        config.setdefaults(
            "app",
            {"debug": False},
        )

    def build_settings(self, settings):
        """Prepare setting panels."""
        jsonpath = Path("./witchcrafted/view/settings.json")
        jsondata = jsonpath.read_text()
        settings.add_json_panel("Settings", self.config, data=jsondata)

    def panel_settings(self):
        """Open the settings panel and swap to default tab."""
        Clock.schedule_once(lambda dt: self.root.switch_to(self.root.default_tab), 0.0)
        self.open_settings()

    def select_for_edit(self, card_id):
        """Select a card and swap to the edit view."""
        self.selected_card_id = card_id
        self.root.switch_to(self.root.card_edit_tab)


def main(opts):
    """Run with asyncio."""
    colorama_init()

    app = WitchcraftedApp(opts)

    asc = Async()
    asc.async_task(app.async_run())

    try:
        asc.run()
    except KeyboardInterrupt:
        asc.shutdown()
    finally:
        app.config.write()


if __name__ == "__main__":
    opts = docopt(__doc__)
    main(opts)
