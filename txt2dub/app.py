import contextlib
import json
import re
from textual import on, work
from textual.app import App as TextualApp
from textual.containers import Container, Vertical
from textual.events import Mount, Unmount
from textual.message import Message
from textual.reactive import var
from textual.widgets import Button, Footer, Header, Static
from .services.tts import create_tts
from .screens.file import LoadScriptFileScreen
from .screens.script import ScriptScreen
from .models import ScriptModel
from .widgets.base import TitledScreen
from .widgets.logo import Logo


class AppActionsToolbar(Static):
    """The toolbar for actions on the top-level app screen."""

    class New(Message):
        """New script requested."""

    class Load(Message):
        """Load script requested."""

    class Quit(Message):
        """Quit requested."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_button = None
        self.load_button = None

    def compose(self):
        with Container(classes="left group"):
            self.new_button = (
                Button(
                    "New",
                    id="new",
                    classes="first control",
                    variant="success"))
            yield self.new_button

            self.load_button = (
                Button(
                    "Load\N{HORIZONTAL ELLIPSIS}",
                    id="load",
                    classes="last control",
                    variant="primary"))
            yield self.load_button

        with Container(classes="right group"):
            yield(
                Button(
                    "Quit",
                    id="quit",
                    classes="singular control"))

    @on(Button.Pressed, "#new")
    def new_pressed(self):
        self.post_message(self.New())

    @on(Button.Pressed, "#load")
    def load_pressed(self):
        self.post_message(self.Load())

    @on(Button.Pressed, "AppActionsToolbar #quit")
    def quit_pressed(self):
        self.post_message(self.Quit())

    def watch_disabled(self):
        if self.new_button is not None:
            self.new_button.disabled = self.disabled
        if self.load_button is not None:
            self.load_button.disabled = self.disabled


class App(TextualApp):
    """A terminal UI application for editing voiceover scripts
    and generating text to speech performances.
    """

    TITLE = "txt2dub"
    SUB_TITLE = "Welcome"
    CSS_PATH = "styles/app.css"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("escape", "quit", "Quit")
    ]

    disabled = var(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tts = None
        self.toolbar = None

    @contextlib.asynccontextmanager
    async def disable(self):
        self.disabled = True
        try:
            yield
        finally:
            self.disabled = False

    def compose(self):
        yield Header()
        with Vertical(classes="container"):
            yield Logo()

            self.toolbar = (
                AppActionsToolbar(
                    classes="bottom horizontal toolbar"))
            yield self.toolbar

        yield Footer()

    def play(self, text, voice, rate):
        return self.tts.play(text, voice, rate)

    def generate(self, path, script):
        return self.tts.generate(path, script)

    def push_screen(self, *args, **kwargs):
        results = super().push_screen(*args, **kwargs)
        self.update_sub_title()
        return results

    def pop_screen(self, *args, **kwargs):
        results = super().pop_screen(*args, **kwargs)
        self.update_sub_title()
        return results

    def switch_screen(self, *args, **kwargs):
        results = super().switch_screen(*args, **kwargs)
        self.update_sub_title()
        return results

    def update_sub_title(self):
        if not isinstance(self.screen, TitledScreen):
            self.sub_title = self.SUB_TITLE

    @work()
    async def new_script(self):
        async with self.disable():
            meta = await self.tts.meta()
            self.push_screen(
                ScriptScreen(
                    None,
                    ScriptModel.new(meta)))
        await (
            self.tts.play(
                "Welcome to text to dub. Have fun writing your new script.",
                meta.voices[0].id,
                175))

    def load_script(self):
        self.push_screen(
            LoadScriptFileScreen(),
            self.load_script_selected)

    @work()
    async def load_script_selected(self, filename):
        if filename:
            async with self.disable():
                meta = await self.tts.meta()
                with open(filename, "r") as script:
                    self.push_screen(
                        ScriptScreen(
                            filename,
                            ScriptModel.deserialize(
                                json.loads(
                                    script.read()),
                                meta)))
            name = (
                " ".join(
                    re.split(
                        r"[-_]",
                        filename.name[
                            0:-sum(
                                len(suffix)
                                    for suffix
                                    in filename.suffixes)])))
            await (
                self.tts.play(
                    f"Welcome back to text to dub. Enjoy your edits to {name}.",
                    meta.voices[0].id,
                    175))

    @on(Mount)
    def app_mounted(self):
        def runner(worker):
            return self.run_worker(worker).wait

        self.tts = create_tts(runner)

    @on(Unmount)
    async def app_unmounted(self):
        if self.tts is not None:
            await self.tts.terminate()

    @on(AppActionsToolbar.New)
    def toolbar_new(self):
        self.new_script()

    @on(AppActionsToolbar.Load)
    def toolbar_load(self):
        self.load_script()

    @on(AppActionsToolbar.Quit)
    def toolbar_quit(self):
        self.exit()

    def action_toggle_dark(self):
        self.dark = not self.dark

    def watch_disabled(self):
        if self.toolbar is not None:
            self.toolbar.disabled = self.disabled


def run():
    App().run()
