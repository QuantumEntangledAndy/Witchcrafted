"""The main panel."""
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import ObjectProperty


class MainPanel(TabbedPanel):
    """The main root panel."""

    selected_card_id = ObjectProperty(None, allownone=True)
    card_view_tab = ObjectProperty(None)
    card_edit_tab = ObjectProperty(None)
