from bson import ObjectId

from odm.type.MongoType import MongoType


class MongoId(MongoType):
    _python_type = str

    def __init__(self, serialize=True):
        super().__init__(serialize=serialize)
