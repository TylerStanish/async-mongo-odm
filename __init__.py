import json

from motor.motor_asyncio import AsyncIOMotorClient

from odm.type import MongoType

client = AsyncIOMotorClient()

from bson import ObjectId

from .meta import Registrar


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
        Serializes all properties of a given object
        :return: A dict of the property variables
        """
        pass

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
        pass

    @classmethod
    def from_id(cls, id_str: str):
        ObjectId(id_str)
        pass

    @classmethod
    def find_one(cls):
        pass

    def save(self):
        pass
