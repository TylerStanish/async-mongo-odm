import numbers

from odm.type.MongoType import MongoType


class MongoNumber(MongoType):
    _python_type = numbers.Number
