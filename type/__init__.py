"""
Step 1: Register all fields that extend from MongoType
Step 2: Make all of these fields properties
Step 2.5: Have getters, setters on the properties that update the _value in each MongoType
"""


class MongoType:
    _value = None


class String(MongoType):
    pass


class Number(MongoType):
    pass