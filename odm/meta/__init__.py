from odm.type import MongoType


def _init_registrar(engine, registrar_cls):

    fields = {}
    collection_name = ''
    for field_name, value in list(vars(registrar_cls).items()):
        if isinstance(value, MongoType):
            # create the properties on all of the fields recognized as MongoType
            fields[field_name] = value

        elif value.__class__ in list(engine.class_col_mappings.keys()):  # meaning an already registered subclass exists
            fields[field_name] = value

        elif field_name == '__collection_name__':
            print('the collection name is: ' + value)
            collection_name = value

    # add the fields dict {'JSON key value': 'Type/Class of that key'} for later use/reference
    engine.class_col_mappings[registrar_cls] = fields

    if collection_name:  # if the user wants to create a collection for this Document
        for field_name, val in fields.items():
            if hasattr(val, 'unique') and val.unique:
                collection = getattr(getattr(engine.client, engine.db_name), collection_name)
                collection.create_index(field_name, unique=True)

            setattr(registrar_cls, field_name, getattr(val, 'default'))  # initialize that field to the default set

    def __init__(self, **kwargs):
        """
        The new monkey-patched constructor for the subclass that extends from Document and
        thus has the Registrar metaclass.

        :param self: The regular 'self' that is given on object instantiation
        :param kwargs: The keyword args that are passed to be populated onto the attributes of 'self'
        :return: An object extending Document
        """
        for field_name, val in kwargs.items():
            if field_name in fields.keys():
                if isinstance(val, dict):
                    # find the type of this 'field_name' from the class_col_mappings and then call the
                    # constructor of that class with the unpacked 'val' here
                    nested_obj = engine.class_col_mappings[self.__class__][field_name].__class__(**val)
                    setattr(self, field_name, nested_obj)
                else:
                    setattr(self, field_name, val)
            else:
                # otherwise we don't recognize it as a MongoType column
                raise ValueError(f'Incorrect keyword argument "{field_name}"')

    registrar_cls.__init__ = __init__
