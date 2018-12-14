from odm.type.MongoType import MongoType


class MongoId(MongoType):
    _python_type = str

    def __init__(self, serialize=True, default=None):
        super().__init__(serialize=serialize, default=default)
