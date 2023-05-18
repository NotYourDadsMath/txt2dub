from textual import on
from textual.events import ScreenResume
from textual.reactive import var
from textual.screen import ModalScreen, Screen


class TitledScreen(Screen):
    """A Textual screen with a title."""

    TITLE = None

    title = var("")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = (
            self.TITLE
                if self.TITLE is not None
                else "")

    @on(ScreenResume)
    def titled_screen_resume(self):
        if self.is_current:
            self.app.sub_title = self.title

    def watch_title(self, title):
        if self.is_current:
            self.app.sub_title = title


class TitledModalScreen(ModalScreen, TitledScreen):
    """A textual modal screen with a title."""
