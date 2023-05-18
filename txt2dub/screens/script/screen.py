import contextlib
import json
from textual import on
from textual.containers import (
        Container, Horizontal, Vertical, VerticalScroll,)
from textual.events import Mount
from textual.message import Message
from textual.reactive import var
from textual.worker import Worker, WorkerState
from textual.widgets import Button, Footer, Header, Static
from ...services.actions import Actions, ActionsManager
from ...widgets.base import TitledScreen
from ..file import (
    SaveBeforeClosingScreen,
    SaveScriptFileScreen,
    SaveGeneratedFileScreen,)
from .messages import (
    ScriptSelectLine, ScriptPlayLine, ScriptEditLineText,
    ScriptEditLineVoiceRate, ScriptEditLineVoiceId,
    ScriptMoveLineUp, ScriptMoveLineDown,
    ScriptRemoveLine, ScriptAddLineAbove, ScriptAddLineBelow,)
from .widgets import ScriptLine


class ScriptScreenActionsToolbar(Static):
    """The toolbar for actions on the script editing screen."""

    class Undo(Message):
        """Undo requested."""

    class Redo(Message):
        """Redo requested."""

    class First(Message):
        """First line requested."""

    class Last(Message):
        """Last line requested."""

    class Play(Message):
        """Play lines requested."""

    class Stop(Message):
        """Stop playback requested."""

    undo_disabled = var(True)
    redo_disabled = var(True)
    stop_disabled = var(True)
    play_disabled = var(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.undo_button = None
        self.redo_button = None
        self.stop_button = None
        self.play_button = None

    def compose(self):
        with Container(classes="group"):
            self.undo_button = (
                Button(
                    "Undo",
                    id="undo",
                    classes="first control",
                    disabled=True))
            yield self.undo_button

            self.redo_button = (
                Button(
                    "Redo",
                    id="redo",
                    classes="control",
                    disabled=True))
            yield self.redo_button

        with Container(classes="group"):
            yield (
                Button(
                    "|\N{BLACK LEFT-POINTING TRIANGLE}",
                    id="first",
                    classes="control"))

            self.stop_button = (
                Button(
                    "\N{BLACK SQUARE}",
                    id="stop",
                    classes="control",
                    variant="error"))
            yield self.stop_button

            self.play_button = (
                Button(
                    "\N{BLACK RIGHT-POINTING TRIANGLE}",
                    id="play",
                    classes="control",
                    variant="success"))
            yield self.play_button

            yield (
                Button(
                    "\N{BLACK RIGHT-POINTING TRIANGLE}|",
                    id="last",
                    classes="last control"))

    @on(Button.Pressed, "#undo")
    def undo_pressed(self):
        self.post_message(self.Undo())

    @on(Button.Pressed, "#redo")
    def redo_pressed(self):
        self.post_message(self.Redo())

    @on(Button.Pressed, "#first")
    def first_pressed(self):
        self.post_message(self.First())

    @on(Button.Pressed, "#last")
    def last_pressed(self):
        self.post_message(self.Last())

    @on(Button.Pressed, "#stop")
    def stop_pressed(self):
        self.post_message(self.Stop())

    @on(Button.Pressed, "#play")
    def play_pressed(self):
        self.post_message(self.Play())

    def watch_undo_disabled(self):
        if self.undo_button is not None:
            self.undo_button.disabled = self.undo_disabled

    def watch_redo_disabled(self):
        if self.redo_button is not None:
            self.redo_button.disabled = self.redo_disabled

    def watch_stop_disabled(self):
        if self.stop_button is not None:
            self.stop_button.disabled = self.stop_disabled

    def watch_play_disabled(self):
        if self.play_button is not None:
            self.play_button.disabled = self.play_disabled


class ScriptScreenFileToolbar(Static):
    """The toolbar for file operations on the script editing screen."""

    save_disabled = var(True)

    class Save(Message):
        """Save requested."""

    class SaveAs(Message):
        """Save as requested."""

    class Generate(Message):
        """Generate requested."""

    class Close(Message):
        """Close requested."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.save_button = None
        self.save_as_button = None
        self.generate_button = None

    def compose(self):
        with Horizontal(classes="left group"):
            self.save_button = (
                Button(
                    "Save",
                    id="save",
                    classes="first control",
                    variant="primary",
                    disabled=True))
            yield self.save_button

            self.save_as_button = (
                Button(
                    "Save as\N{HORIZONTAL ELLIPSIS}",
                    id="save-as",
                    classes="control",
                    variant="primary"))
            yield self.save_as_button

            self.generate_button = (
                Button(
                    "Generate\N{HORIZONTAL ELLIPSIS}",
                    id="generate",
                    classes="last control",
                    variant="warning"))
            yield self.generate_button

        with Horizontal(classes="right group"):
            yield (
                Button(
                    "Close",
                    id="close",
                    classes="singular control"))

    @on(Button.Pressed, "#save")
    def save_pressed(self):
        self.post_message(self.Save())

    @on(Button.Pressed, "#save-as")
    def save_as_pressed(self):
        self.post_message(self.SaveAs())

    @on(Button.Pressed, "#generate")
    def generate_pressed(self):
        self.post_message(self.Generate())

    @on(Button.Pressed, "#close")
    def close_pressed(self):
        self.post_message(self.Close())

    def watch_save_disabled(self):
        self.save_button.disabled = self.save_disabled


class ScriptScreen(TitledScreen):
    """The script editing screen."""

    BINDINGS = [("escape", "close", "Close")]

    selection = var(None)
    filename = var(None)
    play_lines = var(None)

    def __init__(self, filename=None, script=None, *args, **kwargs):
        self.actions = ActionsManager()
        super().__init__(*args, **kwargs)
        self.initial_filename = filename
        self.script = script
        self.actions_toolbar = None
        self.lines = None
        self.file_toolbar = None
        self.play_worker = None

    def compose(self):
        yield Header()
        with Vertical(classes="container"):
            self.actions_toolbar = (
                ScriptScreenActionsToolbar(
                    classes="top horizontal toolbar"))
            yield self.actions_toolbar

            self.lines = VerticalScroll(classes="scrollable")
            with self.lines:
                for line in self.script:
                    yield ScriptLine(line)
            self.file_toolbar = (
                ScriptScreenFileToolbar(
                    classes="bottom horizontal toolbar"))
            yield self.file_toolbar
        yield Footer()

    @contextlib.asynccontextmanager
    async def disable_actions_toolbar(self):
        self.actions_toolbar.undo_disabled = True
        self.actions_toolbar.redo_disabled = True
        try:
            yield
        finally:
            self.actions_toolbar.undo_disabled = self.actions.undo_empty
            self.actions_toolbar.redo_disabled = self.actions.redo_empty
            self.file_toolbar.save_disabled = self.actions.is_clean
            self.update_title()

    def play(self, lines):
        if self.play_worker is None:
            try:
                line = None
                while line is None:
                    line = next(lines)
                    if (line.context is None or
                        not line.text.strip()):

                        line = None

                self.selection = line.context
                self.play_worker = (
                    self.run_worker(
                        self.app.play(
                            line.text.strip(),
                            line.voice.id,
                            line.voice.rate)))
                self.play_lines = lines
            except StopIteration:
                self.play_lines = None
        else:
            self.play_lines = lines

    def stop(self):
        self.play_lines = None

    def generate(self, path):
        self.run_worker(
            self.app.generate(
                path,
                self.script))

    @on(Mount)
    def screen_mounted(self):
        self.filename = self.initial_filename

    @on(Worker.StateChanged)
    def worker_state_changed(self, event):
        if event.worker is self.play_worker:
            if event.state in (
                WorkerState.SUCCESS,
                WorkerState.CANCELLED,
                WorkerState.ERROR,):

                self.play_worker = None
                if self.play_lines is not None:
                    self.play(self.play_lines)

    @on(ScriptScreenActionsToolbar.Undo)
    async def actions_toolbar_undo(self):
        async with self.disable_actions_toolbar():
            await self.actions.undo()

    @on(ScriptScreenActionsToolbar.Redo)
    async def actions_toolbar_redo(self):
        async with self.disable_actions_toolbar():
            await self.actions.redo()

    @on(ScriptScreenActionsToolbar.First)
    def toolbar_first(self):
        self.selection = (
            self.script.head.context
                if self.script.head is not None
                else None)

    @on(ScriptScreenActionsToolbar.Last)
    def toolbar_last(self):
        self.selection = (
            self.script.tail.context
                if self.script.tail is not None
                else None)

    @on(ScriptScreenActionsToolbar.Stop)
    def toolbar_stop(self):
        self.stop()

    @on(ScriptScreenActionsToolbar.Play)
    def toolbar_play(self):
        line = (
            self.selection.line
                if self.selection is not None
                else self.script.head)
        if line is not None:
            self.play(iter(line))

    @on(ScriptScreenFileToolbar.Save)
    def toolbar_save(self):
        self.save()

    @on(ScriptScreenFileToolbar.SaveAs)
    def toolbar_save_as(self):
        self.save_as()

    @on(ScriptScreenFileToolbar.Generate)
    def toolbar_generate(self):
        def handle_generate_screen(result):
            if result is not None:
                self.generate(result.path)

        self.app.push_screen(
            SaveGeneratedFileScreen(),
            handle_generate_screen)

    @on(ScriptScreenFileToolbar.Close)
    def toolbar_close(self):
        self.close()

    @on(ScriptSelectLine)
    def line_selected(self, event):
        self.selection = event.line.context

    @on(ScriptPlayLine)
    def line_played(self, event):
        self.selection = event.line.context
        self.play(
            iter(
                (event.line,)))

    @on(ScriptMoveLineUp)
    async def line_up_moved(self, event):
        async with self.disable_actions_toolbar():
            line = event.line
            if not self.script.is_head(line):
                before, _ = self.script.remove(line)
                self.script.add(line, before=before)

                node = line.context
                self.lines.move_child(
                    node,
                    before=before.context)
                self.selection = node

                self.actions.add(
                    Actions(
                        self.undo_line_up_moved,
                        self.redo_line_up_moved,
                        Actions.context(
                            before=before,
                            line=line)))

    async def undo_line_up_moved(self, before, line, **_):
        self.script.remove(before)
        self.script.add(before, before=line)
        if before.context is not None and line.context is not None:
            self.lines.move_child(
                before.context,
                before=line.context)
            self.selection = line.context
        else:
            raise RuntimeError(
                "Undo line move up is missing a node")

    async def redo_line_up_moved(self, before, line, **_):
        self.script.remove(line)
        self.script.add(line, before=before)
        if before.context is not None and line.context is not None:
            self.lines.move_child(
                line.context,
                before=before.context)
            self.selection = line.context
        else:
            raise RuntimeError(
                "Redo line move up is missing a node")

    @on(ScriptMoveLineDown)
    async def line_down_moved(self, event):
        async with self.disable_actions_toolbar():
            line = event.line
            if not self.script.is_tail(line):
                _, after = self.script.remove(line)
                self.script.add(line, after=after)

                node = line.context
                self.lines.move_child(
                    node,
                    after=after.context)
                self.selection = node

                self.actions.add(
                    Actions(
                        self.undo_line_down_moved,
                        self.redo_line_down_moved,
                        Actions.context(
                            after=after,
                            line=line)))

    async def undo_line_down_moved(self, after, line, **_):
        self.script.remove(after)
        self.script.add(after, after=line)
        if after.context is not None and line.context is not None:
            self.lines.move_child(
                after.context,
                after=line.context)
            self.selection = line.context
        else:
            raise RuntimeError(
                "Undo line move down is missing a node")

    async def redo_line_down_moved(self, after, line, **_):
        self.script.remove(line)
        self.script.add(line, after=after)
        if after.context is not None and line.context is not None:
            self.lines.move_child(
                line.context,
                after=after.context)
            self.selection = line.context
        else:
            raise RuntimeError(
                "Redo line move down is missing a node")

    @on(ScriptEditLineText)
    async def line_text_edited(self, event):
        async with self.disable_actions_toolbar():
            line = event.line
            prev = line.text
            next = event.text
            line.text = next

            node = line.context
            node.text = next
            self.selection = node

            self.actions.add(
                Actions(
                    self.undo_line_text_edited,
                    self.redo_line_text_edited,
                    Actions.context(
                        line=line,
                        prev=prev,
                        next=next)))

            if event.submit:
                self.play(
                    iter(
                        (line,)))

                if (self.script.is_tail(line) and next.strip()):
                    self.post_message(
                        ScriptAddLineBelow(
                            line))

    async def undo_line_text_edited(self, line, prev, **_):
        line.text = prev
        node = line.context
        if node is not None:
            node.text = prev
            self.selection = node
        else:
            raise RuntimeError(
                "Undo line edit text is missing a node")

    async def redo_line_text_edited(self, line, next, **_):
        line.text = next
        node = line.context
        if node is not None:
            node.text = next
            self.selection = node
        else:
            raise RuntimeError(
                "Redo line edit text is missing a node")

    @on(ScriptEditLineVoiceRate)
    async def line_voice_rate_edited(self, event):
        async with self.disable_actions_toolbar():
            line = event.line
            voice = line.voice
            prev = voice.rate
            next = event.rate
            voice.rate = next

            node = voice.context
            node.voice_rate = next
            self.selection = node

            self.actions.add(
                Actions(
                    self.undo_line_voice_rate_edited,
                    self.redo_line_voice_rate_edited,
                    Actions.context(
                        line=line,
                        prev=prev,
                        next=next)))

    async def undo_line_voice_rate_edited(self, line, prev, **_):
        line.voice.rate = prev
        if line.context is not None and line.voice.context is not None:
            line.voice.context.voice_rate = prev
            self.selection = line.context
        else:
            raise RuntimeError(
                "Undo line edit voice rate is missing a node")

    async def redo_line_voice_rate_edited(self, line, next, **_):
        line.voice.rate = next
        if line.context is not None and line.voice.context is not None:
            line.voice.context.voice_rate = next
            self.selection = line.context
        else:
            raise RuntimeError(
                "Redo line edit voice rate is missing a node")

    @on(ScriptEditLineVoiceId)
    async def line_voice_id_edited(self, event):
        async with self.disable_actions_toolbar():
            line = event.line
            voice = line.voice
            prev = voice.id
            next = event.id
            voice.id = next

            node = voice.context
            node.voice_id = next
            self.selection = node

            self.actions.add(
                Actions(
                    self.undo_line_voice_id_edited,
                    self.redo_line_voice_id_edited,
                    Actions.context(
                        line=line,
                        prev=prev,
                        next=next)))

    async def undo_line_voice_id_edited(self, line, prev, **_):
        line.voice.id = prev
        if line.context is not None and line.voice.context is not None:
            line.voice.context.voice_id = prev
            self.selection = line.context
        else:
            raise RuntimeError(
                "Undo line edit voice id is missing a node")

    async def redo_line_voice_id_edited(self, line, next, **_):
        line.voice.id = next
        if line.context is not None and line.voice.context is not None:
            line.voice.context.voice_id = next
            self.selection = line.context
        else:
            raise RuntimeError(
                "Redo line edit voice id is missing a node")

    @on(ScriptAddLineAbove)
    async def line_above_added(self, event):
        async with self.disable_actions_toolbar():
            before = event.line
            line = (
                self.script.add(
                    before.clone(text=""),
                    before=before))

            node = ScriptLine(line)
            await self.lines.mount(node, before=before.context)
            node.editing = True
            self.selection = node

            self.actions.add(
                Actions(
                    self.undo_line_above_added,
                    self.redo_line_above_added,
                    Actions.context(
                        before=before,
                        line=line)))

    async def undo_line_above_added(self, before, line, **_):
        self.script.remove(line)
        if before.context is not None and line.context is not None:
            self.selection = before.context
            await line.context.remove()
        else:
            raise RuntimeError(
                "Undo line addition above is missing a node")

    async def redo_line_above_added(self, before, line, **_):
        self.script.add(line, before=before)
        if before.context is not None:
            node = ScriptLine(line)
            await self.lines.mount(node, before=before.context)
            node.editing = True
            self.selection = node
        else:
            raise RuntimeError(
                "Redo line addition above is missing a node")

    @on(ScriptAddLineBelow)
    async def line_below_added(self, event):
        async with self.disable_actions_toolbar():
            after = event.line
            line = (
                self.script.add(
                    after.clone(text=""),
                    after=after))

            node = ScriptLine(line)
            await self.lines.mount(node, after=after.context)
            node.editing = True
            self.selection = node

            self.actions.add(
                Actions(
                    self.undo_line_below_added,
                    self.redo_line_below_added,
                    Actions.context(
                        after=after,
                        line=line)))

    async def undo_line_below_added(self, after, line, **_):
        self.script.remove(line)
        if after.context is not None and line.context is not None:
            self.selection = after.context
            await line.context.remove()
        else:
            raise RuntimeError(
                "Undo line addition below is missing a node")

    async def redo_line_below_added(self, after, line, **_):
        self.script.add(line, after=after)
        if after.context is not None:
            node = ScriptLine(line)
            await self.lines.mount(node, after=after.context)
            node.editing = True
            self.selection = node
        else:
            raise RuntimeError(
                "Redo line addition below is missing a node")

    @on(ScriptRemoveLine)
    async def line_removed(self, event):
        async with self.disable_actions_toolbar():
            line = event.line
            _, after = self.script.remove(line)

            node = line.context
            if self.selection is node:
                self.selection = None
            await node.remove()

            self.actions.add(
                Actions(
                    self.undo_line_removed,
                    self.redo_line_removed,
                    Actions.context(
                        line=line,
                        after=after)))

    async def undo_line_removed(self, line, after, **_):
        self.script.add(line, before=after)
        if not after or after.context is not None:
            node = ScriptLine(line)
            await self.lines.mount(node, before=after and after.context)
            self.selection = node

    async def redo_line_removed(self, line, **_):
        self.script.remove(line)
        node = line.context
        if node is not None:
            if self.selection is node:
                self.selection = None
            await node.remove()
        else:
            raise RuntimeError(
                "Redo line removal is missing a node")

    def save(self, quit=False):
        if self.filename is not None:
            with open(self.filename, "w") as script:
                script.write(
                    json.dumps(
                        self.script.serialize(),
                        indent=4))
            if quit:
                self.app.pop_screen()
            else:
                self.actions.mark_clean()
                self.file_toolbar.save_disabled = self.actions.is_clean
                self.update_title()
        else:
            self.save_as(quit=quit)

    def save_as(self, quit=False):
        def handle_save_screen(result):
            if result is not None:
                self.filename = result.path
                self.save(quit=quit)

        self.app.push_screen(
            SaveScriptFileScreen(),
            handle_save_screen)

    def close(self):
        def handle_closing_screen(result):
            if result is False:
                self.app.pop_screen()
            elif result is True:
                self.save(quit=True)

        if self.actions.is_clean:
            self.app.pop_screen()
        else:
            self.app.push_screen(
                SaveBeforeClosingScreen(self.filename),
                handle_closing_screen)

    def action_close(self):
        self.close()

    def update_title(self):
        filename = (
            self.filename.name
                if self.filename is not None
                else "[new script]")
        unsaved = (
            ""
                if self.actions.is_clean
                else " *")
        self.title = f"{filename}{unsaved}"

    def watch_selection(self, prev, next):
        if next is not prev:
            if prev is not None:
                prev.editing = False
                prev.selected = False
            if next is not None:
                next.selected = True

    def watch_filename(self):
        self.update_title()

    def watch_play_lines(self):
        self.actions_toolbar.stop_disabled = self.play_lines is None
        self.actions_toolbar.play_disabled = self.play_lines is not None
