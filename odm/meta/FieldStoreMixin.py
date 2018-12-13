from odm.type import MongoType


class FieldStoreMixin:
    @classmethod
    def _get_declared_class_mongo_attrs(cls):
        return [(attr, val) for attr, val in vars(cls).items() if isinstance(val, MongoType)]
