import os
import pathlib
from textual import on
from textual.containers import Container, Grid
from textual.events import Mount
from textual.message import Message
from textual.reactive import var
from textual.widgets import Button, Footer, Header, Input, Label, Static
from ...widgets.base import TitledScreen, TitledModalScreen
from .widgets import ScriptDirectoryTree


SCRIPT_SUFFIXES = (".txt2dub", ".json",)
GENERATED_SUFFIXES = (".txt2dub", ".zip",)


class LoadFileScreenToolbar(Static):
    """The toolbar for the file loading screen."""

    class Cancel(Message):
        """Cancel requested."""

    def compose(self):
        with Container(classes="right group"):
            yield (
                Button(
                    "Cancel",
                    id="cancel",
                    classes="singular control"))

    @on(Button.Pressed, "#cancel")
    def cancel_pressed(self):
        self.post_message(self.Cancel())


class LoadScriptFileScreen(TitledScreen):
    """The script file loading screen."""

    TITLE = "Select a script file to load"
    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directory_tre = None

    def compose(self):
        yield Header()
        with Container(classes="container"):
            self.directory_tree = ScriptDirectoryTree(".", SCRIPT_SUFFIXES, classes="tree")
            yield self.directory_tree

            yield LoadFileScreenToolbar(classes="bottom horizontal toolbar")
        yield Footer()

    @on(ScriptDirectoryTree.FileSelected)
    def file_selected(self, event):
        self.dismiss(event.path)

    @on(LoadFileScreenToolbar.Cancel)
    def toolbar_cancel(self):
        self.app.pop_screen()

    def action_cancel(self):
        self.app.pop_screen()


class SaveFileScreenToolbar(Static):
    """The toolbar for the file saving screen."""

    class Save(Message):
        """Save requested."""

        def __init__(self, path, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.path = path

    class Cancel(Message):
        """Cancel requested."""

    directory = var("")
    filename = var("")

    def __init__(self, suffixes = (), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.suffixes = suffixes

        self.label = None
        self.input = None
        self.save_button = None

    def compose(self):
        with Container(classes="singular group"):
            self.label = Label("", classes="first control")
            yield self.label

            self.input = Input(id="filename", classes="wide control")
            yield self.input

            self.save_button = (
                Button(
                    "Save",
                    id="save",
                    classes="control",
                    variant="primary"))
            yield self.save_button

        with Container(classes="right group"):
            yield (
                Button(
                    "Cancel",
                    id="cancel",
                    classes="singular control"))

    @property
    def path(self):
        if self.directory and self.filename:
            directory = pathlib.Path(self.directory)
            filename = pathlib.Path(self.filename)
            suffixes = filename.suffixes[-len(self.suffixes):]
            if (filename.stem and
                not filename.stem.endswith(".") and (
                    len(suffixes) == 0 or (
                        len(suffixes) == len(self.suffixes) and
                        all(suffix == check
                                for suffix, check
                                in zip(suffixes, self.suffixes))))):
                path = directory / filename
                return (
                    path.with_suffix("".join(self.suffixes))
                        if len(suffixes) == 0
                        else path)

    @on(Input.Changed, "#filename")
    def filename_changed(self, event):
        self.filename = event.value

    @on(Input.Submitted, "#filename")
    def filename_submitted(self):
        path = self.path
        if path is not None:
            print("um", path)
            self.post_message(
                self.Save(path))

    @on(Button.Pressed, "#save")
    def save_pressed(self):
        path = self.path
        if path is not None:
            self.post_message(
                self.Save(path))

    @on(Button.Pressed, "#cancel")
    def cancel_pressed(self):
        self.post_message(
            self.Cancel())

    def watch_filename(self, filename):
        if self.input:
            with self.input.prevent(Input.Changed):
                self.input.value = f"{filename}"
        if self.save_button:
            self.save_button.disabled = self.path is None

    def watch_directory(self, directory):
        if self.label:
            self.label.update(
                f"{directory}{os.path.sep}"
                    if directory is not None
                    else "")


class SaveFileScreen(TitledScreen):
    """The base file saving screen."""

    TITLE = "Save a file"
    SUFFIXES = ()
    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directory_tree = None

    def compose(self):
        yield Header()
        with Container(classes="container"):
            self.directory_tree = (
                ScriptDirectoryTree(
                    ".",
                    self.SUFFIXES,classes="tree"))
            yield self.directory_tree

            self.toolbar = (
                SaveFileScreenToolbar(
                    self.SUFFIXES,
                    classes="bottom horizontal toolbar"))
            yield self.toolbar
        yield Footer()

    @on(Mount)
    def on_mount(self):
        if self.directory_tree is not None and self.toolbar is not None:
            self.toolbar.directory = f"{self.directory_tree.path.absolute()}"

    @on(ScriptDirectoryTree.DirectorySelected)
    def directory_selected(self, event):
        if self.toolbar is not None:
            self.toolbar.directory = f"{event.path.absolute()}"

    @on(ScriptDirectoryTree.FileSelected)
    def file_selected(self, event):
        if self.toolbar is not None:
            self.toolbar.filename = event.path.name
            self.toolbar.directory = f"{event.path.parent.absolute()}"

    @on(SaveFileScreenToolbar.Save)
    def toolbar_save(self, path):
        self.dismiss(path)

    @on(SaveFileScreenToolbar.Cancel)
    def toolbar_cancel(self):
        self.app.pop_screen()

    def action_cancel(self):
        self.app.pop_screen()


class SaveScriptFileScreen(SaveFileScreen):
    """The script file saving screen."""

    TITLE = "Save a script file as..."
    SUFFIXES = SCRIPT_SUFFIXES


class SaveGeneratedFileScreen(SaveFileScreen):
    """The generated file saving screen."""

    TITLE = "Save a generated file as..."
    SUFFIXES = GENERATED_SUFFIXES


class SaveBeforeClosingScreen(TitledModalScreen):
    """Save before closing screen."""

    TITLE = "Save before closing?"
    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename

    def compose(self):
        with Grid(classes="grid"):
            yield (
                Label(
                    "Your script has outstanding changes.\n" +
                    "Do you want to save before closing?",
                    classes="label"))
            yield (
                Button(
                    "Yes"
                        if self.filename
                        else "Yes, save as...",
                    id="yes",
                    variant="primary",
                    classes="control"))
            yield (
                Button(
                    "No",
                    id="no",
                    variant="error",
                    classes="control"))
            yield (
                Button(
                    "Cancel",
                    id="cancel",
                    classes="control"))

    @on(Button.Pressed, "#yes")
    def yes_pressed(self):
        self.dismiss(True)

    @on(Button.Pressed, "#no")
    def no_pressed(self):
        self.dismiss(False)

    @on(Button.Pressed, "#cancel")
    def cancel_pressed(self):
        self.app.pop_screen()

    def action_cancel(self):
        self.app.pop_screen()
