from abc import ABC


class MongoType(ABC):
    _python_type = object

    def __init__(self, unique=False, serialize=True, serialize_as=None, default=None, nullable=True):

        if default and not issubclass(type(default), self._python_type):
            raise TypeError(
                f'Got type {type(default).__name__} for default kwarg '
                f'but must be of type {self._python_type.__name__}'
            )

        self._unique = unique
        self._serialize = serialize
        self._serialize_as = serialize_as
        self._default = default
        self._nullable = nullable

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return \
            self._unique == other._unique and \
            self._serialize == other._serialize and \
            self._default == other._default and \
            self._nullable == other._nullable
