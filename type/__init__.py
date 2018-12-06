"""
Step 1: Register all fields that extend from MongoType
Step 2: Make all of these fields properties
Step 2.5: Have getters, setters on the properties that update the _value in each MongoType
"""


class MongoType:
    pass


class MongoString(MongoType):
    pass


class MongoNumber(MongoType):
    pass


class MongoObject(MongoType):
    pass
