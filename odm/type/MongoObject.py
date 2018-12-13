from odm.meta import FieldStoreMixin
from odm.type.MongoType import MongoType


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
        for attr, val in cls._get_declared_class_mongo_attrs():
            arg_val = kwargs.get(attr)
            if not val._nullable and arg_val is None:
                raise ValueError(f'Got null argument for {attr} but {attr} is not nullable')
            setattr(obj, attr, arg_val)
        return obj

    @classmethod
    def from_dict(cls, d: dict):
        return cls.new(**d)

    def as_dict(self):
        """

        :return: A dict of the declared class fields and their 'self' object values
        """
        return {key: getattr(self, key) for key, val in self._get_declared_class_mongo_attrs()}