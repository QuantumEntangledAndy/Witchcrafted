"""The project view."""

from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.app import App

from witchcrafted.project.project_data import ProjectData
from witchcrafted.utils import Async
from witchcrafted.cards.card_data import CardData
from witchcrafted.dialogs import LoadDialog, SaveDialog


class ProjectView(GridLayout):
    """The project view."""

    project = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        """Init the view."""
        super().__init__(**kwargs)
        self.project = ProjectData()

    def save_project(self):
        """Save the project."""
        Async().async_fire(self.async_save_project())

    async def async_save_project(self):
        """Save the project."""
        if self.project:
            app = App.get_running_app()
            start_path = app.config.get("paths", "output")
            file_paths = await SaveDialog.show(
                extensions=[".mdmod"], start_path=start_path
            )
            if file_paths:
                file_path = file_paths[0]
                await self.project.store()
                await self.project.save(file_path)

    def load_project(self):
        """Load the project."""
        Async().async_fire(self.async_load_project())

    async def async_load_project(self):
        """Load the project."""
        app = App.get_running_app()
        start_path = app.config.get("paths", "output")
        file_paths = await LoadDialog.show(extensions=[".mdmod"], start_path=start_path)
        if file_paths:
            file_path = file_paths[0]
            project = await ProjectData.load(file_path)
            if project:
                self.project = project
                CardData.forget_all()
                await self.apply()

    def revert_project(self):
        """Revert all edited changes to those saved in the project."""
        CardData.forget_all()
        if self.project:
            Async().async_fire(self.project.apply())

    def commit_project(self):
        """Apply all edits to game files."""
