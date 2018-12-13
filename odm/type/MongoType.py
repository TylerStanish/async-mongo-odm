class MongoType:
    def __init__(self, unique=False, serialize=True, default=None, nullable=True):
        self._unique = unique
        self._serialize = serialize
        self._default = default
        self._nullable = nullable

    def __eq__(self, other):
        if not isinstance(other, MongoType):
            return False
        return \
            self._unique == other._unique and \
            self._serialize == other._serialize and \
            self._default == other._default and \
            self._nullable == other._nullable
