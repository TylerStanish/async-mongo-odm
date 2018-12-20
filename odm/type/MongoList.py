from .MongoType import MongoType


class MongoList(MongoType):
    _python_type = list

    def __init__(self, containing_type, **kwargs):
        super().__init__(**kwargs)
        self._containing_type = containing_type
