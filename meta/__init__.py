# This represents a dictionary where each key is a class that extends Document.
# The value is a dictionary where the key is the column name and the value is the type of that column
from odm.type import MongoType, MongoId

class_col_mappings = {}


def id_field_from_class(cls) -> str:
    """

    :param cls:
    :return: A str of the field that is the _id document
    """
    cols = class_col_mappings[cls]
    for key, val in cols.items():
        if val == MongoId:
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
        for var in list(vars(cls).keys()):  # copy .keys() so we don't get RuntimeError: dict changed size in iteration
            if isinstance(getattr(cls, var), MongoType):
                # create the properties on all of the fields recognized as MongoType
                columns[var] = getattr(cls, var).__class__
                setattr(cls, var, None)

            elif getattr(cls, var).__class__ in list(class_col_mappings.keys()):
                columns[var] = getattr(cls, var).__class__

            elif var == '__collection_name__':
                print('the collection name is: ' + getattr(cls, var))

        class_col_mappings[cls] = columns

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
                        nested_obj = class_col_mappings[self.__class__][key](**val)
                        setattr(self, key, nested_obj)
                    # set the property to the value provided
                    else:
                        setattr(self, key, val)
                else:
                    # otherwise we don't recognize it as a MongoType column
                    raise ValueError(f'Incorrect keyword argument "{key}"')

        cls.__init__ = __init__
