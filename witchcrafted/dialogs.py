"""Dialog views such as save and load."""

from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, BooleanProperty
from pathlib import Path

from witchcrafted.utils import Async


class LoadDialog(GridLayout):
    """Load dialog."""

    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    select_multiple = BooleanProperty(False)

    def __init__(self, **kwargs):
        """Create the dialog."""
        self.open_directory = kwargs.pop("open_directory", False)
        self.select_multiple = kwargs.pop("select_multiple", False)
        self.extensions = kwargs.pop("extensions", [])
        super().__init__(**kwargs)

    def path_valid(self, path, selections):
        """Check if paths is valid."""
        if not selections and not self.open_directory:
            return False
        elif selections and self.open_directory:
            return False
        elif len(selections) > 1 and not self.select_multiple:
            return False
        elif self.extensions:
            lower_extensions = list(map(lambda item: item.lower(), self.extensions))
            return not all(
                map(
                    lambda item: Path(item).suffix.lower() in lower_extensions,
                    selections,
                )
            )
        return True

    @classmethod
    async def show(
        cls,
        open_directory=False,
        select_multiple=False,
        extensions=[],
        start_path=None,
    ):
        """Show the load menu and await it's reply."""
        if start_path is None:
            start_path = Path.cwd()
        start_path = Path(start_path)
        if not start_path.is_dir():
            start_path = start_path.parent

        future = Async().async_future()
        result = {}

        popup = Popup(
            title="Save file",
            content=Label(text=""),
            size_hint=(0.9, 0.9),
        )

        def load(path, files):
            """Load it."""
            if files:
                files = list(map(lambda item: Path(item), files))
            else:
                files = [Path(path)]
            result["files"] = files
            popup.dismiss()

        content = LoadDialog(
            load=load,
            cancel=lambda: popup.dismiss(),
            open_directory=open_directory,
            extensions=extensions,
        )
        content.filechooser.path = f"{start_path}"
        popup.content = content

        def on_dismiss(instance):
            Async().async_finish_future(future, result.get("files", None))

        popup.bind(on_dismiss=on_dismiss)
        popup.open()
        return await future


class SaveDialog(GridLayout):
    """Save dialog."""

    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    filechooser = ObjectProperty(None)

    result = ObjectProperty(None)

    def __init__(self, **kwargs):
        """Create the dialog."""
        self.open_directory = kwargs.pop("open_directory", False)
        self.extensions = kwargs.pop("extensions", [])
        super().__init__(**kwargs)

    def path_valid(self, path, file_name):
        """Check if paths is valid."""
        if not file_name and not self.open_directory:
            return False
        elif file_name and self.open_directory:
            return False
        elif self.extensions and Path(file_name).suffix:
            lower_extensions = list(map(lambda item: item.lower(), self.extensions))
            return Path(file_name).suffix.lower() in lower_extensions
        elif self.extensions and not Path(file_name).suffix:
            return Path(file_name).with_suffix(self.extensions[0])
        return True

    @classmethod
    async def show(
        cls,
        open_directory=False,
        extensions=[],
        start_path=None,
        start_file=None,
    ):
        """Show the load menu and await it's reply."""
        if start_path is None:
            start_path = Path.cwd()
        start_path = Path(start_path)
        if not start_path.is_dir():
            start_path = start_path.parent
        future = Async().async_future()
        result = {}
        popup = Popup(
            title="Save file",
            content=Label(text=""),
            size_hint=(0.9, 0.9),
        )

        def save(path, filename):
            """Save it."""
            if filename:
                file_path = Path(filename)
                if not file_path.suffix and extensions:
                    file_path = file_path.with_suffix(f"{extensions[0]}")
            else:
                file_path = Path(path)
            result["files"] = file_path
            popup.dismiss()

        content = SaveDialog(
            save=save,
            cancel=lambda: popup.dismiss(),
            open_directory=open_directory,
            extensions=extensions,
        )
        content.filechooser.path = f"{start_path}"
        if start_file:
            content.text_input.text = start_file
        popup.content = content

        def on_dismiss(instance):
            Async().async_finish_future(future, result.get("files", None))

        popup.bind(on_dismiss=on_dismiss)
        popup.open()
        return await future
