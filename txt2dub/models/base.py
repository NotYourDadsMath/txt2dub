
class Model(object):
    """Base class for models."""

    @property
    def context(self):
        """Application context can be stored in the model, e.g.
        a DOM node that "owns" this model instance."""
        return self._context

    @context.setter
    def context(self, context):
        self._context = context

    def __init__(self):
        self._context = None

    def serialize(self):
        """Returns a JSON-serializable representation of this model."""

        return None

    @classmethod
    def deserialize(cls, data, meta):
        """Returns a model instance for the given deserialized
        JSON representation."""

        return data
