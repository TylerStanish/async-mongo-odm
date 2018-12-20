from abc import ABC

from odm.meta import FieldStoreMixin
from .MongoType import MongoType


class MongoObject(MongoType, FieldStoreMixin, ABC):
    """
    Extend this when you know ahead of time what fields the nested object will have
    """
    @property
    def _python_type(self):
        return self.__class__

    @classmethod
    def new(cls, **kwargs):
        obj = cls()
        FieldStoreMixin.__init__(obj, **kwargs)
        return obj

    @classmethod
    def from_dict(cls, d: dict, _strict=True):
        kwargs = cls._clean_input_dict(d)
        return cls.new(**kwargs)
