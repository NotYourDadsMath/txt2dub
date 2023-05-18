import json
import pathlib
import signal
import sys
import tempfile
import zipfile

import pyttsx3


class Interpreter(object):
    """The text-to-speech interpreter."""

    def __init__(self, version):
        self.version = version
        self.engine = pyttsx3.init()
        self.alive = True
        signal.signal(signal.SIGTERM, self.die)

    def die(self):
        self.alive = False

    def readline(self):
        if self.alive:
            try:
                return sys.stdin.readline()
            except ValueError:
                pass

    def writeline(self, value):
        if self.alive:
            try:
                sys.stdout.write(f"{value}\n")
                sys.stdout.flush()
            except ValueError:
                pass

    def run(self):
        more = True
        while more:
            try:
                request = self.readline()
                if request:
                    try:
                        self.writeline(
                            json.dumps({
                                "type": "result",
                                "value": self.dispatch(json.loads(request)),
                            }))
                    except (json.JSONDecodeError, ValueError) as error:
                        self.writeline(
                            json.dumps({
                                "type": "error",
                                "value": f"{error}",
                            }))
                    except Exception as error:
                        self.writeline(
                            json.dumps({
                                "type": "error",
                                "value": f"{error}",
                            }))
                        more = False
                else:
                    more = False
            except KeyboardInterrupt:
                more = False

    def dispatch(self, request):
        if "command" in request:
            command = request["command"]
            if command == "meta":
                return self.meta()
            elif command == "play":
                if ("text" in request and
                    "voice" in request and
                    "rate" in request):
                    return self.play(request["text"], request["voice"], request["rate"])
                else:
                    raise (
                        ValueError(
                            "play command requires text, voice and rate " \
                            "parameters"))

            elif command == "generate":
                if ("path" in request and
                    "script" in request):
                    return self.generate(request["path"], request["script"])
                else:
                    raise (
                        ValueError(
                            "generate command requires path and script " \
                            "parameters"))
            else:
                raise ValueError(f"Unknown command {command}")

    def meta(self):
        driver = self.engine.proxy._driver.__class__
        return {
           "version": self.version,
           "driver": f"{driver.__module__}.{driver.__name__}",
           "voices": [
                {
                    "id": voice.id,
                    "name": voice.name
                }
                    for voice in
                    self.engine.getProperty("voices")
           ]
        }

    def play(self, text, voice, rate):
        self.engine.setProperty("voice", voice)
        self.engine.setProperty("rate", rate)
        self.engine.say(text)
        self.engine.runAndWait()
        return "ok"

    def generate(self, path, script):
        with zipfile.ZipFile(path, "w") as zf:
            with zf.open("lines.txt", "w") as f:
                for n, line in enumerate(script["lines"]):
                    text = line["text"].strip()
                    f.write(f"{n:0>4d}: {text}\n".encode("utf-8"))
            with zf.open("script.txt", "w") as f:
                for line in script["lines"]:
                    text = line["text"].strip()
                    if text:
                        f.write(f"{text}\n".encode("utf-8"))
            with tempfile.TemporaryDirectory() as tmp:
                for n, line in enumerate(script["lines"]):
                    text = line["text"].strip()
                    if text:
                        name = pathlib.Path(f"{n:0>4d}.mp3")
                        tmp_path = pathlib.Path(tmp) / name
                        self.engine.setProperty("voice", line["voice"]["id"])
                        self.engine.setProperty("rate", line["voice"]["rate"])
                        self.engine.save_to_file(text, f"{tmp_path}")
                        self.engine.runAndWait()
                        with open(tmp_path, "r+b") as t:
                            with zf.open(f"{name}", "w") as f:
                                f.write(t.read())
        return "ok"
