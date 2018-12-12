class MongoType:
    def __init__(self, unique=False, serialize=True, default=None, nullable=True):
        self.unique = unique
        self.serialize = serialize
        self.default = default
        self.nullable = nullable


class MongoId(MongoType):
    pass


class MongoString(MongoType):
    pass


class MongoNumber(MongoType):
    pass
