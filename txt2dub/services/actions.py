import inspect


class Actions(object):
    """Undo/redo actions."""
    def __init__(self, undo=None, redo=None, context=None):
        self.undo = undo
        self.redo = redo
        self.context = context or {}
        self.mark = None

    async def run(self, action):
        if inspect.iscoroutinefunction(action):
            await action(**self.context)
        else:
            action(**self.context)

    async def run_undo(self):
        if self.undo is not None:
            await self.run(self.undo)

    async def run_redo(self):
        if self.redo is not None:
            await self.run(self.redo)

    @staticmethod
    def context(**context):
        return context


class ActionsManager(object):
    """Undo/redo actions manager."""

    @property
    def undo_empty(self):
        return self.index == 0

    @property
    def redo_empty(self):
        return self.index == len(self.queue)

    @property
    def is_clean(self):
        return (
            self.index == 0
                if self.mark is None
                else (
                    self.index > 0 and
                    self.index <= len(self.queue) and
                    self.mark is self.queue[self.index - 1].mark))

    def __init__(self):
        self.queue = []
        self.index = 0
        self.mark = None

    def add(self, actions):
        if self.index != len(self.queue):
            self.queue = self.queue[:self.index]
        self.queue.append(actions)
        self.index += 1
        return self

    async def undo(self):
        if self.index > 0:
            self.index -= 1
            actions = self.queue[self.index]
            await actions.run_undo()

    async def redo(self):
        if self.index < len(self.queue):
            actions = self.queue[self.index]
            self.index += 1
            await actions.run_redo()

    def mark_clean(self):
        self.mark = object()
        if self.index > 0 and self.index <= len(self.queue):
            self.queue[self.index - 1].mark = self.mark


def context(**context):
    return context
