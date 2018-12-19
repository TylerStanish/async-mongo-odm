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

        def __init__(self, _strict: bool=True, **kwargs):
            """
            :param _strict: Used for internal purposes. Don't mess with this but if you do change it to False if
            you don't want type-checking when constructing objects
            """
            self.validate_and_construct(self, kwargs, engine=engine)

        def as_dict(self):
            """
            Serializes all properties of a given object. Should be called recursively for nested Mongo objects
            :return: A dict of the property variables
            """
            d = {}
            for key, val in self._get_declared_class_mongo_attrs(engine):
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
        def from_dict(cls, d: dict, _strict: bool=True):
            """

            :param d:
            :param _strict: Used for internal purposes. Don't mess with this but if you do change it to False if
            you don't want type-checking when constructing objects
            :return:
            """
            return cls(_strict, **d)

        @classmethod
        async def from_id(cls, id_str: str):
            return await cls.find_one({'_id': ObjectId(id_str)})

        @classmethod
        async def find_one(cls, query):
            collection = getattr(engine.client[engine.db_name], cls.__collection_name__)
            return cls.from_dict(await collection.find_one(query), _strict=False)

    return Document
