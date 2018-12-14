import json

from bson import ObjectId

from odm.meta import FieldStoreMixin
from odm.type import MongoType
from odm.type import MongoObject

"""
I plan on validating new objects and not objects from the DB to ensure backwards-compatibility?
"""


def _document_factory(engine, Registrar):
    class Document(FieldStoreMixin, metaclass=Registrar):
        """
        Create a collection for each Document. Do this so that the end user doesn't have to!
        """

        def __init__(self, **kwargs):
            """
            Having this __init__ method gets rid of the warning we got, but wouldn't it be misleading to have this
            even though it is overwritten?
            :param kwargs:
            """
            self.validate_and_construct(self, kwargs)

        def as_dict(self):
            """
            Serializes all properties of a given object. Should be called recursively for nested Mongo objects
            :return: A dict of the property variables
            """
            d = {}
            for key, val in self._get_declared_class_mongo_attrs():
                if val._serialize:
                    if isinstance(val, MongoObject) and getattr(self, key) is not None:
                        d[key] = getattr(self, key).as_dict()
                    else:
                        d[key] = getattr(self, key)
            return d

        def as_json(self):
            return json.dumps(self.as_dict())

        @classmethod
        def from_json(cls, json_str: str):
            jsn = json.loads(json_str)

            # check if the json is an array or a single object
            # try:
            #     iter(jsn)
            # except TypeError:
            #     pass
            if isinstance(jsn, list):
                raise TypeError('Cannot parse JSON list. You must parse each individual object because this is a class method')

            return cls.from_dict(jsn)

        @classmethod
        def from_dict(cls, d: dict):
            return cls(**d)

        @classmethod
        def from_id(cls, id_str: str):
            ObjectId(id_str)
            pass

        @classmethod
        def find_one(cls):
            pass

    return Document
