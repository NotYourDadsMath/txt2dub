import re
from .base import Model


rx_ms_name = re.compile(r"^Microsoft\s+(?P<name>[^\s]+)")


class ScriptVoiceMetadata(object):
    """Metadata used for script voice serialization."""

    def __init__(self, id, name):
        match = rx_ms_name.match(name)

        self.id = id
        self.name = (
            match.group("name")
                if match is not None
                else name)


class ScriptMetadata(object):
    """Metadata used for script serialization."""

    def __init__(self, version, driver, voices):
        """Create script metadata.

        `version`
            the version of txt2dub
        `driver`
            the qualified name of the pyttsx3 driver class,
            usually from `engine.proxy._driver.__class__`
        `voices`
            a list of `ScriptVoiceMetadata` for voices available
            from the driver
        """
        self.version = version
        self.driver = driver
        self.voices = voices


class ScriptVoiceModel(Model):
    """The model for the voice used in one line of a script."""

    def __init__(self, script, id, rate):
        """Create a script voice.

        `script`
            the script this voice belongs to
        `id`
            the voice ID from the TTS driver
        `rate`
            the integer rate rate of speech in words per minutes
        """
        super().__init__()
        self.script = script
        self.id = id
        self.rate = rate

    def clone(self, id=None, rate=None):
        return (
            self.__class__(
                self.script,
                id
                    if id is not None
                    else self.id,
                rate
                    if rate is not None
                    else self.rate))

    def serialize(self):
        return {
            "id": self.id,
            "rate": self.rate,
        }

    @classmethod
    def new(cls, script):
        return cls(script, script.meta.voices[0].id, 200)

    @classmethod
    def deserialize(cls, script, data):
        return (
            cls(script,
                data["id"]
                    if any(
                        data["id"] == voice.id
                            for voice
                            in script.meta.voices)
                    else script.meta.voices[0].id,
                data["rate"]))


class ScriptLineModel(Model):
    """The model for one line of a script."""

    def __init__(self, script, text, voice):
        """Create a script line.

        `script`
            the script this line belongs to
        `text`
            the text for this script line
        `voice`
            the `ScriptVoiceModel` to use for this script line
        """
        super().__init__()
        self.script = script
        self.text = text
        self.voice = voice
        self.prev = None
        self.next = None

    def __iter__(self):
        line = self
        while line is not None:
            yield line
            line = line.next

    def clone(self, text=None, voice=None):
        return (
            self.__class__(
                self.script,
                text
                    if text is not None
                    else self.text,
                voice
                    if voice is not None
                    else self.voice.clone()))

    def link(self, prev, next):
        """Link a script line.

        `prev`
            the previous `ScriptLineModel`
        `next`
            the next `ScriptLineModel`
        """
        self.prev = prev
        self.next = next
        if prev is not None:
            prev.next = self
        if next is not None:
            next.prev = self
        return self

    def serialize(self):
        return {
            "text": self.text,
            "voice": self.voice.serialize()
        }

    @classmethod
    def new(cls, script):
        return cls(script, "", ScriptVoiceModel.new(script))

    @classmethod
    def deserialize(cls, script, data):
        return (
            cls(script,
                data["text"],
                ScriptVoiceModel.deserialize(
                    script,
                    data["voice"])))


class ScriptModel(Model):
    """The model for a script."""

    def __init__(self, meta):
        """Create a script.

        `meta`
            the `ScriptMetadata` used for this model
        """
        super().__init__()
        self.meta = meta
        self.head = None
        self.tail = None

    def __iter__(self):
        line = self.head
        while line is not None:
            yield line
            line = line.next

    def serialize(self):
        return {
            "version": self.meta.version,
            "driver": self.meta.driver,
            "lines": [line.serialize() for line in self]
        }

    def is_empty(self):
        return self.head is None and self.tail is None

    def is_head(self, line):
        return line is not None and line is self.head

    def is_tail(self, line):
        return line is not None and line is self.tail

    def add(self, line, after=None, before=None):
        if after is None and before is None:
            if self.head is None:
                self.head = line
            self.tail = line.link(self.tail, None)
            return line
        elif after is not None:
            if after is self.tail:
                self.tail = line.link(self.tail, None)
                return line
            else:
                return line.link(after, after.next)
        elif before is not None:
            if before is self.head:
                self.head = line.link(None, self.head)
                return line
            else:
                return line.link(before.prev, before)
        else:
            raise (
                ValueError(
                    "Only one of `after` or `before` may be passed"))

    def remove(self, line):
        prev = line.prev
        next = line.next
        if line is self.head:
            self.head = line.next
        else:
            line.prev.next = line.next
        if line is self.tail:
            self.tail = line.prev
        else:
            line.next.prev = line.prev
        line.link(None, None)
        return (prev, next)

    @classmethod
    def new(cls, meta):
        script = cls(meta)
        script.head = script.tail = ScriptLineModel.new(script)
        return script

    @classmethod
    def deserialize(cls, data, meta):
        if data["version"] != meta.version:
            pass
        if data["driver"] != meta.driver:
            pass
        script = cls(meta)
        for line in (
            ScriptLineModel.deserialize(script, line)
                for line
                in data["lines"]):
            if script.head is None:
                script.head = line
            script.tail = line.link(script.tail, None)
        return script
