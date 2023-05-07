from textual import on
from textual.app import App as TextualApp
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Label , Static
from .widgets.logo import Logo

from textual.widgets import ListView, ListItem


class App(TextualApp):
    """A terminal UI application for editing voiceover scripts and generating
    text to speech performances.
    """

    CSS_PATH = "styles/app.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self):
        yield Header()
        with Vertical(id="container"):
            yield Logo()
        yield Footer()

    def action_toggle_dark(self):
        self.dark = not self.dark
