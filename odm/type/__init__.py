class MongoType:
    def __init__(self, unique=False):
        self.unique = unique


class MongoId(MongoType):
    pass


class MongoString(MongoType):
    pass


class MongoNumber(MongoType):
    pass


class MongoObject(MongoType):
    pass
