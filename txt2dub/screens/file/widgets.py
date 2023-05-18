from textual import on
from textual.message import Message
from textual.widgets import DirectoryTree


class ScriptDirectoryTree(DirectoryTree):
    """A directory tree for selecting a path or file."""

    class DirectorySelected(Message):
        """A message for directory selection."""

        def __init__(self, path):
            super().__init__()
            self.path = path

    def __init__(self, path, suffixes, *args, **kwargs):
        super().__init__(path, *args, **kwargs)
        self.suffixes = suffixes

    def filter_paths(self, paths):
        for path in paths:
            if not path.name.startswith("."):
                if path.is_dir():
                    yield path
                elif path.is_file():
                    suffixes = path.suffixes[-len(self.suffixes):]
                    if (len(suffixes) == len(self.suffixes) and
                        all(suffix == check
                                for suffix, check
                                in zip(suffixes, self.suffixes))):
                        yield path

    @on(DirectoryTree.NodeSelected)
    def node_selected(self, event):
        data = event.node.data
        if data is not None and data.path.is_dir():
            self.post_message(
                self.DirectorySelected(
                    data.path))
