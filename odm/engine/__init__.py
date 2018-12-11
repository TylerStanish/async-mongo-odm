import asyncio
import json

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

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

    return Document


def _init_registrar(self, cls, name, bases, namespace):
    print('here in __init__ of registrar', name, bases)

    columns = {}
    collection_name = ''
    for var in list(vars(cls).keys()):  # copy .keys() so we don't get RuntimeError: dict changed size in iteration
        class_var = getattr(cls, var)
        if isinstance(class_var, MongoType):
            # create the properties on all of the fields recognized as MongoType
            columns[var] = class_var

        elif class_var.__class__ in list(self.class_col_mappings.keys()):
            columns[var] = class_var

        elif var == '__collection_name__':
            print('the collection name is: ' + class_var)
            collection_name = class_var

    self.class_col_mappings[cls] = columns
    if collection_name:
        for field_name, val in self.class_col_mappings[cls].items():
            if hasattr(val, 'unique') and val.unique:
                collection = getattr(getattr(self.client, self.db_name), collection_name)
                collection.create_index(field_name, unique=True)

            setattr(cls, field_name, None)  # lastly initialize that field value None

    def __init__(self1, **kwargs):
        """
        The new monkey-patched constructor for the subclass that has the Registrar metaclass.

        :param self1: The regular 'self' that is given on object instantiation
        :param kwargs: The keyword args that are passed to be populated onto the attributes of 'self'
        :return: None
        """
        for key, val in kwargs.items():
            if key in columns.keys():
                if isinstance(val, dict):
                    # find the type of this 'key' from the class_col_mappings and then call the
                    # constructor of that class with the 'val' here
                    nested_obj = self.class_col_mappings[self1.__class__][key].__class__(**val)
                    setattr(self1, key, nested_obj)
                # set the property to the value provided
                else:
                    setattr(self1, key, val)
            else:
                # otherwise we don't recognize it as a MongoType column
                raise ValueError(f'Incorrect keyword argument "{key}"')

    cls.__init__ = __init__


class Engine:
    def __init__(self, db_name: str, host: str = 'localhost', port: int = 27017,
                 loop: asyncio.AbstractEventLoop = None):
        self.client = AsyncIOMotorClient(host=host, port=port, io_loop=loop if loop else asyncio.get_event_loop())
        self.db_name = db_name
        self.class_col_mappings = {}
        self._unique_indexes_to_create = []


        class Registrar(type):
            def __init__(cls, name, bases, namespace):
                super().__init__(cls)
                _init_registrar(self, cls, name, bases, namespace)


        self.Document = _document_factory(Registrar, self)
