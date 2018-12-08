import asyncio

import odm
from odm.type import MongoType, MongoId

# This represents a dictionary where each key is a class that extends Document.
# The value is a dictionary where the key is the column name and the value is (an instance of the) type of that column
class_col_mappings = {}


def id_field_from_class(cls) -> str:
    """

    :param cls:
    :return: A str of the field that is the _id document
    """
    cols = class_col_mappings[cls]
    for key, val in cols.items():
        if isinstance(val, MongoId):
            return key
    raise ValueError('Cannot find _id field on class to persist')


class Registrar(type):
    """
    Metaclass that registers documents to fill the ODM
    """

    def __init__(cls, name, bases, namespace):
        super().__init__(cls)
        print('here in __init__ of registrar', name, bases)

        columns = {}
        collection_name = ''
        for var in list(vars(cls).keys()):  # copy .keys() so we don't get RuntimeError: dict changed size in iteration
            class_var = getattr(cls, var)
            if isinstance(class_var, MongoType):
                # create the properties on all of the fields recognized as MongoType
                columns[var] = class_var  # .__class__
                # setattr(cls, var, None)

            elif class_var.__class__ in list(class_col_mappings.keys()):
                columns[var] = class_var  # .__class__

            elif var == '__collection_name__':
                print('the collection name is: ' + class_var)
                collection_name = class_var

        class_col_mappings[cls] = columns
        if collection_name:
            for field_name, val in class_col_mappings[cls].items():
                if hasattr(val, 'unique') and val.unique:
                    # can't have async/await in __init__, so we must ensure_future to run this thing
                    # also, we don't know what the db_name will be UNTIL the user initializes their app with their
                    # event loop/db_name. So we should add this Task onto a list of Tasks that gets executed
                    # when initialize_asyncio_motor_client() is called?
                    odm._unique_indexes_to_create.append({'collection_name': collection_name, 'field_name': field_name})
                setattr(cls, field_name, None)

        def __init__(self, **kwargs):
            """
            The new monkey-patched constructor for the subclass that has this metaclass.

            :param self: The regular 'self' that is given on object instantiation
            :param kwargs: The keyword args that are passed to be populated onto the attributes of 'self'
            :return: None
            """
            for key, val in kwargs.items():
                if key in columns.keys():
                    if isinstance(val, dict):
                        # find the type of this 'key' from the class_col_mappings and then call the
                        # constructor of that class with the 'val' here
                        nested_obj = class_col_mappings[self.__class__][key].__class__(**val)
                        setattr(self, key, nested_obj)
                    # set the property to the value provided
                    else:
                        setattr(self, key, val)
                else:
                    # otherwise we don't recognize it as a MongoType column
                    raise ValueError(f'Incorrect keyword argument "{key}"')

        cls.__init__ = __init__
