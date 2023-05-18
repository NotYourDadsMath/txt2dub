from textual.message import Message


class ScriptMessage(Message):
    """Base script message."""

    def __init__(self, line, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line = line


class ScriptSelectLine(ScriptMessage):
    """Select line requested."""


class ScriptMoveLineUp(ScriptMessage):
    """Script line move up requested."""


class ScriptMoveLineDown(ScriptMessage):
    """Script line move down requested."""


class ScriptPlayLine(ScriptMessage):
    """Script line play requested."""


class ScriptRemoveLine(ScriptMessage):
    """Script line removal requested."""


class ScriptAddLineAbove(ScriptMessage):
    """Script line add above requested."""


class ScriptAddLineBelow(ScriptMessage):
    """Script line add below requested."""


class ScriptEditLineText(ScriptMessage):
    """Script line edit requested."""

    def __init__(self, line, text, submit, *args, **kwargs):
        super().__init__(line, *args, **kwargs)
        self.text = text
        self.submit = submit


class ScriptEditLineVoiceRate(ScriptMessage):
    """Script line edit voice rate requested."""

    def __init__(self, line, rate, *args, **kwargs):
        super().__init__(line, *args, **kwargs)
        self.rate = rate


class ScriptEditLineVoiceId(ScriptMessage):
    """Script line edit voice id requested."""

    def __init__(self, line, id, *args, **kwargs):
        super().__init__(line, *args, **kwargs)
        self.id = id
