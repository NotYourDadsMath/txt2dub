from textual import on, work
from textual.containers import Container, Vertical
from textual.events import (
    Blur, Click, DescendantFocus, Key, Mount, Unmount,)
from textual.message import Message
from textual.reactive import var
from textual.widgets import Button, Input , Select, Static
from .messages import (
    ScriptSelectLine, ScriptPlayLine, ScriptEditLineText,
    ScriptEditLineVoiceRate, ScriptEditLineVoiceId,
    ScriptMoveLineUp, ScriptMoveLineDown,
    ScriptRemoveLine, ScriptAddLineAbove, ScriptAddLineBelow,)


class ScriptLineEditingToolbar(Static):
    """The toolbar for editing a script line's text."""

    edit_disabled = var(False)

    class Edit(Message):
        """Line edit requested."""

    class Play(Message):
        """Line play requested."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edit_button = None

    def compose(self):
        with Container(classes="singular group"):
            self.edit_button = (
                Button(
                    "\N{PENCIL}",
                    id="edit",
                    classes="first control",
                    variant="primary"))
            yield self.edit_button

            yield (
                Button(
                    "\N{BLACK RIGHT-POINTING TRIANGLE}",
                    id="play",
                    classes="last control",
                    variant="success"))

    @on(Button.Pressed, "#edit")
    def edit_pressed(self):
        self.post_message(self.Edit())

    @on(Button.Pressed, "#play")
    def play_pressed(self):
        self.post_message(self.Play())

    def watch_edit_disabled(self):
        self.edit_button.disabled = self.edit_disabled


class ScriptLineVoiceRateInput(Input):
    """The voice rate input for a script line."""

    class Cancel(Message):
        """Line voice rate cancel requested."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class Edit(Message):
        """Line voice rate edit requested."""

        def __init__(self, play=False, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.play = play

    @on(Key)
    def input_keyed(self, event):
        if event.name == "escape":
            event.stop()
            self.post_message(self.Cancel())

    @on(Blur)
    def input_blurred(self):
        self.post_message(self.Edit())

    @on(Input.Submitted)
    def input_submitted(self, event):
        event.stop()
        self.post_message(self.Edit(play=True))


class ScriptLineVoiceRateButton(Button):
    """The voice rate button for a script line."""

    class Clicked(Message):
        """Button click requested."""

        def __init__(self, button, mouse_event, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.button = button
            self.mouse_event = mouse_event

        @property
        def control(self):
            return self.button

    @on(Click)
    def button_clicked(self, event):
        self.post_message(
            self.Clicked(
                self,
                event))


class ScriptLineVoiceToolbar(Static):
    """The toolbar for modifying a script line's voice settings."""

    MIN_RATE = 25
    MAX_RATE = 500

    voice_id = var(None)
    voice_rate = var(None)

    class Id(Message):
        """Voice id change requested."""

        def __init__(self, id, play=False, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.id = id
            self.play = play

    class Rate(Message):
        """Voice rate change requested."""

        def __init__(self, rate, play=False, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.rate = rate
            self.play = play

    def __init__(self, voice, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.voice = voice
        self.voice_rate_input = None
        self.voice_id_select = None

    def compose(self):
        with Container(classes="column singular"):
            with Container(classes="first row"):
                with Container(classes="singular group"):
                    yield (
                        ScriptLineVoiceRateButton(
                            "-",
                            id="slower",
                            classes="first control"))

                    self.voice_rate_input = (
                        ScriptLineVoiceRateInput(
                            id="rate",
                            value=f"{self.voice.rate}",
                            classes="narrow control"))
                    yield self.voice_rate_input

                    yield (
                        ScriptLineVoiceRateButton(
                            "+",
                            id="faster",
                            classes="last control"))
            with Container(classes="last row"):
                with Container(classes="singular group"):
                    self.voice_id_select = (
                        Select(
                            [
                                (voice.name, voice.id)
                                    for voice
                                    in self.voice.script.meta.voices
                            ],
                            id="id",
                            prompt="Voice",
                            allow_blank=False,
                            value=self.voice.id,
                            classes="singular control"))
                    yield self.voice_id_select

    @on(Mount)
    def voice_mounted(self):
        self.voice.context = self

    @on(Unmount)
    def voice_unmounted(self):
        self.voice.context = None

    # HACK: As of textual@0.24.1, this should use the "#id" selector
    # for potential disambiguation, but the `control` attribute does
    # not appear to be implemented for `Select.Changed`
    @on(Select.Changed)
    def id_changed(self, event):
        self.post_message(
            self.Id(
                event.value,
                play=True))

    @on(ScriptLineVoiceRateInput.Cancel)
    def rate_cancelled(self, event):
        self.voice_rate_input.value = f"{self.voice.rate}"

    @on(ScriptLineVoiceRateInput.Edit)
    def rate_edited(self, event):
        try:
            rate = int(self.voice_rate_input.value)
            if rate >= self.MIN_RATE and rate <= self.MAX_RATE:
                self.post_message(
                    self.Rate(
                        rate,
                        play=event.play))
            else:
                self.voice_rate_input.value = f"{self.voice.rate}"
        except ValueError:
            self.voice_rate_input.value = f"{self.voice.rate}"

    @on(ScriptLineVoiceRateButton.Clicked, "#slower")
    def slower_clicked(self, event):
        rate = (
            (self.voice.rate - 1)
                if event.mouse_event.ctrl
                else ((((self.voice.rate + 24) // 25) - 1) * 25))
        if rate >= self.MIN_RATE and rate <= self.MAX_RATE:
            self.post_message(
                self.Rate(
                    rate,
                    play=True))

    @on(ScriptLineVoiceRateButton.Clicked, "#faster")
    def faster_clicked(self, event):
        rate = (
            (self.voice.rate + 1)
                if event.mouse_event.ctrl
                else (((self.voice.rate // 25) + 1) * 25))
        if rate >= self.MIN_RATE and rate <= self.MAX_RATE:
            self.post_message(
                self.Rate(
                    rate,
                    play=True))

    def watch_voice_id(self):
        if self.voice_id is not None:
            # HACK: As of textual@0.24.1, we can't
            # update the `Select` widget until it has
            # created the `_options` attribute.
            if hasattr(self.voice_id_select, "_options"):
                self.voice_id_select.value = self.voice_id

    def watch_voice_rate(self):
        if self.voice_rate is not None:
            self.voice_rate_input.value = f"{self.voice_rate}"


class ScriptLineMovingToolbar(Static):
    """The toolbar for controlling a script line's position."""

    class Up(Message):
        """Line up requested."""

    class Down(Message):
        """Line down requested."""

    def compose(self):
        with Vertical(classes="singular group"):
            yield (
                Button(
                    "\N{BLACK UP-POINTING TRIANGLE}",
                    id="up",
                    classes="first control"))
            yield (
                Button(
                    "\N{BLACK DOWN-POINTING TRIANGLE}",
                    id="down",
                    classes="last control"))

    @on(Button.Pressed, "#up")
    def up_pressed(self):
        self.post_message(self.Up())

    @on(Button.Pressed, "#down")
    def down_pressed(self):
        self.post_message(self.Down())


class ScriptLineManagingToolbar(Static):
    """The toolbar for managing creation and deletion of script lines."""

    class Remove(Message):
        """Line removal requested."""

    class AddAbove(Message):
        """Line add above requested."""

    class AddBelow(Message):
        """Line add below requested."""

    def compose(self):
        with Container(classes="row singular"):
            with Container(classes="first column"):
                with Container(classes="singular group"):
                    yield (
                        Button(
                            "\N{BLACK UP-POINTING TRIANGLE} +",
                            id="add-above",
                            classes="first control",
                            variant="warning"))
                    yield (
                        Button(
                            "\N{BLACK DOWN-POINTING TRIANGLE} +",
                            id="add-below",
                            classes="last control",
                            variant="warning"))
            with Container(classes="last column"):
                with Container(classes="singular group"):
                    yield(
                        Button(
                            "x",
                            id="remove",
                            classes="singular control",
                            variant="error"))

    @on(Button.Pressed, "#remove")
    def remove_pressed(self):
        self.post_message(self.Remove())

    @on(Button.Pressed, "#add-above")
    def add_above_pressed(self):
        self.post_message(self.AddAbove())

    @on(Button.Pressed, "#add-below")
    def add_below(self):
        self.post_message(self.AddBelow())


class ScriptLineTextContainer(Container):
    """The text container for a script line."""

    class ToggleEditing(Message):
        """Line toggle editing requested."""

    @on(Click)
    def container_clicked(self):
        self.post_message(self.ToggleEditing())


class ScriptLineTextInput(Input):
    """The text input for a script line."""

    class Cancel(Message):
        """Line text cancel requested."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class Edit(Message):
        """Line text edit requested."""

        def __init__(self, submit=False, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.submit = submit

    @on(Key)
    def input_keyed(self, event):
        if not self.disabled and event.name == "escape":
            event.stop()
            self.post_message(self.Cancel())

    @on(Blur)
    def input_blurred(self):
        self.post_message(self.Edit())

    @on(Click)
    def input_clicked(self, event):
        event.stop()

    @on(Input.Submitted)
    def input_submitted(self, event):
        event.stop()
        self.post_message(self.Edit(submit=True))


class ScriptLine(Static):
    """The editor for a script line."""

    editing = var(False)
    selected = var(False)
    text = var(None)

    def __init__(self, line, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line = line
        self.editing_toolbar = None
        self.text_container = None
        self.text_static = None
        self.text_input = None
        line.context = self

    def compose(self):
        self.editing_toolbar = (
            ScriptLineEditingToolbar(
                classes="left vertical toolbar"))
        yield self.editing_toolbar

        yield (
            ScriptLineVoiceToolbar(
                self.line.voice,
                classes="horizontal toolbar width--auto margin-left--1"))

        self.text_container = (
            ScriptLineTextContainer(
                classes="text margin-left--1"))
        with self.text_container:
            self.text_static = Static(self.line.text, id="text")
            yield self.text_static

            self.text_input = ScriptLineTextInput(value=self.line.text)
            yield self.text_input
        yield (
            ScriptLineMovingToolbar(
                classes="vertical toolbar margin-left--1"))
        yield (
            ScriptLineManagingToolbar(
                classes="vertical toolbar height--auto margin-left--1"))

    @on(Unmount)
    def line_unmounted(self):
        self.line.context = None

    @on(Click)
    def line_clicked(self):
        self.post_message(
            ScriptSelectLine(
                self.line))

    @on(DescendantFocus)
    def line_focused(self):
        self.post_message(
            ScriptSelectLine(
                self.line))

    @on(ScriptLineMovingToolbar.Up)
    def toolbar_up(self):
        self.post_message(
            ScriptMoveLineUp(
                self.line))

    @on(ScriptLineMovingToolbar.Down)
    def toolbar_down(self):
        self.post_message(
            ScriptMoveLineDown(
                self.line))

    @on(ScriptLineTextContainer.ToggleEditing)
    def text_container_toggle_editing(self):
        self.editing = not self.editing
        if not self.editing:
            self.text_edited()

    @on(ScriptLineTextInput.Cancel)
    def text_input_cancelled(self):
        self.editing = False
        self.text_input.value = self.line.text

    @on(ScriptLineTextInput.Edit)
    def text_input_edited(self, event):
        self.editing = False
        self.text_edited(submit=event.submit)

    @on(ScriptLineEditingToolbar.Play)
    def toolbar_play(self):
        self.post_message(
            ScriptPlayLine(
                self.line))

    @on(ScriptLineEditingToolbar.Edit)
    def toolbar_edit(self):
        self.editing = True

    @on(ScriptLineVoiceToolbar.Id)
    def toolbar_id(self, event):
        if event.id != self.line.voice.id:
            self.post_message(
                ScriptEditLineVoiceId(
                    self.line,
                    event.id))
            if event.play:
                self.post_message(
                    ScriptPlayLine(
                        self.line))

    @on(ScriptLineVoiceToolbar.Rate)
    def toolbar_rate(self, event):
        if event.rate != self.line.voice.rate:
            self.post_message(
                ScriptEditLineVoiceRate(
                    self.line,
                    event.rate))
            if event.play:
                self.post_message(
                    ScriptPlayLine(
                        self.line))

    @on(ScriptLineManagingToolbar.Remove)
    def toolbar_remove(self):
        self.post_message(
            ScriptRemoveLine(
                self.line))

    @on(ScriptLineManagingToolbar.AddAbove)
    def toolbar_add_above(self):
        self.post_message(
            ScriptAddLineAbove(
                self.line))

    @on(ScriptLineManagingToolbar.AddBelow)
    def toolbar_add_below(self):
        self.post_message(
            ScriptAddLineBelow(
                self.line))

    def text_edited(self, submit=False):
        prev = self.line.text
        next = self.text_input.value
        if (prev != next):
            self.post_message(
                ScriptEditLineText(
                    self.line,
                    next,
                    submit))

    def watch_editing(self):
        if self.editing:
            self.text_container.add_class("editing")
            self.text_input.disabled = False
            self.text_input.focus()
            self.post_message(
                ScriptSelectLine(
                    self.line))
        else:
            self.text_container.remove_class("editing")
            self.text_input.disabled = True
        self.editing_toolbar.edit_disabled = self.editing

    def watch_selected(self):
        if self.selected:
            self.add_class("selected")
            self.scroll_visible()
        else:
            self.remove_class("selected")

    def watch_text(self):
        if self.text is not None:
            self.text_input.value = self.text
            self.text_static.update(self.text)
