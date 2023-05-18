import asyncio
import json
import sys
from ..models import ScriptMetadata, ScriptVoiceMetadata


class TTSInterface(object):
    """The asynchronous text-to-speech interface."""

    def __init__(self, runner):
        self.runner = runner
        self.await_process = None
        self.lock = asyncio.Lock()

    @property
    def process(self):
        if self.await_process is None:
            self.await_process = (
                self.runner(
                    asyncio.create_subprocess_exec(
                        sys.executable,
                        "-m",
                        "txt2dub.tts.__main__",
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE)))
        return self.await_process()

    async def writeline(self, value):
        try:
            process = await self.process
            process.stdin.write(f"{value}\n".encode("utf-8"))
        except ValueError:
            pass

    async def readline(self):
        try:
            process = await self.process
            return (
                (await process.stdout.readline())
                .decode("utf-8"))
        except ValueError:
            pass

    async def request(self, **kwargs):
        async with self.lock:
            await self.writeline(json.dumps(kwargs))
            response = await self.readline()
            if response:
                result = json.loads(response)
                if result and "type" in result and result["type"] == "result":
                    return result["value"]
                else:
                    raise (
                        ValueError(
                            result["value"]
                                if "value" in result
                                else "Unknown TTS engine error"))
            else:
                raise ValueError("TTS engine disconnected")

    async def meta(self):
        meta = await self.request(command="meta")
        return (
            ScriptMetadata(
                meta["version"],
                meta["driver"],
                [
                    ScriptVoiceMetadata(
                        voice["id"],
                        voice["name"])
                        for voice
                        in meta["voices"]
                ]))

    async def play(self, text, voice, rate):
        return (
            await (
                self.request(
                    command="play",
                    text=text,
                    voice=voice,
                    rate=rate)))

    async def generate(self, path, script):
        return (
            await (
                self.request(
                    command="generate",
                    path=f"{path.absolute()}",
                    script=script.serialize())))

    async def terminate(self):
        if self.await_process is not None:
            process = await self.await_process()
            process.terminate()
            self.await_process = None


def create_tts(runner):
    return TTSInterface(runner)
