from odm.meta import FieldStoreMixin
from .MongoType import MongoType


class MongoObject(MongoType, FieldStoreMixin):
    """
    Extend this when you know ahead of time what fields the nested object will have
    """
    @property
    def _python_type(self):
        return self.__class__

    @classmethod
    def new(cls, **kwargs):
        # preferably do some validation, like check if all nullable=False fields are populated, type checking, etc.
        # TODO type-checking
        obj = cls()
        cls.validate_and_construct(obj, kwargs)
        return obj

    @classmethod
    def from_dict(cls, d: dict):
        return cls.new(**d)

    def as_dict(self):
        """

        :return: A dict of the declared class fields and their 'self' object values
        """
        d = {}

        for key, val in self._get_declared_class_mongo_attrs():
            if val._serialize:
                d[key] = getattr(self, key)

        return d
