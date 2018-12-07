import json

from bson import ObjectId

import odm
# here we MUST import odm rather than do 'from odm import client' because we must use the most up-to-date
# version of the odm.client variable since we can call the initialize_asyncio_motor_client function


from odm.meta import Registrar, class_col_mappings, id_field_from_class
from odm.type import MongoType


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
            if isinstance(class_col_mappings[self.__class__][key], Document):
                d[key] = getattr(self, key).as_dict()
            elif isinstance(class_col_mappings[self.__class__][key], MongoType):
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

    async def save(self):
        id_field = id_field_from_class(self.__class__)
        # if self has an id, then we don't want to create a new document for it
        if not getattr(self, id_field):
            res = await getattr(getattr(odm.client, odm.db_name), self.__collection_name__).insert_one(self.as_dict())
            setattr(self, id_field, str(res.inserted_id))
        else:
            # rather we want to update it
            pass  # TODO please add code that updates the document


def is_document_instance(cls, var):
    return isinstance(getattr(cls, var), Document)
