"""Settings for the app."""

from yaml import safe_load as load, dump
from pathlib import Path
from witchcrafted.utils import multiline_strip


class Settings:
    """Settings class."""

    yaml_properties = [
        "debug",
        "out_dir",
        "source_dir",
        "mods_dir",
        "setup",
        "settings_version",
    ]
    yaml_defaults = {"debug": False}

    default_settings = """
    settings_version: "0.0.1"
    out_dir: "./masterduel/output"
    source_dir: "./masterduel/originals"
    mods_dir: "./masterduel/mods"
    setup: False
    """

    def __init__(self, file_name):
        """Create the settings from a file."""
        file_path = Path(file_name)
        if not file_path.exists():
            default_settings = multiline_strip(type(self).default_settings)
            file_path.write_text(default_settings)

        self.source = Path(file_path)

    def __setattr__(self, name, value):
        """Magic setter."""
        if name not in type(self).yaml_properties:
            self.__dict__[name] = value
        else:
            yml = load(self.source.read_text())
            yml[name] = value
            self.source.write_text(dump(yml))

    def __getattr__(self, name):
        """Magic getter."""
        if name in type(self).yaml_properties:
            yml = load(self.source.read_text())
            if name in yml:
                return yml[name]
            elif name in type(self).yaml_defaults:
                return type(self).yaml_defaults[name]
            else:
                None
        elif name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError
