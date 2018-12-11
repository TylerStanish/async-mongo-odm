import json

from bson import ObjectId

from odm.type import MongoType


def _document_factory(Registrar, engine):
    class Document(metaclass=Registrar):
        """
        Create a collection for each Document. Do this so that the end user doesn't have to!
        """

        def __init__(self, **kwargs):
            """
            Having this __init__ method gets rid of the warning we got, but wouldn't it be misleading to have this
            even though it is overwritten?
            :param kwargs:
            """
            pass

        def as_dict(self):
            """
            Serializes all properties of a given object. Should be called recursively for nested Mongo objects
            :return: A dict of the property variables
            """
            d = {}
            for key, val in vars(self).items():
                if isinstance(engine.class_col_mappings[self.__class__][key], Document):
                    d[key] = getattr(self, key).as_dict()
                elif isinstance(engine.class_col_mappings[self.__class__][key], MongoType):
                    d[key] = str(getattr(self, key))
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
                raise ValueError('idk bro. u gave a list when it should just be one object (for now)')

            obj = cls(**jsn)
            return obj

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
