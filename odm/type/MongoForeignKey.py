from bson import ObjectId

from .MongoType import MongoType


class MongoForeignKey(MongoType):
    _python_type = ObjectId
